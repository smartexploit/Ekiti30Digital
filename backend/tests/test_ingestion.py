"""Tests for the Ask Ekiti ingestion pipeline (app/services/ingestion.py).

Uses an in-memory SQLite database for every test — never the real dev.db.
"""

import os

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.models.base import Base
from app.models.knowledge import KnowledgeDocument
from app.services.ingestion import ingest_documents, load_manifest

SAMPLE_MANIFEST = os.path.join(
    os.path.dirname(__file__),
    "..",
    "app",
    "services",
    "sample_data",
    "sample_manifest.csv",
)


@pytest.fixture
def db_session():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    SessionLocal = sessionmaker(bind=engine)
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()


def test_load_manifest_filters_ingestible_rows():
    rows = load_manifest(SAMPLE_MANIFEST)

    # Only "yes" (case-insensitive) rows should come back; the sample file
    # has two "no"/"No" rows mixed in specifically to exercise this.
    assert {row["doc_id"] for row in rows} == {"sample-001", "sample-003", "sample-005"}
    assert all(row["ingestible"].strip().lower() == "yes" for row in rows)


def test_ingest_documents_creates_rows(db_session: Session):
    rows = load_manifest(SAMPLE_MANIFEST)

    count = ingest_documents(rows, db_session)

    assert count == len(rows) == 3
    assert db_session.query(KnowledgeDocument).count() == 3

    doc = db_session.query(KnowledgeDocument).filter_by(doc_id="sample-001").one()
    assert doc.source_title == "History of Ekiti State"
    assert doc.class_ == "history"
    assert doc.tier == "1"
    assert doc.ingestible is True


def test_ingest_documents_upserts_without_duplicating(db_session: Session):
    rows = load_manifest(SAMPLE_MANIFEST)

    first_count = ingest_documents(rows, db_session)
    second_count = ingest_documents(rows, db_session)

    assert first_count == second_count == 3
    assert db_session.query(KnowledgeDocument).count() == 3
