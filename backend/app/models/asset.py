from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Text, DateTime
from app.models.base import Base


def utc_now():
    return datetime.now(timezone.utc)


class Asset(Base):
    __tablename__ = "assets"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=True)
    description = Column(Text, nullable=True)
    category = Column(String(100), nullable=True)
    folder = Column(String(255), nullable=True)
    media_type = Column(String(50), nullable=True)
    
    contributor = Column(String(255), nullable=True)
    contributor_name = Column(String(255), nullable=True)
    contributor_email = Column(String(255), nullable=True)
    rights_status = Column(String(100), nullable=True)
    related_content_id = Column(String(255), nullable=True)
    
    status = Column(String(50), default="pending", nullable=False)
    public_id = Column(String(255), nullable=True)
    secure_url = Column(Text, nullable=True)
    cloudinary_url = Column(Text, nullable=True)
    
    reviewed_by = Column(String(255), nullable=True)
    reviewed_at = Column(DateTime(timezone=True), nullable=True)
    rejection_reason = Column(Text, nullable=True)
    
    created_at = Column(DateTime(timezone=True), default=utc_now)
    updated_at = Column(DateTime(timezone=True), default=utc_now, onupdate=utc_now)
