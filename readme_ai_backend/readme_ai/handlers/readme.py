from typing import Optional
from fastapi import APIRouter, Request, Depends, Query
from fastapi.responses import JSONResponse
from datetime import datetime
from readme_ai.models.requests.readme import Readme, ReadmeUpdate
from readme_ai.services.repository_service import RepositoryService
from sqlalchemy.ext.asyncio import AsyncSession
from readme_ai.auth import ClerkUser, require_auth, require_sse_auth
from readme_ai.database import get_db
from readme_ai.services.miniio_service import MinioService, get_minio_service
from readme_ai.agents.repo_analyzer import RepoAnalyzerService
from readme_ai.agents.readme_agent import ReadmeCompilerAgent
from readme_ai.repositories.readme_repository import ReadmeRepository
from readme_ai.services.readme_service import ReadmeService
from readme_ai.settings import get_settings
from readme_ai.repositories.template_repository import TemplateRepository
from readme_ai.services.template_service import TemplateService
from sse_starlette.sse import EventSourceResponse  # type: ignore
from readme_ai.logging_config import logger
from slowapi import Limiter
from slowapi.util import get_remote_address
import json
from readme_ai.models.responses.readme import ReadmesResponse
from readme_ai.utils.title_parser import extract_title_from_content

settings = get_settings()
router = APIRouter(tags=["readme"])
limiter = Limiter(key_func=get_remote_address)


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
    repo_service = RepositoryService(db_session=db)
    readme_compiler = ReadmeCompilerAgent(repository_service=repo_service)
    repo_analyzer = RepoAnalyzerService(
        github_token=github_token, repository_service=repo_service
    )

    user: ClerkUser = request.state.user

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

            existing_repo = await repo_service.get_repository_by_url(repo_url)

            if not existing_repo:
                repo_name = repo_url.split("/")[-1]

                existing_repo = await repo_service.create_repository(
                    repo_name, repo_url, user.get_user_id()
                )

            if not existing_repo:
                yield {
                    "event": "error",
                    "data": json.dumps(
                        {
                            "message": "Failed to create or fetch repository",
                            "error_code": "INTERNAL_SERVER_ERROR",
                            "timestamp": timestamp,
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

            repo_analysis = await repo_analyzer.analyze_repo(existing_repo)

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
                repository=existing_repo,
                repo_analysis=repo_analysis["analysis"],
                template_content=template_content,
            )

            final_title = title or extract_title_from_content(
                readme_content["readme"])

            readme_repository = ReadmeRepository(db_session=db)
            readme_service = ReadmeService(readme_repository=readme_repository)

            readme = await readme_service.create_readme(
                user_id=user.get_user_id(),
                repository_url=repo_url,
                title=final_title,
            )
            logger.info(f"Created readme with id: {readme.id}")

            await readme_service.create_version(
                readme_id=readme.id, content=readme_content["readme"]
            )
            logger.info(f"Created version for readme id: {readme.id}")

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

        except Exception as e:
            logger.error(f"README generation error: {str(e)}")
            yield {
                "event": "error",
                "message": "Internal server error during README generation",
                "error_code": "INTERNAL_SERVER_ERROR",
                "details": {
                    "error_type": type(e).__name__,
                    "error_message": str(e),
                },
                "timestamp": datetime.now().isoformat(),
            }

    return EventSourceResponse(event_generator())


@router.get("/readmes", response_model=ReadmesResponse)
@limiter.limit("20/minute")
@require_auth()
async def get_user_readmes(
    request: Request,
    db: AsyncSession = Depends(get_db),
    query: str = Query(default=""),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=10, ge=1, le=100),
):
    user: ClerkUser = request.state.user

    try:
        readme_repository = ReadmeRepository(db_session=db)
        readme_service = ReadmeService(readme_repository=readme_repository)

        readmes, total_pages = await readme_service.get_user_readmes(
            user_id=user.get_user_id(), page=page, page_size=page_size, query=query
        )

        logger.info(f"Readmes: {readmes}")

        return ReadmesResponse(
            data=[Readme.from_orm(readme) for readme in readmes],
            total_pages=total_pages,
        )

    except Exception as e:
        logger.error(f"Error fetching user READMEs: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={
                "message": "Error fetching user READMEs",
                "error_code": "INTERNAL_SERVER_ERROR",
                "details": {"error_type": type(e).__name__, "error_message": str(e)},
                "timestamp": datetime.now().isoformat(),
            },
        )


@router.put("/readmes/{id}")
@limiter.limit("20/minute")
@require_auth()
async def update_readme(
    request: Request,
    readme_request: ReadmeUpdate,
    id: int,
    db: AsyncSession = Depends(get_db),
):
    user: ClerkUser = request.state.user
    try:
        readme_repository = ReadmeRepository(db_session=db)
        readme_service = ReadmeService(readme_repository=readme_repository)

        content = readme_request.content

        updated_version = await readme_service.update_readme(
            readme_id=id, user_id=user.get_user_id(), content=content
        )

        if not updated_version:
            raise Exception("Failed to update readme.")

        return {
            "status": "success",
            "message": "README updated successfully",
            "data": {
                "id": updated_version.id,
                "content": updated_version.content,
                "version_number": updated_version.version_number,
                "created_at": updated_version.created_at,
            },
        }
    except ValueError as e:
        return JSONResponse(
            status_code=403,
            content={
                "message": str(e),
                "error_code": "FORBIDDEN",
                "timestamp": datetime.now().isoformat(),
            },
        )
    except Exception as e:
        logger.error(f"Error updating README: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={
                "message": "Error updating README",
                "error_code": "INTERNAL_SERVER_ERROR",
                "details": {"error_type": type(e).__name__, "error_message": str(e)},
                "timestamp": datetime.now().isoformat(),
            },
        )


@router.delete("/readmes/{readme_id}")
@limiter.limit("20/minute")
@require_auth()
async def delete_readme(
    request: Request, readme_id: int, db: AsyncSession = Depends(get_db)
):
    user: ClerkUser = request.state.user
    try:
        readme_repository = ReadmeRepository(db_session=db)
        readme_service = ReadmeService(readme_repository=readme_repository)

        success = await readme_service.delete_readme(
            readme_id=readme_id, user_id=user.get_user_id()
        )

        if success:
            return {"status": "success", "message": "README deleted successfully"}
        else:
            return JSONResponse(
                status_code=404,
                content={
                    "message": "README not found",
                    "error_code": "NOT_FOUND",
                    "timestamp": datetime.now().isoformat(),
                },
            )
    except ValueError as e:
        return JSONResponse(
            status_code=403,
            content={
                "message": str(e),
                "error_code": "FORBIDDEN",
                "timestamp": datetime.now().isoformat(),
            },
        )
    except Exception as e:
        logger.error(f"Error deleting README: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={
                "message": "Error deleting README",
                "error_code": "INTERNAL_SERVER_ERROR",
                "details": {"error_type": type(e).__name__, "error_message": str(e)},
                "timestamp": datetime.now().isoformat(),
            },
        )


@router.get("/readmes/{readme_id}")
@limiter.limit("20/minute")
@require_auth()
async def get_readme(
    request: Request, readme_id: int, db: AsyncSession = Depends(get_db)
):
    user: ClerkUser = request.state.user

    try:
        readme_repository = ReadmeRepository(db_session=db)
        readme_service = ReadmeService(readme_repository=readme_repository)

        # Get readme with all its versions
        readme = await readme_service.get_readme_with_versions(readme_id)

        if not readme:
            return JSONResponse(
                status_code=404,
                content={
                    "message": "README not found",
                    "error_code": "NOT_FOUND",
                    "timestamp": datetime.now().isoformat(),
                },
            )

        # Check if the user is authorized to access this readme
        if readme.user_id != user.get_user_id():
            return JSONResponse(
                status_code=403,
                content={
                    "message": "Not authorized to access this README",
                    "error_code": "FORBIDDEN",
                    "timestamp": datetime.now().isoformat(),
                },
            )

        return Readme.from_orm(readme)

    except Exception as e:
        logger.error(f"Error fetching README: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={
                "message": "Error fetching README",
                "error_code": "INTERNAL_SERVER_ERROR",
                "details": {"error_type": type(e).__name__, "error_message": str(e)},
                "timestamp": datetime.now().isoformat(),
            },
        )
