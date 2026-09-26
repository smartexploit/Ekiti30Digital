from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from pydantic import BaseModel, Field
from datetime import datetime

from app.api.dependencies import get_db
from app.core.auth import require_admin
from app.models.asset import Asset
from app.models.story import Story
from app.schemas.story import StoryRead, StoryStatusUpdate

router = APIRouter(prefix="/api/admin", tags=["admin"])

class RejectionPayload(BaseModel):
    rejection_reason: str = Field(..., min_length=1)

# --- Asset Moderation Endpoints ---

@router.get("/assets/pending", response_model=List[dict])
def list_pending_assets(db: Session = Depends(get_db), admin: dict = Depends(require_admin)):
    assets = db.query(Asset).filter(Asset.status == "pending").all()
    return [
        {
            "id": a.id,
            "folder": a.folder,
            "contributor": a.contributor,
            "rights_status": a.rights_status,
            "status": a.status,
            "rejection_reason": a.rejection_reason,
            "reviewed_by": a.reviewed_by,
            "reviewed_at": a.reviewed_at,
        }
        for a in assets
    ]

@router.post("/assets/{asset_id}/approve")
def approve_asset(asset_id: int, db: Session = Depends(get_db), admin: dict = Depends(require_admin)):
    asset = db.query(Asset).filter(Asset.id == asset_id).first()
    if not asset:
        raise HTTPException(status_code=404, detail="Asset not found")
    if asset.status != "pending":
        raise HTTPException(status_code=409, detail="Asset already reviewed")

    asset.status = "approved"
    asset.reviewed_by = getattr(admin, "email", "admin@example.com")
    asset.reviewed_at = datetime.utcnow()
    asset.rejection_reason = None
    db.commit()
    return {"status": "approved"}

@router.post("/assets/{asset_id}/reject")
def reject_asset(asset_id: int, payload: RejectionPayload, db: Session = Depends(get_db), admin: dict = Depends(require_admin)):
    if not payload.rejection_reason or not payload.rejection_reason.strip():
        raise HTTPException(status_code=422, detail="Rejection reason required")

    asset = db.query(Asset).filter(Asset.id == asset_id).first()
    if not asset:
        raise HTTPException(status_code=404, detail="Asset not found")
    if asset.status != "pending":
        raise HTTPException(status_code=409, detail="Asset already reviewed")

    asset.status = "rejected"
    asset.rejection_reason = payload.rejection_reason
    asset.reviewed_by = getattr(admin, "email", "admin@example.com")
    asset.reviewed_at = datetime.utcnow()
    db.commit()
    return {"status": "rejected"}

# --- Story Moderation Endpoints ---

@router.get("/stories/pending", response_model=List[StoryRead])
def list_pending_stories(db: Session = Depends(get_db), admin: dict = Depends(require_admin)):
    return db.query(Story).filter(Story.status == "pending").all()

@router.patch("/stories/{story_id}/status", response_model=StoryRead)
def update_story_status(story_id: int, payload: StoryStatusUpdate, db: Session = Depends(get_db), admin: dict = Depends(require_admin)):
    story = db.query(Story).filter(Story.id == story_id).first()
    if not story:
        raise HTTPException(status_code=404, detail="Story not found")

    story.status = payload.status
    db.commit()
    db.refresh(story)
    return story
