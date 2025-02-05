from typing import Any, Dict, Optional
from datetime import datetime
import logging
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, HttpUrl
from agents.repo_analyzer import RepoAnalyzerAgent
from agents.readme_agent import ReadmeCompilerAgent
from readme_ai.settings import get_settings
from dotenv import load_dotenv
from hypercorn.config import Config
from hypercorn.asyncio import serve
import asyncio
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
from cache_service.cache import CacheService  # type: ignore

# Load environment variables and configure logging
load_dotenv()
settings = get_settings()
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Initialize agents at startup
repo_analyzer: Optional[RepoAnalyzerAgent] = None
readme_compiler: Optional[ReadmeCompilerAgent] = None


class ErrorResponse(BaseModel):
    status: str = "error"
    message: str
    error_code: str
    details: Optional[Dict[str, Any]] = None
    timestamp: str


# Instantiate CacheService
cache_service = CacheService()


@asynccontextmanager
async def lifespan(_):
    global repo_analyzer, readme_compiler
    try:
        repo_analyzer = RepoAnalyzerAgent(github_token=settings.GITHUB_TOKEN)
        readme_compiler = ReadmeCompilerAgent()
        logger.info("Initialized AI agents")
        yield
    except Exception as e:
        logger.error(f"Startup error: {str(e)}")
        raise
    finally:
        if hasattr(repo_analyzer, "session"):
            await repo_analyzer.session.close()
        logger.info("Cleaned up resources")


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    debug=settings.DEBUG,
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class RepoRequest(BaseModel):
    repo_url: HttpUrl
    branch: Optional[str] = "main"


@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "status": "online",
        "version": settings.APP_VERSION,
        "services": {
            "analyzer": repo_analyzer is not None,
            "compiler": readme_compiler is not None,
        },
    }


@app.post("/generate-readme")
async def generate_readme(request: RepoRequest):
    """Generate README asynchronously with caching"""

    # Generate a timestamp string
    timestamp = datetime.now().isoformat()

    try:
        # Check if the repository's README is already cached
        cached_readme = cache_service.get(str(request.repo_url))
        if cached_readme:
            logger.info(f"Returning cached README for {request.repo_url}")
            return {
                "status": "success",
                "data": cached_readme,
                "timestamp": timestamp,
                "cached": True,
            }

        if not repo_analyzer or not readme_compiler:
            raise HTTPException(
                status_code=503,
                detail=ErrorResponse(
                    message="Service unavailable",
                    error_code="SERVICE_UNAVAILABLE",
                    details={
                        "analyzer": repo_analyzer is not None,
                        "compiler": readme_compiler is not None,
                    },
                    timestamp=timestamp,
                ).dict(),
            )

        # Get repository analysis
        repo_analysis = await repo_analyzer.analyze_repo(repo_url=str(request.repo_url))

        if repo_analysis.get("status") == "error":
            return JSONResponse(
                status_code=422,
                content=ErrorResponse(
                    message="Repository analysis failed",
                    error_code="ANALYSIS_FAILED",
                    details={
                        "repo_url": str(request.repo_url),
                        "error_message": repo_analysis.get("message", "Unknown error"),
                        "branch": request.branch,
                    },
                    timestamp=timestamp,
                ).dict(),
            )

        # Generate README with formatted analysis
        readme_content = await readme_compiler.gen_readme(
            repo_url=str(request.repo_url), repo_analysis=repo_analysis["analysis"]
        )

        # Cache the generated README
        cache_service.set(str(request.repo_url), readme_content["readme"])

        logger.info("README generation completed successfully")
        return {
            "status": "success",
            "data": readme_content["readme"],
            "timestamp": timestamp,
            "cached": False,
        }

    except ValueError as ve:
        logger.error(f"Validation error: {str(ve)}")
        return JSONResponse(
            status_code=400,
            content=ErrorResponse(
                message="Invalid input parameters",
                error_code="VALIDATION_ERROR",
                details={"validation_error": str(ve)},
                timestamp=timestamp,
            ).dict(),
        )

    except Exception as e:
        logger.error(f"README generation error: {str(e)}")
        return JSONResponse(
            status_code=500,
            content=ErrorResponse(
                message="Internal server error during README generation",
                error_code="INTERNAL_SERVER_ERROR",
                details={"error_type": type(e).__name__, "error_message": str(e)},
                timestamp=timestamp,
            ).dict(),
        )


@app.post("/generate-readme-with-retries")
async def generate_readme_with_retries(request: RepoRequest):
    """Generate README with retry tracking"""
    try:
        # Generate a timestamp string
        timestamp = datetime.now().isoformat()

        # Check the retry count
        retry_count = cache_service.get_retry_count(str(request.repo_url))

        if retry_count >= 3:
            raise HTTPException(
                status_code=429,
                detail=ErrorResponse(
                    message="Too many retries",
                    error_code="MAX_RETRIES_REACHED",
                    details={"repo_url": str(request.repo_url), "retries": retry_count},
                    timestamp=timestamp,
                ).dict(),
            )

        # Increment retry count
        cache_service.increment_retry_count(str(request.repo_url))

        # Perform the same process as the original endpoint
        if not repo_analyzer or not readme_compiler:
            raise HTTPException(
                status_code=503,
                detail=ErrorResponse(
                    message="Service unavailable",
                    error_code="SERVICE_UNAVAILABLE",
                    details={
                        "analyzer": repo_analyzer is not None,
                        "compiler": readme_compiler is not None,
                    },
                    timestamp=timestamp,
                ).dict(),
            )

        # Get repository analysis
        repo_analysis = await repo_analyzer.analyze_repo(repo_url=str(request.repo_url))

        if repo_analysis.get("status") == "error":
            return JSONResponse(
                status_code=422,
                content=ErrorResponse(
                    message="Repository analysis failed",
                    error_code="ANALYSIS_FAILED",
                    details={
                        "repo_url": str(request.repo_url),
                        "error_message": repo_analysis.get("message", "Unknown error"),
                        "branch": request.branch,
                    },
                    timestamp=timestamp,
                ).dict(),
            )

        # Generate README with formatted analysis
        readme_content = await readme_compiler.gen_readme(
            repo_url=str(request.repo_url), repo_analysis=repo_analysis["analysis"]
        )

        logger.info("README generation completed successfully")
        return {
            "status": "success",
            "data": readme_content["readme"],
            "timestamp": timestamp,
        }

    except ValueError as ve:
        logger.error(f"Validation error: {str(ve)}")
        return JSONResponse(
            status_code=400,
            content=ErrorResponse(
                message="Invalid input parameters",
                error_code="VALIDATION_ERROR",
                details={"validation_error": str(ve)},
                timestamp=datetime.now().isoformat(),
            ).dict(),
        )

    except Exception as e:
        logger.error(f"README generation error: {str(e)}")
        return JSONResponse(
            status_code=500,
            content=ErrorResponse(
                message="Internal server error during README generation",
                error_code="INTERNAL_SERVER_ERROR",
                details={"error_type": type(e).__name__, "error_message": str(e)},
                timestamp=datetime.now().isoformat(),
            ).dict(),
        )


@app.post("/clear-cache")
async def clear_cache():
    """Clear the cache"""
    try:
        cache_service.clear_all_cache()  # Define this method in CacheService if not already
        return {"status": "success", "message": "Cache cleared successfully"}
    except Exception as e:
        logger.error(f"Error clearing cache: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=ErrorResponse(
                message="Internal server error while clearing cache",
                error_code="CACHE_CLEAR_ERROR",
                details={"error_message": str(e)},
                timestamp=datetime.now().isoformat(),
            ).dict(),
        )


if __name__ == "__main__":
    config = Config()
    asyncio.run(serve(app, config))  # type: ignore
