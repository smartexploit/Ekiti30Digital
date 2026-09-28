from typing import Optional
from pydantic import BaseModel

class StoryBase(BaseModel):
    title: str
    content: str
    author: Optional[str] = None
    email: Optional[str] = None

class StoryCreate(StoryBase):
    pass

class StoryResponse(StoryBase):
    id: str
    status: str
    owner_id: Optional[str] = None

    class Config:
        orm_mode = True
