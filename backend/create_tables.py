from app.models.base import engine, get_db
from app.models.story import Story
from sqlmodel import SQLModel

SQLModel.metadata.create_all(engine)
print("Database schema verified.")
