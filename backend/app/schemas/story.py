from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional

class StoryCreate(BaseModel):
    fullName: str
    email: EmailStr
    title: str
    category: Optional[str] = "Education"
    content: str

class StoryRead(BaseModel):
    id: int
    fullName: str
    title: str
    category: str
    content: str
    status: str
    createdAt: datetime

    class Config:
        from_attributes = True
