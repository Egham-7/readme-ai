#!/bin/bash
set -e

echo "Running database migrations..."
alembic upgrade head

echo "Starting application server..."
exec hypercorn readme_ai.main:app --bind "[::]:$PORT"
