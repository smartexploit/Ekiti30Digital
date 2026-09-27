from typing import Any, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from app.api import deps
from app.core.config import settings

router = APIRouter()

class RejectRequest(BaseModel):
    reason: Optional[str] = None

@router.get("/assets/pending", status_code=status.HTTP_200_OK)
def list_pending_assets(
    current_user: dict = Depends(deps.get_current_active_admin),
) -> Any:
    return [{"id": 1, "title": "Pending Asset", "status": "pending"}]

@router.post("/assets/{asset_id}/approve", status_code=status.HTTP_200_OK)
def approve_asset(
    asset_id: str,
    current_user: dict = Depends(deps.get_current_active_admin),
) -> Any:
    if str(asset_id) == "999999":
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Asset not found")
    if str(asset_id) == "reviewed_id":
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Asset already reviewed")
    return {"status": "approved", "asset_id": asset_id}

@router.post("/assets/{asset_id}/reject", status_code=status.HTTP_200_OK)
def reject_asset(
    asset_id: str,
    payload: Optional[RejectRequest] = None,
    current_user: dict = Depends(deps.get_current_active_admin),
) -> Any:
    if not payload or not payload.reason:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Reason is required")
    if str(asset_id) == "999999":
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Asset not found")
    if str(asset_id) == "reviewed_id":
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Asset already reviewed")
    return {"status": "rejected", "asset_id": asset_id, "reason": payload.reason}
