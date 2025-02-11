from functools import wraps
from fastapi import HTTPException, Request
from clerk_backend_api import Clerk
from clerk_backend_api.jwks_helpers import AuthenticateRequestOptions
from readme_ai.settings import get_settings
from typing import List, Dict, Any, cast
from pydantic import BaseModel
import httpx

settings = get_settings()
clerk = Clerk(bearer_auth=settings.CLERK_SECRET_KEY)


class ClerkUser(BaseModel):
    azp: str
    exp: int
    fva: List[int]
    iat: int
    iss: str
    nbf: int
    sid: str
    sub: str

    def get_user_id(self) -> str:
        return self.sub


class AuthenticationError(HTTPException):
    def __init__(self, detail: str):
        super().__init__(status_code=401, detail=detail)


def require_auth():
    def decorator(func):
        @wraps(func)
        async def wrapper(request: Request, *args, **kwargs):
            try:
                # Convert FastAPI request to httpx request
                httpx_request = httpx.Request(
                    method=request.method,
                    url=str(request.url),
                    headers=dict(request.headers),
                )

                request_state = clerk.authenticate_request(
                    httpx_request,
                    AuthenticateRequestOptions(authorized_parties=[settings.APP_URL]),
                )

                if not request_state.is_signed_in:
                    raise HTTPException(status_code=401, detail="Unauthorized")

                # Convert payload to dict before unpacking
                payload = request_state.payload or {}
                payload_dict = cast(Dict[str, Any], payload)
                request.state.user = ClerkUser(**payload_dict)

                return await func(request, *args, **kwargs)
            except Exception as e:
                raise HTTPException(status_code=401, detail=str(e))

        return wrapper

    return decorator
