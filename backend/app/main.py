from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.routing import APIRouter

from app.api.api import api_router
from app.api.routes import uploads, stories, contributor_admin
from app.core.config import settings

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

if settings.BACKEND_CORS_ORIGINS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

# Mount standard API v1
app.include_router(api_router, prefix=settings.API_V1_STR)
if settings.API_V1_STR != "/api":
    app.include_router(api_router, prefix="/api")

# Mount root-level routers for tests expecting /admin, /stories, /uploads directly
root_router = APIRouter()
root_router.include_router(uploads.router, prefix="/uploads", tags=["uploads"])
root_router.include_router(stories.router, prefix="/stories", tags=["stories"])
root_router.include_router(contributor_admin.router, prefix="/admin", tags=["admin"])
app.include_router(root_router)
