from typing import List, Optional, Tuple
from readme_ai.repositories.readme_repository import ReadmeRepository
from readme_ai.models.readme import Readme, ReadmeVersion


class ReadmeService:
    def __init__(self, readme_repository: ReadmeRepository):
        self.repository = readme_repository

    async def create_readme(
        self, user_id: str, repository_url: str, title: str
    ) -> Readme:
        return await self.repository.create_readme(user_id, repository_url, title)

    async def get_readme(self, readme_id: int) -> Optional[Readme]:
        return await self.repository.get_readme(readme_id)

    async def get_readme_with_versions(self, readme_id: int) -> Optional[Readme]:
        return await self.repository.get_readme_with_versions(readme_id)

    async def get_user_readmes(
        self, user_id: str, page: int = 1, page_size: int = 10
    ) -> Tuple[List[Readme], int]:
        return await self.repository.get_user_readmes(user_id, page, page_size)

    async def create_version(self, readme_id: int, content: str) -> ReadmeVersion:
        readme = await self.repository.get_readme(readme_id)
        if not readme:
            raise ValueError("Readme not found")
        return await self.repository.create_version(readme_id, content)

    async def delete_readme(self, readme_id: int, user_id: str) -> bool:
        readme = await self.repository.get_readme(readme_id)
        if not readme:
            return False
        if readme.user_id != user_id:
            raise ValueError("Not authorized to delete this readme")
        return await self.repository.delete_readme(readme_id)

    async def update_readme(
        self, readme_id: int, user_id: str, content: str
    ) -> Optional[ReadmeVersion]:
        readme = await self.repository.get_readme_with_versions(readme_id)

        if not readme:
            raise ValueError("Readme not found")

        if readme.user_id != user_id:
            raise ValueError("Not authorized to update this readme")

        latest_version = (
            max(readme.versions, key=lambda v: v.version_number)
            if readme.versions
            else None
        )

        if latest_version:
            return await self.repository.update_version(latest_version.id, content)
        else:
            return await self.repository.create_version(readme_id, content)
