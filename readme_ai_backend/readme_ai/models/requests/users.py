from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class UserUpdate(BaseModel):
    email: Optional[str] = None
    tokens_balance: Optional[int] = None
    tokens_last_reset: Optional[datetime] = None
    stripe_customer_id: Optional[str] = None
