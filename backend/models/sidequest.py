from sqlalchemy import Column, String, DateTime, ForeignKey, Integer, CheckConstraint, Uuid
from sqlalchemy.orm import relationship
import uuid
import datetime
from database import Base

class Sidequest(Base):
    __tablename__ = "sidequests"

    id = Column(Uuid, primary_key=True, default=uuid.uuid4)
    title = Column(String, nullable=False)
    description = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)
    reward_xp = Column(Integer, nullable=False)
    
    user_id = Column(Uuid, ForeignKey("users.id"), nullable=False)
    user = relationship("User", back_populates="sidequests")

    __table_args__ = (
        CheckConstraint("reward_xp >= 1", name="check_reward_xp_positive"),
    )
