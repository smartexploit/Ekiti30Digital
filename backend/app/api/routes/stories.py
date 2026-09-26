from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from typing import List
from app.api.dependencies import get_db
from app.models.story import Story
from app.schemas.story import StoryCreate, StoryRead

router = APIRouter(prefix="/api/stories", tags=["stories"])

@router.post("", response_model=StoryRead, status_code=status.HTTP_201_CREATED)
def create_story(payload: StoryCreate, db: Session = Depends(get_db)):
    author_name = payload.author or payload.fullName
    db_story = Story(
        title=payload.title,
        content=payload.content,
        author=author_name,
        email=payload.email,
        category=payload.category,
        status="pending"
    )
    db.add(db_story)
    db.commit()
    db.refresh(db_story)
    return db_story

@router.get("", response_model=List[StoryRead])
def list_public_stories(db: Session = Depends(get_db)):
    return db.query(Story).filter(Story.status == "approved").all()
