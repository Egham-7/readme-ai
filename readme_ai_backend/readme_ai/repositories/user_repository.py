from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Optional, List
from readme_ai.models.users import User


class UserRepository:
    def __init__(self, db_session: AsyncSession):
        self.db_session = db_session

    async def create_user(
        self, clerk_id: str, email: str, stripe_customer_id: Optional[str] = None
    ) -> User:
        user = User(
            clerk_id=clerk_id, email=email, stripe_customer_id=stripe_customer_id
        )
        self.db_session.add(user)
        await self.db_session.commit()
        return user

    async def get_user_by_id(self, user_id: int) -> Optional[User]:
        query = select(User).where(User.id == user_id)
        result = await self.db_session.execute(query)
        return result.scalar_one_or_none()

    async def get_user_by_clerk_id(self, clerk_id: str) -> Optional[User]:
        query = select(User).where(User.clerk_id == clerk_id)
        result = await self.db_session.execute(query)
        return result.scalar_one_or_none()

    async def get_user_by_email(self, email: str) -> Optional[User]:
        query = select(User).where(User.email == email)
        result = await self.db_session.execute(query)
        return result.scalar_one_or_none()

    async def get_all_users(self) -> List[User]:
        query = select(User)
        result = await self.db_session.execute(query)
        return list(result.scalars().all())

    async def update_user(self, user: User) -> User:
        await self.db_session.commit()
        return user

    async def delete_user(self, user_id: int) -> bool:
        user = await self.get_user_by_id(user_id)
        if user:
            await self.db_session.delete(user)
            await self.db_session.commit()
            return True
        return False
