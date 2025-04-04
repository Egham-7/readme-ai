from typing import List, Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession

from readme_ai.repositories.repository_repo import RepositoryRepo
from readme_ai.models.repository import Repository, FileContent  # type: ignore


class RepositoryService:
    def __init__(self, db_session: AsyncSession):
        self.repository_repo = RepositoryRepo(db_session)

    async def create_repository(self, name: str, url: str, user_id: str) -> Repository:
        # Check if repository with the same URL already exists
        existing_repo = await self.repository_repo.get_repository_by_url(url)
        if existing_repo:
            raise ValueError(f"Repository with URL {url} already exists")

        return await self.repository_repo.create_repository(name, url, user_id)

    async def get_repository(self, repository_id: int) -> Optional[Repository]:
        return await self.repository_repo.get_repository_by_id(repository_id)

    async def get_repository_by_url(self, url: str) -> Optional[Repository]:
        return await self.repository_repo.get_repository_by_url(url)

    async def get_user_repositories(self, user_id: int) -> List[Repository]:
        return await self.repository_repo.get_repositories_by_user_id(user_id)

    async def update_repository(
        self, repository_id: int, data: Dict[str, Any]
    ) -> Optional[Repository]:
        return await self.repository_repo.update_repository(repository_id, **data)

    async def delete_repository(self, repository_id: int) -> bool:
        # This will cascade delete all associated file contents
        return await self.repository_repo.delete_repository(repository_id)

    async def add_file_content(
        self, repository_id: int, content: str, embedding: list
    ) -> FileContent:
        # Verify repository exists
        repository = await self.repository_repo.get_repository_by_id(repository_id)
        if not repository:
            raise ValueError(f"Repository with ID {repository_id} not found")

        return await self.repository_repo.add_file_content(
            repository_id, content, embedding
        )

    async def get_file_content(self, file_id: int) -> Optional[FileContent]:
        return await self.repository_repo.get_file_content_by_id(file_id)

    async def get_repository_file_contents(
        self, repository_id: int
    ) -> List[FileContent]:
        return await self.repository_repo.get_file_contents_by_repository_id(
            repository_id
        )

    async def update_file_content(
        self, file_id: int, data: Dict[str, Any]
    ) -> Optional[FileContent]:
        return await self.repository_repo.update_file_content(file_id, **data)

    async def delete_file_content(self, file_id: int) -> bool:
        return await self.repository_repo.delete_file_content(file_id)

    async def search_similar_content(
        self, embedding: list, limit: int = 5
    ) -> List[FileContent]:
        return await self.repository_repo.search_similar_content(embedding, limit)
