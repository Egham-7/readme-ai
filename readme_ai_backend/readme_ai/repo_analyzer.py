import json
import logging
from typing import Any, Dict, TypedDict, Annotated, List
from langgraph.graph import StateGraph, START, END  # type: ignore
from langchain_groq import ChatGroq  # type: ignore
from langchain.prompts import ChatPromptTemplate  # type: ignore
from github import Github  # type: ignore
from langchain_core.pydantic_v1 import BaseModel, Field  # type: ignore
from langchain.output_parsers import PydanticOutputParser  # type: ignore
from pydantic import ValidationError  # type: ignore
from langchain_core.exceptions import OutputParserException  # type: ignore


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class RepoAnalyzerState(TypedDict):
    messages: Annotated[List[Dict[str, str]], "Messages for the analysis"]
    # List to store analysis results for each file
    analysis: List[Dict[str, str]]
    important_files: List[str]  # List of chosen important files (paths)
    repo_tree: str  # Markdown representation of the repository tree structure
    repo_url: str  # The URL of the repository to analyze


class RepoAnalyzerAgent:
    def __init__(self, groq_api_key: str, github_token: str):
        """Initialize the RepoAnalyzerAgent with required tokens and build analysis graph."""
        logger.info("Initializing RepoAnalyzerAgent")
        self.github_token = github_token
        self.llm = ChatGroq(
            groq_api_key=groq_api_key,
            model_name="mixtral-8x7b-32768",
            temperature=0.1,
        )
        self.graph = self._build_analysis_graph()
        logger.info("RepoAnalyzerAgent initialized successfully")

    def _build_analysis_graph(self) -> StateGraph:
        """Construct the analysis graph with nodes and edges."""
        logger.info("Building analysis graph")
        graph = StateGraph(RepoAnalyzerState)

        graph.add_node("choose_files", self._choose_files)
        graph.add_node("analyze_files", self._analyze_files)

        graph.add_edge(START, "choose_files")
        graph.add_edge("choose_files", "analyze_files")
        graph.add_edge("analyze_files", END)

        logger.info("Analysis graph built successfully")
        return graph.compile()

    def _validate_json(self, json_str: str) -> bool:
        """Validate if a string is valid JSON."""
        try:
            json.loads(json_str)
            return True
        except json.JSONDecodeError:
            return False

    def _choose_files(self, state: RepoAnalyzerState) -> RepoAnalyzerState:
        """Choose important files from repository for analysis."""
        print("\n=== CHOOSING IMPORTANT FILES ===")
        print(f"Repository Tree:\n{state['repo_tree']}")

        class ImportantFiles(BaseModel):
            files: List[str] = Field(
                description="List of important repository file paths"
            )

        parser = PydanticOutputParser(pydantic_object=ImportantFiles)
        prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    "You are a code analysis expert. Examine the repository structure and identify the most important files for analysis. "
                    "Return ONLY a valid JSON object with a 'files' array containing the file paths. "
                    "Do not include any additional text or markdown formatting.",
                ),
                (
                    "human",
                    "Here is the repository structure. Return the important files as a JSON object:\n{repo_tree_md}",
                ),
            ]
        ).partial(format_instructions=parser.get_format_instructions())

        try:
            chain = prompt | self.llm
            raw_output = chain.invoke(
                {"repo_tree_md": state["repo_tree"]}).content
            logger.debug(f"Raw LLM output: {raw_output}")

            if self._validate_json(raw_output):
                result = parser.invoke(raw_output)
            else:
                sanitized = raw_output.strip("` \n").replace("json\n", "")
                result = parser.invoke(sanitized)

            valid_files = result.files
            logger.info(f"Selected Important Files: {valid_files}")
            return {**state, "important_files": valid_files}

        except (OutputParserException, ValidationError) as e:
            logger.error(f"Error parsing LLM response: {str(e)}")
            if isinstance(e, OutputParserException):
                logger.error(f"Invalid LLM output: {e.llm_output}")
            return {**state, "important_files": []}

    async def _analyze_files(self, state: RepoAnalyzerState) -> RepoAnalyzerState:
        """Analyze content of selected important files."""
        print("\n=== ANALYZING FILES ===")
        print(f"Files to analyze: {state['important_files']}")

        files_content = {}
        for file_path in state["important_files"]:
            try:
                print(f"\nReading content for: {file_path}")
                content = await read_github_content(
                    state["repo_url"], file_path, self.github_token
                )
                files_content[file_path] = content
                print(f"Successfully read content for {file_path}")
            except Exception as e:
                print(f"ERROR reading {file_path}: {str(e)}")
                continue

        analyses = []
        print(f"\nStarting detailed analysis of {len(files_content)} files")

        for file_path, content in files_content.items():
            print(f"\nAnalyzing: {file_path}")
            if not self._is_binary_file(file_path):
                analysis = await self._analyze_single_file(file_path, content)
                analyses.append(analysis)
                print(f"Analysis completed for: {file_path}")
                print(f"Analysis result: {analysis}")
            else:
                print(f"Skipping binary file: {file_path}")

        print(f"\nCompleted analysis of {len(analyses)} files")
        return {**state, "analysis": analyses}

    def _is_binary_file(self, file_path: str) -> bool:
        """Determine if a file is binary based on its extension."""
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
        extension = "." + \
            file_path.split(".")[-1].lower() if "." in file_path else ""
        return extension in binary_extensions

    async def _analyze_single_file(
        self, file_path: str, content: str
    ) -> Dict[str, str]:
        """Analyze a single file's content using the language model."""
        logger.info(f"Analyzing file: {file_path}")

        analysis_prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    "Analyze this file and extract key information about its purpose and functionality. "
                    "Return your analysis as plain text.",
                ),
                ("human", "File path: {file_path}\nContent:\n{file_content}"),
            ]
        )

        response = self.llm.invoke(
            analysis_prompt.format(file_path=file_path, file_content=content)
        )

        result = {
            "path": file_path,
            "analysis": response.content
            if hasattr(response, "content")
            else str(response),
        }

        logger.debug(f"Analysis completed for {file_path}")
        return result

    async def analyze_repo(self, repo_url: str) -> Dict[str, Any]:
        """Orchestrate the repository analysis process and return results as a dictionary."""
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

        # Run the graph and collect all steps
        results = []
        for step in self.graph.stream(initial_state):
            if hasattr(step, "content"):
                serialized_step = {
                    "content": step.content, "type": "ai_message"}
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
    """Get repository tree structure in markdown format."""
    g = Github(github_token)
    repo_parts = (
        repo_url.rstrip("/").replace(".git",
                                     "").split("github.com/")[1].split("/")
    )
    owner, repo_name = repo_parts[0], repo_parts[1]

    repo = g.get_repo(f"{owner}/{repo_name}")
    contents = repo.get_contents("")
    tree = []

    while contents:
        file_content = contents.pop(0)
        if file_content.type == "dir":
            contents.extend(repo.get_contents(file_content.path))
            tree.append(
                f"{'-' * file_content.path.count('/')} {file_content.name}/")
        else:
            tree.append(
                f"{'-' * file_content.path.count('/')} {file_content.name}")

    return "\n".join(tree)


def read_file_content(file_path: str) -> str:
    """Read content from a local file."""
    with open(file_path, "r", encoding="utf-8") as file:
        return file.read()


async def read_github_content(repo: str, path: str, token: str) -> str:
    """Asynchronously read content from a GitHub repository file."""
    g = Github(token)
    repo_obj = g.get_repo(repo)
    content = repo_obj.get_contents(path)
    return content.decoded_content.decode("utf-8")

