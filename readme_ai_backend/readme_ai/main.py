from typing import Optional, Union
from datetime import datetime
from fastapi import (
    FastAPI,
    HTTPException,
    Depends,
    status,
    Request,
    Query,
    Form,
    UploadFile,
)
from fastapi.middleware.cors import CORSMiddleware
from readme_ai.agents.repo_analyzer import RepoAnalyzerAgent
from readme_ai.agents.readme_agent import ReadmeCompilerAgent
from readme_ai.models.template import Template
from readme_ai.settings import get_settings, MissingEnvironmentVariable
from dotenv import load_dotenv
from hypercorn.config import Config
from hypercorn.asyncio import serve
import asyncio
from fastapi.responses import JSONResponse
from readme_ai.repositories.template_repository import TemplateRepository
from readme_ai.services.template_service import TemplateService
from readme_ai.services.miniio_service import MinioService, get_minio_service
from readme_ai.models.responses.template import TemplatesResponse, TemplateResponse
from readme_ai.logging_config import logger
from readme_ai.database import get_db
from readme_ai.models.requests.readme import ErrorResponse, RepoRequest
from readme_ai.auth import require_auth, ClerkUser

from sqlalchemy.ext.asyncio import AsyncSession

from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from readme_ai.auth import AuthenticationError  # type: ignore

# Load environment variables and configure logging
load_dotenv()

try:
    settings = get_settings()
except MissingEnvironmentVariable as e:
    print(f"Configuration error: {e.message}")
    exit(1)


# Initialize agents at startup
repo_analyzer: Optional[RepoAnalyzerAgent] = None
readme_compiler: Optional[ReadmeCompilerAgent] = None


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    debug=settings.DEBUG,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(AuthenticationError)
async def authentication_error_handler(request: Request, exc: AuthenticationError):
    return JSONResponse(
        status_code=401,
        content={
            "message": "Authentication failed",
            "error_code": "UNAUTHORIZED",
            "details": {
                "reason": exc.detail,
            },
            "timestamp": datetime.now().isoformat(),
        },
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
app.add_exception_handler(RateLimitExceeded, custom_rate_limit_handler)  # type: ignore


@app.get("/")
@limiter.limit("10/minute")
@require_auth()
async def root(request: Request):
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
@require_auth()
async def generate_readme(request: Request, repo_request: RepoRequest):
    """Generate README asynchronously"""
    timestamp = datetime.now().isoformat()

    repo_analyzer = RepoAnalyzerAgent(github_token=settings.GITHUB_TOKEN)
    readme_compiler = ReadmeCompilerAgent()

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
        repo_analysis = await repo_analyzer.analyze_repo(
            repo_url=str(repo_request.repo_url)
        )

        if repo_analysis.get("status") == "error":
            return JSONResponse(
                status_code=422,
                content=ErrorResponse(
                    message="Repository analysis failed",
                    error_code="ANALYSIS_FAILED",
                    details={
                        "repo_url": str(repo_request.repo_url),
                        "error_message": repo_analysis.get("message", "Unknown error"),
                        "branch": repo_request.branch,
                    },
                    timestamp=timestamp,
                ).model_dump(),
            )

        # Generate README with formatted analysis
        readme_content = await readme_compiler.gen_readme(
            repo_url=str(repo_request.repo_url), repo_analysis=repo_analysis["analysis"]
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
                details={"error_type": type(e).__name__, "error_message": str(e)},
                timestamp=timestamp,
            ).dict(),
        )


@app.post(
    "/templates/", response_model=TemplateResponse, status_code=status.HTTP_201_CREATED
)
@limiter.limit("10/minute")
@require_auth()
async def create_template(
    request: Request,
    content: str = Form(...),
    preview_file: UploadFile = Form(None),
    db: AsyncSession = Depends(get_db),
    minio_service: MinioService = Depends(get_minio_service),
):
    timestamp = datetime.now().isoformat()
    user: ClerkUser = request.state.user
    try:
        preview_image_bytes = await preview_file.read() if preview_file else None
        repository = TemplateRepository(db)
        service = TemplateService(repository, minio_service)
        template = await service.create_template(
            content=content,
            user_id=user.get_user_id(),
            preview_image=preview_image_bytes,
        )
        template_dict = template.to_dict()

        logger.info(f"Template Dict: {template_dict} ")

        template_response = TemplateResponse(**template_dict)

        logger.info(f"Templaate Response: {template_response}")

        return template_response

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
@limiter.limit("20/minute")
@require_auth()
async def get_template(
    request: Request,
    template_id: int,
    db: AsyncSession = Depends(get_db),
    minio_service: MinioService = Depends(get_minio_service),
):
    timestamp = datetime.now().isoformat()
    user: ClerkUser = request.state.user
    try:
        repository = TemplateRepository(db)
        service = TemplateService(repository, minio_service)
        template = await service.get_template(template_id)

        if template is None:
            raise HTTPException(status_code=404, detail="Template not found")

        if template.user_id != user.get_user_id():
            raise AuthenticationError("Not allowed to view this template.")

        template_dict = template.to_dict()

        return TemplateResponse(**template_dict)

    except HTTPException as he:
        raise he

    except AuthenticationError as ae:
        raise ae
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


@app.get("/templates/user/{user_id}", response_model=TemplatesResponse)
@limiter.limit("20/minute")
@require_auth()
async def get_user_templates(
    request: Request,
    user_id: str,
    db: AsyncSession = Depends(get_db),
    minio_service: MinioService = Depends(get_minio_service),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=10, ge=1, le=100),
):
    timestamp = datetime.now().isoformat()
    user: ClerkUser = request.state.user

    if user_id != user.get_user_id():
        raise AuthenticationError("Not allowed to view this template.")

    try:
        repository = TemplateRepository(db)
        service = TemplateService(repository, minio_service)
        templates, total_pages = await service.get_all_by_user_id(
            user_id=user_id, page=page, page_size=page_size
        )

        templates_dict = [template.to_dict() for template in templates]

        return TemplatesResponse(data=templates_dict, total_pages=total_pages)

    except HTTPException as he:
        raise he

    except Exception as e:
        logger.error(f"Error retrieving user templates: {str(e)}")
        return JSONResponse(
            status_code=500,
            content=ErrorResponse(
                message="Internal server error while retrieving user templates.",
                error_code="INTERNAL_SERVER_ERROR",
                details={"error_type": type(e).__name__, "error_message": str(e)},
                timestamp=timestamp,
            ).dict(),
        )


@app.get("/templates/", response_model=TemplatesResponse)
@limiter.limit("20/minute")
@require_auth()
async def get_all_templates(
    request: Request,
    db: AsyncSession = Depends(get_db),
    minio_service: MinioService = Depends(get_minio_service),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=10, ge=1, le=100),
):
    timestamp = datetime.now().isoformat()

    try:
        repository = TemplateRepository(db)
        service = TemplateService(repository, minio_service)

        templates, total_pages = await service.get_all_templates(
            page=page, page_size=page_size
        )

        templates_dict = [template.to_dict() for template in templates]

        return TemplatesResponse(data=templates_dict, total_pages=total_pages)

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
@limiter.limit("10/minute")
@require_auth()
async def update_template(
    request: Request,
    template_id: int,
    content: str = Form(...),
    preview_file: UploadFile = Form(None),
    db: AsyncSession = Depends(get_db),
    minio_service: MinioService = Depends(get_minio_service),
) -> Union[TemplateResponse, JSONResponse]:
    timestamp = datetime.now().isoformat()
    user: ClerkUser = request.state.user

    try:
        repository = TemplateRepository(db)
        service = TemplateService(repository, minio_service)

        template = await service.get_template(template_id)

        if not template:
            raise HTTPException(status_code=404, detail="Template not found")

        if template.user_id != user.get_user_id():
            raise AuthenticationError("Not allowed to update this template.")

        preview_image_bytes = await preview_file.read() if preview_file else None
        updated_template: Template = await service.update_template(
            template_id, content, preview_image=preview_image_bytes
        )

        template_dict = updated_template.to_dict()

        return TemplateResponse(**template_dict)

    except HTTPException as he:
        raise he

    except AuthenticationError as ae:
        raise ae
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
@limiter.limit("10/minute")
@require_auth()
async def delete_template(
    request: Request,
    template_id: int,
    db: AsyncSession = Depends(get_db),
    minio_service: MinioService = Depends(get_minio_service),
):
    timestamp = datetime.now().isoformat()
    user: ClerkUser = request.state.user

    try:
        repository = TemplateRepository(db)
        service = TemplateService(repository, minio_service)

        template = await service.get_template(template_id)

        if not template:
            raise HTTPException(status_code=404, detail="Template not found.")

        if template.user_id != user.get_user_id():
            raise AuthenticationError("Not allowed to delete this template")

        await service.delete_template(template_id)

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
