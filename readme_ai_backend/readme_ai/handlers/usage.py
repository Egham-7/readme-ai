from fastapi import APIRouter, Depends, Request
from datetime import datetime, timezone, timedelta
from readme_ai.models.users import User
from readme_ai.database import get_db
from readme_ai.utils.token_reset import scheduler
from readme_ai.models.responses.usage import TokenResetResponse

router = APIRouter()


@router.get("/token-reset-time", response_model=TokenResetResponse)
async def get_token_reset_time(request: Request, db=Depends(get_db)):
    clerk_user = request.state.user
    user = (
        await db.query(User).filter(User.clerk_id == clerk_user.get_user_id()).first()
    )

    job_id = f"token_reset_{user.clerk_id}"
    job = scheduler.get_job(job_id)

    if job:
        next_reset = job.next_run_time
    else:
        next_reset = user.tokens_last_reset + timedelta(hours=3)

    return TokenResetResponse(
        current_token=user.tokens_balance,
        next_reset=next_reset.isoformat(),
        time_remaining=int((next_reset - datetime.now(timezone.utc)).total_seconds()),
    )

