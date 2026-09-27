from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.api.dependencies import get_db

router = APIRouter()

@router.post("/contributors/{contributor_id}/review")
def review_contributor(
    contributor_id: int,
    action: str,
    db: Session = Depends(get_db),
):
    from app.models.contributor import ContributorAccount

    contributor = (
        db.query(ContributorAccount)
        .filter(ContributorAccount.id == contributor_id)
        .first()
    )
    
    if not contributor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Contributor not found",
        )
        
    return {"status": "success", "contributor_id": contributor_id, "action": action}
