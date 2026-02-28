#!/bin/bash
set -e

# Run database migrations
echo "Running alembic migrations..."
alembic upgrade head

# Start server
echo "Starting FastAPI server..."
exec uvicorn main:app --host 0.0.0.0 --port 8000
