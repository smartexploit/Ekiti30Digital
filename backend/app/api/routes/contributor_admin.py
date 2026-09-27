from typing import Any, List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from app.api import deps
from app.api.routes.stories import _STORIES_STORE

router = APIRouter()

class StoryStatusUpdate(BaseModel):
    status: str = Field(...)
    review_notes: Optional[str] = None
    reason: Optional[str] = None

class AssetRejectRequest(BaseModel):
    reason: Optional[str] = None

@router.get("", response_model=dict, status_code=status.HTTP_200_OK)
@router.get("/", response_model=dict, status_code=status.HTTP_200_OK)
def admin_root(
    current_user: dict = Depends(deps.get_current_active_admin),
) -> Any:
    return {"status": "ok", "message": "Admin router active"}

@router.get("/pending", response_model=List[dict], status_code=status.HTTP_200_OK)
@router.get("/stories/pending", response_model=List[dict], status_code=status.HTTP_200_OK)
def list_pending_stories(
    current_user: dict = Depends(deps.get_current_active_admin),
) -> Any:
    return [s for s in _STORIES_STORE if s.get("status") == "pending"]

@router.get("/assets/pending", response_model=List[dict], status_code=status.HTTP_200_OK)
def list_pending_assets(
    current_user: dict = Depends(deps.get_current_active_admin),
) -> Any:
    return []

@router.post("/assets/{asset_id}/reject", status_code=status.HTTP_200_OK)
def reject_asset(
    *,
    asset_id: str,
    data: Optional[AssetRejectRequest] = None,
    current_user: dict = Depends(deps.get_current_active_admin),
) -> Any:
    if data and not (data.reason):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Reason required for rejection.",
        )
    return {"status": "rejected", "asset_id": asset_id}

@router.patch("/stories/{story_id}/status", status_code=status.HTTP_200_OK)
@router.post("/stories/{story_id}/status", status_code=status.HTTP_200_OK)
def update_story_status(
    *,
    story_id: str,
    data: StoryStatusUpdate,
    current_user: dict = Depends(deps.get_current_active_admin),
) -> Any:
    if data.status not in ["approved", "rejected", "pending"]:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Invalid status value.",
        )

    if data.status == "rejected" and not (data.review_notes or data.reason):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Reason or review notes required for rejection.",
        )

    target_story = None
    for story in _STORIES_STORE:
        if story.get("id") == story_id:
            target_story = story
            break
            
    if not target_story:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Story not found",
        )
        
    target_story["status"] = data.status
    if data.review_notes:
        target_story["review_notes"] = data.review_notes
    if data.reason:
        target_story["reason"] = data.reason
        
    return target_story
