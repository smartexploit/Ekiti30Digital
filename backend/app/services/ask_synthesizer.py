"""Provider-neutral grounded synthesis for Ask Ekiti."""

import json
from collections.abc import Callable
from typing import Any

import httpx

from app.core.config import settings

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


def _call_groq(packet: dict[str, Any]) -> dict[str, Any]:
    if not settings.GROQ_API_KEY:
        raise RuntimeError(
            "Ask Ekiti synthesis is enabled but "
            "GROQ_API_KEY is not configured"
        )

    body = {
        "model": settings.GROQ_MODEL,
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
        "model": settings.GROQ_MODEL,
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
