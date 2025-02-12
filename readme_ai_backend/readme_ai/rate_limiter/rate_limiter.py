from fastapi_limiter import FastAPILimiter
from fastapi_limiter.depends import RateLimiter
import redis.asyncio as redis
from fastapi import HTTPException
import logging

logger = logging.getLogger(__name__)

async def setup_rate_limiter():
    redis_instance = await redis.Redis(
        host="localhost",
        port=6379,
        db=0,
        encoding="utf-8",
        decode_responses=True
    )
    await FastAPILimiter.init(redis_instance)

# Custom rate limiter for different user types
def rate_limit_by_user_type():
    async def limit_handler(request):
        if request.user.is_admin:  # Assuming you have user authentication
            return None  # No rate limit for admins
        elif request.user.is_authenticated:
            return RateLimiter(times=100, seconds=60)  # 100 requests per minute for authenticated users
        else:
            return RateLimiter(times=20, seconds=60)  # 20 requests per minute for anonymous users
    return limit_handler


