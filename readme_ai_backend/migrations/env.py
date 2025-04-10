# ruff: noqa: F401
from logging.config import fileConfig
from sqlalchemy import engine_from_config
from sqlalchemy import pool
from alembic import context

from readme_ai.models.base import Base
from readme_ai.models.readme import Readme, ReadmeVersion, ChatMessage
from readme_ai.models.template import Template
from readme_ai.models.users import User
from readme_ai.models.repository import Repository, FileContent
from readme_ai.settings import get_settings

config = context.config
settings = get_settings()
db_url = settings.DATABASE_URL

# Need to use synchronous url for migrations
config.set_main_option(
    "sqlalchemy.url", str(db_url).replace("postgresql+asyncpg", "postgresql")
)

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Set the metadata object for our models
target_metadata = Base.metadata


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
