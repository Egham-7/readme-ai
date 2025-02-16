from typing import Union
from fastapi import (
    APIRouter,
    Request,
    Depends,
    Query,
    Form,
    UploadFile,
    HTTPException,
    status,
)
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from readme_ai.auth import require_auth, ClerkUser, AuthenticationError
from readme_ai.database import get_db
from readme_ai.services.miniio_service import MinioService, get_minio_service
from readme_ai.repositories.template_repository import TemplateRepository
from readme_ai.services.template_service import TemplateService
from readme_ai.models.responses.template import TemplatesResponse, TemplateResponse
from readme_ai.models.requests.readme import ErrorResponse
from readme_ai.logging_config import logger
from fastapi.responses import JSONResponse
from slowapi import Limiter
from slowapi.util import get_remote_address

router = APIRouter(prefix="/templates", tags=["templates"])
limiter = Limiter(key_func=get_remote_address)


@router.post("/", response_model=TemplateResponse, status_code=status.HTTP_201_CREATED)
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
        logger.info(f"Template Dict: {template_dict}")
        template_response = TemplateResponse(**template_dict)
        logger.info(f"Template Response: {template_response}")
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


@router.get("/{template_id}", response_model=TemplateResponse)
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


@router.get("/user/{user_id}", response_model=TemplatesResponse)
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


@router.get("/", response_model=TemplatesResponse)
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


@router.put("/{template_id}", response_model=TemplateResponse)
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
        updated_template = await service.update_template(
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


@router.delete("/{template_id}")
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
