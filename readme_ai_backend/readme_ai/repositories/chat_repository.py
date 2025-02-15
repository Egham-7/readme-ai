from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List, Optional

from readme_ai.models.readme import ChatMessage


class ChatRepository:
    def __init__(self, db_session: AsyncSession):
        self.db_session = db_session

    async def create_message(
        self,
        readme_id: int,
        role: str,
        content: str,
        readme_version_id: Optional[int] = None,
    ) -> ChatMessage:
        message = ChatMessage(
            readme_id=readme_id,
            readme_version_id=readme_version_id,
            role=role,
            content=content,
        )
        self.db_session.add(message)
        await self.db_session.commit()
        return message

    async def get_readme_messages(self, readme_id: int) -> List[ChatMessage]:
        query = (
            select(ChatMessage)
            .where(ChatMessage.readme_id == readme_id)
            .order_by(ChatMessage.created_at)
        )
        result = await self.db_session.execute(query)
        return list(result.scalars().all())

    async def delete_messages(self, readme_id: int) -> bool:
        query = select(ChatMessage).where(ChatMessage.readme_id == readme_id)
        result = await self.db_session.execute(query)
        messages = result.scalars().all()

        for message in messages:
            await self.db_session.delete(message)

        await self.db_session.commit()
        return True
