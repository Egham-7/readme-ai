from typing import Optional
from datetime import datetime, timezone
from pydantic import BaseModel, EmailStr, Field


class UserResponse(BaseModel):
    id: int
    clerk_id: str
    email: EmailStr
    tokens_balance: int = Field(default=0)
    tokens_last_reset: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )
    stripe_customer_id: Optional[str] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    class Config:
        from_attributes = True
