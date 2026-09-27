import uuid
from sqlalchemy import Column, String, Text
from app.db.base_class import Base

class Story(Base):
    __tablename__ = "stories"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    title = Column(String, nullable=False)
    content = Column(Text, nullable=False)
    category = Column(String, default="general", nullable=True)
    status = Column(String, default="pending", nullable=False)
    owner_id = Column(String, nullable=True)
    review_notes = Column(Text, nullable=True)
    reason = Column(Text, nullable=True)
