from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select
from typing import List

from app.models.base import get_db
from app.models.story import Story, StoryStatus
from app.schemas.story import StoryCreate, StoryRead

router = APIRouter()

@router.post("/", response_model=StoryRead, status_code=status.HTTP_201_CREATED)
def create_story(story_in: StoryCreate, db: Session = Depends(get_db)):
    """Persist new story submission with default 'pending' status."""
    db_story = Story(**story_in.model_dump())
    db_story.status = StoryStatus.PENDING
    db.add(db_story)
    db.commit()
    db.refresh(db_story)
    return db_story

@router.get("/public", response_model=List[StoryRead])
def get_public_stories(db: Session = Depends(get_db)):
    """Fetch ONLY approved stories for public feed."""
    statement = select(Story).where(Story.status == StoryStatus.APPROVED)
    return db.exec(statement).all()

@router.patch("/{story_id}/status", response_model=StoryRead)
def update_story_status(story_id: int, new_status: StoryStatus, db: Session = Depends(get_db)):
    """Moderation endpoint to update story status."""
    story = db.get(Story, story_id)
    if not story:
        raise HTTPException(status_code=404, detail="Story not found")
    story.status = new_status
    db.add(story)
    db.commit()
    db.refresh(story)
    return story
