from app.db.base_class import Base
from app.models.asset import Asset
from app.models.story import Story

try:
    from app.models.knowledge import Knowledge
except ImportError:
    pass

__all__ = ["Base", "Asset", "Story"]
