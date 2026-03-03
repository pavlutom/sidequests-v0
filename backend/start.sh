#!/bin/bash
set -e

# Run database migrations
echo "Running alembic migrations..."
alembic upgrade head

# Start server
echo "Starting FastAPI server..."
if [ "$DEBUG" = "true" ]; then
    echo "Running in DEBUG mode with debugpy"
    exec python -Xfrozen_modules=off -m debugpy --listen 0.0.0.0:5678 -m uvicorn main:app --host 0.0.0.0 --port 8000
else
    exec uvicorn main:app --host 0.0.0.0 --port 8000
fi
