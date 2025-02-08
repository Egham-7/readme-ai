from functools import wraps
from fastapi import HTTPException, Request
from clerk_backend_api import Clerk
from clerk_backend_api.jwks_helpers import (
    AuthenticateRequestOptions,
)
from readme_ai.settings import get_settings

settings = get_settings()
clerk = Clerk(bearer_auth=settings.CLERK_SECRET_KEY)


class AuthenticationError(HTTPException):
    def __init__(self, detail: str):
        super().__init__(status_code=401, detail=detail)


def require_auth():
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            request = next((arg for arg in args if isinstance(arg, Request)), None)
            if not request:
                raise HTTPException(status_code=400, detail="No request object found")

            try:
                request_state = clerk.authenticate_request(
                    request,
                    AuthenticateRequestOptions(authorized_parties=[settings.APP_URL]),
                )

                if not request_state.is_signed_in:
                    raise HTTPException(status_code=401, detail="Unauthorized")

                # Add user data to request state
                request.state.user = request_state.payload
                return await func(*args, **kwargs)

            except Exception as e:
                raise HTTPException(status_code=401, detail=str(e))

        return wrapper

    return decorator
