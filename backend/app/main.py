from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import ask_ekiti, health, lgas, stories, timeline, vision2056
from app.core.config import settings

app = FastAPI(title=settings.PROJECT_NAME)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router)
app.include_router(timeline.router)
app.include_router(lgas.router)
app.include_router(stories.router)
app.include_router(vision2056.router)
app.include_router(ask_ekiti.router)
