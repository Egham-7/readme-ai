from typing import Optional, List
from datetime import datetime
from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, HttpUrl
from readme_ai.agents.repo_analyzer import RepoAnalyzerAgent
from readme_ai.agents.readme_agent import ReadmeCompilerAgent
from readme_ai.settings import get_settings
from dotenv import load_dotenv
from hypercorn.config import Config
from hypercorn.asyncio import serve
import asyncio
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
from readme_ai.services.cache_service import CacheService  # type: ignore
from readme_ai.repositories.template_repository import TemplateRepository
from readme_ai.services.template_service import TemplateService
from readme_ai.services.miniio_service import MinioService, get_minio_service
from readme_ai.models.requests.templates import (
    TemplateCreate,
    TemplateUpdate,
    TemplateResponse,
)
from readme_ai.logging_config import logger
from readme_ai.database import get_db
from readme_ai.models.requests.readme import ErrorResponse

from sqlalchemy.orm import Session

# Load environment variables and configure logging
load_dotenv()
settings = get_settings()


# Initialize agents at startup
repo_analyzer: Optional[RepoAnalyzerAgent] = None
readme_compiler: Optional[ReadmeCompilerAgent] = None


# Instantiate CacheService
cache_service = CacheService()


@asynccontextmanager
async def lifespan(_):
    global repo_analyzer, readme_compiler
    try:
        repo_analyzer = RepoAnalyzerAgent(github_token=settings.GITHUB_TOKEN)
        readme_compiler = ReadmeCompilerAgent()
        logger.info("Initialized AI agents")
        yield
    except Exception as e:
        logger.error(f"Startup error: {str(e)}")
        raise
    finally:
        if hasattr(repo_analyzer, "session"):
            await repo_analyzer.session.close()
        logger.info("Cleaned up resources")


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    debug=settings.DEBUG,
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class RepoRequest(BaseModel):
    repo_url: HttpUrl
    branch: Optional[str] = "main"


@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "status": "online",
        "version": settings.APP_VERSION,
        "services": {
            "analyzer": repo_analyzer is not None,
            "compiler": readme_compiler is not None,
        },
    }


@app.post("/generate-readme")
async def generate_readme(request: RepoRequest):
    """Generate README asynchronously with caching"""

    # Generate a timestamp string
    timestamp = datetime.now().isoformat()

    try:
        # Check if the repository's README is already cached
        cached_readme = cache_service.get(str(request.repo_url))
        if cached_readme:
            logger.info(f"Returning cached README for {request.repo_url}")
            return {
                "status": "success",
                "data": cached_readme,
                "timestamp": timestamp,
                "cached": True,
            }

        if not repo_analyzer or not readme_compiler:
            raise HTTPException(
                status_code=503,
                detail=ErrorResponse(
                    message="Service unavailable",
                    error_code="SERVICE_UNAVAILABLE",
                    details={
                        "analyzer": repo_analyzer is not None,
                        "compiler": readme_compiler is not None,
                    },
                    timestamp=timestamp,
                ).dict(),
            )

        # Get repository analysis
        repo_analysis = await repo_analyzer.analyze_repo(repo_url=str(request.repo_url))

        if repo_analysis.get("status") == "error":
            return JSONResponse(
                status_code=422,
                content=ErrorResponse(
                    message="Repository analysis failed",
                    error_code="ANALYSIS_FAILED",
                    details={
                        "repo_url": str(request.repo_url),
                        "error_message": repo_analysis.get("message", "Unknown error"),
                        "branch": request.branch,
                    },
                    timestamp=timestamp,
                ).model_dump(),
            )

        # Generate README with formatted analysis
        readme_content = await readme_compiler.gen_readme(
            repo_url=str(request.repo_url), repo_analysis=repo_analysis["analysis"]
        )

        # Cache the generated README
        cache_service.set(str(request.repo_url), readme_content["readme"], 24 * 60 * 60)

        logger.info("README generation completed successfully")
        return {
            "status": "success",
            "data": readme_content["readme"],
            "timestamp": timestamp,
            "cached": False,
        }

    except ValueError as ve:
        logger.error(f"Validation error: {str(ve)}")
        return JSONResponse(
            status_code=400,
            content=ErrorResponse(
                message="Invalid input parameters",
                error_code="VALIDATION_ERROR",
                details={"validation_error": str(ve)},
                timestamp=timestamp,
            ).dict(),
        )

    except Exception as e:
        logger.error(f"README generation error: {str(e)}")
        return JSONResponse(
            status_code=500,
            content=ErrorResponse(
                message="Internal server error during README generation",
                error_code="INTERNAL_SERVER_ERROR",
                details={"error_type": type(e).__name__, "error_message": str(e)},
                timestamp=timestamp,
            ).dict(),
        )


@app.post(
    "/templates/", response_model=TemplateResponse, status_code=status.HTTP_201_CREATED
)
async def create_template(
    template: TemplateCreate,
    db: Session = Depends(get_db),
    minio_service: MinioService = Depends(get_minio_service),
):
    timestamp = datetime.now().isoformat()
    try:
        preview_image_bytes = (
            await template.preview_file.read() if template.preview_file else None
        )
        repository = TemplateRepository(db)
        service = TemplateService(repository, minio_service)
        return service.create_template(
            content=template.content,
            user_id=template.user_id,
            preview_image=preview_image_bytes,
        )
    except Exception as e:
        logger.error(f"Template creation error: {str(e)}")
        return JSONResponse(
            status_code=500,
            content=ErrorResponse(
                message="Internal server error during template creation.",
                error_code="INTERNAL_SERVER_ERROR",
                details={"error_type": type(e).__name__, "error_message": str(e)},
                timestamp=timestamp,
            ).dict(),
        )


@app.get("/templates/{template_id}", response_model=TemplateResponse)
def get_template(
    template_id: int,
    db: Session = Depends(get_db),
    minio_service: MinioService = Depends(get_minio_service),
):
    timestamp = datetime.now().isoformat()
    try:
        repository = TemplateRepository(db)
        service = TemplateService(repository, minio_service)
        template = service.get_template(template_id)
        if template is None:
            raise HTTPException(status_code=404, detail="Template not found")
        return template
    except HTTPException as he:
        raise he
    except Exception as e:
        logger.error(f"Error retrieving template: {str(e)}")
        return JSONResponse(
            status_code=500,
            content=ErrorResponse(
                message="Internal server error while retrieving template.",
                error_code="INTERNAL_SERVER_ERROR",
                details={"error_type": type(e).__name__, "error_message": str(e)},
                timestamp=timestamp,
            ).dict(),
        )


@app.get("/templates/", response_model=List[TemplateResponse])
def get_all_templates(
    db: Session = Depends(get_db),
    minio_service: MinioService = Depends(get_minio_service),
):
    timestamp = datetime.now().isoformat()
    try:
        repository = TemplateRepository(db)
        service = TemplateService(repository, minio_service)
        return service.get_all_templates()
    except Exception as e:
        logger.error(f"Error retrieving all templates: {str(e)}")
        return JSONResponse(
            status_code=500,
            content=ErrorResponse(
                message="Internal server error while retrieving templates.",
                error_code="INTERNAL_SERVER_ERROR",
                details={"error_type": type(e).__name__, "error_message": str(e)},
                timestamp=timestamp,
            ).dict(),
        )


@app.put("/templates/{template_id}", response_model=TemplateResponse)
async def update_template(
    template_id: int,
    template: TemplateUpdate,
    db: Session = Depends(get_db),
    minio_service: MinioService = Depends(get_minio_service),
):
    timestamp = datetime.now().isoformat()
    try:
        repository = TemplateRepository(db)
        service = TemplateService(repository, minio_service)
        preview_image_bytes = (
            await template.preview_file.read() if template.preview_file else None
        )
        updated_template = service.update_template(
            template_id, template.content, preview_image=preview_image_bytes
        )
        if updated_template is None:
            raise HTTPException(status_code=404, detail="Template not found")
        return updated_template
    except HTTPException as he:
        raise he
    except Exception as e:
        logger.error(f"Error updating template: {str(e)}")
        return JSONResponse(
            status_code=500,
            content=ErrorResponse(
                message="Internal server error while updating template.",
                error_code="INTERNAL_SERVER_ERROR",
                details={"error_type": type(e).__name__, "error_message": str(e)},
                timestamp=timestamp,
            ).dict(),
        )


@app.delete("/templates/{template_id}")
def delete_template(
    template_id: int,
    db: Session = Depends(get_db),
    minio_service: MinioService = Depends(get_minio_service),
):
    timestamp = datetime.now().isoformat()
    try:
        repository = TemplateRepository(db)
        service = TemplateService(repository, minio_service)
        if not service.delete_template(template_id):
            raise HTTPException(status_code=404, detail="Template not found")
        return {"message": "Template deleted successfully"}
    except HTTPException as he:
        raise he
    except Exception as e:
        logger.error(f"Error deleting template: {str(e)}")
        return JSONResponse(
            status_code=500,
            content=ErrorResponse(
                message="Internal server error while deleting template.",
                error_code="INTERNAL_SERVER_ERROR",
                details={"error_type": type(e).__name__, "error_message": str(e)},
                timestamp=timestamp,
            ).dict(),
        )


if __name__ == "__main__":
    config = Config()
    asyncio.run(serve(app, config))  # type: ignore
