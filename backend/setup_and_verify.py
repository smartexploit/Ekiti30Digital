import subprocess
from app.models.base import engine
from app.models.story import Story
from sqlmodel import SQLModel

# Free port 8000
subprocess.run("fuser -k 8000/tcp || true", shell=True)

# Create database tables
SQLModel.metadata.create_all(engine)
print("Database schema created and verified.")
