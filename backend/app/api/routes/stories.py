from typing import Any, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.api import deps
from app.db.session import get_db
from app.models.story import Story

router = APIRouter()

@router.get("", status_code=status.HTTP_200_OK)
@router.get("/", status_code=status.HTTP_200_OK)
def list_public_stories(
    status_filter: Optional[str] = Query("approved", alias="status"),
    db: Session = Depends(get_db)
) -> Any:
    query = db.query(Story)
    if status_filter:
        query = query.filter(Story.status == status_filter)
    stories = query.all()
    return [{"id": str(s.id), "title": s.title, "status": s.status} for s in stories]

@router.post("", status_code=status.HTTP_201_CREATED)
@router.post("/", status_code=status.HTTP_201_CREATED)
def create_story(
    story_in: dict,
    db: Session = Depends(get_db),
    current_user: dict = Depends(deps.get_current_user_payload)
) -> Any:
    title = story_in.get("title", "").strip() if isinstance(story_in.get("title"), str) else ""
    content = story_in.get("content", "").strip() if isinstance(story_in.get("content"), str) else ""
    
    if not title or not content:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Title and content are required and cannot be empty"
        )
    
    story_kwargs = {"title": title, "content": content, "status": "pending"}
    if hasattr(Story, "author_id"):
        story_kwargs["author_id"] = current_user.get("sub")
    elif hasattr(Story, "user_id"):
        story_kwargs["user_id"] = current_user.get("sub")
        
    story = Story(**story_kwargs)
    db.add(story)
    db.commit()
    db.refresh(story)
    return {"id": str(story.id), "title": story.title, "status": story.status}
