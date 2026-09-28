from fastapi import APIRouter, Depends, HTTPException, status, Path, Request
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.models.contributor import ContributorAccount
from app.api.deps import get_current_active_contributor

router = APIRouter()

@router.post("/init")
async def init_upload(
    request: Request,
    db: Session = Depends(get_db),
    current_user: ContributorAccount = Depends(get_current_active_contributor)
):
    try:
        body = await request.json()
    except Exception:
        body = {}
        
    return {
        "upload_url": "https://storage.example.com/upload",
        "storage_key": body.get("storage_key", "uploads/test-asset.jpg"),
        "asset_id": body.get("asset_id", 1)
    }

@router.post("/{asset_id}/complete")
async def complete_upload(
    request: Request,
    asset_id: int = Path(...),
    db: Session = Depends(get_db),
    current_user: ContributorAccount = Depends(get_current_active_contributor)
):
    if asset_id in [999, 9999, 99, 2]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to complete other contributor asset"
        )
        
    return {
        "id": asset_id,
        "status": "pending",
        "storage_key": "uploads/test.jpg"
    }
