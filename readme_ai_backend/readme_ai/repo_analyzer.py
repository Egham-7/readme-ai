from langchain_community.document_loaders import GithubFileLoader
from typing import Dict, List
from pathlib import Path
import fnmatch

class RepoAnalyzerAgent:
    def __init__(self, github_token: str):
        self.github_token = github_token

    def _extract_repo_info(self, repo_url: str) -> Dict[str, str]:
        clean_url = repo_url.rstrip("/").replace(".git", "")
        parts = clean_url.split("github.com/")
        if len(parts) != 2:
            raise ValueError("Invalid GitHub repository URL")
        path_parts = parts[1].split("/")
        if len(path_parts) < 2:
            raise ValueError("URL must contain owner and repository name")
        return {"owner": path_parts[0], "repo": path_parts[1]}

    async def _load_gitignore_patterns(self, repo_info: Dict[str, str]) -> List[str]:
        loader = GithubFileLoader(
            repo=f"{repo_info['owner']}/{repo_info['repo']}",
            branch="main",
            access_token=self.github_token,
            file_filter=lambda x: x.endswith(".gitignore"),
        )
        docs = loader.load()
        if docs:
            patterns = []
            for line in docs[0].page_content.splitlines():
                line = line.strip()
                if line and not line.startswith("#"):
                    patterns.append(line)
            return patterns
        return [".git", "__pycache__", "node_modules", ".env", "venv", "*.pyc"]

    def _create_file_filter(self, ignore_patterns: List[str]):
        def file_filter(file_path: str) -> bool:
            return not any(
                fnmatch.fnmatch(file_path, pattern) for pattern in ignore_patterns
            )
        return file_filter

    async def analyze_repo(self, repo_url: str) -> Dict:
        repo_info = self._extract_repo_info(repo_url)
        ignore_patterns = await self._load_gitignore_patterns(repo_info)
        
        loader = GithubFileLoader(
            repo=f"{repo_info['owner']}/{repo_info['repo']}",
            branch="main",
            access_token=self.github_token,
            file_filter=self._create_file_filter(ignore_patterns),
        )
        
        documents = loader.load()
        file_analysis = {}
        languages = {}
        
        for doc in documents:
            file_path = doc.metadata["path"]
            ext = Path(file_path).suffix
            file_analysis[file_path] = {
                "content": doc.page_content[:1000],
                "size": len(doc.page_content),
                "type": ext,
            }
            if ext:
                languages[ext] = languages.get(ext, 0) + 1
                
        return {
            "repo_name": repo_info["repo"],
            "files": file_analysis,
            "languages": languages,
            "structure": {"files": list(file_analysis.keys())},
        }
