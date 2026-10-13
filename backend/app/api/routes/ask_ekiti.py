from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from typing import Literal
from app.core.config import settings
from app.services.ask_answers import response
from app.services.ask_synthesizer import (
    answer_general_ekiti,
    answer_web_researched,
    get_grounded_synthesizer,
)
from app.services.knowledge_fulltext import retrieve_fulltext
from sqlalchemy.orm import Session

from app.models.base import get_db
from app.services.knowledge_pipeline import retrieve

router = APIRouter(prefix="/api/ask-ekiti", tags=["ask_ekiti"])


@router.get("")
def ask_ekiti_status() -> dict:
    return {
        "status": "ready",
        "answer_mode": "sourced facts",
        "languages": ["en", "yo"],
    }


class AskRequest(BaseModel):
    question: str = Field(max_length=10000)
    category: str | None = None
    language: Literal["en", "yo"] = "en"


@router.post("")
def ask_ekiti(request: AskRequest, db: Session = Depends(get_db)) -> dict:
    """Return only cited facts; language templates do not add factual claims."""
    def search(question, *, category, doc_ids, fact_kind, limit):
        if settings.ASK_EKITI_RETRIEVAL_MODE == "fulltext":
            if db.bind.dialect.name != "postgresql":
                raise RuntimeError("Ask Ekiti text search requires PostgreSQL")
            return retrieve_fulltext(question, db, category=category, doc_ids=doc_ids,
                                     fact_kind=fact_kind, limit=limit)
        return retrieve(
            question,
            db,
            category=category,
            doc_ids=doc_ids,
            fact_kind=fact_kind,
            limit=limit,
        )

    try:
        synthesizer = get_grounded_synthesizer()

        result = response(
            request.question.strip(),
            request.language,
            search,
            request.category,
            synthesizer=synthesizer,
        )

        # If the reviewed KB cannot fully answer the question, optionally
        # research the live web. This path is also used for current/latest
        # questions, which must not be answered from model memory.
        if (
            settings.ASK_EKITI_WEB_RESEARCH_ENABLED
            and (
                result.get("reason") == "no_supported_match"
                or result.get("reason") == "needs_current_source"
                or result.get("coverage") == "partial"
            )
        ):
            try:
                researched = answer_web_researched(
                    request.question.strip(),
                    request.language,
                )
            except RuntimeError:
                # A failed external lookup must not erase the safe KB result.
                return result

            if researched["status"] == "answered":
                return {
                    **result,
                    "answer": researched["answer"],
                    "answer_status": "answered",
                    "coverage": "web_researched",
                    "reason": "web_research_fallback",
                    "kb_citations": result.get("citations", []),
                    "citations": researched.get("citations", []),
                    "statements": [],
                    "synthesis_mode": "web",
                    "web_researched": True,
                    "general_ai": False,
                }

        # Legacy model-memory fallback remains available only when web
        # research is disabled.
        if (
            not settings.ASK_EKITI_WEB_RESEARCH_ENABLED
            and settings.ASK_EKITI_GENERAL_FALLBACK_ENABLED
            and result.get("reason") == "no_supported_match"
        ):
            try:
                general = answer_general_ekiti(
                    request.question.strip(),
                    request.language,
                )
            except RuntimeError:
                # Groq failure must not erase the safe KB response.
                return result

            if general["status"] == "answered":
                return {
                    **result,
                    "answer": general["answer"],
                    "answer_status": "answered",
                    "coverage": "general_ai",
                    "reason": "general_ekiti_fallback",
                    "missing": [],
                    "citations": [],
                    "statements": [],
                    "synthesis_mode": "general",
                    "general_ai": True,
                }

            if general["status"] == "needs_current_source":
                return {
                    **result,
                    "answer": general["answer"],
                    "reason": "needs_current_source",
                    "general_ai": True,
                }

        return result
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
