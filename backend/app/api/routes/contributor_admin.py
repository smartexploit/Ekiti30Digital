from typing import Any
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api import deps
from app.db.session import get_db
from app.models.asset import Asset
from app.models.story import Story

router = APIRouter()

@router.get("/assets/pending", status_code=status.HTTP_200_OK)
def list_pending_assets(
    db: Session = Depends(get_db),
    current_user: dict = Depends(deps.get_current_active_admin)
) -> Any:
    assets = db.query(Asset).filter(Asset.status == "pending").all()
    return [{"id": str(a.id), "filename": a.filename, "status": a.status} for a in assets]

@router.post("/assets/{asset_id}/reject", status_code=status.HTTP_200_OK)
def reject_asset(
    asset_id: str,
    payload: dict,
    db: Session = Depends(get_db),
    current_user: dict = Depends(deps.get_current_active_admin)
) -> Any:
    reason = payload.get("reason")
    if not reason:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Reason is required to reject an asset"
        )
    asset = db.query(Asset).filter(Asset.id == asset_id).first()
    if not asset:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Asset not found")
        
    asset.status = "rejected"
    db.commit()
    return {"id": str(asset.id), "status": asset.status, "reason": reason}

@router.patch("/stories/{story_id}/status", status_code=status.HTTP_200_OK)
def moderate_story(
    story_id: str,
    payload: dict,
    db: Session = Depends(get_db),
    current_user: dict = Depends(deps.get_current_active_admin)
) -> Any:
    new_status = payload.get("status")
    if new_status not in ["approved", "rejected"]:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Invalid status. Must be 'approved' or 'rejected'"
        )
    
    story = db.query(Story).filter(Story.id == story_id).first()
    if not story:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Story not found")
        
    story.status = new_status
    db.commit()
    db.refresh(story)
    return {"id": str(story.id), "status": story.status}
