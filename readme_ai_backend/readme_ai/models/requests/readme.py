from typing import List, Optional, Any, Dict
from datetime import datetime
from pydantic import BaseModel


class ErrorResponse(BaseModel):
    status: str = "error"
    message: str
    error_code: str
    details: Optional[Dict[str, Any]] = None
    timestamp: str


class ChatMessageBase(BaseModel):
    role: str
    content: str


class ChatMessageCreate(ChatMessageBase):
    pass


class ChatMessage(ChatMessageBase):
    id: int
    readme_id: int
    created_at: datetime
    readme_version_id: Optional[int]

    class Config:
        from_attributes = True


class ReadmeVersionBase(BaseModel):
    content: str


class ReadmeVersion(ReadmeVersionBase):
    id: int
    readme_id: int
    version_number: int
    created_at: datetime

    class Config:
        from_attributes = True


class ReadmeBase(BaseModel):
    repository_url: str
    title: str


class Readme(ReadmeBase):
    id: int
    user_id: str
    created_at: datetime
    updated_at: Optional[datetime]
    versions: List[ReadmeVersion]
    chat_messages: List[ChatMessage]

    class Config:
        from_attributes = True


class ReadmeUpdate(BaseModel):
    content: str
