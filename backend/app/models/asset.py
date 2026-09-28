import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime, Text, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from app.db.base_class import Base

class Asset(Base):
    __tablename__ = "assets"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    filename = Column(String, nullable=False)
    url = Column(String, nullable=False)
    folder = Column(String, default="uploads")
    status = Column(String, default="pending")  # pending, approved, rejected
    user_id = Column(String, nullable=True)
    contributor = Column(String, nullable=True)
    rights_status = Column(String, default="pending")
    rejection_reason = Column(Text, nullable=True)
    reviewed_by = Column(String, nullable=True)
    reviewed_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
