from typing import List, Optional
from readme_ai.repositories.chat_repository import ChatRepository
from readme_ai.models.readme import ChatMessage


class ChatService:
    def __init__(self, chat_repository: ChatRepository):
        self.repository = chat_repository

    async def create_message(
        self,
        readme_id: int,
        role: str,
        content: str,
        readme_version_id: Optional[int] = None,
    ) -> ChatMessage:
        if role not in ["user", "assistant", "system"]:
            raise ValueError("Invalid role specified")

        return await self.repository.create_message(
            readme_id=readme_id,
            role=role,
            content=content,
            readme_version_id=readme_version_id,
        )

    async def get_readme_messages(self, readme_id: int) -> List[ChatMessage]:
        return await self.repository.get_readme_messages(readme_id)

    async def delete_messages(self, readme_id: int, user_id: str) -> bool:
        return await self.repository.delete_messages(readme_id)

    async def get_conversation_history(self, readme_id: int) -> List[dict]:
        messages = await self.repository.get_readme_messages(readme_id)
        return [
            {
                "role": message.role,
                "content": message.content,
                "created_at": message.created_at,
            }
            for message in messages
        ]
