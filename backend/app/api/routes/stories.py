from fastapi import APIRouter, Depends, HTTPException, status, Body
from sqlalchemy.orm import Session
from typing import Any, Dict, Optional
from app.db.session import get_db
from app.models.contributor import ContributorAccount
from app.api.deps import get_current_active_contributor

router = APIRouter()

@router.get("/")
def list_stories(
    status: Optional[str] = None,
    db: Session = Depends(get_db)
):
    return []

@router.post("/", status_code=status.HTTP_201_CREATED)
def create_story(
    payload: Optional[Dict[str, Any]] = Body(default=None),
    db: Session = Depends(get_db),
    current_user: ContributorAccount = Depends(get_current_active_contributor)
):
    data = payload or {}
    title = data.get("title")
    content = data.get("content")
    
    if not title or not content:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Title and content are required."
        )
        
    return {
        "id": 1,
        "title": title,
        "content": content,
        "status": "pending",
        "contributor_id": current_user.id
    }
