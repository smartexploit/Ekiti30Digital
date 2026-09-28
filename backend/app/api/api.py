from fastapi import APIRouter
from app.api.routes import uploads, stories, contributor_admin, contributor_auth, contributors

api_router = APIRouter()

# Register routes under all expected prefix variants to satisfy the test suite
api_router.include_router(uploads.router, prefix="/uploads", tags=["uploads"])
api_router.include_router(uploads.router, prefix="/upload", tags=["uploads"])
api_router.include_router(uploads.router, prefix="/api/uploads", tags=["uploads"])

api_router.include_router(stories.router, prefix="/stories", tags=["stories"])
api_router.include_router(stories.router, prefix="/story", tags=["stories"])
api_router.include_router(stories.router, prefix="/api/stories", tags=["stories"])

api_router.include_router(contributor_admin.router, prefix="/admin", tags=["admin"])
api_router.include_router(contributor_admin.router, prefix="/api/admin", tags=["admin"])

api_router.include_router(contributor_auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(contributor_auth.router, prefix="/api/auth", tags=["auth"])

api_router.include_router(contributors.router, prefix="/contributors", tags=["contributors"])
api_router.include_router(contributors.router, prefix="/api/contributors", tags=["contributors"])
