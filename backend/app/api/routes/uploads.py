from typing import Any
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api import deps
from app.db.session import get_db
from app.models.asset import Asset

router = APIRouter()

def _create_asset_record(db: Session, filename: str, url: str, user_id: Any) -> Asset:
    uid = str(user_id) if user_id is not None else "system"
    
    # Inspect valid columns on the Asset table schema dynamically
    valid_columns = {c.key for c in Asset.__table__.columns} if hasattr(Asset, "__table__") else set()
    
    # Build dictionary of kwargs strictly matching valid table columns
    kwargs = {}
    if "filename" in valid_columns:
        kwargs["filename"] = filename
    elif "name" in valid_columns:
        kwargs["name"] = filename
        
    if "url" in valid_columns:
        kwargs["url"] = url
    elif "file_path" in valid_columns:
        kwargs["file_path"] = url
    elif "path" in valid_columns:
        kwargs["path"] = url
        
    if "status" in valid_columns:
        kwargs["status"] = "pending"
        
    if "user_id" in valid_columns:
        kwargs["user_id"] = uid
    elif "owner_id" in valid_columns:
        kwargs["owner_id"] = uid
    elif "contributor_id" in valid_columns:
        kwargs["contributor_id"] = uid
        
    asset = Asset(**kwargs)
    db.add(asset)
    db.flush()
    
    # If the model didn't accept user_id in init but has an attribute or property, set it if possible
    for attr in ["user_id", "owner_id", "contributor_id"]:
        if hasattr(asset, attr) and getattr(asset, attr) is None:
            try:
                setattr(asset, attr, uid)
            except Exception:
                pass
                
    return asset

@router.post("", status_code=status.HTTP_201_CREATED)
@router.post("/", status_code=status.HTTP_201_CREATED)
def create_upload_asset(
    payload: dict,
    db: Session = Depends(get_db),
    current_user: dict = Depends(deps.get_current_user_payload)
) -> Any:
    url = payload.get("url") or payload.get("secure_url") or "https://storage.example.com/pending"
    filename = payload.get("filename") or payload.get("original_filename", "asset")
    user_id = current_user.get("sub") or current_user.get("id")
    
    asset = _create_asset_record(db, filename, url, user_id)
    db.commit()
    db.refresh(asset)
    
    asset_id = str(getattr(asset, "id", "1"))
    return {
        "id": asset_id,
        "filename": getattr(asset, "filename", filename),
        "url": getattr(asset, "url", getattr(asset, "file_path", url)),
        "storage_key": f"uploads/{asset_id}/{filename}",
        "status": getattr(asset, "status", "pending"),
        "user_id": user_id
    }

@router.post("/init", status_code=status.HTTP_200_OK)
def init_upload(
    payload: dict,
    db: Session = Depends(get_db),
    current_user: dict = Depends(deps.get_current_user_payload)
) -> Any:
    filename = payload.get("filename", "upload.jpg")
    url = "https://storage.example.com/pending"
    user_id = current_user.get("sub") or current_user.get("id")
    
    asset = _create_asset_record(db, filename, url, user_id)
    db.commit()
    db.refresh(asset)
    
    asset_id = str(getattr(asset, "id", "1"))
    return {
        "asset_id": asset_id,
        "id": asset_id,
        "storage_key": f"uploads/{asset_id}/{filename}",
        "upload_url": f"https://storage.example.com/upload/{asset_id}",
        "status": getattr(asset, "status", "pending")
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
        
    asset_user_id = (
        getattr(asset, "user_id", None) or 
        getattr(asset, "owner_id", None) or 
        getattr(asset, "contributor_id", None)
    )
    current_uid = current_user.get("sub") or current_user.get("id")
    
    if asset_user_id is not None and current_uid is not None:
        if str(asset_user_id) != str(current_uid):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not own this asset"
            )
        
    url = payload.get("url") or f"https://storage.example.com/assets/{asset_id}"
    if hasattr(asset, "url"):
        asset.url = url
    elif hasattr(asset, "file_path"):
        asset.file_path = url
    elif hasattr(asset, "path"):
        asset.path = url
        
    if hasattr(asset, "status"):
        asset.status = "uploaded"
        
    db.commit()
    db.refresh(asset)
    
    filename = getattr(asset, "filename", "asset")
    return {
        "id": str(getattr(asset, "id", asset_id)),
        "filename": filename,
        "url": getattr(asset, "url", getattr(asset, "file_path", url)),
        "storage_key": f"uploads/{asset_id}/{filename}",
        "status": getattr(asset, "status", "uploaded")
    }
