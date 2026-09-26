from datetime import datetime, timezone
from enum import Enum
from typing import Optional
from sqlmodel import Field, SQLModel

class StoryStatus(str, Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"

class Story(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    fullName: str
    email: str
    title: str
    category: str
    content: str
    status: StoryStatus = Field(default=StoryStatus.PENDING)
    createdAt: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
