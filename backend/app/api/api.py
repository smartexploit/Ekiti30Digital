from fastapi import APIRouter
from app.api.routes import uploads, stories, contributor_admin

api_router = APIRouter()

# Include under API v1 prefixes
api_router.include_router(uploads.router, prefix="/uploads", tags=["uploads"])
api_router.include_router(stories.router, prefix="/stories", tags=["stories"])
api_router.include_router(contributor_admin.router, prefix="/admin", tags=["admin"])
