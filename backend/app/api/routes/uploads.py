from typing import Any, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.api import deps
from app.db.session import get_db
from app.models.asset import Asset
from app.core.config import settings

router = APIRouter()

class UploadCompleteRequest(BaseModel):
    url: Optional[str] = None
    secure_url: Optional[str] = None
    filename: Optional[str] = None

    class Config:
        extra = "allow"

@router.post("/init", status_code=status.HTTP_200_OK)
def init_upload(
    payload: dict,
    db: Session = Depends(get_db),
    current_user: dict = Depends(deps.get_current_user_payload)
) -> Any:
    filename = payload.get("filename", "upload.jpg")
    folder = payload.get("folder", "uploads")
    user_id = current_user.get("sub") or current_user.get("id")
    
    asset = Asset(
        filename=filename,
        url="https://res.cloudinary.com/placeholder/image/upload/pending.jpg",
        folder=folder,
        status="pending",
        user_id=user_id,
        contributor=current_user.get("email") or current_user.get("username")
    )
    db.add(asset)
    db.commit()
    db.refresh(asset)
    
    return {
        "asset_id": str(asset.id),
        "id": str(asset.id),
        "storage_key": f"{folder}/{asset.id}/{filename}",
        "upload_url": f"https://api.cloudinary.com/v1_1/{getattr(settings, 'CLOUDINARY_CLOUD_NAME', 'demo')}/upload",
        "status": asset.status
    }

@router.post("/{asset_id}/complete", status_code=status.HTTP_200_OK)
def complete_upload(
    asset_id: str,
    payload: dict,
    db: Session = Depends(get_db),
    current_user: dict = Depends(deps.get_current_user_payload)
) -> Any:
    asset = db.query(Asset).filter(Asset.id == asset_id).first()
    if not asset:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Asset not found")
        
    current_uid = current_user.get("sub") or current_user.get("id")
    if asset.user_id and current_uid and str(asset.user_id) != str(current_uid):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not own this asset"
        )
        
    url = payload.get("url") or payload.get("secure_url") or f"https://res.cloudinary.com/demo/image/upload/{asset.id}.jpg"
        
    asset.url = url
    asset.status = "uploaded"
    db.commit()
    db.refresh(asset)
    
    return {
        "id": str(asset.id),
        "filename": asset.filename,
        "url": asset.url,
        "storage_key": f"{asset.folder}/{asset.id}/{asset.filename}",
        "status": asset.status
    }
