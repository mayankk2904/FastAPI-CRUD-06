from pydantic import BaseModel, Field
from typing import Optional, List

class UserBase(BaseModel):
    name : str
    email : str
    age: int = Field(..., ge=0, le=120)
    marks: Optional[float] = Field(..., ge=0, le=100)

class UserCreate(UserBase):
    pass

class UserResponse(UserBase):
    id: str

class UserBulkCreate(BaseModel):
    users: List[UserCreate]