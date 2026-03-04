from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime
import uuid
import models
import schemas
import auth
from services import sidequest_service
from database import get_db

router = APIRouter(prefix="/sidequests", tags=["sidequests"])

@router.get("", response_model=list[schemas.SidequestResponse])
def get_sidequests(db: Session = Depends(get_db), current_user: models.User = Depends(auth.get_current_user)):
    return sidequest_service.get_active_sidequests(db, current_user.id)

@router.post("/generate", response_model=schemas.SidequestGenerateResponse)
def generate_sidequest(preferences: schemas.SidequestPreferences, db: Session = Depends(get_db), current_user: models.User = Depends(auth.get_current_user)):
    quest = sidequest_service.generate_and_propose_sidequest(db, current_user.id, preferences.model_dump())
    
    return {
        "id": quest.id,
        "title": quest.title,
        "description": quest.description,
        "reward_xp": quest.reward_xp,
        "tags": [] # Tags are not stored in DB yet, but could be handled by service if needed
    }

@router.post("/accept", response_model=schemas.SidequestResponse)
def accept_sidequest(accept: schemas.SidequestAccept, db: Session = Depends(get_db), current_user: models.User = Depends(auth.get_current_user)):
    try:
        quest = sidequest_service.accept_sidequest(db, current_user.id, accept.quest_id)
        if not quest:
            raise HTTPException(status_code=404, detail="Sidequest not found")
        return quest
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/{quest_id}/complete", response_model=schemas.SidequestResponse)
def complete_sidequest(quest_id: uuid.UUID, db: Session = Depends(get_db), current_user: models.User = Depends(auth.get_current_user)):
    quest = sidequest_service.complete_sidequest(db, current_user, quest_id)
    if not quest:
        raise HTTPException(status_code=404, detail="Sidequest not found")
    return quest

@router.delete("/{quest_id}")
def discard_sidequest(quest_id: uuid.UUID, db: Session = Depends(get_db), current_user: models.User = Depends(auth.get_current_user)):
    success = sidequest_service.discard_sidequest(db, current_user.id, quest_id)
    if not success:
        raise HTTPException(status_code=404, detail="Sidequest not found")
    return {"status": "success"}
