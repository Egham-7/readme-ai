from pydantic import BaseModel
from typing import List, Optional


class TemplateResponse(BaseModel):
    id: int
    content: str
    user_id: str
    preview_url: Optional[str]
    featured: bool = False

    class Config:
        from_attributes = True


class TemplatesResponse(BaseModel):
    data: List[TemplateResponse]
    total_pages: int
