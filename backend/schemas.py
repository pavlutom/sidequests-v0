from pydantic import BaseModel, EmailStr
import uuid
from datetime import datetime

class UserBase(BaseModel):
    email: EmailStr

class UserCreate(UserBase):
    password: str

class UserResponse(UserBase):
    id: uuid.UUID
    total_xp: int
    created_at: datetime

    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: str | None = None

# Sidequest Schemas
class SidequestBase(BaseModel):
    title: str
    description: str | None = None
    reward_xp: int

class SidequestCreate(SidequestBase):
    pass

class SidequestResponse(SidequestBase):
    id: uuid.UUID
    user_id: uuid.UUID
    created_at: datetime
    completed_at: datetime | None = None

    class Config:
        from_attributes = True

class SidequestGenerateResponse(BaseModel):
    title: str
    description: str
    reward_xp: int
