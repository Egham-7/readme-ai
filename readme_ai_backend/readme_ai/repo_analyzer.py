from urllib.parse import urlparse
from github.ContentFile import ContentFile
from github import Github, UnknownObjectException
from typing import List
import logging
from typing import Dict, Any, TypedDict, Annotated, cast
from langgraph.graph import StateGraph, START, END
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
    def __init__(self, groq_api_key: str, github_token: str):
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

    def _analyze_files(self, state: RepoAnalyzerState) -> RepoAnalyzerState:
        print("\n=== ANALYZING FILES ===")
        print(f"Files to analyze: {state['important_files']}")

        files_content = {}
        for file_path in state["important_files"]:
            try:
                print(f"\nReading content for: {file_path}")
                content = read_github_content(
                    state["repo_url"], file_path, self.github_token
                )
                files_content[file_path] = content
                print(f"Successfully read content for {file_path}")
            except Exception as e:
                print(f"ERROR reading {file_path}: {str(e)}")
                continue

        analyses = []
        print(f"\nStarting detailed analysis of {len(files_content)} files")

        structured_llm = self.llm.with_structured_output(FileAnalysis)

        for file_path, content in files_content.items():
            print(f"\nAnalyzing: {file_path}")
            if not self._is_binary_file(file_path):
                analysis = self._analyze_single_file(file_path, content, structured_llm)
                analyses.append(analysis)
                print(f"Analysis completed for: {file_path}")
                print(f"Analysis result: {analysis}")
            else:
                print(f"Skipping binary file: {file_path}")

        print(f"\nCompleted analysis of {len(analyses)} files")
        return {**state, "analysis": analyses}

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
        data_extensions = {'.csv', '.json', '.xml', '.yaml', '.yml', '.dat'}
        extension = "." + file_path.split(".")[-1].lower() if "." in file_path else ""
        
        if extension in data_extensions:
            return {
                "path": file_path,
                "analysis": f"Data file {file_path} containing structured data for the application"
            }

        analysis_prompt = ChatPromptTemplate.from_messages([
            (
                "system",
                """Extract key README documentation elements:
                1. Setup & Installation
                2. Core Features & Usage
                3. Configuration
                4. Quick Start Examples"""
            ),
            (
                "human",
                """File: {file_path}
                Content: {file_content}
                
                Extract the essential documentation points."""
            )
        ])

        result = structured_llm.invoke(
            analysis_prompt.format(file_path=file_path, file_content=content)
        )

        return {"path": result.path, "analysis": result.analysis}


    def analyze_repo(self, repo_url: str) -> Dict[str, Any]:
        print("\n=== STARTING REPOSITORY ANALYSIS ===")
        print(f"Repository URL: {repo_url}")

        repo_tree = get_repo_tree(repo_url, self.github_token)
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

        results = []
        for step in self.graph.stream(initial_state):
            if hasattr(step, "content"):
                serialized_step = {"content": step.content, "type": "ai_message"}
            else:
                serialized_step = step
            results.append(serialized_step)
            print(f"\nStep Output: {serialized_step}")

        print("\n=== ANALYSIS COMPLETED ===")

        return {
            "repo_url": repo_url,
            "repo_tree": repo_tree,
            "important_files": results[-1].get("important_files", []),
            "analysis": results[-1].get("analysis", []),
            "steps": results,
        }


def get_repo_tree(repo_url: str, github_token: str) -> str:
    """
    Generate a tree-like structure of files and directories from a GitHub repository.

    Args:
        repo_url: GitHub repository URL
        github_token: GitHub authentication token

    Returns:
        String representation of the repository structure

    Raises:
        ValueError: If the repository URL is invalid
        UnknownObjectException: If the repository is not found
    """

    def parse_github_url(url: str) -> tuple[str, str]:
        """Extract owner and repo name from GitHub URL"""
        parsed = urlparse(url)
        if "github.com" not in parsed.netloc:
            raise ValueError("Invalid GitHub URL")

        path_parts = parsed.path.strip("/").split("/")
        if len(path_parts) < 2:
            raise ValueError("Invalid repository path")

        return path_parts[0], path_parts[1].replace(".git", "")

    def build_tree(content_list: List[ContentFile], repo) -> List[str]:
        """Recursively build tree structure"""
        tree = []
        contents = content_list.copy()

        while contents:
            file_content = contents.pop(0)
            indent = "  " * file_content.path.count("/")

            if file_content.type == "dir":
                tree.append(f"{indent}📁 {file_content.name}/")
                contents.extend(repo.get_contents(file_content.path))
            else:
                tree.append(f"{indent}📄 {file_content.name}")

        return tree

    github_client = Github(github_token)
    owner, repo_name = parse_github_url(repo_url)

    try:
        repo = github_client.get_repo(f"{owner}/{repo_name}")
        initial_contents = repo.get_contents("")

        if not isinstance(initial_contents, list):
            initial_contents = [initial_contents]

        tree_structure = build_tree(initial_contents, repo)
        return "\n".join(tree_structure)

    except UnknownObjectException:
        raise ValueError(f"Repository {owner}/{repo_name} not found")
    finally:
        github_client.close()


async def read_github_content(repo: str, path: str, token: str) -> str:
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
