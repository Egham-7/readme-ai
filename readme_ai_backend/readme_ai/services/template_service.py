from typing import List, Optional
import io
from typing_extensions import Tuple
from readme_ai.repositories.template_repository import TemplateRepository
from readme_ai.models.template import Template
from readme_ai.services.miniio_service import MinioService
import math


class TemplateService:
    def __init__(
        self, template_repository: TemplateRepository, minio_service: MinioService
    ):
        self.repository = template_repository
        self.minio_service = minio_service

    async def create_template(
        self,
        title: str,
        content: str,
        user_id: str,
        preview_image: Optional[bytes] = None,
    ) -> Template:
        try:
            preview_file_name = None
            if preview_image:
                image_stream = io.BytesIO(preview_image)
                preview_file_name = self.minio_service.upload_file(
                    image_stream, "image/png"
                )
            return await self.repository.create(
                title=title,
                content=content,
                user_id=user_id,
                preview_image=preview_file_name,
            )
        except Exception as e:
            raise Exception(f"Failed to create template: {str(e)}")

    async def update_template(
        self,
        template_id: int,
        title: str,
        content: str,
        preview_image: Optional[bytes] = None,
    ) -> Template:
        template = await self.repository.get_by_id(template_id)
        if not template:
            raise Exception(f"Template with id {template_id} not found")

        try:
            if preview_image:
                if template.preview_image:
                    self.minio_service.delete_file(template.preview_image)
                image_stream = io.BytesIO(preview_image)
                preview_file_name = self.minio_service.upload_file(
                    image_stream, "image/png"
                )
                template_with_image = await self.repository.update(
                    template_id, title, content, preview_file_name
                )
                if not template_with_image:
                    raise Exception(f"Failed to update template with id {template_id}")
                return template_with_image

            template = await self.repository.update(template_id, title, content)
            if not template:
                raise Exception(f"Failed to update template with id {template_id}")
            return template
        except Exception as e:
            raise Exception(f"Failed to update template: {str(e)}")

    # Other methods remain unchanged
    async def get_template(self, template_id: int) -> Optional[Template]:
        template = await self.repository.get_by_id(template_id)
        if not template:
            return None
        if not template.preview_image:
            return template
        try:
            template.preview_url = self.minio_service.get_file_url(
                template.preview_image
            )
        except Exception as e:
            raise Exception(f"Failed to get preview URL: {str(e)}")
        return template

    async def get_all_templates(
        self, page: int = 1, page_size: int = 10
    ) -> Tuple[List[Template], int]:
        try:
            templates = await self.repository.get_all(page=page, page_size=page_size)
            total_count = await self.repository.get_total_count()
            total_pages = math.ceil(total_count / page_size)
            for template in templates:
                if not template.preview_image:
                    continue
                template.preview_url = self.minio_service.get_file_url(
                    template.preview_image
                )
            return templates, total_pages
        except Exception as e:
            raise Exception(f"Failed to fetch templates: {str(e)}")

    async def delete_template(self, template_id: int) -> bool:
        template = await self.repository.get_by_id(template_id)
        if not template:
            raise Exception(f"Template with id {template_id} not found")
        try:
            if template.preview_image:
                self.minio_service.delete_file(template.preview_image)
            return await self.repository.delete(template_id)
        except Exception as e:
            raise Exception(f"Failed to delete template: {str(e)}")

    async def get_all_by_user_id(
        self, user_id: str, page: int = 1, page_size: int = 10
    ) -> Tuple[List[Template], int]:
        try:
            templates = await self.repository.get_all_by_user_id(
                user_id=user_id, page=page, page_size=page_size
            )
            total_count = await self.repository.get_total_count_by_user_id(user_id)
            total_pages = math.ceil(total_count / page_size)
            for template in templates:
                if template.preview_image:
                    template.preview_url = self.minio_service.get_file_url(
                        template.preview_image
                    )
            return templates, total_pages
        except Exception as e:
            raise Exception(f"Failed to fetch user templates: {str(e)}")
