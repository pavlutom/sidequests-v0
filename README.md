# Sidequests

A minimal full-stack scaffold for the Sidequests app.

## Stack
- Backend: FastAPI, SQLAlchemy 2.0, Alembic, PostgreSQL
- Frontend: React, Vite, TypeScript
- Infra: Docker Compose

## How to run

1. Copy the example environment variables:
   ```bash
   cp .env.example .env
   ```

2. Build and run with Docker Compose:
   ```bash
   docker compose up --build
   ```

3. Open the frontend:
   Navigate to [http://localhost:5173](http://localhost:5173) to see the React app render "Backend: ok".

4. Verify backend:
   The API is available at [http://localhost:8000/docs](http://localhost:8000/docs).
   A simple health check at `curl http://localhost:8000/api/health` will return status ok.
