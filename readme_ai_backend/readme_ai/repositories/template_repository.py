from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, or_
from typing import List, Optional
from readme_ai.models.template import Template


class TemplateRepository:
    def __init__(self, db_session: AsyncSession):
        self.db_session = db_session

    async def create(
        self,
        title: str,
        content: str,
        user_id: Optional[str] = None,
        preview_image: Optional[str] = None,
    ) -> Template:
        template = Template(
            title=title, content=content, user_id=user_id, preview_image=preview_image
        )
        self.db_session.add(template)
        await self.db_session.commit()
        await self.db_session.refresh(template)
        return template

    async def update(
        self,
        template_id: int,
        title: str,
        content: str,
        preview_image: Optional[str] = None,
    ) -> Optional[Template]:
        template = await self.get_by_id(template_id)
        if template:
            template.title = title
            template.content = content
            if preview_image is not None:
                template.preview_image = preview_image
            await self.db_session.commit()
            await self.db_session.refresh(template)
        return template

    # Existing methods remain unchanged
    async def get_by_id(self, template_id: int) -> Optional[Template]:
        result = await self.db_session.execute(
            select(Template).filter(Template.id == template_id)
        )
        return result.scalar_one_or_none()

    async def get_all(
        self, query: Optional[str], page: int = 1, page_size: int = 10
    ) -> List[Template]:
        offset = (page - 1) * page_size

        stmt = select(Template)

        if query:
            stmt = stmt.filter(
                or_(
                    func.to_tsvector("english", Template.title).op("@@")(
                        func.plainto_tsquery("english", query)
                    ),
                    func.to_tsvector("english", Template.content).op("@@")(
                        func.plainto_tsquery("english", query)
                    ),
                )
            )

        # Add pagination
        stmt = stmt.offset(offset).limit(page_size)

        # Execute the query
        result = await self.db_session.execute(stmt)

        return list(result.scalars().all())

    async def get_all_by_user_id(
        self, user_id: str, query: Optional[str], page: int = 1, page_size: int = 10
    ) -> List[Template]:
        offset = (page - 1) * page_size

        # Start building the base query
        stmt = select(Template).filter(Template.user_id == user_id)

        # Add search filter if query is not empty
        if query:
            # Using PostgreSQL full-text search
            # Search in both title and content
            stmt = stmt.filter(
                or_(
                    func.to_tsvector("english", Template.title).op("@@")(
                        func.plainto_tsquery("english", query)
                    ),
                    func.to_tsvector("english", Template.content).op("@@")(
                        func.plainto_tsquery("english", query)
                    ),
                )
            )

        # Add pagination
        stmt = stmt.offset(offset).limit(page_size)

        # Execute the query
        result = await self.db_session.execute(stmt)

        return list(result.scalars().all())

    async def delete(self, template_id: int) -> bool:
        template = await self.get_by_id(template_id)
        if template:
            await self.db_session.delete(template)
            await self.db_session.commit()
            return True
        return False

    async def get_total_count(self) -> int:
        try:
            result = await self.db_session.execute(select(Template))
            return len(result.scalars().all())
        except Exception as e:
            raise Exception(f"Failed to get total count: {str(e)}")

    async def get_total_count_by_user_id(self, user_id: str) -> int:
        try:
            result = await self.db_session.execute(
                select(Template).filter(Template.user_id == user_id)
            )
            return len(result.scalars().all())
        except Exception as e:
            raise Exception(f"Failed to get total count: {str(e)}")
