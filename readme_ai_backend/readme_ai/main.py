# type: ignore
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, HttpUrl
from typing import Optional
from readme_ai.repo_analyzer import RepoAnalyzerAgent
from readme_ai.readme_agent import ReadmeCompilerAgent
from readme_ai.settings import get_settings
from dotenv import load_dotenv
import logging
from hypercorn.config import Config
from hypercorn.asyncio import serve
import asyncio
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager

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


@asynccontextmanager
async def lifespan(_):
    # Initialize agents on startup
    global repo_analyzer, readme_compiler
    repo_analyzer = RepoAnalyzerAgent(github_token=settings.GITHUB_TOKEN)
    readme_compiler = ReadmeCompilerAgent()
    logger.info("Initialized AI agents")
    yield
    # Cleanup on shutdown
    if hasattr(repo_analyzer, "session"):
        await repo_analyzer.session.close()
    logger.info("Cleaned up resources")


# Initialize FastAPI app with lifespan
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    debug=settings.DEBUG,
    lifespan=lifespan,
)

# Configure CORS
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
    """Generate README asynchronously"""
    try:
        if not repo_analyzer or not readme_compiler:
            raise RuntimeError("Services not properly initialized")

        # Get repository analysis
        repo_analysis = await repo_analyzer.analyze_repo(repo_url=str(request.repo_url))

        # Handle analysis errors
        if repo_analysis.get("status") == "error":
            return JSONResponse(
                status_code=422,
                content={
                    "status": "error",
                    "message": "Repository analysis failed",
                    "details": repo_analysis.get("message", "Unknown error"),
                },
            )

        # Generate README with formatted analysis
        readme_content = await readme_compiler.gen_readme(
            repo_url=request.repo_url, repo_analysis=repo_analysis["analysis"]
        )

        logger.info("README generation completed successfully")

        return readme_content["readme"]

    except ValueError as ve:
        logger.error(f"Validation error: {str(ve)}")
        return JSONResponse(
            status_code=400,
            content={
                "status": "error",
                "message": "Invalid input parameters",
                "details": str(ve),
            },
        )
    except Exception as e:
        logger.error(f"README generation error: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={
                "status": "error",
                "message": "Internal server error during README generation",
                "error_code": type(e).__name__,
                "details": str(e),
            },
        )


if __name__ == "__main__":
    config = Config()
    asyncio.run(serve(app, config))
