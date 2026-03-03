from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text
from database import get_db
from config import settings

router = APIRouter(prefix="/health", tags=["system"])

@router.get("")
def health_check(db: Session = Depends(get_db)):
    health_status = {"status": "ok", "db": "connected"}
    try:
        # Verify db is reachable
        db.execute(text("SELECT 1"))
    except Exception as e:
        health_status = {"status": "error", "detail": str(e), "db": "disconnected"}
    
    return {
        **health_status,
        "generator_config": {
            "generator_type": settings.generator_type,
            "openai_model": settings.openai_model
        }
    }
