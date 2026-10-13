"""Compose cited facts with explicit missing coverage; never synthesize new facts."""
import re
from collections import defaultdict
from app.services.ask_language import message, yoruba_fact
from app.services.ask_planner import plan, entities, topic_category
from app.services.ask_grounding import (
    build_evidence_packet,
    synthesize_or_fallback,
)

CITATION_KEYS = (
    "doc_id", "source_ids", "source_titles", "source_urls", "source_url",
    "category", "tier", "last_verified", "evidence_status",
    "ask_ekiti_approved", "ask_ekiti_approved_date", "path"
)

_CURRENT_TERMS = (
    "current",
    "currently",
    "today",
    "latest",
    "right now",
    "ongoing",
    "recent",
    "this year",
    "present governor",
    "present commissioner",
)

_GENERIC_STOPWORDS = {
    "a", "about", "an", "and", "are", "as", "at", "be", "been",
    "by", "ekiti", "for", "found", "from", "give", "in", "is",
    "major", "me", "of", "on", "state", "tell", "that", "the",
    "their", "there", "these", "this", "to", "what", "which",
    "who", "with",
}


def _needs_current_source(question):
    value = question.casefold()
    return any(term in value for term in _CURRENT_TERMS)


def _term_set(value):
    terms = set()

    for token in re.findall(r"[a-z0-9]+", value.casefold()):
        if token in _GENERIC_STOPWORDS or len(token) < 3:
            continue

        # Tiny normalization for common plural forms. This is deliberately
        # conservative; it is only a guard against obviously unrelated hits.
        if token.endswith("s") and len(token) > 4:
            token = token[:-1]

        terms.add(token)

    return terms


def _generic_hit_is_relevant(question, hit):
    question_terms = _term_set(question)

    if not question_terms:
        return False

    evidence_terms = _term_set(hit.get("content", ""))

    return bool(question_terms & evidence_terms)


def _missing_category(category, language):
    labels = {
        "tourism": ("tourism", "ìrìn àjò afẹ́"),
        "culture": ("culture", "àṣà"),
        "education": ("education", "ẹ̀kọ́"),
        "health": ("health", "ìlera"),
        "agriculture": ("agriculture", "iṣẹ́ àgbẹ̀"),
        "statistics": ("statistics", "ìṣirò"),
        "history": ("history", "ìtàn"),
        "lgas": ("local government information", "àlàyé ìjọba ìbílẹ̀"),
    }
    value = labels.get(category, (category, category))
    return value[language == "yo"]


def response(
    question,
    language,
    search,
    category=None,
    synthesizer=None,
):
    p = plan(question, language)

    base = {
        "answer_status": "insufficient",
        "language": language,
        "citations": [],
        "statements": [],
        "coverage": "none",
        "missing": [],
    }

    if p.policy:
        return dict(base, answer=message(p.policy, language), reason=p.policy)

    # The current reviewed KB is historical/static knowledge. Until the
    # controlled current-information layer is implemented, never answer
    # live/latest/ongoing questions from stale or merely related records.
    if _needs_current_source(question):
        return dict(
            base,
            answer=message("insufficient", language),
            reason="no_supported_match",
        )

    hits = []

    # An explicit API category is authoritative.
    if category:
        doc_ids = entities(question) if category == "lgas" else None
        hits = search(
            question,
            category=category,
            doc_ids=doc_ids,
            fact_kind=None,
            limit=5,
        )

    elif p.queries:
        # Execute exact/specialised queries first.
        covered_categories = set()

        for query, ids, kind in p.queries:
            planned_category = {
                "creation": "history",
                "headquarters": "lgas",
                "identity": "lgas",
            }.get(kind)

            found = search(
                query,
                category=planned_category,
                doc_ids=ids,
                fact_kind=kind,
                limit=20,
            )
            hits.extend(found)

            if planned_category:
                covered_categories.add(planned_category)

            if kind == "headquarters":
                present = {hit["doc_id"] for hit in found}
                p.missing.extend(
                    ident.removeprefix("lga-")
                    + " headquarters / olú ìjọba"
                    for ident in ids
                    if ident not in present
                )

        # A question may also request other domains.
        # Search each one independently rather than dropping it.
        for requested_category in p.categories:
            if requested_category in covered_categories:
                continue

            doc_ids = (
                entities(question)
                if requested_category == "lgas"
                else None
            )

            found = search(
                question,
                category=requested_category,
                doc_ids=doc_ids,
                fact_kind=None,
                limit=5,
            )
            hits.extend(found)

            if not found:
                p.missing.append(
                    _missing_category(requested_category, language)
                )

    elif p.categories:
        # No special query: retrieve independently from every detected domain.
        for requested_category in p.categories:
            doc_ids = (
                entities(question)
                if requested_category == "lgas"
                else None
            )

            found = search(
                question,
                category=requested_category,
                doc_ids=doc_ids,
                fact_kind=None,
                limit=5,
            )
            hits.extend(found)

            if len(p.categories) > 1 and not found:
                p.missing.append(
                    _missing_category(requested_category, language)
                )

    else:
        # Generic Ekiti question with no explicit domain.
        requested_ids = entities(question)

        hits = search(
            question,
            category=None,
            doc_ids=requested_ids,
            fact_kind=None,
            limit=5,
        )

        # Hybrid/vector retrieval can return records that are about Ekiti
        # but do not answer the user's actual generic question. If no
        # explicit entity constrained the search, require at least one
        # meaningful question/evidence term in common before treating a
        # retrieved record as supporting evidence.
        if not requested_ids:
            hits = [
                hit
                for hit in hits
                if _generic_hit_is_relevant(question, hit)
            ]

    seen = set()
    statements, citations = [], []

    for hit in hits:
        key = (hit["doc_id"], hit["content"])
        if key in seen:
            continue

        seen.add(key)

        # Grounded LLM synthesis receives the original sourced fact,
        # regardless of output language. The selected language controls
        # synthesis, while the evidence itself remains unchanged.
        #
        # Without a synthesizer, Yoruba continues using the bounded,
        # deterministic translations already supported by Ask Ekiti.
        content = (
            hit["content"]
            if language == "en" or synthesizer is not None
            else yoruba_fact(hit["content"])
        )

        if content is None:
            p.missing.append(message("translation", language))
            continue

        citations.append(
            {key: hit.get(key) for key in CITATION_KEYS}
        )
        statements.append(
            {
                "text": content,
                "citation_index": len(citations) - 1,
            }
        )

    if not statements:
        return dict(
            base,
            answer=message("insufficient", language),
            missing=list(dict.fromkeys(p.missing)),
            reason="no_supported_match",
        )

    fallback_core_answer = "\n".join(
        f"{item['text']} [{item['citation_index'] + 1}]"
        for item in statements
    )

    packet = build_evidence_packet(
        question,
        language,
        statements,
        citations,
    )

    synthesis = synthesize_or_fallback(
        synthesizer,
        packet,
        fallback_core_answer,
    )

    answer = synthesis["answer"]

    # If live Yoruba synthesis fails, never silently return an English
    # generated fallback as though it were Yoruba. Use a reviewed bounded
    # translation when one exists; otherwise state that translation is not
    # available.
    if (
        language == "yo"
        and synthesizer is not None
        and synthesis["mode"] == "fallback"
    ):
        reviewed = []

        for item in statements:
            translated = yoruba_fact(item["text"])

            if translated is None:
                reviewed = []
                break

            reviewed.append(
                f"{translated} [{item['citation_index'] + 1}]"
            )

        answer = (
            "\n".join(reviewed)
            if reviewed
            else message("translation", "yo")
        )

    signatures = defaultdict(set)

    for hit in hits:
        signature = re.sub(
            r"\d+(?:[.,]\d+)*",
            "#",
            hit["content"],
        )
        signatures[signature].add(hit["content"])

    conflict = any(
        len(values) > 1
        for values in signatures.values()
    )

    if conflict:
        answer += "\n" + (
            "The retrieved sources give different figures or dates. "
            "Compare the cited statements and their periods; "
            "no resolution is assumed."
            if language == "en"
            else
            "Àwọn orísun tí a rí ní iye tàbí ọjọ́ tó yàtọ̀. "
            "Ṣe àfiwé àwọn ọ̀rọ̀ àti àsìkò wọn; "
            "a kò tíì pinnu èyí tó tọ́."
        )

    if any(
        term in question.casefold()
        for term in ("current", "today", "still operating")
    ):
        dates = sorted(
            {
                hit.get("last_verified")
                for hit in hits
                if hit.get("last_verified")
            }
        )

        if dates:
            joined_dates = ", ".join(dates)
            answer += "\n" + (
                "Last verified: "
                + joined_dates
                + ". This does not confirm live conditions."
                if language == "en"
                else
                "Ọjọ́ ìjẹ́rìí: "
                + joined_dates
                + ". Èyí kò jẹ́rìí sí ipò ní báyìí."
            )

    if any(
        hit.get("evidence_status") != "verified"
        for hit in hits
    ):
        answer += "\n" + (
            "Some cited material is approved for Ask Ekiti "
            "but is not yet fully verified."
            if language == "en"
            else
            "Díẹ̀ nínú ẹ̀rí náà ni a fọwọ́ sí fún Ask Ekiti, "
            "ṣùgbọ́n a kò tíì jẹ́rìí rẹ̀ ní kíkún."
        )

    if p.missing:
        prefix = (
            "Not covered by the retrieved sourced evidence: "
            if language == "en"
            else "Ẹ̀rí tí a rí kò bo àwọn wọ̀nyí: "
        )
        answer += (
            "\n"
            + prefix
            + "; ".join(dict.fromkeys(p.missing))
            + "."
        )

    return dict(
        base,
        answer=answer,
        answer_status="answered",
        citations=citations,
        statements=statements,
        missing=list(dict.fromkeys(p.missing)),
        coverage="partial" if p.missing else "supported",
        sources_differ=conflict,
        synthesis_mode=synthesis["mode"],
    )
