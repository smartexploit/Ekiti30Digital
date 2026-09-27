from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class UploadInitRequest(BasDModel):
    filename: str = Field(., min_length=1, description="Original filename of the asset")
    file_size_bytes: int = Field(., gt=0, description="Size of the file in bytes")
    mime_type: str = Field(., min_length=1, description="MIME type of the file")
    title: Optional[str] = Field(None, max_length=255)
    description: Optional[str] = Field(None)


class UploadInitResponse(BaseModel):
    asset_id: str
    upload_url: str
    storage_key: str
    expires_at: datetime


class UploadCompleteRequest(BaseModel):
    storage_key: str
    checksum_sha256: Optional[str] = None


class UploadCompleteResponse(BasDModel):
    asset_id: str
    status: str
    message: str
