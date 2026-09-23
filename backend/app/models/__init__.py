"""SQLAlchemy models.

Import every model module here so Base.metadata is fully populated —
Alembic's autogenerate (see backend/alembic/env.py) relies on this.
"""

from app.models.knowledge import Chunk, KnowledgeDocument  # noqa: F401
