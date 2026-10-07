"""Ask Ekiti synthesis must remain opt-in and fail closed."""

import pytest

from app.core.config import settings
from app.services.ask_synthesizer import (
    _call_baalebos,
    get_grounded_synthesizer,
)


def test_synthesis_disabled_returns_no_generator(monkeypatch):
    monkeypatch.setattr(
        settings,
        "ASK_EKITI_SYNTHESIS_ENABLED",
        False,
    )

    assert get_grounded_synthesizer() is None


@pytest.mark.parametrize(
    ("setting", "message"),
    [
        (
            "ASK_EKITI_LLM_WEBHOOK_URL",
            "ASK_EKITI_LLM_WEBHOOK_URL",
        ),
        (
            "ASK_EKITI_LLM_WEBHOOK_KEY",
            "ASK_EKITI_LLM_WEBHOOK_KEY",
        ),
    ],
)
def test_enabled_synthesis_requires_configuration(
    monkeypatch,
    setting,
    message,
):
    monkeypatch.setattr(
        settings,
        "ASK_EKITI_SYNTHESIS_ENABLED",
        True,
    )

    monkeypatch.setattr(
        settings,
        "ASK_EKITI_LLM_WEBHOOK_URL",
        "https://example.org/gateway",
    )
    monkeypatch.setattr(
        settings,
        "ASK_EKITI_LLM_WEBHOOK_KEY",
        "secret",
    )
    monkeypatch.setattr(
        settings,
        "LLM_MODEL",
        "example-model",
    )

    monkeypatch.setattr(settings, setting, None)

    with pytest.raises(RuntimeError, match=message):
        get_grounded_synthesizer()


def test_auto_mode_returns_configured_synthesizer(
    monkeypatch,
):
    monkeypatch.setattr(
        settings,
        "ASK_EKITI_SYNTHESIS_ENABLED",
        True,
    )
    monkeypatch.setattr(
        settings,
        "ASK_EKITI_LLM_WEBHOOK_URL",
        "https://example.org/gateway",
    )
    monkeypatch.setattr(
        settings,
        "ASK_EKITI_LLM_WEBHOOK_KEY",
        "secret",
    )
    monkeypatch.setattr(
        settings,
        "ASK_EKITI_LLM_MODE",
        "auto",
    )
    monkeypatch.setattr(
        settings,
        "LLM_MODEL",
        None,
    )

    assert callable(get_grounded_synthesizer())


def test_manual_mode_requires_model(
    monkeypatch,
):
    monkeypatch.setattr(
        settings,
        "ASK_EKITI_SYNTHESIS_ENABLED",
        True,
    )
    monkeypatch.setattr(
        settings,
        "ASK_EKITI_LLM_WEBHOOK_URL",
        "https://example.org/gateway",
    )
    monkeypatch.setattr(
        settings,
        "ASK_EKITI_LLM_WEBHOOK_KEY",
        "secret",
    )
    monkeypatch.setattr(
        settings,
        "ASK_EKITI_LLM_MODE",
        "manual",
    )
    monkeypatch.setattr(
        settings,
        "LLM_MODEL",
        None,
    )

    with pytest.raises(
        RuntimeError,
        match="requires LLM_MODEL",
    ):
        get_grounded_synthesizer()


def _creation_hit():
    return {
        "doc_id": "history-state-creation-1996",
        "content": "Ekiti State was created on 1 October 1996.",
        "category": "history",
        "source_ids": ["SRC-001"],
        "source_titles": ["Official creation source"],
        "source_urls": ["https://example.org/creation"],
        "source_url": "https://example.org/creation",
        "tier": "A",
        "last_verified": "2026-09-29",
        "evidence_status": "verified",
        "ask_ekiti_approved": False,
        "ask_ekiti_approved_date": None,
        "path": "01_History/state-creation-1996.md",
    }


def test_api_uses_valid_grounded_synthesizer(
    client,
    monkeypatch,
):
    from app.api.routes import ask_ekiti

    monkeypatch.setattr(
        ask_ekiti,
        "retrieve",
        lambda *args, **kwargs: [_creation_hit()],
    )

    def synthesizer(packet):
        assert packet["question"] == "When was Ekiti State created?"
        assert packet["evidence"][0]["id"] == 1

        return {
            "statements": [
                {
                    "text": (
                        "Ekiti State came into existence "
                        "on 1 October 1996."
                    ),
                    "citations": [1],
                }
            ]
        }

    monkeypatch.setattr(
        ask_ekiti,
        "get_grounded_synthesizer",
        lambda: synthesizer,
    )

    response = client.post(
        "/api/ask-ekiti",
        json={
            "question": "When was Ekiti State created?",
            "language": "en",
        },
    )

    assert response.status_code == 200

    payload = response.json()

    assert payload["synthesis_mode"] == "grounded"
    assert (
        "Ekiti State came into existence "
        "on 1 October 1996. [1]"
        in payload["answer"]
    )
    assert payload["citations"][0]["source_ids"] == ["SRC-001"]


def test_api_invalid_synthesis_falls_back_safely(
    client,
    monkeypatch,
):
    from app.api.routes import ask_ekiti

    monkeypatch.setattr(
        ask_ekiti,
        "retrieve",
        lambda *args, **kwargs: [_creation_hit()],
    )

    def invalid_synthesizer(_packet):
        return {
            "statements": [
                {
                    "text": "Ekiti was created by an unsupported person.",
                    "citations": [99],
                }
            ]
        }

    monkeypatch.setattr(
        ask_ekiti,
        "get_grounded_synthesizer",
        lambda: invalid_synthesizer,
    )

    response = client.post(
        "/api/ask-ekiti",
        json={
            "question": "When was Ekiti State created?",
            "language": "en",
        },
    )

    assert response.status_code == 200

    payload = response.json()

    assert payload["synthesis_mode"] == "fallback"
    assert (
        "Ekiti State was created on 1 October 1996. [1]"
        in payload["answer"]
    )
    assert "unsupported person" not in payload["answer"]



def test_baalebos_auto_request_and_response_contract(monkeypatch):
    captured = {}

    class FakeResponse:
        def raise_for_status(self):
            return None

        def json(self):
            return {
                "success": True,
                "text": (
                    '{"statements":['
                    '{"text":"Ekiti State was created on 1 October 1996.",'
                    '"citations":[1]}'
                    ']}'
                ),
                "usedModel": "groq-llama-3.3-70b",
                "classification": "general",
                "mode": "auto",
                "routingSummary": [],
            }

    def fake_post(url, *, headers, json, timeout):
        captured["url"] = url
        captured["headers"] = headers
        captured["json"] = json
        captured["timeout"] = timeout
        return FakeResponse()

    monkeypatch.setattr(
        settings,
        "ASK_EKITI_LLM_WEBHOOK_URL",
        "https://gateway.baalebo.xyz/webhook/baalebos-ai",
    )
    monkeypatch.setattr(
        settings,
        "ASK_EKITI_LLM_WEBHOOK_KEY",
        "team-secret-key",
    )
    monkeypatch.setattr(
        settings,
        "ASK_EKITI_LLM_MODE",
        "auto",
    )
    monkeypatch.setattr(
        settings,
        "ASK_EKITI_LLM_TIMEOUT_SECONDS",
        60.0,
    )

    monkeypatch.setattr(
        "app.services.ask_synthesizer.httpx.post",
        fake_post,
    )

    packet = {
        "question": "When was Ekiti State created?",
        "language": "en",
        "rules": [
            "Use only the supplied evidence.",
        ],
        "evidence": [
            {
                "id": 1,
                "fact": (
                    "Ekiti State was created "
                    "on 1 October 1996."
                ),
                "doc_id": "history-state-creation-1996",
                "source_ids": ["SRC-001"],
            }
        ],
        "output_schema": {
            "statements": [
                {
                    "text": "supported statement",
                    "citations": [1],
                }
            ]
        },
    }

    result = _call_baalebos(packet)

    assert captured["url"] == (
        "https://gateway.baalebo.xyz/webhook/baalebos-ai"
    )

    assert captured["headers"]["Content-Type"] == "application/json"
    assert captured["headers"]["x-api-key"] == "team-secret-key"

    assert captured["json"]["mode"] == "auto"
    assert "model" not in captured["json"]

    prompt = captured["json"]["message"]

    assert "Use ONLY the evidence supplied in INPUT." in prompt
    assert "Ekiti State was created on 1 October 1996." in prompt
    assert '"id":1' in prompt
    assert captured["timeout"] == 60.0

    assert result == {
        "statements": [
            {
                "text": (
                    "Ekiti State was created "
                    "on 1 October 1996."
                ),
                "citations": [1],
            }
        ]
    }

    # Credentials must never become part of the generated result.
    assert "team-secret-key" not in str(result)


@pytest.mark.parametrize("status_code", [401, 429, 502])
def test_baalebos_http_errors_fail_closed(
    monkeypatch,
    status_code,
):
    import httpx

    request = httpx.Request(
        "POST",
        "https://gateway.baalebo.xyz/webhook/baalebos-ai",
    )

    response = httpx.Response(
        status_code,
        request=request,
        json={
            "status": "error",
            "code": status_code,
        },
    )

    def fake_post(*args, **kwargs):
        return response

    monkeypatch.setattr(
        settings,
        "ASK_EKITI_LLM_WEBHOOK_URL",
        "https://gateway.baalebo.xyz/webhook/baalebos-ai",
    )
    monkeypatch.setattr(
        settings,
        "ASK_EKITI_LLM_WEBHOOK_KEY",
        "secret",
    )
    monkeypatch.setattr(
        settings,
        "ASK_EKITI_LLM_MODE",
        "auto",
    )
    monkeypatch.setattr(
        "app.services.ask_synthesizer.httpx.post",
        fake_post,
    )

    with pytest.raises(
        RuntimeError,
        match=f"HTTP {status_code}",
    ):
        _call_baalebos(
            {
                "question": "Test",
                "language": "en",
                "rules": [],
                "evidence": [],
                "output_schema": {},
            }
        )


def test_baalebos_invalid_outer_json_fails_closed(monkeypatch):
    class FakeResponse:
        def raise_for_status(self):
            return None

        def json(self):
            raise ValueError("invalid json")

    monkeypatch.setattr(
        settings,
        "ASK_EKITI_LLM_WEBHOOK_URL",
        "https://gateway.baalebo.xyz/webhook/baalebos-ai",
    )
    monkeypatch.setattr(
        settings,
        "ASK_EKITI_LLM_WEBHOOK_KEY",
        "secret",
    )
    monkeypatch.setattr(
        settings,
        "ASK_EKITI_LLM_MODE",
        "auto",
    )
    monkeypatch.setattr(
        "app.services.ask_synthesizer.httpx.post",
        lambda *args, **kwargs: FakeResponse(),
    )

    with pytest.raises(
        RuntimeError,
        match="returned invalid JSON",
    ):
        _call_baalebos(
            {
                "question": "Test",
                "language": "en",
                "rules": [],
                "evidence": [],
                "output_schema": {},
            }
        )


def test_baalebos_non_json_synthesis_text_fails_closed(monkeypatch):
    class FakeResponse:
        def raise_for_status(self):
            return None

        def json(self):
            return {
                "success": True,
                "text": "This is not JSON.",
                "mode": "auto",
            }

    monkeypatch.setattr(
        settings,
        "ASK_EKITI_LLM_WEBHOOK_URL",
        "https://gateway.baalebo.xyz/webhook/baalebos-ai",
    )
    monkeypatch.setattr(
        settings,
        "ASK_EKITI_LLM_WEBHOOK_KEY",
        "secret",
    )
    monkeypatch.setattr(
        settings,
        "ASK_EKITI_LLM_MODE",
        "auto",
    )
    monkeypatch.setattr(
        "app.services.ask_synthesizer.httpx.post",
        lambda *args, **kwargs: FakeResponse(),
    )

    with pytest.raises(
        RuntimeError,
        match="synthesis was not valid JSON",
    ):
        _call_baalebos(
            {
                "question": "Test",
                "language": "en",
                "rules": [],
                "evidence": [],
                "output_schema": {},
            }
        )
