from sqlmodel import SQLModel, create_engine
from app.models.story import Story
from app.models.base import engine

def init_db():
    SQLModel.metadata.create_all(engine)
    print("Database tables initialized successfully!")

if __name__ == "__main__":
    init_db()
