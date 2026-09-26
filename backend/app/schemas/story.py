from pydantic import BaseModel, ConfigDict, Field
from typing import Optional
from datetime import datetime

class StoryCreate(BaseModel):
    title: str = Field(..., min_length=1)
    content: str = Field(..., min_length=1)
    author: Optional[str] = None
    fullName: Optional[str] = None
    email: Optional[str] = None
    category: Optional[str] = None

class StoryRead(BaseModel):
    id: int
    title: str
    content: str
    author: Optional[str] = None
    email: Optional[str] = None
    category: Optional[str] = None
    status: str
    created_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)

class StoryStatusUpdate(BaseModel):
    status: str  # approved, rejected
