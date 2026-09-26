from pydantic import BaseModel, ConfigDict
from typing import Optional

class StoryBase(BaseModel):
    title: str
    content: str
    author: Optional[str] = None

class StoryCreate(StoryBase):
    pass

class StoryRead(StoryBase):
    id: int

    model_config = ConfigDict(from_attributes=True)
