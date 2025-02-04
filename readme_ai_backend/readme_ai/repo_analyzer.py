import asyncio
from urllib.parse import urlparse
from github.ContentFile import ContentFile
from github import Github, UnknownObjectException
from typing import List
import logging
from typing import Dict, Any, TypedDict, Annotated, cast
from langgraph.graph import StateGraph, START, END  # type:ignore
from langchain_groq import ChatGroq
from langchain.prompts import ChatPromptTemplate
from pydantic import BaseModel, Field

logging.basicConfig(level=logging.INFO)
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


class RepoAnalyzerAgent:
    def __init__(self, github_token: str):
        logger.info("Initializing RepoAnalyzerAgent")
        self.github_token = github_token
        self.llm = ChatGroq(
            model="mixtral-8x7b-32768",
            temperature=0.1,
        )
        self.graph = self._build_analysis_graph()
        logger.info("RepoAnalyzerAgent initialized successfully")

    def _build_analysis_graph(self) -> StateGraph:
        logger.info("Building analysis graph")
        graph = StateGraph(RepoAnalyzerState)

        graph.add_node("choose_files", self._choose_files)
        graph.add_node("analyze_files", self._analyze_files)

        graph.add_edge(START, "choose_files")
        graph.add_edge("choose_files", "analyze_files")
        graph.add_edge("analyze_files", END)

        logger.info("Analysis graph built successfully")
        return graph.compile()

    def _choose_files(self, state: RepoAnalyzerState) -> RepoAnalyzerState:
        print("\n=== CHOOSING IMPORTANT FILES ===")
        print(f"Repository Tree:\n{state['repo_tree']}")

        structured_llm = self.llm.with_structured_output(ImportantFiles)

        prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    "You are a code analysis expert. Examine the repository structure and identify the most important files for analysis.",
                ),
                (
                    "human",
                    "Here is the repository structure. Return the important files:\n{repo_tree_md}",
                ),
            ]
        )

        result = cast(
            ImportantFiles,
            structured_llm.invoke(prompt.format(repo_tree_md=state["repo_tree"])),
        )

        logger.info(f"Selected Important Files: {result.files}")
        return {**state, "important_files": result.files}

    async def _analyze_files(self, state: RepoAnalyzerState) -> RepoAnalyzerState:
        try:
            print("\n=== ANALYZING FILES ===")
            # Add await for async file reading
            files_content = await self._read_files_concurrently(
                state["repo_url"], state["important_files"]
            )

            if not files_content:
                raise AnalysisError("Failed to read any files")

            # Add await for async analysis
            analyses = await self._analyze_files_concurrently(files_content)

            return {**state, "analysis": analyses}
        except Exception as e:
            if isinstance(e, AnalysisError):
                raise e
            raise AnalysisError("File analysis failed", {"error": str(e)})

    def _is_binary_file(self, file_path: str) -> bool:
        binary_extensions = {
            ".png",
            ".jpg",
            ".jpeg",
            ".gif",
            ".bmp",
            ".ico",
            ".svg",
            ".pdf",
            ".doc",
            ".docx",
            ".xls",
            ".xlsx",
            ".ppt",
            ".pptx",
            ".zip",
            ".tar",
            ".gz",
            ".7z",
            ".rar",
            ".pyc",
            ".exe",
            ".dll",
            ".so",
            ".class",
            ".db",
            ".sqlite",
            ".sqlite3",
            ".bin",
            ".dat",
        }
        extension = "." + file_path.split(".")[-1].lower() if "." in file_path else ""
        return extension in binary_extensions

    def _analyze_single_file(
        self, file_path: str, content: str, structured_llm
    ) -> Dict[str, str]:
        logger.info(f"Analyzing file: {file_path}")

        # Skip data files that don't need analysis
        data_extensions = {".csv", ".json", ".xml", ".yaml", ".yml", ".dat"}
        extension = "." + file_path.split(".")[-1].lower() if "." in file_path else ""

        if extension in data_extensions:
            return {
                "path": file_path,
                "analysis": f"Data file {file_path} containing structured data for the application",
            }

        analysis_prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    """Extract key README documentation elements:
                1. Setup & Installation
                2. Core Features & Usage
                3. Configuration
                4. Quick Start Examples""",
                ),
                (
                    "human",
                    """File: {file_path}
                Content: {file_content}
                
                Extract the essential documentation points.""",
                ),
            ]
        )

        result = structured_llm.invoke(
            analysis_prompt.format(file_path=file_path, file_content=content)
        )

        return {"path": result.path, "analysis": result.analysis}

    async def analyze_repo(self, repo_url: str) -> Dict[str, Any]:
        try:
            print("\n=== STARTING REPOSITORY ANALYSIS ===")
            # Ensure async tree generation
            repo_tree = await self.get_repo_tree(repo_url, self.github_token)
            
            initial_state = {
                "messages": [{"role": "user", "content": f"Analyze repository: {repo_url}"}],
                "repo_tree": repo_tree,
                "repo_url": repo_url,
                "important_files": [],
                "analysis": [],
            }

            # Proper async graph execution
            result = await self.graph.ainvoke(initial_state)
            
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


async def get_repo_tree(self, repo_url: str, github_token: str) -> str:
    async def build_tree(content_list: List[ContentFile], repo) -> List[str]:
        tree = []
        contents = content_list.copy()
        
        while contents:
            file_content = contents.pop(0)
            full_path = file_content.path
            depth = full_path.count('/')

            if file_content.type == "dir":
                tree.append(f"{'|   ' * depth}+-- {file_content.name}/")
                # Async directory content retrieval
                dir_contents = await asyncio.to_thread(repo.get_contents, full_path)
                contents.extend(dir_contents)
            else:
                tree.append(f"{'|   ' * depth}+-- {file_content.name}")

        return tree

    try:
        github_client = Github(github_token)
        owner, repo_name = self.parse_github_url(repo_url)
        
        # Async repo access
        repo = await asyncio.to_thread(
            github_client.get_repo, f"{owner}/{repo_name}"
        )
        initial_contents = await asyncio.to_thread(repo.get_contents, "")
        
        tree_structure = await build_tree(initial_contents, repo)
        return '\n'.join(tree_structure)
        
    except UnknownObjectException:
        raise ValueError("Repository not found")
    finally:
        github_client.close()

async def read_github_content(self, repo_url: str, path: str, token: str) -> str:
    try:
        github_client = Github(token)
        owner, repo_name = self.parse_github_url(repo_url)
        
        # Async repo and content access
        repo_obj = await asyncio.to_thread(
            github_client.get_repo, f"{owner}/{repo_name}"
        )
        content = await asyncio.to_thread(repo_obj.get_contents, path)
        
        if isinstance(content, list):
            raise ValueError("Path points to a directory, not a file")
            
        return content.decoded_content.decode('utf-8')
        
    except Exception as e:
        logger.error(f"Error reading GitHub content: {e}")
        raise AnalysisError(
            "Failed to read GitHub content",
            {"repo": repo_url, "path": path, "error": str(e)},
        )
    finally:
        github_client.close()

def read_github_content(repo: str, path: str, token: str) -> str:
    """
    Read content from a GitHub repository file.

    Args:
        repo: Repository full name (owner/repo)
        path: File path in the repository
        token: GitHub authentication token

    Returns:
        File content as string

    Raises:
        ValueError: If the path points to a directory instead of a file
    """
    github_client = Github(token)
    try:
        repo_obj = github_client.get_repo(repo)
        content = repo_obj.get_contents(path)
        if isinstance(content, list):
            raise ValueError("Path points to a directory, not a file")
        return content.decoded_content.decode("utf-8")
    finally:
        github_client.close()


class AnalysisError(Exception):
    def __init__(self, message, details=None):
        super().__init__(message)
        self.details = details