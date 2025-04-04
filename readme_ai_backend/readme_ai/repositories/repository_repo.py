from typing import List, Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from readme_ai.models.repository import Repository, FileContent  # type: ignore


class RepositoryRepo:
    def __init__(self, db_session: AsyncSession):
        self.db_session = db_session

    async def create_repository(self, name: str, url: str, user_id: str) -> Repository:
        repository = Repository(name=name, url=url, user_id=user_id)
        self.db_session.add(repository)
        await self.db_session.commit()
        await self.db_session.refresh(repository)
        return repository

    async def get_repository_by_id(self, repository_id: int) -> Optional[Repository]:
        query = select(Repository).where(Repository.id == repository_id)
        result = await self.db_session.execute(query)
        return result.scalars().first()

    async def get_repository_by_url(self, url: str) -> Optional[Repository]:
        query = select(Repository).where(Repository.url == url)
        result = await self.db_session.execute(query)
        return result.scalars().first()

    async def get_repositories_by_user_id(self, user_id: int) -> List[Repository]:
        query = select(Repository).where(Repository.user_id == user_id)
        result = await self.db_session.execute(query)
        return list(result.scalars().all())

    async def update_repository(
        self, repository_id: int, **kwargs
    ) -> Optional[Repository]:
        repository = await self.get_repository_by_id(repository_id)
        if not repository:
            return None

        for key, value in kwargs.items():
            if hasattr(repository, key):
                setattr(repository, key, value)

        await self.db_session.commit()
        await self.db_session.refresh(repository)
        return repository

    async def delete_repository(self, repository_id: int) -> bool:
        repository = await self.get_repository_by_id(repository_id)
        if not repository:
            return False

        await self.db_session.delete(repository)
        await self.db_session.commit()
        return True

    async def add_file_content(
        self,
        repository_id: int,
        content: str,
        content_embedding: list[float],
        path: str,
    ) -> FileContent:
        file_content = FileContent(
            content=content,
            repository_id=repository_id,
            content_embedding=content_embedding,
            path=path,
        )
        self.db_session.add(file_content)
        await self.db_session.commit()
        await self.db_session.refresh(file_content)
        return file_content

    async def get_file_content_by_id(self, file_id: int) -> Optional[FileContent]:
        query = select(FileContent).where(FileContent.id == file_id)
        result = await self.db_session.execute(query)
        return result.scalars().first()

    async def get_file_contents_by_repository_id(
        self, repository_id: int
    ) -> List[FileContent]:
        query = select(FileContent).where(FileContent.repository_id == repository_id)
        result = await self.db_session.execute(query)
        return list(result.scalars().all())

    async def update_file_content(
        self, file_id: int, **kwargs
    ) -> Optional[FileContent]:
        file_content = await self.get_file_content_by_id(file_id)
        if not file_content:
            return None

        for key, value in kwargs.items():
            if hasattr(file_content, key):
                setattr(file_content, key, value)

        await self.db_session.commit()
        await self.db_session.refresh(file_content)
        return file_content

    async def delete_file_content(self, file_id: int) -> bool:
        file_content = await self.get_file_content_by_id(file_id)
        if not file_content:
            return False

        await self.db_session.delete(file_content)
        await self.db_session.commit()
        return True

    async def search_similar_content(
        self, embedding: list, limit: int = 5
    ) -> List[FileContent]:
        query = (
            select(FileContent)
            .order_by(FileContent.content_embedding.cosine_distance(embedding))
            .limit(limit)
        )
        result = await self.db_session.execute(query)
        return list(result.scalars().all())
