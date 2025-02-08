from typing import List, Optional
import io
from readme_ai.repositories.template_repository import TemplateRepository
from readme_ai.models.template import Template
from readme_ai.services.miniio_service import MinioService  # type: ignore


class TemplateService:
    def __init__(
        self, template_repository: TemplateRepository, minio_service: MinioService
    ):
        self.repository = template_repository
        self.minio_service = minio_service

    def create_template(
        self,
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
            return self.repository.create(
                content=content, user_id=user_id, preview_image=preview_file_name
            )
        except Exception as e:
            raise Exception(f"Failed to create template: {str(e)}")

    def get_template(self, template_id: int) -> Template:
        template = self.repository.get_by_id(template_id)
        if not template:
            raise Exception(f"Template with id {template_id} not found")

        if template.preview_image:
            try:
                template.preview_url = self.minio_service.get_file_url(
                    template.preview_image
                )
            except Exception as e:
                raise Exception(f"Failed to get preview URL: {str(e)}")
        return template

    def get_all_templates(self) -> List[Template]:
        try:
            templates = self.repository.get_all()
            for template in templates:
                if template.preview_image:
                    template.preview_url = self.minio_service.get_file_url(
                        template.preview_image
                    )
            return templates
        except Exception as e:
            raise Exception(f"Failed to fetch templates: {str(e)}")

    def update_template(
        self, template_id: int, content: str, preview_image: Optional[bytes] = None
    ) -> Template:
        template = self.repository.get_by_id(template_id)
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
                template_with_image = self.repository.update(
                    template_id, content, preview_file_name
                )

                if not template_with_image:
                    raise Exception(f"Failed to update template with id {template_id}")

                return template_with_image

            template = self.repository.update(template_id, content)

            if not template:
                raise Exception(f"Failed to update template with id {template_id}")

            return template
        except Exception as e:
            raise Exception(f"Failed to update template: {str(e)}")

    def delete_template(self, template_id: int) -> bool:
        template = self.repository.get_by_id(template_id)
        if not template:
            raise Exception(f"Template with id {template_id} not found")

        try:
            if template.preview_image:
                self.minio_service.delete_file(template.preview_image)
            return self.repository.delete(template_id)
        except Exception as e:
            raise Exception(f"Failed to delete template: {str(e)}")
