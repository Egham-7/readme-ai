from readme_ai.settings import get_settings
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker

settings = get_settings()

engine = create_async_engine(settings.DATABASE_URL)
AsyncSessionLocal = async_sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)


async def get_db():
    async with AsyncSessionLocal() as db:
        yield db
