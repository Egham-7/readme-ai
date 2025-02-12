# Use Python 3.13-slim as base image
FROM python:3.13-slim AS python-base

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
  PYTHONDONTWRITEBYTECODE=1 \
  PIP_NO_CACHE_DIR=off \
  PIP_DISABLE_PIP_VERSION_CHECK=on \
  PIP_DEFAULT_TIMEOUT=100 \
  POETRY_VERSION=2.0.1 \
  POETRY_HOME="/opt/poetry" \
  POETRY_VIRTUALENVS_IN_PROJECT=true \
  POETRY_NO_INTERACTION=1 \
  PYSETUP_PATH="/opt/pysetup" \
  VENV_PATH="/opt/pysetup/.venv"

# Add Poetry to PATH
ENV PATH="$POETRY_HOME/bin:$VENV_PATH/bin:$PATH"

# Build dependencies stage
FROM python-base AS builder-base

# Install system dependencies required for psycopg2
RUN apt-get update && apt-get install --no-install-recommends -y \
  curl \
  build-essential \
  libpq-dev \
  python3-dev \
  gcc

# Install Poetry
RUN curl -sSL https://install.python-poetry.org | python3 -

# Copy project dependency files
WORKDIR $PYSETUP_PATH
COPY poetry.lock pyproject.toml README.md ./
RUN poetry lock

# Install runtime dependencies
RUN poetry install --only main --no-root

# Runtime stage
FROM python-base AS production

# Copy virtual environment from builder
COPY --from=builder-base $PYSETUP_PATH $PYSETUP_PATH

# Create and switch to non-root user
RUN useradd --create-home appuser
USER appuser

# Set working directory
WORKDIR /app

COPY --chown=appuser:appuser ./readme_ai ./readme_ai
COPY --chown=appuser:appuser entrypoint.sh /entrypoint.sh
COPY --chown=appuser:appuser alembic.ini /alembic.ini

# Make entrypoint script executable
RUN chmod +x /entrypoint.sh

# Expose port
EXPOSE 8000

# Run migrations and start the application
ENTRYPOINT ["/entrypoint.sh"]

