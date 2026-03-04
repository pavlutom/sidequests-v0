from sqlalchemy.orm import Session
from datetime import datetime
from config import settings
import uuid
from typing import Any
import models
import schemas
import generators

def get_active_sidequests(db: Session, user_id: uuid.UUID) -> list[models.Sidequest]:
    """Retrieve all accepted but not completed sidequests for a user."""
    return db.query(models.Sidequest).filter(
        models.Sidequest.user_id == user_id,
        models.Sidequest.accepted_at != None
    ).order_by(models.Sidequest.created_at.desc()).all()

def generate_and_propose_sidequest(db: Session, user_id: uuid.UUID, preferences: dict[str, Any]) -> models.Sidequest:
    """Clean up old proposed quests and generate a new one, saving it as proposed."""
    # Cleanup: remove previous proposed quests for this user
    db.query(models.Sidequest).filter(
        models.Sidequest.user_id == user_id,
        models.Sidequest.accepted_at == None
    ).delete()
    
    # Generate new quest data
    quest_data = generators.generate_sidequest(user_id, preferences)
    
    # Save as proposed quest
    new_quest = models.Sidequest(
        title=quest_data["title"],
        description=quest_data["description"],
        reward_xp=quest_data["reward_xp"],
        user_id=user_id,
        accepted_at=None
    )
    db.add(new_quest)
    db.commit()
    db.refresh(new_quest)
    
    # Return both the model and any extra metadata if needed (like tags)
    # For now, we return the model. The caller can wrap it in a response schema.
    return new_quest

def accept_sidequest(db: Session, user_id: uuid.UUID, quest_id: uuid.UUID) -> models.Sidequest:
    """Accept a proposed sidequest."""
    quest = db.query(models.Sidequest).filter(
        models.Sidequest.id == quest_id,
        models.Sidequest.user_id == user_id
    ).first()
    
    if not quest:
        return None
    
    if quest.accepted_at:
        raise ValueError("Sidequest already accepted")
        
    quest.accepted_at = datetime.now(settings.tz)
    db.commit()
    db.refresh(quest)
    return quest

def complete_sidequest(db: Session, user: models.User, quest_id: uuid.UUID) -> models.Sidequest | None:
    """Mark a sidequest as completed and reward XP."""
    quest = db.query(models.Sidequest).filter(
        models.Sidequest.id == quest_id, 
        models.Sidequest.user_id == user.id
    ).first()
    
    if not quest:
        return None
    
    if not quest.completed_at:
        quest.completed_at = datetime.now(settings.tz)
        user.total_xp += quest.reward_xp
        db.add(user)
        db.commit()
        db.refresh(quest)
        db.refresh(user)
    return quest

def discard_sidequest(db: Session, user_id: uuid.UUID, quest_id: uuid.UUID) -> bool:
    """Delete a sidequest."""
    quest = db.query(models.Sidequest).filter(
        models.Sidequest.id == quest_id, 
        models.Sidequest.user_id == user_id
    ).first()
    
    if not quest:
        return False
    
    db.delete(quest)
    db.commit()
    return True
