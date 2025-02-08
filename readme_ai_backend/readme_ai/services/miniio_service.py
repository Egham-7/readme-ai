from minio import Minio
from typing import BinaryIO
import uuid

from readme_ai.settings import get_settings

settings = get_settings()


class MinioService:
    def __init__(self):
        self.client = Minio(
            endpoint=settings.MINIO_PRIVATE_ENDPOINT,
            access_key=settings.MINIO_ROOT_USER,
            secret_key=settings.MINIO_ROOT_PASSWORD,
            secure=settings.MINIO_SECURE,
        )
        self.bucket_name = "templates"
        self._ensure_bucket_exists()

    def _ensure_bucket_exists(self):
        if not self.client.bucket_exists(self.bucket_name):
            self.client.make_bucket(self.bucket_name)

    def upload_file(self, file_data: BinaryIO, content_type: str) -> str:
        file_id = str(uuid.uuid4())
        file_name = f"{file_id}.png"

        # Get file size
        file_data.seek(0, 2)  # Seek to end
        file_size = file_data.tell()  # Get position (size)
        file_data.seek(0)  # Reset to beginning

        self.client.put_object(
            bucket_name=self.bucket_name,
            object_name=file_name,
            data=file_data,
            length=file_size,
            content_type=content_type,
        )

        return file_name

    def get_file_url(self, file_name: str) -> str:
        return self.client.presigned_get_object(
            bucket_name=self.bucket_name,
            object_name=file_name,
            expires=3600,  # URL expires in 1 hour
        )

    def delete_file(self, file_name: str) -> None:
        self.client.remove_object(self.bucket_name, file_name)


def get_minio_service():
    return MinioService()
