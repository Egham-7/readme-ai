from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from sqlalchemy.orm import joinedload
from typing import List, Optional, Tuple, cast

from readme_ai.models.readme import Readme, ReadmeVersion


class ReadmeRepository:
    def __init__(self, db_session: AsyncSession):
        self.db_session = db_session

    async def create_readme(
        self, user_id: str, repository_url: str, title: str
    ) -> Readme:
        readme = Readme(user_id=user_id, repository_url=repository_url, title=title)
        self.db_session.add(readme)
        await self.db_session.commit()
        return readme

    async def get_readme(self, readme_id: int) -> Optional[Readme]:
        query = select(Readme).where(Readme.id == readme_id)
        result = await self.db_session.execute(query)
        return result.scalar_one_or_none()

    async def get_readme_with_versions(self, readme_id: int) -> Optional[Readme]:
        query = (
            select(Readme)
            .options(joinedload(Readme.versions))
            .where(Readme.id == readme_id)
        )
        result = await self.db_session.execute(query)
        return result.scalar_one_or_none()

    async def get_user_readmes(
        self, user_id: str, page: int = 1, page_size: int = 10
    ) -> Tuple[List[Readme], int]:
        base_query = (
            select(Readme)
            .options(joinedload(Readme.versions))
            .where(Readme.user_id == user_id)
        )

        # Fix the select_from issue by using the correct table
        count_query = select(func.count()).select_from(Readme)
        total = await self.db_session.execute(count_query)
        total_count = cast(int, total.scalar() or 0)

        query = base_query.offset((page - 1) * page_size).limit(page_size)
        result = await self.db_session.execute(query)
        readmes = list(result.scalars().all())  # Convert to list explicitly

        total_pages = (total_count + page_size - 1) // page_size
        return readmes, total_pages

    async def create_version(self, readme_id: int, content: str) -> ReadmeVersion:
        # Get the latest version number
        query = select(func.max(ReadmeVersion.version_number)).where(
            ReadmeVersion.readme_id == readme_id
        )
        result = await self.db_session.execute(query)
        latest_version = result.scalar() or 0

        version = ReadmeVersion(
            readme_id=readme_id, version_number=latest_version + 1, content=content
        )
        self.db_session.add(version)
        await self.db_session.commit()
        return version

    async def delete_readme(self, readme_id: int) -> bool:
        readme = await self.get_readme(readme_id)
        if readme:
            await self.db_session.delete(readme)
            await self.db_session.commit()
            return True
        return False
