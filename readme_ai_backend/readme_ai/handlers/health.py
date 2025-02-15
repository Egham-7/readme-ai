from fastapi import APIRouter, Request
from slowapi import Limiter
from slowapi.util import get_remote_address
from readme_ai.auth import require_auth
from readme_ai.settings import get_settings

settings = get_settings()
router = APIRouter(tags=["health"])
limiter = Limiter(key_func=get_remote_address)


@router.get("/")
@limiter.limit("10/minute")
@require_auth()
async def root(request: Request):
    """Health check endpoint"""
    return {
        "status": "online",
        "version": settings.APP_VERSION,
        "services": {
            "analyzer": True,
            "compiler": True,
        },
    }

