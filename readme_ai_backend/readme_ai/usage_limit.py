from fastapi import Request
from fastapi.responses import JSONResponse
from datetime import datetime, timedelta, timezone
from functools import wraps
import logging
from app.db.session import get_db  # type: ignore
from app.models.user import User  # type: ignore
from readme_ai.utils.token_reset import schedule_token_reset  # type: ignore

logger = logging.getLogger(__name__)


def check_token_usage():
    def decorator(func):
        @wraps(func)
        async def wrapper(request: Request, *args, **kwargs):
            try:
                db = await get_db()
                clerk_user = request.state.user
                user = (
                    await db.query(User)
                    .filter(User.clerk_id == clerk_user.get_user_id())
                    .first()
                )

                if not user:
                    return JSONResponse(
                        status_code=404,
                        content={
                            "message": "User not found",
                            "error_code": "USER_NOT_FOUND",
                            "details": {
                                "error_type": "NotFoundError",
                                "error_message": "User does not exist in database",
                            },
                            "timestamp": datetime.now(timezone.utc).isoformat(),
                        },
                    )

                current_time = datetime.now(timezone.utc)
                if current_time - user.tokens_last_reset > timedelta(hours=3):
                    user.tokens_balance = 0
                    user.tokens_last_reset = current_time
                    await db.commit()

                if user.tokens_balance <= 0:
                    reset_time = datetime.now(timezone.utc) + timedelta(hours=3)
                    schedule_token_reset(user.clerk_id, reset_time, db)
                    return JSONResponse(
                        status_code=403,
                        content={
                            "message": "No tokens available",
                            "error_code": "INSUFFICIENT_TOKENS",
                            "details": {
                                "error_type": "TokenError",
                                "error_message": "Please purchase more tokens to continue or wait for your tokens to reset",
                                "reset": reset_time,
                            },
                            "timestamp": datetime.now(timezone.utc).isoformat(),
                        },
                    )

                user.tokens_balance -= 1
                await db.commit()
                return await func(request, *args, **kwargs)

            except Exception as e:
                logger.error(f"Error in token usage check: {str(e)}")
                return JSONResponse(
                    status_code=500,
                    content={
                        "message": "Error checking token usage",
                        "error_code": "INTERNAL_SERVER_ERROR",
                        "details": {
                            "error_type": type(e).__name__,
                            "error_message": str(e),
                        },
                        "timestamp": datetime.now(timezone.utc).isoformat(),
                    },
                )

        return wrapper

    return decorator
