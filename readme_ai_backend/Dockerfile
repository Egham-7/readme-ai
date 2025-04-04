# Use Python 3.13-alpine as base image
FROM python:3.13-alpine AS python-base

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
  PYTHONDONTWRITEBYTECODE=1 \
  PIP_NO_CACHE_DIR=off \
  PIP_DISABLE_PIP_VERSION_CHECK=on \
  PIP_DEFAULT_TIMEOUT=100 \
  POETRY_VERSION=2.1.2 \
  POETRY_HOME="/opt/poetry" \
  POETRY_VIRTUALENVS_IN_PROJECT=true \
  POETRY_NO_INTERACTION=1 \
  PYSETUP_PATH="/opt/pysetup" \
  VENV_PATH="/opt/pysetup/.venv"

# Add Poetry to PATH
ENV PATH="$POETRY_HOME/bin:$VENV_PATH/bin:$PATH"

# Build dependencies stage
FROM python-base AS builder-base

# Install system dependencies required for building packages
RUN apk add --no-cache \
  curl \
  build-base \
  postgresql-dev \
  python3-dev \
  gcc \
  musl-dev \
  openssl-dev \
  cargo \
  rust \ 
  libgcc

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

# Install runtime dependencies (libpq for PostgreSQL and bash for shell script)
RUN apk add --no-cache libpq bash libgcc

# Copy virtual environment from builder
COPY --from=builder-base $PYSETUP_PATH $PYSETUP_PATH

# Create and switch to non-root user
RUN adduser -D appuser
USER appuser

# Set working directory
WORKDIR /app
COPY --chown=appuser:appuser ./readme_ai ./readme_ai
COPY --chown=appuser:appuser entrypoint.sh /entrypoint.sh
COPY --chown=appuser:appuser alembic.ini /app/alembic.ini
COPY --chown=appuser:appuser migrations /app/migrations

# Make entrypoint script executable and ensure proper line endings
USER root
RUN sed -i 's/\r$//' /entrypoint.sh && \
  chmod +x /entrypoint.sh
USER appuser

# Expose port
EXPOSE 8000

# Run migrations and start the application
ENTRYPOINT ["/bin/bash", "/entrypoint.sh"]

