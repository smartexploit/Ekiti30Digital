from fastapi import APIRouter
from app.api.routes import uploads, contributor_admin as admin

api_router = APIRouter()

api_router.include_router(uploads.router, prefix="/uploads", tags=["uploads"])
api_router.include_router(admin.router, prefix="/admin", tags=["admin"])
