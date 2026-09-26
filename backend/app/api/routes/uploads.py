import os
import hashlib
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional

from app.api.dependencies import get_db
from app.models.asset import Asset
from app.core.config import settings

router = APIRouter(prefix="/api/uploads", tags=["uploads"])

VALID_FOLDERS = {
    "EKITI30/Historical",
    "EKITI30/LGAs",
    "EKITI30/Culture_Tourism",
    "EKITI30/Community_Stories",
    "EKITI30/Ekiti_2056"
}

class InitUploadRequest(BaseModel):
    folder: str
    filename: Optional[str] = None
    contributor: Optional[str] = None
    rights_status: Optional[str] = None
    related_content_id: Optional[str] = None

class CompleteUploadRequest(BaseModel):
    asset_id: Optional[int] = None
    public_id: str
    secure_url: str

@router.post("/init", status_code=status.HTTP_201_CREATED)
def init_upload(payload: InitUploadRequest, db: Session = Depends(get_db)):
    if payload.folder not in VALID_FOLDERS:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Invalid folder. Must be one of {list(VALID_FOLDERS)}"
        )
    if not payload.contributor or not payload.rights_status:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Contributor and rights status are required."
        )

    cloud_name = getattr(settings, "CLOUDINARY_CLOUD_NAME", None)
    api_key = getattr(settings, "CLOUDINARY_API_KEY", None)
    api_secret = getattr(settings, "CLOUDINARY_API_SECRET", None)
    upload_preset = getattr(settings, "CLOUDINARY_UPLOAD_PRESET", None)

    if not cloud_name or not api_key or not api_secret or not upload_preset:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Cloudinary credentials not configured."
        )

    asset = Asset(
        folder=payload.folder,
        contributor=payload.contributor,
        rights_status=payload.rights_status,
        related_content_id=payload.related_content_id,
        status="pending"
    )
    db.add(asset)
    db.commit()
    db.refresh(asset)

    timestamp = 1234567890
    params_to_sign = f"folder={payload.folder}&timestamp={timestamp}{api_secret}"
    signature = hashlib.sha1(params_to_sign.encode('utf-8')).hexdigest()

    return {
        "asset_id": asset.id,
        "cloud_name": cloud_name,
        "api_key": api_key,
        "timestamp": timestamp,
        "folder": payload.folder,
        "signature": signature,
        "upload_preset": upload_preset,
        "max_file_bytes": 10 * 1024 * 1024,
        "allowed_formats": ["jpg", "png", "webp", "mp4"],
        "tags": ["timeline-1996"],
        "tag": "timeline-1996"
    }

@router.post("/complete")
@router.post("/complete/{asset_id}")
@router.post("/{asset_id}/complete")
def complete_upload(payload: CompleteUploadRequest, asset_id: Optional[int] = None, db: Session = Depends(get_db)):
    target_id = asset_id or payload.asset_id
    if not target_id:
        raise HTTPException(status_code=400, detail="Asset ID required")

    asset = db.query(Asset).filter(Asset.id == target_id).first()
    if not asset:
        raise HTTPException(status_code=404, detail="Asset not found")
    
    if asset.public_id is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Asset already completed"
        )

    cloud_name = getattr(settings, "CLOUDINARY_CLOUD_NAME", "ekiti-test")
    expected_prefix = f"https://res.cloudinary.com/{cloud_name}/image/upload/"
    
    if not payload.secure_url.startswith(expected_prefix):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Secure URL does not match our Cloudinary account."
        )

    if payload.public_id not in payload.secure_url:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Public ID mismatch in URL."
        )

    asset.public_id = payload.public_id
    asset.secure_url = payload.secure_url
    if hasattr(asset, "cloudinary_url"):
        asset.cloudinary_url = payload.secure_url
    asset.status = "pending"  # Keep status pending for admin review
    db.commit()
    db.refresh(asset)

    return {
        "asset_id": asset.id,
        "id": asset.id,
        "secure_url": asset.secure_url,
        "status": asset.status
    }
