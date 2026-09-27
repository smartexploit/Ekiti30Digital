from typing import Optional
from pydantic import BaseModel, Field

class UploadInitRequest(BaseModel):
    filename: str
    file_size_bytes: int = Field(..., gt=0)
    mime_type: str

class UploadInitResponse(BaseModel):
    asset_id: str
    upload_id: str
    storage_key: str
    upload_url: str

class UploadCompleteRequest(BaseModel):
    storage_key: Optional[str] = None
    asset_id: Optional[str] = None
    upload_id: Optional[str] = None

class UploadCompleteResponse(BaseModel):
    status: str
    message: str
    asset_id: str
    upload_id: str
    storage_key: str
