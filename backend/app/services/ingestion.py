"""Ask Ekiti knowledge base ingestion.

Infrastructure only — loads the KB manifest and upserts document rows.
Chunking and embedding generation are intentionally not implemented here
(see the TODO in ingest_documents); no LLM/embeddings provider has been
chosen yet.

The real kb_manifest.csv and any validator are still pending from the
AI/Data lead. This is written against the column names given in the Ask
Ekiti infra ticket (doc_id, source_title, source_url, class, tier,
last_verified, ingestible) and will likely need adjusting once the real
file and its exact format/validator arrive.
"""

import csv
from datetime import datetime

from sqlalchemy.orm import Session

from app.models.knowledge import KnowledgeDocument

# Assumed manifest date format for last_verified, e.g. "2026-01-15".
# Adjust once the real kb_manifest.csv / validator is available.
_LAST_VERIFIED_FORMAT = "%Y-%m-%d"


def load_manifest(csv_path: str) -> list[dict]:
    """Read the KB manifest CSV and return only ingestible rows.

    Expects at least the columns: doc_id, source_title, source_url, class,
    tier, last_verified, ingestible. Any other columns the real manifest
    has are read but currently ignored downstream. A row is included only
    if its `ingestible` value is "yes" (case-insensitive).
    """
    with open(csv_path, newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))

    return [
        row for row in rows if (row.get("ingestible") or "").strip().lower() == "yes"
    ]


def ingest_documents(rows: list[dict], db_session: Session) -> int:
    """Upsert manifest rows into KnowledgeDocument.

    Creates a new KnowledgeDocument for a doc_id that doesn't exist yet,
    or updates the existing row's fields otherwise. Returns the number of
    rows processed.
    """
    count = 0

    for row in rows:
        doc_id = row["doc_id"]

        document = (
            db_session.query(KnowledgeDocument).filter_by(doc_id=doc_id).one_or_none()
        )
        if document is None:
            document = KnowledgeDocument(doc_id=doc_id)
            db_session.add(document)

        document.source_title = row.get("source_title", "")
        document.source_url = row.get("source_url") or None
        document.class_ = row.get("class", "")
        document.tier = row.get("tier", "")
        document.last_verified = datetime.strptime(
            row["last_verified"], _LAST_VERIFIED_FORMAT
        ).date()
        document.ingestible = (row.get("ingestible") or "").strip().lower() == "yes"

        # TODO: chunk raw_content and generate embeddings once LLM/embeddings
        # provider is confirmed.

        count += 1

    db_session.commit()
    return count
