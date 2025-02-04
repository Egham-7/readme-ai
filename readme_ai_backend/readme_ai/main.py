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
        cached_result = cache_service.get(str(request.repo_url))
        if cached_result:
            elapsed_time = time.time() - start_time
            logger.info(f"Cache hit - Retrieved result in {elapsed_time:.2f} seconds")
            return cached_result

        # Cache miss - proceed with generation
        logger.info(f"Cache miss for {request.repo_url} - Generating new README")

        # Repository analysis
        repo_analyzer = RepoAnalyzerAgent(
            github_token=settings.GITHUB_TOKEN,
        )
        repo_analysis = repo_analyzer.analyze_repo(repo_url=str(request.repo_url))
    
        formatted_analysis = {
            "files": str(repo_analysis),
            "repo_url": str(request.repo_url),
        }

        # Generate README
        readme_compiler = ReadmeCompilerAgent(
            groq_api_key=settings.GROQ_API_KEY,
        )
        readme_content = readme_compiler.gen_readme(
            repo_url=request.repo_url,
            repo_analysis=formatted_analysis["files"]
        )

        response = {
            "status": "completed",
            "content": readme_content["readme"],
            "repo_url": str(request.repo_url),
            "analysis": formatted_analysis,
        }
        print("RESULT: ",readme_content["readme"])
        # Store in cache
        # In generate_readme()
        content = readme_content["readme"]
        cache_service.set(repo_url=str(request.repo_url), content=content)

        elapsed_time = time.time() - start_time
        logger.info(f"Generated and cached README in {elapsed_time:.2f} seconds")
        
        return response

    except Exception as e:
        elapsed_time = time.time() - start_time
        logger.error(f"Error generating README after {elapsed_time:.2f} seconds: {str(e)}")
        raise HTTPException(
            status_code=500, detail=f"Failed to generate README: {str(e)}"
        )

@app.post("/clear-cache")
async def clear_cache(request: RepoRequest):
    """Clear cache for a specific repository"""
    cache_key = cache_service._generate_cache_key(str(request.repo_url))
    cache_service.delete(cache_key)
    return {"status": "success", "message": "Cache cleared"}

if __name__ == "__main__":
    logger.info("Starting README Generation Service...")
    asyncio.run(serve(app, Config()))
