from langchain_community.document_loaders import GithubFileLoader
from typing import Dict, List
from pathlib import Path
import fnmatch
import logging
import mimetypes

# Configure logging
logger = logging.getLogger(__name__)

class RepoAnalyzerAgent:
    def __init__(self, github_token: str):
        self.github_token = github_token
        logger.info("RepoAnalyzerAgent initialized")
        
    def _is_binary_file(self, file_path: str) -> bool:

         # Initialize MIME types database
        mimetypes.init()
        
        # Get MIME type for the file
        mime_type, _ = mimetypes.guess_type(file_path)
        
        # If MIME type couldn't be determined, check extension
        if mime_type is None:
            return True
            
        # Check if the MIME type is binary
        is_binary = not mime_type.startswith(('text/', 'application/json', 'application/xml'))

        return is_binary
        

    def _extract_repo_info(self, repo_url: str) -> Dict[str, str]:
        logger.debug(f"Extracting repo info from URL: {repo_url}")
        clean_url = repo_url.rstrip("/").replace(".git", "")
        parts = clean_url.split("github.com/")


            
        if len(parts) != 2:
            logger.error(f"Invalid GitHub URL format: {repo_url}")
            raise ValueError("Invalid GitHub repository URL")

        path_parts = parts[1].split("/")
        if len(path_parts) < 2:
            logger.error(f"Missing owner or repository name in URL: {repo_url}")
            raise ValueError("URL must contain owner and repository name")

        repo_info = {"owner": path_parts[0], "repo": path_parts[1]}
        logger.info(f"Successfully extracted repo info: {repo_info}")
        return repo_info

    async def _load_gitignore_patterns(self, repo_info: Dict[str, str]) -> List[str]:
        logger.debug(f"Loading .gitignore patterns for {repo_info['owner']}/{repo_info['repo']}")
        
        loader = GithubFileLoader(
            repo=f"{repo_info['owner']}/{repo_info['repo']}",
            branch="main",
            access_token=self.github_token,
            file_filter=lambda x: x.endswith(".gitignore"),
        )

        try:
            docs = loader.load()
            if docs:
                patterns = []
                for line in docs[0].page_content.splitlines():
                    line = line.strip()
                    if line and not line.startswith("#"):
                        patterns.append(line)
                logger.info(f"Loaded {len(patterns)} patterns from .gitignore")
                return patterns
        except Exception as e:
            logger.warning(f"Failed to load .gitignore: {str(e)}")

        default_patterns = [".git", "__pycache__", "node_modules", ".env", "venv", "*.pyc"]
        logger.info("Using default ignore patterns")
        return default_patterns

    def _create_file_filter(self, ignore_patterns: List[str]):
        logger.debug(f"Creating file filter with {len(ignore_patterns)} patterns")
        
        def file_filter(file_path: str) -> bool:

            if self._is_binary_file(file_path):
                logger.debug(f"Filtering out binary file: {file_path}")
                return False
    
            should_include = not any(
                fnmatch.fnmatch(file_path, pattern) for pattern in ignore_patterns
            )
            if not should_include:
                logger.debug(f"Filtering out file: {file_path}")
            return should_include

        return file_filter

    async def analyze_repo(self, repo_url: str) -> Dict:
        logger.info(f"Starting repository analysis for {repo_url}")
        
        repo_info = self._extract_repo_info(repo_url)
        ignore_patterns = await self._load_gitignore_patterns(repo_info)
        logger.debug(f"Ignore Patterns {ignore_patterns}")
        logger.debug("Initializing GitHub file loader")
        loader = GithubFileLoader(
            repo=f"{repo_info['owner']}/{repo_info['repo']}",
            branch="main",
            access_token=self.github_token,
            file_filter=self._create_file_filter(ignore_patterns),
        )
        
        try:
            logger.info("Loading repository documents")
            documents = loader.load()
            
            file_analysis = {}
            languages = {}
            
            logger.debug(f"Analyzing {len(documents)} documents")
            for doc in documents:
                file_path = doc.metadata["path"]
                ext = Path(file_path).suffix
                
                file_analysis[file_path] = {
                    "content": doc.page_content[:200],
                    "size": len(doc.page_content),
                    "type": ext,
                }
                
                if ext:
                    languages[ext] = languages.get(ext, 0) + 1
            
            analysis_result = {
                "repo_name": repo_info["repo"],
                "files": file_analysis,
                "languages": languages,
                "structure": {"files": list(file_analysis.keys())},
            }
            
            logger.info(f"Analysis complete. Found {len(file_analysis)} files in {len(languages)} languages")
            return analysis_result
            
        except Exception as e:
            logger.error(f"Error during repository analysis: {str(e)}")
            raise
