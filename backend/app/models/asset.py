import uuid
from sqlalchemy import Column, String, Integer, Text
from app.db.base_class import Base

class Asset(Base):
    __tablename__ = "assets"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    filename = Column(String, nullable=False)
    file_size = Column(Integer, nullable=True)
    content_type = Column(String, nullable=True)
    status = Column(String, default="pending", nullable=False)
    owner_id = Column(String, nullable=True)
    storage_key = Column(String, nullable=True)
    review_notes = Column(Text, nullable=True)
    reason = Column(Text, nullable=True)
