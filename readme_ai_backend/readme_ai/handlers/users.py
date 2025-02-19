from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from readme_ai.database import get_db
from readme_ai.repositories.user_repository import UserRepository
from readme_ai.services.user_service import UserService
from readme_ai.models.requests.users import UserUpdate
from readme_ai.models.user import User  # type: ignore
from readme_ai.auth import require_auth
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)
router = APIRouter(prefix="/users", tags=["users"])


async def get_user_service(
    session: AsyncSession = Depends(get_db),
) -> UserService:
    repository = UserRepository(session)
    return UserService(repository)


@router.get("", response_model=List[User])
@limiter.limit("10/minute")
@require_auth()
async def get_users(
    request: Request,
    user_service: UserService = Depends(get_user_service),
) -> List[User]:
    return await user_service.get_all_users()


@router.get("/{user_id}", response_model=User)
@limiter.limit("10/minute")
@require_auth()
async def get_user(
    request: Request,
    user_id: int,
    user_service: UserService = Depends(get_user_service),
) -> User:
    user = await user_service.get_user_by_id(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.patch("/{user_id}", response_model=User)
@limiter.limit("10/minute")
@require_auth()
async def update_user(
    request: Request,
    user_id: int,
    update_data: UserUpdate,
    user_service: UserService = Depends(get_user_service),
) -> User:
    user = await user_service.update_user(user_id, update_data)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.delete("/{user_id}")
@limiter.limit("10/minute")
@require_auth()
async def delete_user(
    request: Request,
    user_id: int,
    user_service: UserService = Depends(get_user_service),
) -> dict:
    deleted = await user_service.delete_user(user_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="User not found")
    return {"message": "User deleted successfully"}


@router.post("/webhook/clerk")
async def clerk_webhook(
    request: Request, user_service: UserService = Depends(get_user_service)
) -> dict:
    payload = await request.json()
    event_type = payload.get("type")
    data = payload.get("data", {})

    match event_type:
        case "user.created":
            await user_service.create_user(
                clerk_id=data["id"], email=data["email_addresses"][0]["email_address"]
            )
            return {"status": "user created"}

        case "user.updated":
            user = await user_service.get_user_by_clerk_id(data["id"])
            if user:
                update_data = UserUpdate(
                    email=data["email_addresses"][0]["email_address"]
                )
                await user_service.update_user(user.id, update_data)
            return {"status": "user updated"}

        case "user.deleted":
            user = await user_service.get_user_by_clerk_id(data["id"])
            if user:
                await user_service.delete_user(user.id)
            return {"status": "user deleted"}

    return {"status": "event ignored"}
