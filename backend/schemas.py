from pydantic import BaseModel, EmailStr, ConfigDict
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

    model_config = ConfigDict(from_attributes=True)

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: str | None = None

class SidequestPreferences(BaseModel):
    categories: list[str] = ["fun"]
    estimated_cost: str = "minimal"
    goal: str = "fun"

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

    model_config = ConfigDict(from_attributes=True)

class SidequestGenerateResponse(BaseModel):
    title: str
    description: str
    reward_xp: int
    tags: list[str] = []

class GeneratorConfig(BaseModel):
    generator_type: str
    openai_model: str | None = None
