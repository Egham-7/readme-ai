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
)
import pathspec  # type: ignore

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
        self._gitignore_cache: dict[str, list[str]] = {}
        self.analyzer_factory = AnalyzerFactory()
        self.repository_service = repository_service
        logger.info("FileAnalyzerService initialized")

    async def __aenter__(self):
        return self

    async def __aexit__(self, *args):
        await self.session.close()

    async def _parse_gitignore(self, content: str) -> List[str]:
        """Parse a .gitignore file and return a list of patterns"""
        patterns = []
        for line in content.splitlines():
            line = line.strip()
            # Skip empty lines and comments
            if not line or line.startswith("#"):
                continue
            patterns.append(line)
        return patterns

    async def _get_gitignore_for_path(self, repo_url: str, file_path: str) -> List[str]:
        """Get the applicable gitignore patterns for a given file path"""
        # Split the path into components
        path_components = file_path.split("/")
        # Check each directory level for a .gitignore file
        current_path = ""
        applicable_patterns = []
        # Add binary extensions
        for extension in binary_extensions:
            applicable_patterns.append(f"*{extension}")
        # Check for .gitignore files at each directory level
        for i in range(len(path_components)):
            if i == len(path_components) - 1:  # Skip the file itself
                break
            if i > 0:
                current_path = "/".join(path_components[:i])
            gitignore_path = f"{current_path}{'/' if current_path else ''}.gitignore"
            # Check if we've already parsed this .gitignore
            if gitignore_path in self._gitignore_cache:
                applicable_patterns.extend(self._gitignore_cache[gitignore_path])
                continue
            # Try to read the .gitignore file
            try:
                gitignore_content = await self.read_github_content(
                    repo_url, gitignore_path, self.github_token
                )
                patterns = await self._parse_gitignore(gitignore_content)
                self._gitignore_cache[gitignore_path] = patterns
                applicable_patterns.extend(patterns)
            except Exception:
                # No .gitignore at this level, continue
                pass
        return applicable_patterns

    async def _should_ignore_file(self, file_path: str, repo_url: str) -> bool:
        """Check if a file should be ignored based on .gitignore patterns"""
        # Get applicable gitignore patterns
        patterns = await self._get_gitignore_for_path(repo_url, file_path)
        if not patterns:
            return False
        # Create a PathSpec object with the patterns
        spec = pathspec.PathSpec.from_lines(
            pathspec.patterns.GitWildMatchPattern, patterns
        )
        # Check if the file matches any pattern
        return spec.match_file(file_path)

    async def analyze_repo(self, repo: Repository) -> Dict[str, Any]:
        """
        Analyze a repository and store the results in the database with embeddings
        """
        try:
            repo_url = repo.url
            await self.get_github_repo_metadata(repo_url, self.github_token)

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

    async def _collect_files(self, repo_url: str, max_depth: int = 2) -> List[str]:
        """Collect all files from the repository that aren't in the ignore list, with configurable max depth"""
        try:
            with Github(self.github_token) as github_client:
                owner, repo_name = self.parse_github_url(repo_url)
                repo = github_client.get_repo(f"{owner}/{repo_name}")

                all_files = []

                # Use a queue-based approach for breadth-first traversal
                # Each item is (path, current_depth)
                queue = [("", 0)]

                while queue:
                    current_path, current_depth = queue.pop(0)

                    # Skip if we've reached max depth
                    if current_depth > max_depth:
                        continue

                    try:
                        contents = repo.get_contents(current_path)
                        if not isinstance(contents, list):
                            contents = [contents]

                        for content in contents:
                            if content.type == "dir":
                                # Only add directories to the queue if we haven't reached max depth
                                if current_depth < max_depth:
                                    queue.append((content.path, current_depth + 1))
                            else:
                                # Check if we should ignore this file
                                if not await self._should_ignore_file(
                                    content.path, repo_url
                                ):
                                    all_files.append(content.path)
                    except Exception as e:
                        logger.warning(f"Error accessing path {current_path}: {e}")

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
