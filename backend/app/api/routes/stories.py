from typing import Any, List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from app.api import deps

router = APIRouter()

# In-memory store or db mock for stories
_STORIES_STORE = [
    {
        "id": "story_default_1",
        "title": "Historical Roots of Ekiti",
        "content": "Ekiti is known as the fountain of knowledge with a rich heritage.",
        "category": "culture",
        "status": "approved",
        "user_id": "system"
    }
]

class StoryCreate(BaseModel):
    title: str = Field(..., min_length=3)
    content: str = Field(..., min_length=10)
    category: Optional[str] = "general"

class StoryResponse(BaseModel):
    id: str
    title: str
    content: str
    category: str
    status: str
    user_id: str

@router.get("", response_model=List[StoryResponse], status_code=status.HTTP_200_OK)
def list_stories(
    status_filter: Optional[str] = "approved",
) -> Any:
    """Return stories filtered by status (default approved for public)."""
    if status_filter:
        return [s for s in _STORIES_STORE if s.get("status") == status_filter]
    return _STORIES_STORE

@router.post("", response_model=StoryResponse, status_code=status.HTTP_201_CREATED)
def create_story(
    *,
    data: StoryCreate,
    current_user: dict = Depends(deps.get_current_active_contributor),
) -> Any:
    """Create a new story submission (default status: pending)."""
    user_id = current_user.get("sub") or current_user.get("user_id") or "contributor_1"
    if isinstance(user_id, dict):
        user_id = user_id.get("id", "contributor_1")
        
    story_id = f"story_{abs(hash(data.title + str(user_id))) % 100000}"
    
    new_story = {
        "id": story_id,
        "title": data.title,
        "content": data.content,
        "category": data.category or "general",
        "status": "pending",
        "user_id": str(user_id),
    }
    _STORIES_STORE.append(new_story)
    return new_story
