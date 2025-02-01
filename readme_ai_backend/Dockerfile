# Use Python 3.13-slim as base image
FROM python:3.13-slim as python-base

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
  PYTHONDONTWRITEBYTECODE=1 \
  PIP_NO_CACHE_DIR=off \
  PIP_DISABLE_PIP_VERSION_CHECK=on \
  PIP_DEFAULT_TIMEOUT=100 \
  POETRY_VERSION=1.7.1 \
  POETRY_HOME="/opt/poetry" \
  POETRY_VIRTUALENVS_IN_PROJECT=true \
  POETRY_NO_INTERACTION=1 \
  PYSETUP_PATH="/opt/pysetup" \
  VENV_PATH="/opt/pysetup/.venv"

# Add Poetry to PATH
ENV PATH="$POETRY_HOME/bin:$VENV_PATH/bin:$PATH"

# Build dependencies stage
FROM python-base as builder-base
RUN apt-get update && apt-get install --no-install-recommends -y \
  curl \
  build-essential

# Install Poetry
RUN curl -sSL https://install.python-poetry.org | python3 -

# Copy project dependency files
WORKDIR $PYSETUP_PATH
COPY poetry.lock pyproject.toml ./

# Install runtime dependencies
RUN poetry install --only main --no-interaction --no-root



# Runtime stage
FROM python-base as production

# Copy virtual environment from builder
COPY --from=builder-base $PYSETUP_PATH $PYSETUP_PATH

# Create and switch to non-root user
RUN useradd --create-home appuser
USER appuser

# Set working directory
WORKDIR /readme_ai

# Copy project files
COPY --chown=appuser:appuser ./readme_ai ./readme_ai

# Expose port
EXPOSE 8000

# Start the FastAPI application with Hypercorn
CMD ["hypercorn", "readme_ai.main:app", "--bind", "0.0.0.0:${PORT:-8000}"]

