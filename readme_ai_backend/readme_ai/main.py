# type: ignore
from fastapi import FastAPI, HTTPException
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

# Load environment variables and configure logging
load_dotenv()
settings = get_settings()
logging.basicConfig(level=logging.DEBUG)
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
    return {"status": "online", "version": settings.APP_VERSION}


# Update the generate_readme endpoint to use the correct method name
@app.post("/generate-readme")
async def generate_readme(request: RepoRequest):
    """Generate README asynchronously"""
    try:
        # Get repository analysis
        repo_analysis = repo_analyzer.analyze_repo(repo_url=str(request.repo_url))

        # Convert analysis results to proper format
        formatted_analysis = {
            "files": str(repo_analysis),
            "repo_url": str(request.repo_url),
        }

        # Generate README with formatted analysis
        readme_content = readme_compiler.gen_readme(
            repo_url=request.repo_url, repo_analysis=formatted_analysis["files"]
        )

        return {
            "status": "completed",
            "content": readme_content["readme"],
            "repo_url": str(request.repo_url),
            "analysis": formatted_analysis,
        }
    except Exception as e:
        logger.error(f"Error in README generation: {str(e)}")
        raise HTTPException(
            status_code=500, detail=f"Failed to generate README: {str(e)}"
        )


if __name__ == "__main__":
    asyncio.run(serve(app, Config()))
