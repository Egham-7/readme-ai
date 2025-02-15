from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime
from dotenv import load_dotenv
from hypercorn.config import Config
from hypercorn.asyncio import serve
import asyncio

from readme_ai.settings import get_settings, MissingEnvironmentVariable
from readme_ai.auth import AuthenticationError
from readme_ai.logging_config import logger
from readme_ai.models.requests.readme import ErrorResponse

from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from fastapi.responses import JSONResponse

from readme_ai.handlers import health, readme, templates

# Load environment variables
load_dotenv()

# Initialize settings
try:
    settings = get_settings()
except MissingEnvironmentVariable as e:
    print(f"Configuration error: {e.message}")
    exit(1)

# Initialize FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    debug=settings.DEBUG,
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Rate limiter configuration
limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter


# Exception handlers
@app.exception_handler(AuthenticationError)
async def authentication_error_handler(request: Request, exc: AuthenticationError):
    return JSONResponse(
        status_code=401,
        content=ErrorResponse(
            message="Authentication failed",
            error_code="UNAUTHORIZED",
            details={
                "reason": exc.detail,
            },
            timestamp=datetime.now().isoformat(),
        ).dict(),
    )


@app.exception_handler(RateLimitExceeded)
async def custom_rate_limit_handler(request: Request, exc: RateLimitExceeded):
    logger.warning(f"Rate limit exceeded: {repr(exc)}")
    return JSONResponse(
        status_code=429,
        content=ErrorResponse(
            message="Rate limit exceeded",
            error_code="RATE_LIMIT_EXCEEDED",
            details={
                "limit": str(exc.limit),
                "reset_at": exc.reset_at.isoformat() if exc.reset_at else None,
                "retry_after": exc.retry_after,
            },
            timestamp=datetime.now().isoformat(),
        ).dict(),
    )


# Register routers
app.include_router(health.router)
app.include_router(readme.router)
app.include_router(templates.router)

# Register rate limit handler
app.add_exception_handler(RateLimitExceeded, custom_rate_limit_handler)


# Startup and shutdown events
@app.on_event("startup")
async def startup_event():
    logger.info(f"Starting {settings.APP_NAME} v{settings.APP_VERSION}")


@app.on_event("shutdown")
async def shutdown_event():
    logger.info(f"Shutting down {settings.APP_NAME}")


# Main execution
if __name__ == "__main__":
    config = Config()
    config.bind = [f"{settings.HOST}:{settings.PORT}"]
    config.worker_class = "asyncio"
    asyncio.run(serve(app, config))

