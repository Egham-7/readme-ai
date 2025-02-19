from typing import Optional, List
from readme_ai.repositories.user_repository import UserRepository
from readme_ai.models.users import User
from readme_ai.models.requests.users import UserUpdate


class UserService:
    def __init__(self, user_repository: UserRepository):
        self.user_repository = user_repository

    async def create_user(
        self, clerk_id: str, email: str, stripe_customer_id: Optional[str] = None
    ) -> User:
        return await self.user_repository.create_user(
            clerk_id=clerk_id, email=email, stripe_customer_id=stripe_customer_id
        )

    async def get_user_by_id(self, user_id: int) -> Optional[User]:
        return await self.user_repository.get_user_by_id(user_id)

    async def get_user_by_clerk_id(self, clerk_id: str) -> Optional[User]:
        return await self.user_repository.get_user_by_clerk_id(clerk_id)

    async def get_user_by_email(self, email: str) -> Optional[User]:
        return await self.user_repository.get_user_by_email(email)

    async def get_all_users(self) -> List[User]:
        return await self.user_repository.get_all_users()

    async def update_user(
        self, user_id: int, update_data: UserUpdate
    ) -> Optional[User]:
        user = await self.get_user_by_id(user_id)
        if user:
            user_data = update_data.model_dump(exclude_unset=True)
            for key, value in user_data.items():
                setattr(user, key, value)
            return await self.user_repository.update_user(user)
        return None

    async def delete_user(self, user_id: int) -> bool:
        return await self.user_repository.delete_user(user_id)
