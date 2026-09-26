from fastapi import FastAPI
from app.api.routes import admin, stories, uploads

app = FastAPI(title="Ekiti30Digital API")

# Mount routes matching test expectations
app.include_router(stories.router, prefix="/api/stories", tags=["stories"])
app.include_router(admin.router)
app.include_router(uploads.router)
