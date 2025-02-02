import json
import logging
import asyncio  
from dotenv import load_dotenv
from langgraph.graph import StateGraph, START, END
from typing import Dict, TypedDict, Annotated, List
from langchain_groq import ChatGroq
from langchain.prompts import ChatPromptTemplate
from github import Github  
import settings  
from langchain_core.pydantic_v1 import BaseModel, Field  
from langchain.output_parsers import PydanticOutputParser
from pydantic import BaseModel, Field, ValidationError
from langchain_core.exceptions import OutputParserException

# Load environment variables from .env file
load_dotenv()
settings = settings.get_settings()

# Configure logging for debugging and monitoring
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# Define the state used by the repository analysis graph.
class RepoAnalyzerState(TypedDict):
    messages: Annotated[List, "Messages for the analysis"]
    analysis: List         # List to store analysis results for each file
    important_files: List  # List of chosen important files (paths)
    repo_tree: str         # Markdown representation of the repository tree structure
    repo_url: str          # The URL of the repository to analyze


class RepoAnalyzerAgent:
    def __init__(self, groq_api_key: str, github_token: str):
        """
        Initializes the RepoAnalyzerAgent with the required tokens and builds the analysis graph.
        """
        logger.info("Initializing RepoAnalyzerAgent")
        self.github_token = github_token

        # Initialize the language model (ChatGroq) with the given API key and model settings.
        self.llm = ChatGroq(
            groq_api_key=groq_api_key,
            model_name="mixtral-8x7b-32768",  # Change this as needed for your use case.
            temperature=0.1
        )

        # Build the analysis graph which defines the steps of the analysis pipeline.
        self.graph = self._build_analysis_graph()
        logger.info("RepoAnalyzerAgent initialized successfully")

    def _build_analysis_graph(self) -> StateGraph:
        """
        Constructs the analysis graph with nodes and edges representing different steps.
        The graph comprises:
        - 'choose_files': Choose the important files from the repository tree.
        - 'analyze_files': Analyze each of the chosen files.
        """
        logger.info("Building analysis graph")
        graph = StateGraph(RepoAnalyzerState)
        # Add node to choose important files
        graph.add_node("choose_files", self._choose_files)
        # Add node to analyze files
        graph.add_node("analyze_files", self._analyze_files)
        # Define the order: start -> choose_files -> analyze_files -> end
        graph.add_edge(START, "choose_files")
        graph.add_edge("choose_files", "analyze_files")
        graph.add_edge("analyze_files", END)
        logger.info("Analysis graph built successfully")
        return graph.compile()

    def _validate_json(self, json_str: str) -> bool:
        try:
            json.loads(json_str)
            return True
        except json.JSONDecodeError:
            return False

    def _choose_files(self, state: RepoAnalyzerState):
        """
        Analyzes the repository tree structure (markdown) to choose the most important files for further analysis.
        
        This function:
          - Prints the repository tree for debugging.
          - Uses a Pydantic model to define the expected output schema.
          - Builds and invokes a prompt via ChatPromptTemplate to get the list of important file paths.
          - Returns the state with the chosen important files.
        """
        print("\n=== CHOOSING IMPORTANT FILES ===")
        print(f"Repository Tree:\n{state['repo_tree']}")

        # Define the expected structure for important files using Pydantic.
        class ImportantFiles(BaseModel):
            files: List[str] = Field(description="List of important repository file paths")

        # Create an output parser based on the Pydantic model to enforce the structure.
        parser = PydanticOutputParser(pydantic_object=ImportantFiles)

        # Build the prompt with clear instructions for the LLM.
        prompt = ChatPromptTemplate.from_messages([
            (
                "system",
                "You are a code analysis expert. Examine the repository structure and identify the most important files for analysis. "
                "Return ONLY a valid JSON object with a 'files' array containing the file paths. "
                "Do not include any additional text or markdown formatting."
            ),
            (
                "human",
                "Here is the repository structure. Return the important files as a JSON object:\n{repo_tree_md}"
            )
        ]).partial(format_instructions=parser.get_format_instructions())
    
        try:
            # Chain the prompt and LLM to get the raw output.
            chain = prompt | self.llm
            raw_output = chain.invoke({"repo_tree_md": state["repo_tree"]}).content
            logger.debug(f"Raw LLM output: {raw_output}")
            
            # Check if the output is valid JSON and parse it.
            if self._validate_json(raw_output):
                result = parser.invoke(raw_output)
            else:
                # Attempt to sanitize the output and re-parse.
                sanitized = raw_output.strip("` \n").replace("json\n", "")
                result = parser.invoke(sanitized)
            
            # Directly use the files provided by the LLM without additional filtering.
            valid_files = result.files
            logger.info(f"Selected Important Files: {valid_files}")
            
            return {**state, "important_files": valid_files}
        
        except (OutputParserException, ValidationError) as e:
            logger.error(f"Error parsing LLM response: {str(e)}")
            if isinstance(e, OutputParserException):
                logger.error(f"Invalid LLM output: {e.llm_output}")
            # If parsing fails, return an empty list.
            return {**state, "important_files": []}

    def _analyze_files(self, state: RepoAnalyzerState):
        """
        Analyzes the content of the important files selected in the previous step.
        
        For each important file:
          - Reads its content from GitHub.
          - If the file is not binary, performs a detailed analysis using the language model.
          - Collects and returns the analysis results.
        """
        print("\n=== ANALYZING FILES ===")
        print(f"Files to analyze: {state['important_files']}")
        
        files_content = {}
        # Loop through the list of important file paths and read their content.
        for file_path in state['important_files']:
            try:
                print(f"\nReading content for: {file_path}")
                content = read_github_content(state['repo_url'], file_path, self.github_token)
                files_content[file_path] = content
                print(f"Successfully read content for {file_path}")
            except Exception as e:
                print(f"ERROR reading {file_path}: {str(e)}")
                continue
        
        analyses = []
        print(f"\nStarting detailed analysis of {len(files_content)} files")
        
        # Analyze each file's content individually.
        for file_path, content in files_content.items():
            print(f"\nAnalyzing: {file_path}")
            if not self._is_binary_file(file_path):
                analysis = self._analyze_single_file(file_path, content)
                analyses.append(analysis)
                print(f"Analysis completed for: {file_path}")
                print(f"Analysis result: {analysis}")
            else:
                print(f"Skipping binary file: {file_path}")
        
        print(f"\nCompleted analysis of {len(analyses)} files")
        return {**state, "analysis": analyses}

    def _is_binary_file(self, file_path: str) -> bool:
        """
        Determines whether a file is likely binary by checking its extension.
        
        Args:
            file_path (str): The file path to check.
        
        Returns:
            bool: True if the file is binary, False otherwise.
        """
        binary_extensions = {
            # Image files
            '.png', '.jpg', '.jpeg', '.gif', '.bmp', '.ico', '.svg',
            # Document files
            '.pdf', '.doc', '.docx', '.xls', '.xlsx', '.ppt', '.pptx',
            # Archives
            '.zip', '.tar', '.gz', '.7z', '.rar',
            # Compiled or binary files
            '.pyc', '.exe', '.dll', '.so', '.class',
            # Database files
            '.db', '.sqlite', '.sqlite3',
            # Other binary types
            '.bin', '.dat'
        }
        extension = '.' + file_path.split('.')[-1].lower() if '.' in file_path else ''
        return extension in binary_extensions

    def _analyze_single_file(self, file_path: str, content: str):
        """
        Analyzes a single file's content by sending it to the language model for extraction of key details.
        
        Args:
            file_path (str): The file path being analyzed.
            content (str): The file's content.
        
        Returns:
            dict: A dictionary containing the file path and its analysis.
        """
        logger.info(f"Analyzing file: {file_path}")
        analysis_prompt = ChatPromptTemplate.from_messages([
            (
                "system",
                "Analyze this file and extract key information about its purpose and functionality. "
                "Return your analysis as plain text."
            ),
            (
                "human",
                "File path: {file_path}\nContent:\n{file_content}"
            )
        ])
        
        # Invoke the language model with the formatted prompt.
        response = self.llm.invoke(analysis_prompt.format(
            file_path=file_path,
            file_content=content
        ))
        
        # Extract the content of the response.
        result = {
            "path": file_path,
            "analysis": response.content if hasattr(response, 'content') else str(response)
        }
        
        logger.debug(f"Analysis completed for {file_path}")
        return result
    
    async def analyze_repo(self, repo_url: str):
        """
        Top-level asynchronous generator that orchestrates the entire repository analysis.
        
        Steps:
          1. Retrieve the repository tree structure using get_repo_tree.
          2. Initialize the analysis state.
          3. Stream through each step of the analysis graph.
          4. Yield each step's output as a JSON string.
        """
        print("\n=== STARTING REPOSITORY ANALYSIS ===")
        print(f"Repository URL: {repo_url}")
        
        # Retrieve the repository tree (markdown representation) using a helper function.
        repo_tree = get_repo_tree(repo_url)
        print(f"\nRepository Structure:\n{repo_tree}")
        
        # Initialize the analysis state with the repository details.
        initial_state = {
            "messages": [{"role": "user", "content": f"Analyze repository: {repo_url}"}],
            "repo_tree": repo_tree,
            "repo_url": repo_url,
            "important_files": [],
            "analysis": []
        }
        
        print("\n=== STARTING ANALYSIS STREAM ===")
        # Stream through each step in the analysis graph.
        for step in self.graph.stream(initial_state):
            # If step is an AIMessage, convert it to a serializable dictionary.
            if hasattr(step, 'content'):
                serialized_step = {
                    "content": step.content,
                    "type": "ai_message"
                }
            else:
                serialized_step = step
                
            print(f"\nStep Output: {serialized_step}")
            # Yield each step as a JSON string with a newline.
            yield json.dumps(serialized_step) + "\n"
            await asyncio.sleep(0)  # Allow async context switching
        
        print("\n=== ANALYSIS COMPLETED ===")


def get_repo_tree(repo_url: str) -> str:
    """
    Retrieves the tree structure of a GitHub repository in markdown format.
    
    Args:
        repo_url (str): The URL of the GitHub repository.
    
    Returns:
        str: A markdown string representing the repository's file structure.
    """
    # Initialize GitHub client using the provided token from settings.
    g = Github(settings.GITHUB_TOKEN)
    
    # Parse the repository URL to extract owner and repository name.
    repo_parts = repo_url.rstrip("/").replace(".git", "").split("github.com/")[1].split("/")
    owner, repo_name = repo_parts[0], repo_parts[1]
    
    # Get the repository using the GitHub API.
    repo = g.get_repo(f"{owner}/{repo_name}")
    contents = repo.get_contents("")
    tree = []
    
    # Traverse the repository contents recursively.
    while contents:
        file_content = contents.pop(0)
        if file_content.type == "dir":
            # Extend the list with files inside the directory.
            contents.extend(repo.get_contents(file_content.path))
            tree.append(f"{'-' * file_content.path.count('/')} {file_content.name}/")
        else:
            tree.append(f"{'-' * file_content.path.count('/')} {file_content.name}")
    
    # Join the list into a markdown formatted string.
    return "\n".join(tree)


def read_file_content(file_path: str) -> str:
    """
    Reads and returns the content of a local file.
    
    Args:
        file_path (str): The local file path.
    
    Returns:
        str: The content of the file.
    """
    with open(file_path, 'r', encoding='utf-8') as file:
        return file.read()


async def read_github_content(repo: str, path: str, token: str) -> str:
    """
    Asynchronously reads and returns the content of a file from a GitHub repository.
    
    Args:
        repo (str): Repository in the format "owner/repo".
        path (str): The file path in the repository.
        token (str): GitHub access token.
    
    Returns:
        str: The decoded file content.
    """
    g = Github(token)
    repo_obj = g.get_repo(repo)
    content = repo_obj.get_contents(path)
    # Decode the content from bytes to UTF-8 string.
    return content.decoded_content.decode('utf-8')