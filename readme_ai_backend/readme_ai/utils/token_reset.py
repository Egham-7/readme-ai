from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from readme_ai.models.users import User
from apscheduler.schedulers.asyncio import AsyncIOScheduler  # type: ignore
from apscheduler.triggers.date import DateTrigger  # type: ignore


async def reset_user_tokens(user_id: str, db: AsyncSession):
    # Query single user instead of all users
    query = select(User).where(User.clerk_id == user_id)
    result = await db.execute(query)
    user = result.scalar_one_or_none()

    if user:
        user.tokens_last_reset = datetime.now(timezone.utc)
        user.tokens_balance = 0  # Or set to default amount
        await db.commit()


scheduler = AsyncIOScheduler()
scheduler.start()


def schedule_token_reset(user_id: str, reset_time: datetime, db: AsyncSession):
    job_id = f"token_reset_{user_id}"

    if scheduler.get_job(job_id):
        scheduler.remove_job(job_id)

    scheduler.add_job(
        reset_user_tokens,
        trigger=DateTrigger(run_date=reset_time),
        id=job_id,
        args=[user_id, db],
    )
