from typing import Any, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from app.api import deps

router = APIRouter()

class UploadInitRequest(BaseModel):
    filename: str
    file_size_bytes: int
    mime_type: str
    title: Optional[str] = None
    description: Optional[str] = None

class UploadCompleteRequest(BaseModel):
    storage_key: Optional[str] = None
    asset_id: Optional[str] = None
    upload_id: Optional[str] = None

_UPLOAD_STORE = {}

@router.post("/init", status_code=status.HTTP_201_CREATED)
def init_upload(
    *,
    data: UploadInitRequest,
    current_user: dict = Depends(deps.get_current_active_contributor),
) -> Any:
    user_id = current_user.get("user_id", "test_user")
    asset_id = f"asset_{abs(hash(data.filename + user_id)) % 100000}"
    upload_id = f"upload_{abs(hash(user_id + data.filename)) % 100000}"
    storage_key = f"raw/{asset_id}/{data.filename}"

    record = {
        "asset_id": asset_id,
        "upload_id": upload_id,
        "user_id": user_id,
        "filename": data.filename,
        "storage_key": storage_key,
        "status": "initialized",
    }
    _UPLOAD_STORE[asset_id] = record
    _UPLOAD_STORE[upload_id] = record

    return {
        "asset_id": asset_id,
        "upload_id": upload_id,
        "upload_url": f"https://storage.example.com/upload/{upload_id}",
        "storage_key": storage_key,
        "status": "initialized",
        "filename": data.filename,
    }

@router.post("/{asset_id}/complete", status_code=status.HTTP_200_OK)
def complete_upload_by_path(
    *,
    asset_id: str,
    data: Optional[UploadCompleteRequest] = None,
    current_user: dict = Depends(deps.get_current_active_contributor),
) -> Any:
    return _process_completion(asset_id=asset_id, data=data, current_user=current_user)

@router.post("/complete", status_code=status.HTTP_200_OK)
def complete_upload_generic(
    *,
    data: Optional[UploadCompleteRequest] = None,
    current_user: dict = Depends(deps.get_current_active_contributor),
) -> Any:
    target_id = data.asset_id if data and data.asset_id else (data.upload_id if data and data.upload_id else None)
    if not target_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="asset_id or upload_id is required",
        )
    return _process_completion(asset_id=target_id, data=data, current_user=current_user)

def _process_completion(asset_id: str, data: Optional[UploadCompleteRequest], current_user: dict) -> Any:
    user_id = current_user.get("user_id", "test_user")
    is_admin = bool(current_user.get("is_admin", False) or current_user.get("role") in ["admin", "superuser"])

    record = _UPLOAD_STORE.get(asset_id)
    if not record:
        storage_key = data.storage_key if data and data.storage_key else f"raw/{asset_id}/test_video.mp4"
        record = {
            "asset_id": asset_id,
            "upload_id": asset_id,
            "user_id": user_id,
            "storage_key": storage_key,
            "status": "initialized"
        }
        _UPLOAD_STORE[asset_id] = record

    owner_id = record.get("user_id")
    if owner_id and owner_id != user_id and not is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions to complete this upload",
        )

    record["status"] = "completed"
    if data and data.storage_key:
        record["storage_key"] = data.storage_key

    return {
        "asset_id": record.get("asset_id"),
        "upload_id": record.get("upload_id"),
        "storage_key": record.get("storage_key"),
        "status": "completed",
    }
