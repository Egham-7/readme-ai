from langchain_community.document_loaders import GithubFileLoader
from typing import Dict
from pathlib import Path
import logging
import mimetypes

logger = logging.getLogger(__name__)

class RepoAnalyzerAgent:
    def __init__(self, github_token: str):
        self.github_token = github_token
        mimetypes.init()

    def _is_binary_file(self, file_path: str) -> bool:
        mime_type, _ = mimetypes.guess_type(file_path)
        return not mime_type or not mime_type.startswith(('text/', 'application/json', 'application/xml'))

    def _extract_repo_info(self, repo_url: str) -> Dict[str, str]:
        parts = repo_url.rstrip("/").replace(".git", "").split("github.com/")[1].split("/")
        return {"owner": parts[0], "repo": parts[1]}

    def _sample_content(self, content: str, segments: int = 10, sample_ratio: float = 0.01) -> str:
        if not content:
            return ""

        lines = content.splitlines()
        total_lines = len(lines)
        segment_size = total_lines // segments  # Size of each 10% segment
        sampled_lines = []

        for i in range(segments):
            start = i * segment_size
            end = start + segment_size
            segment_lines = lines[start:end]  # Extract segment

            if segment_lines:
                sample_size = max(1, int(len(segment_lines) * sample_ratio))  # Take 1% of this segment
                sampled_lines.extend(segment_lines[:sample_size])  # Take from the start of the segment

        return "\n".join(sampled_lines)


    async def analyze_repo(self, repo_url: str) -> Dict:
        repo_info = self._extract_repo_info(repo_url)
        
        loader = GithubFileLoader(
            repo=f"{repo_info['owner']}/{repo_info['repo']}",
            branch="main",
            access_token=self.github_token,
            file_filter=lambda x: not self._is_binary_file(x)
        )

        try:
            project_analysis = {
                "repo_name": repo_info["repo"],
                "files": {},
                "languages": {},
                "structure": []
            }

            for doc in loader.load():
                file_path = doc.metadata["path"]
                file_name = Path(file_path).name
                ext = Path(file_path).suffix

                # Track language statistics
                if ext:
                    project_analysis["languages"][ext] = project_analysis["languages"].get(ext, 0) + 1

                file_content = {
                    "content": self._sample_content(doc.page_content),
                    "size": len(doc.page_content),
                    "type": ext
                }

                # Store file analysis
                project_analysis["files"][file_path] = file_content
                project_analysis["structure"].append(file_path)

            return project_analysis

        except Exception as e:
            logger.error(f"Error analyzing repository: {str(e)}")
            raise
