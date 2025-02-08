from pydantic import BaseModel, Field, validator

from typing import Optional
from fastapi import UploadFile


class TemplateCreate(BaseModel):
    content: str = Field(
        min_length=1, max_length=10000, description="Markdown template content"
    )
    preview_file: Optional[UploadFile] = Field(
        default=None, description="Optional preview image (PNG or JPEG, max 5MB)"
    )

    @validator("preview_file")
    def validate_file(cls, v):
        if v:
            if v.content_type not in ["image/png", "image/jpeg", "image/jpg"]:
                raise ValueError("Preview image must be PNG or JPEG format")

            # Read file size
            file_content = v.file.read()
            v.file.seek(0)  # Reset file pointer

            if len(file_content) > 1 * 1024 * 1024:  # 1MB
                raise ValueError("Preview image must be less than 5MB")
        return v

    class Config:
        arbitrary_types_allowed = True


class TemplateUpdate(BaseModel):
    content: str = Field(min_length=1, max_length=10000)
    preview_file: Optional[UploadFile] = None

    class Config:
        arbitrary_types_allowed = True


class TemplateResponse(BaseModel):
    id: int
    content: str
    user_id: Optional[str]
    preview_url: Optional[str]

    class Config:
        from_attributes = True
