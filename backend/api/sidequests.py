from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime
import uuid
import models
import schemas
import auth
import generator
from database import get_db

router = APIRouter(prefix="/sidequests", tags=["sidequests"])

@router.get("", response_model=list[schemas.SidequestResponse])
def get_sidequests(db: Session = Depends(get_db), current_user: models.User = Depends(auth.get_current_user)):
    return db.query(models.Sidequest).filter(models.Sidequest.user_id == current_user.id).order_by(models.Sidequest.created_at.desc()).all()

@router.post("/generate", response_model=schemas.SidequestGenerateResponse)
def generate_sidequest(current_user: models.User = Depends(auth.get_current_user)):
    return generator.generate_sidequest(current_user.id)

@router.post("/accept", response_model=schemas.SidequestResponse)
def accept_sidequest(quest: schemas.SidequestCreate, db: Session = Depends(get_db), current_user: models.User = Depends(auth.get_current_user)):
    new_quest = models.Sidequest(
        title=quest.title,
        description=quest.description,
        reward_xp=quest.reward_xp,
        user_id=current_user.id
    )
    db.add(new_quest)
    db.commit()
    db.refresh(new_quest)
    return new_quest

@router.post("/{quest_id}/complete", response_model=schemas.SidequestResponse)
def complete_sidequest(quest_id: uuid.UUID, db: Session = Depends(get_db), current_user: models.User = Depends(auth.get_current_user)):
    quest = db.query(models.Sidequest).filter(models.Sidequest.id == quest_id, models.Sidequest.user_id == current_user.id).first()
    if not quest:
        raise HTTPException(status_code=404, detail="Sidequest not found")
    
    if not quest.completed_at:
        quest.completed_at = datetime.utcnow()
        db.add(current_user)
        current_user.total_xp += quest.reward_xp
        db.commit()
        db.refresh(quest)
        db.refresh(current_user)
    return quest

@router.delete("/{quest_id}")
def discard_sidequest(quest_id: uuid.UUID, db: Session = Depends(get_db), current_user: models.User = Depends(auth.get_current_user)):
    quest = db.query(models.Sidequest).filter(models.Sidequest.id == quest_id, models.Sidequest.user_id == current_user.id).first()
    if not quest:
        raise HTTPException(status_code=404, detail="Sidequest not found")
    
    db.delete(quest)
    db.commit()
    return {"status": "success"}
