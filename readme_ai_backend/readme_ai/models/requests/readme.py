from pydantic import BaseModel
from typing import Dict, Optional, Any


class ErrorResponse(BaseModel):
    status: str = "error"
    message: str
    error_code: str
    details: Optional[Dict[str, Any]] = None
    timestamp: str
