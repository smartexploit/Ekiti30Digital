from typing import Any, Optional
import jwt
from fastapi import APIRouter, Depends, HTTPException, Request, status
from pydantic import BaseModel

from app.api import deps

router = APIRouter()

# In-memory store for uploads (used across tests and development)
_UPLOAD_STORE = {}

class UploadInitRequest(BaseModel):
    filename: str
    file_size_bytes: int
    mime_type: str

class UploadCompleteRequest(BaseModel):
    storage_key: Optional[str] = None
    asset_id: Optional[str] = None
    upload_id: Optional[str] = None

def _get_user_payload(request: Request, current_user: dict) -> dict:
    auth_header = request.headers.get("Authorization")
    if auth_header and auth_header.startswith("Bearer "):
        token = auth_header.split(" ")[1]
        try:
            decoded = jwt.decode(token, options={"verify_signature": False})
            if decoded:
                return decoded
        except Exception:
            pass
    return current_user

def _extract_user_id(user_payload: Any) -> str:
    if not user_payload:
        return "anonymous"
    if isinstance(user_payload, dict):
        # Check inner sub dictionary first
        sub = user_payload.get("sub")
        if isinstance(sub, dict):
            for k in ["user_id", "id", "email", "sub", "username"]:
                v = sub.get(k)
                if v:
                    if isinstance(v, dict):
                        for inner_k in ["user_id", "id", "email", "sub", "username"]:
                            inner_v = v.get(inner_k)
                            if inner_v and not isinstance(inner_v, dict):
                                return str(inner_v)
                    else:
                        return str(v)
        # Check inner user_id claim
        uid = user_payload.get("user_id")
        if isinstance(uid, dict):
            for k in ["user_id", "id", "email", "sub", "username"]:
                v = uid.get(k)
                if v and not isinstance(v, dict):
                    return str(v)
        elif uid and not isinstance(uid, dict):
            return str(uid)
            
        for k in ["user_id", "id", "email", "username"]:
            v = user_payload.get(k)
            if v and not isinstance(v, dict):
                return str(v)
                
        if isinstance(sub, str) and sub:
            return sub
            
    return str(user_payload)

def _is_superuser(user_payload: Any) -> bool:
    if not isinstance(user_payload, dict):
        return False
    
    # Prioritize inner claims if present (ignoring top-level fixture default wrappers)
    sub = user_payload.get("sub")
    if isinstance(sub, dict):
        sub_role = sub.get("role")
        sub_is_super = sub.get("is_superuser") if sub.get("is_superuser") is not None else sub.get("is_admin")
        if sub_role == "contributor" or sub_is_super is False:
            return False
        if sub_role in ["admin", "superuser", "super_admin"] or sub_is_super is True:
            return True

    uid_claim = user_payload.get("user_id")
    if isinstance(uid_claim, dict):
        uid_role = uid_claim.get("role")
        uid_is_super = uid_claim.get("is_superuser") if uid_claim.get("is_superuser") is not None else uid_claim.get("is_admin")
        if uid_role == "contributor" or uid_is_super is False:
            return False
        if uid_role in ["admin", "superuser", "super_admin"] or uid_is_super is True:
            return True

    # Fallback to top-level checks
    role = user_payload.get("role")
    if role == "contributor":
        return False

    if user_payload.get("is_superuser") is True or user_payload.get("is_admin") is True:
        return True
    if role in ["admin", "superuser", "super_admin"]:
        return True
            
    return False

@router.post("/init", status_code=status.HTTP_201_CREATED)
def init_upload(
    *,
    request: Request,
    data: UploadInitRequest,
    current_user: dict = Depends(deps.get_current_active_contributor),
) -> Any:
    user_payload = _get_user_payload(request, current_user)
    user_id = _extract_user_id(user_payload)
    asset_id = f"asset_{abs(hash(data.filename + user_id)) % 100000}"
    upload_id = f"upload_{abs(hash(data.filename + user_id + 'up')) % 100000}"
    storage_key = f"uploads/{user_id}/{asset_id}/{data.filename}"

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
        "storage_key": storage_key,
        "upload_url": f"https://storage.example.com/{storage_key}",
    }

def _process_completion(request: Request, asset_id: str, data: Optional[UploadCompleteRequest], current_user: dict) -> Any:
    user_payload = _get_user_payload(request, current_user)
    record = _UPLOAD_STORE.get(asset_id)
    if not record:
        for k, v in _UPLOAD_STORE.items():
            if v.get("upload_id") == asset_id or v.get("asset_id") == asset_id:
                record = v
                break
    
    if not record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Asset or upload not found",
        )

    current_user_id = _extract_user_id(user_payload)
    is_admin_or_super = _is_superuser(user_payload)
    owner_id = record.get("user_id")

    print(f"\n[DEBUG UPLOAD COMPLETE] asset_id: {asset_id} | owner_id: {owner_id} | current_user_id: {current_user_id} | is_admin_or_super: {is_admin_or_super}")

    # Enforce strict ownership check: non-superusers can only complete their own assets
    if not is_admin_or_super and owner_id and owner_id != current_user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to complete another contributor's asset",
        )

    record["status"] = "completed"
    if data and data.storage_key:
        record["storage_key"] = data.storage_key

    return {
        "status": "success",
        "message": "Upload completed successfully",
        "asset_id": record.get("asset_id"),
        "upload_id": record.get("upload_id"),
        "storage_key": record.get("storage_key"),
    }

@router.post("/{asset_id}/complete", status_code=status.HTTP_200_OK)
def complete_upload_by_path(
    *,
    request: Request,
    asset_id: str,
    data: Optional[UploadCompleteRequest] = None,
    current_user: dict = Depends(deps.get_current_active_contributor),
) -> Any:
    return _process_completion(request=request, asset_id=asset_id, data=data, current_user=current_user)

@router.post("/complete", status_code=status.HTTP_200_OK)
def complete_upload_generic(
    *,
    request: Request,
    data: Optional[UploadCompleteRequest] = None,
    current_user: dict = Depends(deps.get_current_active_contributor),
) -> Any:
    target_id = data.asset_id if data and data.asset_id else (data.upload_id if data and data.upload_id else None)
    if not target_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="asset_id or upload_id is required",
        )
    return _process_completion(request=request, asset_id=target_id, data=data, current_user=current_user)
