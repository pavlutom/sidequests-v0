from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import text
from database import SessionLocal, engine
from config import settings
# Import models to ensure they are registered with SQLAlchemy
import models
import schemas
import auth
import generator
from fastapi.security import OAuth2PasswordRequestForm
from datetime import timedelta, datetime
import uuid

app = FastAPI(title="Sidequests API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

from database import SessionLocal, engine, get_db

@app.post("/api/auth/register", response_model=schemas.UserResponse)
def register(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = db.query(models.User).filter(models.User.email == user.email).first()
    if db_user:
        from fastapi import HTTPException
        raise HTTPException(status_code=400, detail="Email already registered")
    
    hashed_password = auth.get_password_hash(user.password)
    new_user = models.User(email=user.email, hashed_password=hashed_password)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

@app.post("/api/auth/login", response_model=schemas.Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    db_user = db.query(models.User).filter(models.User.email == form_data.username).first()
    from fastapi import HTTPException
    if not db_user or not auth.verify_password(form_data.password, db_user.hashed_password):
        raise HTTPException(status_code=400, detail="Incorrect email or password")
    
    access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
    access_token = auth.create_access_token(
        data={"sub": db_user.email}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/api/auth/me", response_model=schemas.UserResponse)
def get_me(current_user: models.User = Depends(auth.get_current_user)):
    return current_user

@app.get("/api/health")
def health_check(db: Session = Depends(get_db)):
    try:
        # Verify db is reachable
        db.execute(text("SELECT 1"))
        return {"status": "ok", "db": "connected"}
    except Exception as e:
        return {"status": "error", "detail": str(e)}

@app.get("/api/sidequests", response_model=list[schemas.SidequestResponse])
def get_sidequests(db: Session = Depends(get_db), current_user: models.User = Depends(auth.get_current_user)):
    return db.query(models.Sidequest).filter(models.Sidequest.user_id == current_user.id).order_by(models.Sidequest.created_at.desc()).all()

@app.post("/api/sidequests/generate", response_model=schemas.SidequestGenerateResponse)
def generate_sidequest(current_user: models.User = Depends(auth.get_current_user)):
    return generator.generate_sidequest(current_user.id)

@app.post("/api/sidequests/accept", response_model=schemas.SidequestResponse)
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

@app.post("/api/sidequests/{quest_id}/complete", response_model=schemas.SidequestResponse)
def complete_sidequest(quest_id: uuid.UUID, db: Session = Depends(get_db), current_user: models.User = Depends(auth.get_current_user)):
    from fastapi import HTTPException
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

@app.delete("/api/sidequests/{quest_id}")
def discard_sidequest(quest_id: uuid.UUID, db: Session = Depends(get_db), current_user: models.User = Depends(auth.get_current_user)):
    from fastapi import HTTPException
    quest = db.query(models.Sidequest).filter(models.Sidequest.id == quest_id, models.Sidequest.user_id == current_user.id).first()
    if not quest:
        raise HTTPException(status_code=404, detail="Sidequest not found")
    
    db.delete(quest)
    db.commit()
    return {"status": "success"}
