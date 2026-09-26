from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.models.story import Story
from app.schemas.story import StoryCreate, StoryRead

router = APIRouter(prefix="/api/stories", tags=["stories"])

@router.post("", response_model=StoryRead, status_code=status.HTTP_201_CREATED)
def create_story(payload: StoryCreate, db: Session = Depends(get_db)):
    db_story = Story(
        title=payload.title,
        content=payload.content,
        author=payload.author,
        status="pending"  # Enforce default pending moderation state
    )
    db.add(db_story)
    db.commit()
    db.refresh(db_story)
    return db_story

@router.get("", response_model=List[StoryRead])
def list_public_stories(db: Session = Depends(get_db)):
    # Strict public filtering: only return approved stories
    stories = db.query(Story).filter(Story.status == "approved").all()
    return stories
