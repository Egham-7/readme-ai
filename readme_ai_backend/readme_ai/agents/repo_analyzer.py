from urllib.parse import urlparse
import logging
import asyncio
from typing import List, Optional, Dict, Any
from github import Github, GithubException  # type: ignore
from langchain_openai import OpenAIEmbeddings
from aiohttp import ClientSession  # type:ignore
from readme_ai.models.repository import Repository  # type: ignore
from readme_ai.services.repository_service import RepositoryService
from readme_ai.services.file_analyzers import AnalyzerFactory, FileAnalyzer  # type: ignore
from readme_ai.prompts import (
    binary_extensions,
    gitignore_by_language,
)

logger = logging.getLogger(__name__)


class AnalysisError(Exception):
    def __init__(self, message: str, details: Optional[Dict] = None):
        self.message = message
        self.details = details or {}
        super().__init__(self.message)


class RepoAccessError(AnalysisError):
    pass


class RepoAnalyzerService:
    def __init__(self, github_token: str, repository_service: RepositoryService):
        self.github_token = github_token
        self.embeddings = OpenAIEmbeddings(model="text-embedding-3-large")
        self.session = ClientSession()
        self._file_content_cache: dict[str, str] = {}
        self.analyzer_factory = AnalyzerFactory()
        self.repository_service = repository_service
        logger.info("FileAnalyzerService initialized")

    async def __aenter__(self):
        return self

    async def __aexit__(self, *args):
        await self.session.close()

    async def _is_ignore_file(self, file_path: str, repo_url: str) -> bool:
        extension = "." + file_path.split(".")[-1].lower() if "." in file_path else ""
        repo_metadata = await self.get_github_repo_metadata(repo_url, self.github_token)
        specific_extensions = gitignore_by_language.get(repo_metadata["language"], [])
        general_extensions = gitignore_by_language.get("General", [])
        return (
            extension in binary_extensions
            or extension in specific_extensions
            or extension in general_extensions
        )

    async def analyze_repo(self, repo: Repository) -> Dict[str, Any]:
        """
        Analyze a repository and store the results in the database with embeddings
        """
        try:
            repo_url = repo.url
            await self.get_github_repo_metadata(repo_url, self.github_token)
            repo_tree = await self.get_repo_tree(repo_url, self.github_token)

            # Collect files
            files_to_analyze = await self._collect_files(repo_url)

            # Read and analyze files
            files_content = await self._read_files_concurrently(
                repo_url, files_to_analyze
            )
            if not files_content:
                raise AnalysisError("Failed to read any files")

            analyses = await self._analyze_files_concurrently(files_content, repo_url)

            # Store file analyses in the database with embeddings
            for file_analysis in analyses:
                # Generate embeddings for the file content analysis
                analysis_text = file_analysis["analysis"]
                embedding = self.embeddings.embed_query(analysis_text)

                # Store the file content and analysis in the database
                await self.repository_service.add_file_content(
                    repository_id=repo.id, content=analysis_text, embedding=embedding
                )

            return {
                "status": "success",
                "repo_url": repo_url,
                "repo_tree": repo_tree,
                "files_analyzed": len(analyses),
                "analysis": analyses,
            }
        except RepoAccessError as e:
            return {
                "status": "error",
                "message": str(e),
                "error_code": "REPO_ACCESS_ERROR",
                "details": e.details,
            }
        except Exception as e:
            error_details = {
                "status": "error",
                "message": str(e),
                "error_code": "ANALYSIS_ERROR",
                "details": getattr(e, "details", None),
            }
            logger.error(f"Repository analysis failed: {error_details}")
            return error_details

    async def _collect_files(self, repo_url: str) -> List[str]:
        """Collect all files from the repository that aren't in the ignore list"""
        try:
            with Github(self.github_token) as github_client:
                owner, repo_name = self.parse_github_url(repo_url)
                repo = github_client.get_repo(f"{owner}/{repo_name}")

                # Get all files recursively
                all_files = []

                async def collect_files_recursively(path=""):
                    contents = repo.get_contents(path)
                    if not isinstance(contents, list):
                        contents = [contents]

                    for content in contents:
                        if content.type == "dir":
                            await collect_files_recursively(content.path)
                        else:
                            if not await self._is_ignore_file(content.path, repo_url):
                                all_files.append(content.path)

                await collect_files_recursively()

                return all_files
        except Exception as e:
            raise AnalysisError(
                "Failed to collect files",
                {
                    "step": "collect_files",
                    "error": str(e),
                },
            )

    async def _analyze_files_concurrently(
        self, files_content: Dict[str, str], repo_url: str
    ) -> List[Dict[str, str]]:
        async def analyze_single_file(file_path: str, content: str) -> Dict[str, str]:
            try:
                analyzer: FileAnalyzer = self.analyzer_factory.get_analyzer(file_path)
                technical_analysis = analyzer.analyze(content, file_path)
                return {"path": file_path, "analysis": technical_analysis}
            except Exception as e:
                logger.error(f"Error analyzing {file_path}: {e}")
                return {"path": file_path, "analysis": f"Analysis failed: {str(e)}"}

        return await asyncio.gather(
            *[
                analyze_single_file(file_path, content)
                for file_path, content in files_content.items()
            ]
        )

    async def _read_files_concurrently(
        self, repo_url: str, file_paths: List[str]
    ) -> Dict[str, str]:
        async def read_single_file(file_path: str) -> tuple[str, Optional[str]]:
            if file_path in self._file_content_cache:
                return file_path, self._file_content_cache[file_path]
            try:
                content = await self.read_github_content(
                    repo_url, file_path, self.github_token
                )
                self._file_content_cache[file_path] = content
                return file_path, content
            except Exception as e:
                logger.error(f"Error reading {file_path}: {e}")
                return file_path, None

        results = await asyncio.gather(*[read_single_file(path) for path in file_paths])
        return {path: content for path, content in results if content is not None}

    def parse_github_url(self, url: str) -> tuple[str, str]:
        parsed = urlparse(url)
        path_parts = parsed.path.strip("/").split("/")
        if (
            parsed.hostname
            and (
                parsed.hostname == "github.com"
                or parsed.hostname.endswith(".github.com")
            )
            and len(path_parts) >= 2
        ):
            return path_parts[0], path_parts[1].replace(".git", "")
        if len(path_parts) == 2:
            return path_parts[0], path_parts[1].replace(".git", "")
        raise ValueError(f"Invalid GitHub URL format {url}")

    async def get_repo_tree(self, repo_url: str, github_token: str) -> str:
        """Get a string representation of the repository tree"""
        with Github(github_token) as github_client:
            try:
                owner, repo_name = self.parse_github_url(repo_url)
                repo = github_client.get_repo(f"{owner}/{repo_name}")

                tree_lines = []

                async def build_tree_recursively(path="", prefix=""):
                    contents = repo.get_contents(path)
                    if not isinstance(contents, list):
                        contents = [contents]

                    # Sort contents: directories first, then files
                    contents = sorted(
                        contents, key=lambda x: (0 if x.type == "dir" else 1, x.name)
                    )

                    for i, content in enumerate(contents):
                        is_last = i == len(contents) - 1
                        connector = "└── " if is_last else "├── "

                        if content.type == "dir":
                            tree_lines.append(f"{prefix}{connector}{content.name}/")
                            new_prefix = prefix + ("    " if is_last else "│   ")
                            await build_tree_recursively(content.path, new_prefix)
                        else:
                            if not await self._is_ignore_file(content.path, repo_url):
                                tree_lines.append(f"{prefix}{connector}{content.name}")

                await build_tree_recursively()
                return "\n".join(tree_lines)
            except GithubException as e:
                error_mapping = {
                    404: ("Repository not found", 404),
                    403: (
                        "Access denied. This repository may be private and requires authentication.",
                        403,
                    ),
                }
                if e.status in error_mapping:
                    msg, code = error_mapping[e.status]
                    raise RepoAccessError(msg, {"status_code": code})
                raise RepoAccessError(
                    f"GitHub API error: {str(e)}", {"status_code": e.status}
                )

    async def read_github_content(self, repo_url: str, path: str, token: str) -> str:
        """Read the content of a file from GitHub"""
        with Github(token) as github_client:
            try:
                owner, repo_name = self.parse_github_url(repo_url)
                repo = github_client.get_repo(f"{owner}/{repo_name}")
                content = repo.get_contents(path)
                if isinstance(content, list):
                    raise ValueError("Path points to a directory, not a file")
                return content.decoded_content.decode("utf-8")
            except GithubException as e:
                if e.status in (403, 404):
                    raise RepoAccessError(
                        "Unable to access repository content",
                        {"path": path, "status_code": e.status},
                    )
                raise RepoAccessError(
                    f"GitHub API error: {str(e)}",
                    {"path": path, "status_code": e.status},
                )

    async def get_github_repo_metadata(self, repo_url: str, token: str) -> dict:
        """Get metadata about a GitHub repository"""
        with Github(token) as github_client:
            try:
                owner, repo_name = self.parse_github_url(repo_url)
                repo = github_client.get_repo(f"{owner}/{repo_name}")
                return {
                    "full_name": repo.full_name,
                    "description": repo.description,
                    "stars": repo.stargazers_count,
                    "forks": repo.forks_count,
                    "open_issues": repo.open_issues_count,
                    "watchers": repo.watchers_count,
                    "language": repo.language,
                    "created_at": repo.created_at.isoformat(),
                    "updated_at": repo.updated_at.isoformat(),
                }
            except GithubException as e:
                error_mapping = {
                    404: ("Repository not found", 404),
                    403: (
                        "Access denied. This repository may be private and requires authentication.",
                        403,
                    ),
                }
                if e.status in error_mapping:
                    msg, code = error_mapping[e.status]
                    raise RepoAccessError(msg, {"status_code": code})
                raise RepoAccessError(
                    f"GitHub API error: {str(e)}", {"status_code": e.status}
                )
