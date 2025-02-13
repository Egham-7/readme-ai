from pydantic import BaseModel, HttpUrl
from typing import Dict, Optional, Any


class ErrorResponse(BaseModel):
    status: str = "error"
    message: str
    error_code: str
    details: Optional[Dict[str, Any]] = None
    timestamp: str


class RepoRequest(BaseModel):
    repo_url: HttpUrl
    branch: Optional[str] = "main"
    template_id: Optional[int] = None
