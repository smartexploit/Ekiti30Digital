import uuid
from datetime import datetime
from sqlalchemy import Column, String, Text, DateTime
from app.db.base_class import Base

class Story(Base):
    __tablename__ = "stories"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    title = Column(String, nullable=False)
    content = Column(Text, nullable=False)
    status = Column(String, default="pending")
    owner_id = Column(String, nullable=True)
    author = Column(String, nullable=True)
    email = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
