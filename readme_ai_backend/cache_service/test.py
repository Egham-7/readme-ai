from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, HttpUrl
from typing import Optional
from readme_ai.repo_analyzer import RepoAnalyzerAgent
from readme_ai.readme_agent import ReadmeCompilerAgent
from readme_ai.settings import get_settings
from dotenv import load_dotenv
import logging
import time
from hypercorn.config import Config
from hypercorn.asyncio import serve
import asyncio
from cache_service.cache import CacheService

# Initialize cache service
cache_service = CacheService()

# Load environment variables and configure logging
load_dotenv()
settings = get_settings()

# Enhanced logging configuration
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title=settings.APP_NAME, version=settings.APP_VERSION, debug=settings.DEBUG
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize both agents
repo_analyzer = RepoAnalyzerAgent(
    github_token=settings.GITHUB_TOKEN, groq_api_key=settings.GROQ_API_KEY
)

readme_compiler = ReadmeCompilerAgent(
    groq_api_key=settings.GROQ_API_KEY,
)

class RepoRequest(BaseModel):
    repo_url: HttpUrl
    branch: Optional[str] = "main"

@app.get("/")
async def root():
    """Health check endpoint"""
    logger.info("Health check endpoint accessed")
    return {"status": "online", "version": settings.APP_VERSION}

@app.post("/generate-readme")
async def generate_readme(request: RepoRequest):
    """Generate README asynchronously with caching"""
    start_time = time.time()
    logger.info(f"Starting README generation for repo: {request.repo_url}")

    try:
        # Check cache first
        logger.debug(f"Checking cache for repo: {request.repo_url}")
        cached_result = cache_service.get(str(request.repo_url))
        
        if cached_result:
            elapsed_time = time.time() - start_time
            logger.info(f"Cache HIT! Retrieved result for {request.repo_url} in {elapsed_time:.2f} seconds")
            return cached_result

        logger.info(f"Cache MISS for {request.repo_url}. Proceeding with analysis...")

        # Get repository analysis
        logger.debug("Starting repository analysis...")
        repo_analysis = repo_analyzer.analyze_repo(repo_url=str(request.repo_url))
        logger.info("Repository analysis completed successfully")

        # Convert analysis results to proper format
        formatted_analysis = {
            "files": str(repo_analysis),
            "repo_url": str(request.repo_url),
        }
        logger.debug("Analysis results formatted")

        # Generate README with formatted analysis
        logger.debug("Starting README compilation...")
        readme_content = readme_compiler.gen_readme(
            repo_url=request.repo_url, repo_analysis=formatted_analysis["files"]
        )
        logger.info("README compilation completed successfully")

        # Prepare response
        response = {
            "status": "completed",
            "content": readme_content["readme"],
            "repo_url": str(request.repo_url),
            "analysis": formatted_analysis,
        }

        # Cache the result
        logger.debug(f"Caching results for {request.repo_url}")
        cache_service.set(str(request.repo_url), response)
        logger.info("Results cached successfully")

        elapsed_time = time.time() - start_time
        logger.info(f"README generation completed in {elapsed_time:.2f} seconds")
        
        return response

    except Exception as e:
        elapsed_time = time.time() - start_time
        logger.error(f"Error in README generation after {elapsed_time:.2f} seconds: {str(e)}")
        raise HTTPException(
            status_code=500, detail=f"Failed to generate README: {str(e)}"
        )

@app.post("/clear-cache")
async def clear_cache(request: RepoRequest):
    """Clear cache for a specific repository"""
    logger.info(f"Clearing cache for repo: {request.repo_url}")
    cache_key = cache_service._generate_cache_key(str(request.repo_url))
    cache_service.delete(cache_key)
    logger.info(f"Cache cleared successfully for {request.repo_url}")
    return {"status": "success", "message": "Cache cleared"}

if __name__ == "__main__":
    logger.info("Starting README Generation Service...")
    asyncio.run(serve(app, Config()))
