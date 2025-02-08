from pydantic_settings import BaseSettings  # type: ignore
from functools import lru_cache
import os


class Settings(BaseSettings):
    # API Keys
    GROQ_API_KEY: str = "test"
    GITHUB_TOKEN: str = "test"

    # App Settings
    APP_NAME: str = "README Generator"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False

    # Server Settings
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    WORKERS: int = 4

    # Repository Settings
    TEMP_DIR: str = "temp_repos"
    MAX_REPO_SIZE: int = 100_000_000  # 100MB

    # Model Settings
    MODEL_NAME: str = "mixtral-8x7b-32768"
    TEMPERATURE: float = 0.7

    # Cache Settings
    CACHE_TTL: int = 3600  # 1 hour
    MAX_CACHE_SIZE: int = 100

    DATABASE_URL: str = (
        f"postgresql://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}@{
        os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}"
    )

    class Config:
        env_file = ".env"
        case_sensitive = True


@lru_cache
def get_settings() -> Settings:
    return Settings()
