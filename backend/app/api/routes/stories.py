from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.models.base import get_db
from app.models.asset import Asset
from app.schemas.assets import UploadInitRequest, AssetOut

router = APIRouter(prefix="/stories", tags=["Stories"])

@router.post("/", response_model=AssetOut, status_code=status.HTTP_201_CREATED)
def create_community_story(
    story_in: UploadInitRequest,
    db: Session = Depends(get_db)
):
    """
    Submit a new 'My Story' entry for community archiving and admin review.
    Keeps uploads.py and config.py completely untouched.
    """
    db_asset = Asset(
        description=story_in.description,
        folder=story_in.folder,
        rights_status=story_in.rights_status,
        source=story_in.source,
        location_lga=story_in.location_lga,
        related_content_id=story_in.related_content_id,
        status="pending",
    )
    db.add(db_asset)
    db.commit()
    db.refresh(db_asset)
    return db_asset
