from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict


class UploadInitPayload(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    category: Optional[str] = None
    folder: Optional[str] = None
    media_type: Optional[str] = None
    contributor: Optional[str] = None
    contributor_name: Optional[str] = None
    contributor_email: Optional[str] = None
    rights_status: Optional[str] = None

    model_config = ConfigDict(extra="ignore")


class UploadInitRequest(UploadInitPayload):
    pass


class UploadInitResponse(BaseModel):
    asset_id: int
    upload_preset: str
    cloud_name: str
    folder: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class UploadCompletePayload(BaseModel):
    public_id: str
    secure_url: str

    model_config = ConfigDict(extra="ignore")


class UploadCompleteRequest(UploadCompletePayload):
    pass


class AssetOut(BaseModel):
    id: int
    title: Optional[str] = None
    description: Optional[str] = None
    category: Optional[str] = None
    folder: Optional[str] = None
    media_type: Optional[str] = None
    contributor: Optional[str] = None
    rights_status: Optional[str] = None
    status: str
    public_id: Optional[str] = None
    secure_url: Optional[str] = None
    reviewed_by: Optional[str] = None
    rejection_reason: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)
