from pydantic_settings import BaseSettings
from functools import lru_cache
from typing import Optional


class MissingEnvironmentVariable(Exception):
    """Exception raised when a required environment variable is missing"""

    def __init__(self, variable_name: str):
        self.message = f"Critical environment variable {variable_name} is missing"
        super().__init__(self.message)


class Settings(BaseSettings):
    # API Keys
    GROQ_API_KEY: str = ""
    GITHUB_TOKEN: str = ""

    # App Settings
    APP_NAME: str = "README Generator"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False

    # Server Settings
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    WORKERS: int = 4

    # Model Settings
    MODEL_NAME: str = "mixtral-8x7b-32768"
    TEMPERATURE: float = 0.7

    # Cache Settings
    CACHE_TTL: int = 3600  # 1 hour
    MAX_CACHE_SIZE: int = 100

    # Database Settings
    DATABASE_URL: str = "postgresql://postgres:secretpassword@postgres:5432/readmeai"

    # MinIO Settings
    MINIO_PRIVATE_ENDPOINT: str = "minio:9000"
    MINIO_ROOT_USER: str = "minioadmin"
    MINIO_ROOT_PASSWORD: str = "minioadmin"
    MINIO_BUCKET_NAME: str = "readmeai"
    MINIO_SECURE: bool = False

    # Logging Settings
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

    # Authentication Settings
    CLERK_SECRET_KEY: Optional[str] = None
    CLERK_PUBLISHABLE_KEY: Optional[str] = None
    APP_URL: str = "http://localhost:3000"

    class Config:
        env_file = ".env"
        case_sensitive = True

    def validate_critical_variables(self):
        critical_vars = {
            "CLERK_SECRET_KEY": self.CLERK_SECRET_KEY,
            "CLERK_PUBLISHABLE_KEY": self.CLERK_PUBLISHABLE_KEY,
            "DATABASE_URL": self.DATABASE_URL,
            "GITHUB_TOKEN": self.GITHUB_TOKEN,
            "GROQ_API_KEY": self.GROQ_API_KEY,
            "MINIO_PRIVATE_ENDPOINT": self.MINIO_PRIVATE_ENDPOINT,
            "MINIO_ROOT_USER": self.MINIO_ROOT_USER,
            "MINIO_ROOT_PASSWORD": self.MINIO_ROOT_PASSWORD,
            "MINIO_BUCKET_NAME": self.MINIO_BUCKET_NAME,
        }

        for var_name, var_value in critical_vars.items():
            if not var_value or var_value == "test":
                raise MissingEnvironmentVariable(var_name)


@lru_cache
def get_settings() -> Settings:
    settings = Settings()
    settings.validate_critical_variables()
    return settings
