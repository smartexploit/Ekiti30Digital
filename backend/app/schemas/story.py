from pydantic import BaseModel, ConfigDict, Field
from typing import Optional
from datetime import datetime

class StoryBase(BaseModel):
    title: str = Field(..., min_length=1)
    content: str = Field(..., min_length=1)
    author: Optional[str] = None

class StoryCreate(StoryBase):
    pass

class StoryRead(StoryBase):
    id: int
    status: str
    created_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)

class StoryStatusUpdate(BaseModel):
    status: str  # approved, rejected
