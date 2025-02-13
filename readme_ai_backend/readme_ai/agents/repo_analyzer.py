# Standard library imports
from urllib.parse import urlparse
import logging
import asyncio

# Third-party imports
from github.ContentFile import ContentFile  # type:ignore
from github import Github, UnknownObjectException  # type: ignore
from typing import List, Optional, Dict, Any, TypedDict, Annotated, cast
from langgraph.graph import StateGraph, START, END  # type: ignore
from langchain_groq import ChatGroq  # type: ignore
from pydantic import BaseModel, Field  # type:ignore
from aiohttp import ClientSession  # type:ignore
from readme_ai.services.file_analyzers import AnalyzerFactory, FileAnalyzer  # type: ignore

# Local imports
from readme_ai.prompts import (
    choose_file_prompt,
    binary_extensions,
    analyse_file_prompt,
    gitignore_by_language,
)

logger = logging.getLogger(__name__)


class ImportantFiles(BaseModel):
    """Model for storing important repository file paths"""

    files: List[str] = Field(description="List of important repository file paths")


class FileAnalysis(BaseModel):
    """Model for storing file analysis results"""

    path: str = Field(description="Path of the analyzed file")
    analysis: str = Field(
        description="Detailed analysis of the file's purpose and functionality"
    )


class RepoAnalyzerState(TypedDict):
    """Type definition for the analyzer state"""

    messages: Annotated[List[Dict[str, str]], "Messages for the analysis"]
    analysis: List[Dict[str, str]]
    important_files: List[str]
    repo_tree: str
    repo_url: str


class AnalysisError(Exception):
    """Custom exception for analysis errors"""

    def __init__(self, message: str, details: Optional[Dict] = None):
        self.message = message
        self.details = details or {}
        super().__init__(self.message)


class RepoAnalyzerAgent:
    """Main class for analyzing GitHub repositories"""

    def __init__(self, github_token: str):
        logger.info("Initializing RepoAnalyzerAgent")
        self.github_token = github_token
        self.llm = ChatGroq(
            model="llama-3.3-70b-versatile",
            temperature=0.1,
        )
        self.graph = self._build_analysis_graph()
        self.session = ClientSession()
        self._file_content_cache: dict[str, str] = {}
        self.analyzer_factory = AnalyzerFactory()

        logger.info("RepoAnalyzerAgent initialized successfully")

    async def __aenter__(self):
        return self

    async def __aexit__(self):
        await self.session.close()

    def _build_analysis_graph(self) -> Any:
        logger.info("Building analysis graph")
        graph = StateGraph(RepoAnalyzerState)
        graph.add_node("choose_files", self._choose_files)
        graph.add_node("analyze_files", self._analyze_files)
        graph.add_edge(START, "choose_files")
        graph.add_edge("choose_files", "analyze_files")
        graph.add_edge("analyze_files", END)
        return graph

    async def _choose_files(self, state: RepoAnalyzerState) -> RepoAnalyzerState:
        try:
            print("\n=== CHOOSING IMPORTANT FILES ===")
            print(f"Repository Tree:\n{state['repo_tree']}")

            prompt = choose_file_prompt

            structured_llm = self.llm.with_structured_output(ImportantFiles)
            result = cast(
                ImportantFiles,
                await structured_llm.ainvoke(
                    prompt.format(repo_tree_md=state["repo_tree"])
                ),
            )

            files = result.files
            logger.info(f"Selected Important Files: {files}")
            return {**state, "important_files": files}
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
        # These file extensions should always be analyzed
        always_analyze = {".yml", ".yaml", ".py", ".json", ".sh", ".md", ".txt"}

        extension = "." + file_path.split(".")[-1].lower() if "." in file_path else ""

        # If it's in our always analyze list, return False
        if extension in always_analyze:
            return False

        # Otherwise check against binary and language-specific extensions
        repo_metadata = await self.get_github_repo_metadata(repo_url, self.github_token)
        print("LANGUAGE", repo_metadata["language"])
        specific_extensions: List[str] = gitignore_by_language.get(
            repo_metadata["language"], []
        )

        return extension in binary_extensions or extension in specific_extensions

    async def _analyze_files_concurrently(
        self, files_content: Dict[str, str], repo_url: str
    ) -> List[Dict[str, str]]:
        async def analyze_single_file(file_path: str, content: str) -> Dict[str, str]:
            try:
                """
                if await self._is_ignore_file(file_path, repo_url):
                    return {
                        "path": file_path,
                        "analysis": "Binary file - analysis skipped",
                    }
                """
                analyzer: FileAnalyzer = self.analyzer_factory.get_analyzer(file_path)
                technical_analysis = analyzer.analyze(content, file_path)

                logger.info(f"File Content: {content}")
                structured_llm = self.llm.with_structured_output(FileAnalysis)

                result = cast(
                    FileAnalysis,
                    await structured_llm.ainvoke(
                        analyse_file_prompt.format(
                            file_path=file_path, file_content=technical_analysis
                        )
                    ),
                )
                logger.info(f"Analysis Result: {result}")
                return {"path": result.path, "analysis": result.analysis}

            except Exception as e:
                logger.error(f"Error analyzing {file_path}: {e}")
                return {"path": file_path, "analysis": f"Analysis failed: {str(e)}"}

        tasks = [
            analyze_single_file(file_path, content)
            for file_path, content in files_content.items()
        ]
        return await asyncio.gather(*tasks)

    async def _read_files_concurrently(
        self, repo_url: str, file_paths: List[str]
    ) -> Dict[str, str]:
        async def read_single_file(file_path: str) -> tuple[str, Optional[str]]:
            try:
                if file_path in self._file_content_cache:
                    return file_path, self._file_content_cache[file_path]

                content = await self.read_github_content(
                    repo_url, file_path, self.github_token
                )
                self._file_content_cache[file_path] = content
                return file_path, content
            except Exception as e:
                logger.error(f"Error reading {file_path}: {e}")
                return file_path, None

        tasks = [read_single_file(path) for path in file_paths]
        results = await asyncio.gather(*tasks)
        return {path: content for path, content in results if content is not None}

    async def _analyze_files(self, state: RepoAnalyzerState) -> RepoAnalyzerState:
        try:
            print("\n=== ANALYZING FILES ===")
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
            print("\n=== STARTING REPOSITORY ANALYSIS ===")
            print(f"Repository URL: {repo_url}")

            repo_tree = await self.get_repo_tree(repo_url, self.github_token)
            print(f"\nRepository Structure:\n{repo_tree}")

            initial_state = {
                "messages": [
                    {"role": "user", "content": f"Analyze repository: {repo_url}"}
                ],
                "repo_tree": repo_tree,
                "repo_url": repo_url,
                "important_files": [],
                "analysis": [],
            }

            print("\n=== STARTING ANALYSIS ===")
            compiled_graph = self.graph.compile()
            result = await compiled_graph.ainvoke(initial_state)

            print("\n=== ANALYSIS COMPLETED ===")

            logger.info(f"Final Analysis: {result.get('analysis', [])}")
            return {
                "repo_url": repo_url,
                "repo_tree": repo_tree,
                "important_files": result.get("important_files", []),
                "analysis": result.get("analysis", []),
                "status": "success",
            }
        except Exception as e:
            error_details = {
                "status": "error",
                "message": str(e),
                "details": e.details if isinstance(e, AnalysisError) else None,
            }
            logger.error(f"Repository analysis failed: {error_details}")
            return error_details

    def parse_github_url(self, url: str) -> tuple[str, str]:
        parsed = urlparse(url)
        path_parts = parsed.path.strip("/").split("/")

        if "github.com" in parsed.netloc:
            if len(path_parts) < 2:
                raise ValueError("Invalid repository path")
            return path_parts[0], path_parts[1].replace(".git", "")

        if len(path_parts) == 2:
            return path_parts[0], path_parts[1].replace(".git", "")

        raise ValueError(f"Invalid GitHub URL format {url}")

    async def get_repo_tree(self, repo_url: str, github_token: str) -> str:
        async def build_tree_async(
            content_list: List[ContentFile], repo, base_path: str = ""
        ) -> List[str]:
            tree = []
            contents = content_list.copy()

            while contents:
                file_content = contents.pop(0)
                full_path = f"{base_path}/{file_content.path}".lstrip("/")
                depth = full_path.count("/")

                # For files, check if they should be ignored
                if file_content.type != "dir":
                    should_ignore = await self._is_ignore_file(full_path, repo_url)
                    if should_ignore:
                        continue

                if file_content.type == "dir":
                    tree.append(
                        f"{'|   ' * depth}+-- {file_content.name}/ ({full_path})"
                    )
                    dir_contents = repo.get_contents(full_path)
                    if isinstance(dir_contents, list):
                        contents.extend(dir_contents)
                else:
                    tree.append(
                        f"{'|   ' * depth}+-- {file_content.name} ({full_path})"
                    )

            return tree

        github_client = Github(github_token)
        try:
            owner, repo_name = self.parse_github_url(repo_url)
            repo = github_client.get_repo(f"{owner}/{repo_name}")
            initial_contents = repo.get_contents("")

            if not isinstance(initial_contents, list):
                initial_contents = [initial_contents]

            tree_lines = await build_tree_async(initial_contents, repo)
            return "\n".join(tree_lines)
        except UnknownObjectException:
            raise ValueError("Repository not found")
        finally:
            github_client.close()

    async def read_github_content(self, repo_url: str, path: str, token: str) -> str:
        github_client = Github(token)
        try:
            owner, repo_name = self.parse_github_url(repo_url)
            repo_full_name = f"{owner}/{repo_name}"
            repo_obj = github_client.get_repo(repo_full_name)

            logger.info(f"Repo Object: {repo_obj.__str__()}")
            logger.info(f"Path: {path}")

            content = repo_obj.get_contents(path)
            if isinstance(content, list):
                raise ValueError("Path points to a directory, not a file")

            return content.decoded_content.decode("utf-8")
        except Exception as e:
            logger.error(f"Error reading GitHub content: {e}")
            raise AnalysisError(
                "Failed to read GitHub content",
                {"repo": repo_url, "path": path, "error": str(e)},
            )
        finally:
            github_client.close()

    async def get_github_repo_metadata(self, repo_url: str, token: str) -> dict:
        github_client = Github(token)
        try:
            owner, repo_name = self.parse_github_url(repo_url)
            repo_full_name = f"{owner}/{repo_name}"
            repo_obj = github_client.get_repo(repo_full_name)

            metadata = {
                "full_name": repo_obj.full_name,
                "description": repo_obj.description,
                "stars": repo_obj.stargazers_count,
                "forks": repo_obj.forks_count,
                "open_issues": repo_obj.open_issues_count,
                "watchers": repo_obj.watchers_count,
                "language": repo_obj.language,
                "created_at": repo_obj.created_at.isoformat(),
                "updated_at": repo_obj.updated_at.isoformat(),
            }

            logger.info(f"Repo Metadata: {metadata}")
            return metadata
        except Exception as e:
            logger.error(f"Error fetching GitHub metadata: {e}")
            raise AnalysisError(
                "Failed to fetch GitHub metadata",
                {"repo": repo_url, "error": str(e)},
            )
        finally:
            github_client.close()
