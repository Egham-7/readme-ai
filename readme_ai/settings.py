from pydantic_settings import BaseSettings
from typing import Optional
from functools import lru_cache


class Settings(BaseSettings):
    # API Keys
    GROQ_API_KEY: str
    GITHUB_TOKEN: str 

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

    class Config:
        env_file = ".env"
        case_sensitive = True


@lru_cache
def get_settings() -> Settings:
    return Settings()
