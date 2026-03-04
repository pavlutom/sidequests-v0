from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime
import uuid
import models
import schemas
import auth
import generators
from database import get_db

router = APIRouter(prefix="/sidequests", tags=["sidequests"])

@router.get("", response_model=list[schemas.SidequestResponse])
def get_sidequests(db: Session = Depends(get_db), current_user: models.User = Depends(auth.get_current_user)):
    return db.query(models.Sidequest).filter(
        models.Sidequest.user_id == current_user.id,
        models.Sidequest.accepted_at != None
    ).order_by(models.Sidequest.created_at.desc()).all()

@router.post("/generate", response_model=schemas.SidequestGenerateResponse)
def generate_sidequest(preferences: schemas.SidequestPreferences, db: Session = Depends(get_db), current_user: models.User = Depends(auth.get_current_user)):
    print("najeb si ty kokot drbnuty")
    
    # Cleanup: remove previous proposed quests for this user
    db.query(models.Sidequest).filter(
        models.Sidequest.user_id == current_user.id,
        models.Sidequest.accepted_at == None
    ).delete()
    
    # Generate new quest data
    quest_data = generators.generate_sidequest(current_user.id, preferences.model_dump())
    
    # Save as proposed quest
    new_quest = models.Sidequest(
        title=quest_data["title"],
        description=quest_data["description"],
        reward_xp=quest_data["reward_xp"],
        user_id=current_user.id,
        accepted_at=None
    )
    db.add(new_quest)
    db.commit()
    db.refresh(new_quest)
    
    return {
        "id": new_quest.id,
        "title": new_quest.title,
        "description": new_quest.description,
        "reward_xp": new_quest.reward_xp,
        "tags": quest_data.get("tags", [])
    }

@router.post("/accept", response_model=schemas.SidequestResponse)
def accept_sidequest(accept: schemas.SidequestAccept, db: Session = Depends(get_db), current_user: models.User = Depends(auth.get_current_user)):
    quest = db.query(models.Sidequest).filter(
        models.Sidequest.id == accept.quest_id,
        models.Sidequest.user_id == current_user.id
    ).first()
    
    if not quest:
        raise HTTPException(status_code=404, detail="Sidequest not found")
    
    if quest.accepted_at:
        raise HTTPException(status_code=400, detail="Sidequest already accepted")
        
    quest.accepted_at = datetime.utcnow()
    db.commit()
    db.refresh(quest)
    return quest

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
