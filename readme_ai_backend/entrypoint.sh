#!/bin/bash
set -e

echo "Starting application server..."
exec hypercorn readme_ai.main:app --bind "[::]:$PORT"
