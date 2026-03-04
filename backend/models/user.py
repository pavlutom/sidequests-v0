from sqlalchemy import Column, String, DateTime, Integer, Uuid
from sqlalchemy.orm import relationship
import uuid
import datetime
from database import Base
from config import settings

class User(Base):
    __tablename__ = "users"

    id = Column(Uuid, primary_key=True, default=uuid.uuid4)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    total_xp = Column(Integer, default=0, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.datetime.now(settings.tz))
    
    # Needs to be string referencing full package path or lazy loading to prevent circular import
    sidequests = relationship("Sidequest", back_populates="user", cascade="all, delete-orphan")
