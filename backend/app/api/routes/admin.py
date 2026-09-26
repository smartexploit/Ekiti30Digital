from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.models.base import get_db
from app.models.asset import Asset
from app.schemas.asset import AssetResponse, AssetRejectPayload
from app.api.dependencies import get_current_admin_user

router = APIRouter(prefix="/api/admin", tags=["admin"])


@router.get("/assets/pending", response_model=list[AssetResponse])
def list_pending_assets(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_admin_user)
):
    return db.query(Asset).filter(Asset.status == "pending").all()


@router.post("/assets/{asset_id}/approve", response_model=AssetResponse)
def approve_asset(
    asset_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_admin_user)
):
    asset = db.query(Asset).filter(Asset.id == asset_id).first()
    if not asset:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Asset not found")
    
    if asset.status != "pending":
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Asset already reviewed")

    asset.status = "approved"
    asset.reviewed_by = getattr(current_user, "email", "admin")
    asset.reviewed_at = datetime.now(timezone.utc)
    
    db.commit()
    db.refresh(asset)
    return asset


@router.post("/assets/{asset_id}/reject", response_model=AssetResponse)
def reject_asset(
    asset_id: int,
    payload: AssetRejectPayload,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_admin_user)
):
    asset = db.query(Asset).filter(Asset.id == asset_id).first()
    if not asset:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Asset not found")

    if asset.status != "pending":
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Asset already reviewed")

    if not payload.rejection_reason:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Rejection reason required")

    asset.status = "rejected"
    asset.rejection_reason = payload.rejection_reason
    asset.reviewed_by = getattr(current_user, "email", "admin")
    asset.reviewed_at = datetime.now(timezone.utc)

    db.commit()
    db.refresh(asset)
    return asset
