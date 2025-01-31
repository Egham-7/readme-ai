from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, HttpUrl
from typing import Optional, Dict
from readme_ai.repo_analyzer import RepoAnalyzerAgent
from readme_ai.readme_agent import ReadmeCompilerAgent
from readme_ai.settings import get_settings
from dotenv import load_dotenv
import logging
import uuid
from datetime import datetime

# Load environment variables and configure logging
load_dotenv()
settings = get_settings()
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    debug=settings.DEBUG
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
repo_analyzer = RepoAnalyzerAgent(github_token=settings.GITHUB_TOKEN)
readme_compiler = ReadmeCompilerAgent(
    api_key=settings.GROQ_API_KEY,
    model_name=settings.MODEL_NAME,
    temperature=settings.TEMPERATURE,
    streaming=True
)

# In-memory job storage
jobs: Dict[str, Dict] = {}

class RepoRequest(BaseModel):
    repo_url: HttpUrl
    branch: Optional[str] = "main"

async def generate_readme_process(repo_url: str, job_id: str):
    """Background process for README generation"""
    try:
        # Update job status to analyzing
        jobs[job_id].update({
            "status": "analyzing",
            "updated_at": datetime.now()
        })
        
        # Step 1: Analyze repository
        repo_analysis = await repo_analyzer.analyze_repo(str(repo_url))
        
        # Update job status to generating
        jobs[job_id].update({
            "status": "generating",
            "updated_at": datetime.now()
        })
        
        # Step 2: Generate README
        readme_content = []
        async for chunk in readme_compiler.generate_readme(repo_analysis):
            readme_content.append(chunk)
            
        # Update job with completed status and content
        jobs[job_id].update({
            "status": "completed",
            "content": "".join(readme_content),
            "updated_at": datetime.now()
        })
        
    except Exception as e:
        logger.error(f"Error in README generation process: {str(e)}")
        jobs[job_id].update({
            "status": "failed",
            "error": str(e),
            "updated_at": datetime.now()
        })

@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "status": "online",
        "version": settings.APP_VERSION
    }

@app.post("/generate-readme/stream")
async def stream_readme(request: RepoRequest):
    """Stream README generation in real-time"""
    try:
        # First analyze the repository
        repo_analysis = await repo_analyzer.analyze_repo(str(request.repo_url))

        logger.debug(f"Repo Analysis: {repo_analysis}")
        
        # Then stream the README generation
        return StreamingResponse(
            readme_compiler.generate_readme(repo_analysis),
            media_type="text/markdown"
        )
    except Exception as e:
        logger.error(f"Error in streaming README generation: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate README: {str(e)}"
        )

@app.post("/generate-readme")
async def generate_readme(request: RepoRequest, background_tasks: BackgroundTasks):
    """Generate README asynchronously"""
    try:
        # Create unique job ID using UUID
        job_id = str(uuid.uuid4())
        
        # Initialize job entry
        jobs[job_id] = {
            "status": "pending",
            "created_at": datetime.now(),
            "updated_at": datetime.now(),
            "repo_url": str(request.repo_url)
        }
        
        # Add to background tasks
        background_tasks.add_task(
            generate_readme_process,
            str(request.repo_url),
            job_id
        )
        
        return {
            "status": "processing",
            "job_id": job_id,
            "message": "README generation started"
        }
        
    except Exception as e:
        logger.error(f"Error initiating README generation: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to start README generation: {str(e)}"
        )

@app.get("/status/{job_id}")
async def get_job_status(job_id: str):
    """Check the status of a README generation job"""
    try:
        if job_id not in jobs:
            raise HTTPException(
                status_code=404,
                detail="Job not found"
            )
        return jobs[job_id]
        
    except Exception as e:
        logger.error(f"Error checking job status: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to check job status: {str(e)}"
        )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        workers=settings.WORKERS,
    )
