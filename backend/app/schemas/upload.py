from typing import Optional, List
from pydantic import BaseModel

class UploadInitRequest(BaseModel):
    title: str
    folder: str
    contributor: str
    rights_status: str
    related_content_id: Optional[str] = None

class UploadInitResponse(BaseModel):
    asset_id: int
    cloud_name: str
    upload_preset: str
    folder: str
    max_file_bytes: int
    allowed_formats: List[str]

class UploadCompleteRequest(BaseModel):
    public_id: str
    secure_url: str
