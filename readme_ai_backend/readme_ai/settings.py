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

    # Database Settings
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL", "postgresql://postgres:secretpassword@postgres:5432/readmeai"
    )

    # MinIO Settings
    MINIO_PRIVATE_ENDPOINT: str = os.getenv("MINIO_PRIVATE_ENDPOINT", "minio:9000")
    MINIO_ROOT_USER: str = os.getenv("MINIO_ROOT_USER", "minioadmin")
    MINIO_ROOT_PASSWORD: str = os.getenv("MINIO_ROOT_PASSWORD", "minioadmin")
    MINIO_BUCKET_NAME: str = "readmeai"
    MINIO_SECURE: bool = False

    # Logging Settings
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

    # Security Settings
    SECRET_KEY: str = "your-secret-key"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    ALGORITHM: str = "HS256"

    class Config:
        env_file = ".env"
        case_sensitive = True


@lru_cache
def get_settings() -> Settings:
    return Settings()
