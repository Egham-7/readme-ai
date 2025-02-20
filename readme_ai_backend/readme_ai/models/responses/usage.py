from pydantic import BaseModel


class TokenResetResponse(BaseModel):
    current_token: int
    next_reset: str
    time_remaining: int
