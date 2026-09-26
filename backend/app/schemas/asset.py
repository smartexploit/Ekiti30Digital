from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import datetime

class AssetBase(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    category: Optional[str] = None
    folder: Optional[str] = None
    media_type: Optional[str] = None
    contributor: Optional[str] = None
    contributor_name: Optional[str] = None
    contributor_email: Optional[str] = None
    rights_status: Optional[str] = None
    related_content_id: Optional[str] = None

class AssetResponse(AssetBase):
    id: int
    public_id: Optional[str] = None
    secure_url: Optional[str] = None
    cloudinary_url: Optional[str] = None
    status: str
    created_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)

class AssetRejectPayload(BaseModel):
    rejection_reason: str
