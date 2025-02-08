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
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

# Load environment variables and configure logging
load_dotenv()
settings = get_settings()


# Initialize agents at startup
repo_analyzer: Optional[RepoAnalyzerAgent] = None
readme_compiler: Optional[ReadmeCompilerAgent] = None


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


@app.exception_handler(RateLimitExceeded)
async def custom_rate_limit_handler(request, exc):
    print(f"Rate limit exceeded: {repr(exc)}")
    return JSONResponse(
        status_code=429,
        content={
            "message": "Rate limit exceeded",
            "error_code": "RATE_LIMIT_EXCEEDED",
            "details": {
                "limit": str(exc.limit),
                "reset_at": exc.reset_at.isoformat() if exc.reset_at else None,
                "retry_after": exc.retry_after,
            },
            "timestamp": datetime.now().isoformat(),
        },
    )


limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(
    RateLimitExceeded, custom_rate_limit_handler)  # type: ignore


class RepoRequest(BaseModel):
    repo_url: HttpUrl
    branch: Optional[str] = "main"


@app.get("/")
@limiter.limit("10/minute")
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
@limiter.limit("5/minute")
async def generate_readme(request: RepoRequest):
    """Generate README asynchronously"""
    timestamp = datetime.now().isoformat()

    try:
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

        logger.info("README generation completed successfully")
        return {
            "status": "success",
            "data": readme_content["readme"],
            "timestamp": timestamp,
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
                details={"error_type": type(
                    e).__name__, "error_message": str(e)},
                timestamp=timestamp,
            ).dict(),
        )


@app.post(
    "/templates/", response_model=TemplateResponse, status_code=status.HTTP_201_CREATED
)
@limiter.limit("10/minute")
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
                details={"error_type": type(
                    e).__name__, "error_message": str(e)},
                timestamp=timestamp,
            ).dict(),
        )


@app.get("/templates/{template_id}", response_model=TemplateResponse)
@limiter.limit("20/minute")
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
                details={"error_type": type(
                    e).__name__, "error_message": str(e)},
                timestamp=timestamp,
            ).dict(),
        )


@app.get("/templates/", response_model=List[TemplateResponse])
@limiter.limit("20/minute")
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
                details={"error_type": type(
                    e).__name__, "error_message": str(e)},
                timestamp=timestamp,
            ).dict(),
        )


@app.put("/templates/{template_id}", response_model=TemplateResponse)
@limiter.limit("10/minute")
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
                details={"error_type": type(
                    e).__name__, "error_message": str(e)},
                timestamp=timestamp,
            ).dict(),
        )


@app.delete("/templates/{template_id}")
@limiter.limit("10/minute")
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
                details={"error_type": type(
                    e).__name__, "error_message": str(e)},
                timestamp=timestamp,
            ).dict(),
        )


if __name__ == "__main__":
    config = Config()
    asyncio.run(serve(app, config))  # type: ignore
