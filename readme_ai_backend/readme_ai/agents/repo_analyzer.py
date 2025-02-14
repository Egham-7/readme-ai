from urllib.parse import urlparse
import logging
import asyncio
from github.ContentFile import ContentFile  # type:ignore
from github import Github, GithubException  # type: ignore
from typing import List, Optional, Dict, Any, TypedDict, Annotated, cast
from langgraph.graph import StateGraph, START, END  # type: ignore
from langchain_groq import ChatGroq  # type: ignore
from pydantic import BaseModel, Field  # type:ignore
from aiohttp import ClientSession  # type:ignore
from readme_ai.services.file_analyzers import AnalyzerFactory, FileAnalyzer  # type: ignore
from readme_ai.prompts import (
    choose_file_prompt,
    binary_extensions,
    analyse_file_prompt,
    gitignore_by_language,
)
from collections import deque
logger = logging.getLogger(__name__)


class ImportantFiles(BaseModel):
    files: List[str] = Field(description="List of important repository file paths")


class FileAnalysis(BaseModel):
    path: str = Field(description="Path of the analyzed file")
    analysis: str = Field(
        description="Detailed analysis of the file's purpose and functionality"
    )


class RepoAnalyzerState(TypedDict):
    messages: Annotated[List[Dict[str, str]], "Messages for the analysis"]
    analysis: List[Dict[str, str]]
    important_files: List[str]
    repo_tree: str
    repo_url: str


class AnalysisError(Exception):
    def __init__(self, message: str, details: Optional[Dict] = None):
        self.message = message
        self.details = details or {}
        super().__init__(self.message)


class RepoAccessError(AnalysisError):
    pass


class RepoAnalyzerAgent:
    def __init__(self, github_token: str):
        self.github_token = github_token
        self.llm = ChatGroq(model="llama-3.3-70b-versatile", temperature=0.1)
        self.graph = self._build_analysis_graph()
        self.session = ClientSession()
        self._file_content_cache: dict[str, str] = {}
        self.analyzer_factory = AnalyzerFactory()
        logger.info("RepoAnalyzerAgent initialized")

    async def __aenter__(self):
        return self

    async def __aexit__(self):
        await self.session.close()

    def _build_analysis_graph(self) -> StateGraph:
        graph = StateGraph(RepoAnalyzerState)
        graph.add_node("choose_files", self._choose_files)
        graph.add_node("analyze_files", self._analyze_files)
        graph.add_edge(START, "choose_files")
        graph.add_edge("choose_files", "analyze_files")
        graph.add_edge("analyze_files", END)
        return graph

    async def _choose_files(self, state: RepoAnalyzerState) -> RepoAnalyzerState:
        try:
            structured_llm = self.llm.with_structured_output(ImportantFiles)
            result = cast(
                ImportantFiles,
                await structured_llm.ainvoke(
                    choose_file_prompt.format(repo_tree_md=state["repo_tree"])
                ),
            )
            return {**state, "important_files": result.files}
        except Exception as e:
            raise AnalysisError(
                "Failed to choose important files",
                {
                    "step": "choose_files",
                    "error": str(e),
                    "repo_tree": state["repo_tree"],
                },
            )

    async def _is_ignore_file(self, file_path: str, repo_url: str) -> bool:
        extension = "." + file_path.split(".")[-1].lower() if "." in file_path else ""

        repo_metadata = await self.get_github_repo_metadata(repo_url, self.github_token)
        specific_extensions = gitignore_by_language.get(repo_metadata["language"], [])
        return extension in binary_extensions or extension in specific_extensions

    async def _analyze_files_concurrently(
        self, files_content: Dict[str, str], repo_url: str
    ) -> List[Dict[str, str]]:
        async def analyze_single_file(file_path: str, content: str) -> Dict[str, str]:
            try:
                analyzer: FileAnalyzer = self.analyzer_factory.get_analyzer(file_path)
                technical_analysis = analyzer.analyze(content, file_path)
                structured_llm = self.llm.with_structured_output(FileAnalysis)
                result = cast(
                    FileAnalysis,
                    await structured_llm.ainvoke(
                        analyse_file_prompt.format(
                            file_path=file_path, file_content=technical_analysis
                        )
                    ),
                )
                return {"path": result.path, "analysis": result.analysis}
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

    async def _analyze_files(self, state: RepoAnalyzerState) -> RepoAnalyzerState:
        try:
            files_content = await self._read_files_concurrently(
                state["repo_url"], state["important_files"]
            )
            if not files_content:
                raise AnalysisError("Failed to read any files")
            analyses = await self._analyze_files_concurrently(
                files_content, state["repo_url"]
            )
            return {**state, "analysis": analyses}
        except Exception as e:
            if isinstance(e, AnalysisError):
                raise e
            raise AnalysisError("File analysis failed", {"error": str(e)})

    async def analyze_repo(self, repo_url: str) -> Dict[str, Any]:
        try:
            await self.get_github_repo_metadata(repo_url, self.github_token)
            repo_tree = await self.get_repo_tree(repo_url, self.github_token)

            initial_state = {
                "messages": [
                    {"role": "user", "content": f"Analyze repository: {repo_url}"}
                ],
                "repo_tree": repo_tree,
                "repo_url": repo_url,
                "important_files": [],
                "analysis": [],
            }

            result = await self.graph.compile().ainvoke(initial_state)

            return {
                "status": "success",
                "repo_url": repo_url,
                "repo_tree": repo_tree,
                "important_files": result.get("important_files", []),
                "analysis": result.get("analysis", []),
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
        async def build_tree_async(
                content_list: List[ContentFile], repo, base_path: str = ""
            ) -> List[str]:
                tree = []
                contents = deque(content_list)
                MAX_DEPTH = 2

                while contents:
                    file_content = contents.popleft()
                    full_path = f"{base_path}/{file_content.path}".lstrip("/")
                    depth = full_path.count("/")

                    if depth > MAX_DEPTH:
                        continue

                    if file_content.type != "dir" and await self._is_ignore_file(
                        full_path, repo_url
                    ):
                        continue

                    prefix = "|   " * depth
                    if file_content.type == "dir":
                        tree.append(f"{prefix}+-- {file_content.name}/ ({full_path})")
                        if depth < MAX_DEPTH:
                            dir_contents = repo.get_contents(full_path)
                            if isinstance(dir_contents, list):
                                contents.extend(dir_contents)
                    else:
                        tree.append(f"{prefix}+-- {file_content.name} ({full_path})")

                return tree

        with Github(github_token) as github_client:
            try:
                owner, repo_name = self.parse_github_url(repo_url)
                repo = github_client.get_repo(f"{owner}/{repo_name}")
                initial_contents = repo.get_contents("")

                if not isinstance(initial_contents, list):
                    initial_contents = [initial_contents]

                tree_lines = await build_tree_async(initial_contents, repo)
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