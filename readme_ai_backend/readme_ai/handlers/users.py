from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import JSONResponse
from readme_ai.settings import get_settings
from sqlalchemy.ext.asyncio import AsyncSession
from readme_ai.database import get_db
from readme_ai.repositories.user_repository import UserRepository
from readme_ai.services.user_service import UserService
from readme_ai.models.requests.users import UserUpdate
from readme_ai.models.users import User
from readme_ai.auth import require_auth
from slowapi import Limiter
from slowapi.util import get_remote_address
from svix.webhooks import Webhook, WebhookVerificationError
from readme_ai.models.responses.users import UserResponse

limiter = Limiter(key_func=get_remote_address)
router = APIRouter(prefix="/users", tags=["users"])
settings = get_settings()


async def get_user_service(
    session: AsyncSession = Depends(get_db),
) -> UserService:
    repository = UserRepository(session)
    return UserService(repository)


@router.get("/{user_id}", response_model=UserResponse)
@limiter.limit("10/minute")
@require_auth()
async def get_user(
    request: Request,
    user_id: str,
    user_service: UserService = Depends(get_user_service),
):
    user = await user_service.get_user_by_clerk_id(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return UserResponse.from_orm(user)


@router.patch("/{user_id}", response_model=UserResponse)
@limiter.limit("10/minute")
@require_auth()
async def update_user(
    request: Request,
    user_id: int,
    update_data: UserUpdate,
    user_service: UserService = Depends(get_user_service),
):
    user = await user_service.update_user(user_id, update_data)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return UserResponse.from_orm(user)


@router.delete("/{user_id}")
@limiter.limit("10/minute")
@require_auth()
async def delete_user(
    request: Request,
    user_id: int,
    user_service: UserService = Depends(get_user_service),
) -> JSONResponse:
    deleted = await user_service.delete_user(user_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="User not found")
    return JSONResponse(content={"message": "User deleted successfully"})


@router.post("/webhook/clerk")
async def clerk_webhook(
    request: Request, user_service: UserService = Depends(get_user_service)
) -> JSONResponse:
    # Verify IP address
    client_ip = request.client.host if request.client else None
    if not client_ip or client_ip not in settings.SVIX_ALLOWED_IPS:
        raise HTTPException(status_code=403, detail="Invalid source IP")

    # Verify webhook signature
    svix_id = request.headers.get("svix-id", "")
    svix_timestamp = request.headers.get("svix-timestamp", "")
    svix_signature = request.headers.get("svix-signature", "")

    if not all([svix_id, svix_timestamp, svix_signature]):
        raise HTTPException(status_code=400, detail="Missing webhook headers")

    body = await request.body()
    wh = Webhook(settings.WEBHOOK_SECRET)
    try:
        payload = wh.verify(
            body,
            {
                "svix-id": svix_id,
                "svix-timestamp": svix_timestamp,
                "svix-signature": svix_signature,
            },
        )
    except WebhookVerificationError:
        raise HTTPException(status_code=400, detail="Invalid webhook signature")

    data = payload.get("data", {})
    event_type = payload.get("type")

    match event_type:
        case "user.created":
            created_user = await user_service.create_user(
                clerk_id=data["id"], email=data["email_addresses"][0]["email_address"]
            )
            if not created_user:
                raise HTTPException(status_code=400, detail="Failed to create user")
            return JSONResponse(
                content={"status": "user created", "user_id": created_user.id}
            )

        case "user.updated":
            found_user = await user_service.get_user_by_clerk_id(data["id"])
            if found_user:
                update_data = UserUpdate(
                    email=data["email_addresses"][0]["email_address"]
                )
                await user_service.update_user(found_user.id, update_data)
            return JSONResponse(content={"status": "user updated"})

        case "user.deleted":
            found_user = await user_service.get_user_by_clerk_id(data["id"])
            if found_user:
                await user_service.delete_user(found_user.id)
            return JSONResponse(content={"status": "user deleted"})

    return JSONResponse(content={"status": "event ignored"})
