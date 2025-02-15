from typing import Optional
from fastapi import APIRouter, Request, Depends, Query
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from readme_ai.auth import require_sse_auth
from readme_ai.database import get_db
from readme_ai.services.miniio_service import MinioService, get_minio_service
from readme_ai.agents.repo_analyzer import RepoAnalyzerAgent
from readme_ai.agents.readme_agent import ReadmeCompilerAgent
from readme_ai.repositories.readme_repository import ReadmeRepository
from readme_ai.services.readme_service import ReadmeService
from readme_ai.settings import get_settings
from readme_ai.repositories.template_repository import TemplateRepository
from readme_ai.services.template_service import TemplateService
from sse_starlette.sse import EventSourceResponse
from readme_ai.logging_config import logger
from slowapi import Limiter
from slowapi.util import get_remote_address
import json

settings = get_settings()
router = APIRouter(tags=["readme"])
limiter = Limiter(key_func=get_remote_address)


def extract_title_from_content(content: str) -> str:
    """Extract title from README content using the first heading"""
    lines = content.splitlines()
    for line in lines:
        line = line.strip()
        if line.startswith("#"):
            return line.lstrip("#").strip()
    return "Untitled README"


@router.get("/generate-readme")
@limiter.limit("5/minute")
@require_sse_auth()
async def generate_readme(
    request: Request,
    token: str = Query(...),
    title: str = Query(None),
    repo_url: str = "",
    template_id: Optional[int] = None,
    db: AsyncSession = Depends(get_db),
    minio_service: MinioService = Depends(get_minio_service),
):
    github_token = settings.GITHUB_TOKEN
    repo_analyzer = RepoAnalyzerAgent(github_token=github_token)
    readme_compiler = ReadmeCompilerAgent()
    user = request.state.user

    async def event_generator():
        timestamp = datetime.now().isoformat()
        try:
            yield {
                "event": "progress",
                "data": json.dumps(
                    {
                        "stage": "init",
                        "message": "Starting repository analysis...",
                        "progress": 0.0,
                        "timestamp": datetime.now().isoformat(),
                    }
                ),
            }

            yield {
                "event": "progress",
                "data": json.dumps(
                    {
                        "stage": "analysis",
                        "message": "Analyzing repository structure...",
                        "progress": 0.3,
                        "timestamp": datetime.now().isoformat(),
                    }
                ),
            }

            repo_analysis = await repo_analyzer.analyze_repo(repo_url=repo_url)

            if repo_analysis.get("status") == "error":
                yield {
                    "event": "error",
                    "data": json.dumps(
                        {
                            "message": repo_analysis.get(
                                "message", "Repository analysis failed"
                            ),
                            "error_code": repo_analysis.get(
                                "error_code", "INTERNAL_SERVER_ERROR"
                            ),
                            "timestamp": timestamp,
                        }
                    ),
                }
                return

            yield {
                "event": "progress",
                "data": json.dumps(
                    {
                        "stage": "template",
                        "message": "Fetching template...",
                        "progress": 0.5,
                        "timestamp": datetime.now().isoformat(),
                    }
                ),
            }

            template_content: Optional[str] = None
            if template_id:
                repository = TemplateRepository(db_session=db)
                template_service = TemplateService(
                    template_repository=repository, minio_service=minio_service
                )
                template = await template_service.get_template(template_id)
                template_content = template.content if template else None

            yield {
                "event": "progress",
                "data": json.dumps(
                    {
                        "stage": "generation",
                        "message": "Generating README content...",
                        "progress": 0.99,
                        "timestamp": datetime.now().isoformat(),
                    }
                ),
            }

            readme_content = await readme_compiler.gen_readme(
                repo_url=repo_url,
                repo_analysis=repo_analysis["analysis"],
                template_content=template_content,
            )

            yield {
                "event": "complete",
                "data": json.dumps(
                    {
                        "status": "success",
                        "data": readme_content["readme"],
                        "timestamp": datetime.now().isoformat(),
                    }
                ),
            }

            final_title = title or extract_title_from_content(
                readme_content["readme"])

            readme_repository = ReadmeRepository(db_session=db)
            readme_service = ReadmeService(readme_repository=readme_repository)

            async with db.begin():
                readme = await readme_service.create_readme(
                    user_id=user.get_user_id(),
                    repository_url=repo_url,
                    title=final_title,
                )
                await readme_service.create_version(
                    readme_id=readme.id, content=readme_content["readme"]
                )

        except Exception as e:
            logger.error(f"README generation error: {str(e)}")
            yield {
                "event": "error",
                "data": json.dumps(
                    {
                        "message": "Internal server error during README generation",
                        "error_code": "INTERNAL_SERVER_ERROR",
                        "details": {
                            "error_type": type(e).__name__,
                            "error_message": str(e),
                        },
                        "timestamp": datetime.now().isoformat(),
                    }
                ),
            }

    return EventSourceResponse(event_generator())
