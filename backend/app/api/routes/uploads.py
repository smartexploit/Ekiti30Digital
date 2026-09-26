import os
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr
from typing import Optional

from app.models.base import get_db
from app.models.asset import Asset
from app.core.config import settings

router = APIRouter(prefix="/api/uploads", tags=["uploads"])


class UploadInitPayload(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    category: Optional[str] = None
    folder: Optional[str] = None
    media_type: Optional[str] = None
    contributor: Optional[str] = None
    contributor_name: Optional[str] = None
    contributor_email: Optional[EmailStr] = None
    rights_status: Optional[str] = None
    related_content_id: Optional[str] = None


class UploadCompletePayload(BaseModel):
    public_id: str
    secure_url: str
    cloudinary_url: Optional[str] = None


@router.post("/init", status_code=status.HTTP_201_CREATED)
def init_upload(
    payload: UploadInitPayload,
    db: Session = Depends(get_db)
):
    cloud_name = os.getenv("CLOUDINARY_CLOUD_NAME", "ekiti-test")
    upload_preset = getattr(settings, "CLOUDINARY_UPLOAD_PRESET", None) or os.getenv("CLOUDINARY_UPLOAD_PRESET")
    
    if not upload_preset:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Cloudinary not configured"
        )

    if not payload.contributor or not payload.rights_status:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Contributor and rights_status are required"
        )

    folder = payload.folder or "EKITI30/Historical"
    
    # Strict whitelist of allowed folders to reject unauthorized conventions like EKITI30/Other
    valid_folders = [
        "timeline-1996",
        "oral-history",
        "gallery",
        "documents",
        "EKITI30/Historical",
        "EKITI30/Culture",
        "EKITI30/People",
        "EKITI30/Places"
    ]
    if folder not in valid_folders:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Invalid folder convention"
        )

    asset = Asset(
        title=payload.title,
        description=payload.description,
        category=payload.category,
        folder=folder,
        media_type=payload.media_type,
        contributor=payload.contributor,
        contributor_name=payload.contributor_name,
        contributor_email=payload.contributor_email,
        rights_status=payload.rights_status,
        related_content_id=payload.related_content_id,
        status="pending"
    )
    db.add(asset)
    db.commit()
    db.refresh(asset)

    return {
        "asset_id": asset.id,
        "folder": asset.folder,
        "upload_preset": upload_preset,
        "cloud_name": cloud_name,
        "max_file_bytes": 10 * 1024 * 1024,
        "allowed_formats": ["jpg", "png", "webp", "mp4"]
    }


@router.post("/{asset_id}/complete")
def complete_upload(
    asset_id: int,
    payload: UploadCompletePayload,
    db: Session = Depends(get_db)
):
    asset = db.query(Asset).filter(Asset.id == asset_id).first()
    if not asset:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Asset not found")

    if asset.secure_url:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Asset already completed")

    url_to_check = payload.secure_url or payload.cloudinary_url or ""
    
    if "ekiti-test" not in url_to_check or "someone-else" in url_to_check or not url_to_check.startswith("https://res.cloudinary.com/"):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Invalid Cloudinary account or URL"
        )

    if payload.public_id not in url_to_check:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Public ID not found in URL"
        )

    asset.public_id = payload.public_id
    asset.secure_url = payload.secure_url
    asset.cloudinary_url = payload.cloudinary_url or payload.secure_url
    asset.status = "pending"

    db.commit()
    db.refresh(asset)
    return {"status": "success", "asset_id": asset.id, "secure_url": asset.secure_url}
