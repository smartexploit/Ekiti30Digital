"""Provider-neutral grounded synthesis for Ask Ekiti."""

import json
from collections.abc import Callable
from typing import Any

import httpx

from app.core.config import settings
from app.services.ask_grounding import (
    GroundingError,
    build_evidence_packet,
    render_grounded_statements,
    validate_synthesis,
)

GroundedSynthesizer = Callable[
    [dict[str, Any]],
    dict[str, Any],
]


def _groq_system_prompt(language: str) -> str:
    if language == "yo":
        output_language = (
            "Write the answer in clear Standard Yoruba. "
            "Preserve proper names, dates, figures, and place names accurately."
        )
    else:
        output_language = "Write the answer in clear English."

    return (
        "You are the grounded synthesis layer for Ask Ekiti, "
        "an assistant about Ekiti State, Nigeria. "
        "Use ONLY the evidence supplied by the application. "
        "Do not use outside knowledge or model memory. "
        "Do not invent facts. "
        "Every factual statement must reference at least one supplied "
        "evidence ID. "
        "Do not invent evidence IDs. "
        "If a requested fact is unsupported, omit it. "
        + output_language
        + " Return ONLY a valid JSON object. "
        "Do not include Markdown or citation markers such as [1] "
        "inside statement text. "
        'Use exactly this structure: '
        '{"statements":[{"text":"supported statement",'
        '"citations":[1]}]}'
    )


def _parse_groq_response(payload: Any) -> dict[str, Any]:
    if not isinstance(payload, dict):
        raise RuntimeError("Groq returned an invalid response object")

    choices = payload.get("choices")

    if not isinstance(choices, list) or not choices:
        raise RuntimeError("Groq returned no completion choices")

    first = choices[0]

    if not isinstance(first, dict):
        raise RuntimeError("Groq returned an invalid completion")

    message = first.get("message")

    if not isinstance(message, dict):
        raise RuntimeError("Groq returned no completion message")

    content = message.get("content")

    if not isinstance(content, str) or not content.strip():
        raise RuntimeError("Groq returned empty synthesis content")

    try:
        value = json.loads(content)
    except json.JSONDecodeError as exc:
        raise RuntimeError(
            "Groq synthesis was not valid JSON"
        ) from exc

    if not isinstance(value, dict):
        raise RuntimeError(
            "Groq synthesis must be a JSON object"
        )

    return value


def _call_groq(
    packet: dict[str, Any],
    model: str | None = None,
) -> dict[str, Any]:
    if not settings.GROQ_API_KEY:
        raise RuntimeError(
            "Ask Ekiti synthesis is enabled but "
            "GROQ_API_KEY is not configured"
        )

    body = {
        "model": model or settings.GROQ_SYNTHESIS_MODEL,
        "messages": [
            {
                "role": "system",
                "content": _groq_system_prompt(
                    packet.get("language", "en")
                ),
            },
            {
                "role": "user",
                "content": json.dumps(
                    packet,
                    ensure_ascii=False,
                    separators=(",", ":"),
                ),
            },
        ],
        "temperature": settings.GROQ_TEMPERATURE,
        "response_format": {
            "type": "json_object",
        },
    }

    try:
        response = httpx.post(
            settings.GROQ_API_URL,
            headers={
                "Authorization": (
                    f"Bearer {settings.GROQ_API_KEY}"
                ),
                "Content-Type": "application/json",
            },
            json=body,
            timeout=settings.GROQ_TIMEOUT_SECONDS,
        )

        response.raise_for_status()

    except httpx.HTTPStatusError as exc:
        raise RuntimeError(
            "Groq returned HTTP "
            f"{exc.response.status_code}"
        ) from exc

    except httpx.RequestError as exc:
        raise RuntimeError(
            "Groq request failed"
        ) from exc

    try:
        payload = response.json()
    except ValueError as exc:
        raise RuntimeError(
            "Groq returned invalid JSON"
        ) from exc

    return _parse_groq_response(payload)



CURRENT_INFO_TERMS = (
    "current",
    "currently",
    "today",
    "latest",
    "right now",
    "present governor",
    "present commissioner",
    "ongoing",
    "recent",
    "this year",
    "2026",
)


def _needs_current_source(question: str) -> bool:
    """Keep time-sensitive claims out of model-memory fallback."""
    value = question.casefold()

    return any(
        term in value
        for term in CURRENT_INFO_TERMS
    )


def _general_ekiti_prompt(language: str) -> str:
    if language == "yo":
        language_rule = (
            "Answer in clear Standard Yoruba. Preserve proper names, "
            "dates, numbers and place names accurately."
        )
    else:
        language_rule = "Answer in clear English."

    return (
        "You are Ask Ekiti, an assistant about Ekiti State, Nigeria. "
        "This is a GENERAL BACKGROUND fallback used only when the "
        "project's verified knowledge base has no matching evidence. "
        "Answer only questions that are genuinely about Ekiti State, "
        "its people, places, history, culture, institutions, economy, "
        "education, tourism, agriculture or other Ekiti-related topics. "
        "If the question is not about Ekiti, return status out_of_scope. "
        "Do not claim that the answer is verified by Ask Ekiti. "
        "Do not invent citations or sources. "
        "Do not answer current, latest, live, ongoing, election, "
        "current-officeholder or other time-sensitive questions from "
        "model memory; return status needs_current_source instead. "
        + language_rule
        + " Return ONLY valid JSON with exactly this shape: "
        '{"status":"answered|out_of_scope|needs_current_source",'
        '"answer":"response text"}'
    )


def _parse_general_groq_response(payload: Any) -> dict[str, str]:
    if not isinstance(payload, dict):
        raise RuntimeError(
            "Groq returned an invalid general response object"
        )

    choices = payload.get("choices")

    if not isinstance(choices, list) or not choices:
        raise RuntimeError(
            "Groq returned no general completion choices"
        )

    try:
        content = choices[0]["message"]["content"]
    except (KeyError, TypeError, IndexError) as exc:
        raise RuntimeError(
            "Groq returned an invalid general completion"
        ) from exc

    if not isinstance(content, str) or not content.strip():
        raise RuntimeError(
            "Groq returned empty general-answer content"
        )

    try:
        value = json.loads(content)
    except json.JSONDecodeError as exc:
        raise RuntimeError(
            "Groq general answer was not valid JSON"
        ) from exc

    if not isinstance(value, dict):
        raise RuntimeError(
            "Groq general answer must be a JSON object"
        )

    status = value.get("status")
    answer = value.get("answer")

    if status not in {
        "answered",
        "out_of_scope",
        "needs_current_source",
    }:
        raise RuntimeError(
            "Groq general answer returned an invalid status"
        )

    if not isinstance(answer, str):
        raise RuntimeError(
            "Groq general answer text is invalid"
        )

    return {
        "status": status,
        "answer": answer.strip(),
    }


def answer_general_ekiti(
    question: str,
    language: str,
) -> dict[str, str]:
    """Answer stable Ekiti background questions when KB evidence is absent."""
    if not settings.GROQ_API_KEY:
        raise RuntimeError(
            "GROQ_API_KEY is not configured"
        )

    if _needs_current_source(question):
        return {
            "status": "needs_current_source",
            "answer": (
                "Ìbéèrè yìí nílò orísun tuntun tí a lè ṣàyẹ̀wò "
                "kí a tó dáhùn rẹ̀."
                if language == "yo"
                else
                "This question requires a current verifiable source "
                "before it can be answered."
            ),
        }

    body = {
        "model": settings.GROQ_SYNTHESIS_MODEL,
        "messages": [
            {
                "role": "system",
                "content": _general_ekiti_prompt(language),
            },
            {
                "role": "user",
                "content": question,
            },
        ],
        "temperature": settings.GROQ_TEMPERATURE,
        "response_format": {
            "type": "json_object",
        },
    }

    try:
        response = httpx.post(
            settings.GROQ_API_URL,
            headers={
                "Authorization": (
                    f"Bearer {settings.GROQ_API_KEY}"
                ),
                "Content-Type": "application/json",
            },
            json=body,
            timeout=settings.GROQ_TIMEOUT_SECONDS,
        )

        response.raise_for_status()

    except httpx.HTTPStatusError as exc:
        raise RuntimeError(
            "Groq returned HTTP "
            f"{exc.response.status_code}"
        ) from exc

    except httpx.RequestError as exc:
        raise RuntimeError(
            "Groq general-answer request failed"
        ) from exc

    try:
        payload = response.json()
    except ValueError as exc:
        raise RuntimeError(
            "Groq returned invalid JSON"
        ) from exc

    return _parse_general_groq_response(payload)



def _web_research_system_prompt(language: str) -> str:
    if language == "yo":
        language_rule = (
            "Answer in clear Standard Yoruba. Preserve official names, "
            "people's names, dates, numbers, titles and place names accurately."
        )
    else:
        language_rule = "Answer in clear English."

    return (
        "You are the web-research layer for Ask Ekiti. "
        "The user is asking about Ekiti State, Nigeria. "
        "Use browser search to research the question before answering. "
        "Do not answer factual claims only from model memory. "
        "Prefer primary and authoritative sources such as the Ekiti State "
        "Government, Nigerian government agencies, INEC, official public "
        "institutions, universities and other primary sources. "
        "When primary sources are unavailable, use reputable established "
        "news or institutional sources and cross-check important claims. "
        "For current officeholders, projects, elections, appointments, "
        "policies and other time-sensitive facts, prioritize the newest "
        "reliable information and distinguish current facts from historical "
        "facts. "
        "Do not invent facts, URLs, quotations or citations. "
        "Keep the final answer focused on the user's question. "
        "Use the citations produced by browser search for factual claims. "
        + language_rule
    )



def _web_source_rank(url: str) -> int:
    """Prefer authoritative Nigerian/Ekiti sources."""
    value = url.casefold()

    if "ekitistate.gov.ng" in value:
        return 0

    if ".gov.ng" in value:
        return 1

    if ".edu.ng" in value:
        return 2

    if "wikipedia.org" in value:
        return 4

    return 3


def _clean_web_source_title(
    title: str | None,
    content: str,
    url: str,
) -> str:
    """Return a human-readable title for browser-opened sources."""
    value = title.strip() if isinstance(title, str) else ""

    # Groq browser.open may return titles like:
    # "www.example.gov.ng - viewing lines [0 - 96] of 96"
    # The actual page title is usually present near the top of content.
    if " - viewing lines [" in value:
        for line in content.splitlines()[:8]:
            if line.startswith("L2: "):
                candidate = line.removeprefix("L2: ").strip()
                if candidate:
                    return candidate

    if value:
        return value

    return url


def _extract_web_evidence(payload: Any) -> list[dict[str, str]]:
    """Extract pages actually opened by Groq browser search.

    Search-result titles alone are not evidence. Prefer browser.open/find
    results containing page text, deduplicate by URL, and keep the richest
    copy of each page.
    """
    if not isinstance(payload, dict):
        return []

    choices = payload.get("choices")

    if not isinstance(choices, list) or not choices:
        return []

    message = choices[0].get("message")

    if not isinstance(message, dict):
        return []

    executed = message.get("executed_tools")

    if not isinstance(executed, list):
        return []

    by_url: dict[str, dict[str, str]] = {}

    for tool in executed:
        if not isinstance(tool, dict):
            continue

        search_results = tool.get("search_results")

        if not isinstance(search_results, dict):
            continue

        results = search_results.get("results")

        if not isinstance(results, list):
            continue

        for result in results:
            if not isinstance(result, dict):
                continue

            url = result.get("url")
            title = result.get("title")
            content = result.get("content")

            if (
                not isinstance(url, str)
                or not url.strip()
                or not isinstance(content, str)
                or not content.strip()
            ):
                continue

            item = {
                "title": _clean_web_source_title(
                    title,
                    content,
                    url.strip(),
                ),
                "url": url.strip(),
                # Keep the second grounded Groq call small enough for
                # low-token-rate deployments. Browser search can return very
                # large opened pages; only a focused excerpt is needed for
                # grounded synthesis.
                "content": content.strip()[:2500],
            }

            existing = by_url.get(item["url"])

            if (
                existing is None
                or len(item["content"]) > len(existing["content"])
            ):
                by_url[item["url"]] = item

    ranked = sorted(
        by_url.values(),
        key=lambda item: (
            _web_source_rank(item["url"]),
            -len(item["content"]),
        ),
    )

    # When authoritative Nigerian government sources are available, keep
    # them first while still allowing a small number of corroborating
    # sources for questions that need comparison or freshness.
    official = [
        item
        for item in ranked
        if _web_source_rank(item["url"]) <= 1
    ]

    if official:
        others = [
            item
            for item in ranked
            if item not in official
        ]
        return (official[:2] + others[:1])[:3]

    return ranked[:3]


def answer_web_researched(
    question: str,
    language: str,
) -> dict[str, Any]:
    """Research the web, then ground a second synthesis on opened pages."""
    if not settings.GROQ_API_KEY:
        raise RuntimeError(
            "GROQ_API_KEY is not configured"
        )

    body = {
        "model": settings.GROQ_RESEARCH_MODEL,
        "messages": [
            {
                "role": "system",
                "content": _web_research_system_prompt(language),
            },
            {
                "role": "user",
                "content": question,
            },
        ],
        "temperature": settings.GROQ_TEMPERATURE,
        "max_completion_tokens": 1000,
        "reasoning_effort": "low",
        "tool_choice": "required",
        "tools": [
            {
                "type": "browser_search",
            }
        ],
    }

    research_models = [
        settings.GROQ_RESEARCH_MODEL,
    ]

    if (
        settings.GROQ_SYNTHESIS_MODEL
        not in research_models
    ):
        research_models.append(
            settings.GROQ_SYNTHESIS_MODEL
        )

    payload = None
    research_model = None
    last_status = None
    rate_limited_models: set[str] = set()

    for candidate_model in research_models:
        body["model"] = candidate_model

        try:
            response = httpx.post(
                settings.GROQ_API_URL,
                headers={
                    "Authorization": (
                        f"Bearer {settings.GROQ_API_KEY}"
                    ),
                    "Content-Type": "application/json",
                },
                json=body,
                timeout=settings.GROQ_TIMEOUT_SECONDS,
            )

            response.raise_for_status()

        except httpx.HTTPStatusError as exc:
            last_status = exc.response.status_code

            # Groq applies model-specific rate-limit buckets.
            # If one GPT-OSS model is temporarily exhausted,
            # try the other supported browser-search model.
            if last_status == 429:
                rate_limited_models.add(candidate_model)
                continue

            raise RuntimeError(
                "Groq web research returned HTTP "
                f"{last_status}"
            ) from exc

        except httpx.RequestError as exc:
            raise RuntimeError(
                "Groq web research request failed"
            ) from exc

        try:
            payload = response.json()
        except ValueError as exc:
            raise RuntimeError(
                "Groq web research returned invalid JSON"
            ) from exc

        research_model = candidate_model
        break

    if payload is None or research_model is None:
        raise RuntimeError(
            "Groq web research is temporarily rate limited"
        )

    sources = _extract_web_evidence(payload)

    if not sources:
        raise RuntimeError(
            "Groq web research returned no usable source evidence"
        )

    citations = []
    statements = []

    for index, source in enumerate(sources):
        citations.append(
            {
                "doc_id": f"web-{index + 1}",
                "category": "web",
                "source_ids": [f"WEB-{index + 1}"],
                "source_titles": [source["title"]],
                "source_urls": [source["url"]],
                "source_url": source["url"],
                "tier": "web",
                "last_verified": None,
                "evidence_status": "web_researched",
                "ask_ekiti_approved": False,
                "ask_ekiti_approved_date": None,
                "path": None,
            }
        )

        statements.append(
            {
                "text": source["content"],
                "citation_index": index,
            }
        )

    packet = build_evidence_packet(
        question,
        language,
        statements,
        citations,
    )

    # Important: do not expose the first browser-generated prose.
    # The final answer must come from a second structured synthesis that
    # is restricted to the retrieved web evidence above.
    synthesis_model = settings.GROQ_SYNTHESIS_MODEL

    # Prefer a different model for synthesis after browser research,
    # but never switch back to a model that already returned HTTP 429.
    if research_model == synthesis_model:
        alternate_model = settings.GROQ_RESEARCH_MODEL

        if (
            alternate_model != research_model
            and alternate_model not in rate_limited_models
        ):
            synthesis_model = alternate_model

    raw = _call_groq(
        packet,
        model=synthesis_model,
    )

    try:
        validated = validate_synthesis(
            raw,
            evidence_count=len(packet["evidence"]),
        )
    except GroundingError as exc:
        raise RuntimeError(
            "Web research synthesis failed grounding validation"
        ) from exc

    used_citations = []

    for statement in validated:
        for citation in statement["citations"]:
            if citation not in used_citations:
                used_citations.append(citation)

    return {
        "status": "answered",
        "answer": render_grounded_statements(validated),
        "citations": citations,
        "used_citations": used_citations,
    }


def get_grounded_synthesizer() -> GroundedSynthesizer | None:
    """Return the configured grounded-answer generator."""
    if not settings.ASK_EKITI_SYNTHESIS_ENABLED:
        return None

    if settings.ASK_EKITI_LLM_PROVIDER == "groq":
        if not settings.GROQ_API_KEY:
            raise RuntimeError(
                "Ask Ekiti synthesis is enabled but "
                "GROQ_API_KEY is not configured"
            )

        return _call_groq

    raise RuntimeError(
        "Baalebos synthesis is temporarily suspended"
    )
