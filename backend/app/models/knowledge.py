"""Ask Ekiti knowledge base storage models.

Infrastructure only: this is the storage layer for the knowledge base that
will back the Ask Ekiti assistant. Chunking and embedding generation are not
implemented here — see app/services/ingestion.py for the ingestion skeleton
and its TODOs. No LLM/embeddings provider has been chosen yet.
"""

from datetime import date, datetime

from pgvector.sqlalchemy import Vector
from sqlalchemy import Boolean, Date, DateTime, ForeignKey, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base

# Placeholder embedding dimension. Update this once the embeddings
# provider/model is chosen — dimension varies by model (e.g. 1536 for
# OpenAI text-embedding-3-small, 384/768 for many sentence-transformers
# models). Changing this requires a new migration.
EMBEDDING_DIMENSIONS = 1536


class KnowledgeDocument(Base):
    """A single sourced document from the knowledge base manifest."""

    __tablename__ = "knowledge_documents"

    id: Mapped[int] = mapped_column(primary_key=True)

    # Matches the manifest's doc_id (see app/services/ingestion.py).
    doc_id: Mapped[str] = mapped_column(unique=True, index=True)

    source_title: Mapped[str]
    source_url: Mapped[str | None]

    # `class` is a reserved word in Python, so the attribute is `class_`
    # while the actual DB column is named `class` to match the manifest.
    class_: Mapped[str] = mapped_column("class")

    tier: Mapped[str]
    last_verified: Mapped[date] = mapped_column(Date)
    ingestible: Mapped[bool] = mapped_column(Boolean)

    # Source content prior to chunking. Nullable since a document row can
    # exist (from the manifest) before its content has been ingested.
    raw_content: Mapped[str | None] = mapped_column(Text)

    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), onupdate=func.now()
    )

    chunks: Mapped[list["Chunk"]] = relationship(
        back_populates="document",
        cascade="all, delete-orphan",
    )


class Chunk(Base):
    """A chunk of a document's content, with its embedding vector."""

    __tablename__ = "chunks"

    id: Mapped[int] = mapped_column(primary_key=True)

    document_id: Mapped[int] = mapped_column(
        ForeignKey("knowledge_documents.id", ondelete="CASCADE")
    )

    # Position of this chunk within the document's raw_content.
    chunk_index: Mapped[int]

    content: Mapped[str] = mapped_column(Text)

    # TODO: EMBEDDING_DIMENSIONS is a placeholder (1536) until the
    # embeddings provider/model is confirmed — update it and generate a new
    # migration once that's decided.
    embedding: Mapped[list[float] | None] = mapped_column(Vector(EMBEDDING_DIMENSIONS))

    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    document: Mapped["KnowledgeDocument"] = relationship(back_populates="chunks")
