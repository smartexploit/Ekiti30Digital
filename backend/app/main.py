from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import (
    health,
    uploads,
    admin,
    stories,
)

app = FastAPI(
    title="Ekiti30 Digital API",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router, tags=["health"])
app.include_router(uploads.router, prefix="/api/uploads", tags=["uploads"])
app.include_router(admin.router, prefix="/api/admin", tags=["admin"])
app.include_router(stories.router, prefix="/api/stories", tags=["stories"])
