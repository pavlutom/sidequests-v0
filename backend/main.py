from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from config import settings
from api import auth, sidequests, health

app = FastAPI(
    title="Sidequests API",
    docs_url="/api/docs",
    openapi_url="/api/openapi.json"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Root-level /api prefix for all routers to maintain compatibility with existing frontend
app.include_router(auth.router, prefix="/api")
app.include_router(sidequests.router, prefix="/api")
app.include_router(health.router, prefix="/api")

@app.get("/")
def read_root():
    return {"message": "Welcome to Sidequests API"}
