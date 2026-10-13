"""Groq synthesis must remain grounded, opt-in and fail closed."""

import pytest

from app.core.config import settings
from app.services.ask_synthesizer import (
    _call_groq,
    get_grounded_synthesizer,
)


def test_synthesis_disabled_returns_no_generator(monkeypatch):
    monkeypatch.setattr(
        settings,
        "ASK_EKITI_SYNTHESIS_ENABLED",
        False,
    )

    assert get_grounded_synthesizer() is None


def test_enabled_groq_requires_api_key(monkeypatch):
    monkeypatch.setattr(
        settings,
        "ASK_EKITI_SYNTHESIS_ENABLED",
        True,
    )
    monkeypatch.setattr(
        settings,
        "ASK_EKITI_LLM_PROVIDER",
        "groq",
    )
    monkeypatch.setattr(
        settings,
        "GROQ_API_KEY",
        None,
    )

    with pytest.raises(RuntimeError, match="GROQ_API_KEY"):
        get_grounded_synthesizer()


def test_enabled_groq_returns_generator(monkeypatch):
    monkeypatch.setattr(
        settings,
        "ASK_EKITI_SYNTHESIS_ENABLED",
        True,
    )
    monkeypatch.setattr(
        settings,
        "ASK_EKITI_LLM_PROVIDER",
        "groq",
    )
    monkeypatch.setattr(
        settings,
        "GROQ_API_KEY",
        "test-key",
    )

    assert callable(get_grounded_synthesizer())


def test_baalebos_provider_is_suspended(monkeypatch):
    monkeypatch.setattr(
        settings,
        "ASK_EKITI_SYNTHESIS_ENABLED",
        True,
    )
    monkeypatch.setattr(
        settings,
        "ASK_EKITI_LLM_PROVIDER",
        "baalebos",
    )

    with pytest.raises(RuntimeError, match="temporarily suspended"):
        get_grounded_synthesizer()


def test_groq_request_and_response_contract(monkeypatch):
    captured = {}

    class FakeResponse:
        def raise_for_status(self):
            return None

        def json(self):
            return {
                "choices": [
                    {
                        "message": {
                            "role": "assistant",
                            "content": (
                                '{"statements":['
                                '{"text":"Ekiti State was created '
                                'on 1 October 1996.",'
                                '"citations":[1]}]}'
                            ),
                        }
                    }
                ]
            }

    def fake_post(url, *, headers, json, timeout):
        captured["url"] = url
        captured["headers"] = headers
        captured["body"] = json
        captured["timeout"] = timeout
        return FakeResponse()

    monkeypatch.setattr(settings, "GROQ_API_KEY", "secret")
    monkeypatch.setattr(
        settings,
        "GROQ_API_URL",
        "https://api.groq.com/openai/v1/chat/completions",
    )
    monkeypatch.setattr(
        "app.services.ask_synthesizer.httpx.post",
        fake_post,
    )

    result = _call_groq(
        {
            "question": "When was Ekiti State created?",
            "language": "en",
            "rules": [],
            "evidence": [
                {
                    "id": 1,
                    "fact": (
                        "Ekiti State was created "
                        "on 1 October 1996."
                    ),
                }
            ],
            "output_schema": {},
        }
    )

    assert captured["headers"]["Authorization"] == "Bearer secret"
    assert captured["body"]["model"] == settings.GROQ_SYNTHESIS_MODEL
    assert captured["body"]["response_format"] == {
        "type": "json_object"
    }
    assert "Use ONLY the evidence" in (
        captured["body"]["messages"][0]["content"]
    )

    assert result["statements"][0]["citations"] == [1]
    assert "secret" not in str(result)


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
    assert "1 October 1996. [1]" in payload["answer"]


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

    monkeypatch.setattr(
        ask_ekiti,
        "get_grounded_synthesizer",
        lambda: (
            lambda packet: {
                "statements": [
                    {
                        "text": "Unsupported generated claim.",
                        "citations": [99],
                    }
                ]
            }
        ),
    )

    response = client.post(
        "/api/ask-ekiti",
        json={
            "question": "When was Ekiti State created?",
            "language": "en",
        },
    )

    payload = response.json()

    assert payload["synthesis_mode"] == "fallback"
    assert "Unsupported generated claim" not in payload["answer"]
    assert "1 October 1996. [1]" in payload["answer"]


def test_current_question_does_not_use_model_memory(monkeypatch):
    from app.services.ask_synthesizer import answer_general_ekiti

    monkeypatch.setattr(settings, "GROQ_API_KEY", "secret")

    def forbidden(*args, **kwargs):
        pytest.fail("Current question must not call Groq model memory")

    monkeypatch.setattr(
        "app.services.ask_synthesizer.httpx.post",
        forbidden,
    )

    result = answer_general_ekiti(
        "Who is the current governor of Ekiti?",
        "en",
    )

    assert result["status"] == "needs_current_source"


def test_general_ekiti_fallback_supports_yoruba(monkeypatch):
    from app.services.ask_synthesizer import answer_general_ekiti

    captured = {}

    class FakeResponse:
        def raise_for_status(self):
            return None

        def json(self):
            return {
                "choices": [
                    {
                        "message": {
                            "content": (
                                '{"status":"answered",'
                                '"answer":"Èkìtì ní àṣà ọlọ́rọ̀."}'
                            )
                        }
                    }
                ]
            }

    def fake_post(url, *, headers, json, timeout):
        captured["body"] = json
        return FakeResponse()

    monkeypatch.setattr(settings, "GROQ_API_KEY", "secret")
    monkeypatch.setattr(
        "app.services.ask_synthesizer.httpx.post",
        fake_post,
    )

    result = answer_general_ekiti(
        "Sọ fún mi nípa àṣà Èkìtì.",
        "yo",
    )

    assert result["status"] == "answered"
    assert "Èkìtì" in result["answer"]
    assert "Standard Yoruba" in (
        captured["body"]["messages"][0]["content"]
    )


def test_api_uses_general_ekiti_fallback_when_kb_has_no_match(
    client,
    monkeypatch,
):
    from app.api.routes import ask_ekiti

    monkeypatch.setattr(
        settings,
        "ASK_EKITI_GENERAL_FALLBACK_ENABLED",
        True,
    )

    # This test exercises the legacy/model-memory fallback behavior.
    # Web research is tested separately and must not depend on the
    # developer's active shell environment.
    monkeypatch.setattr(
        settings,
        "ASK_EKITI_WEB_RESEARCH_ENABLED",
        False,
    )

    monkeypatch.setattr(
        ask_ekiti,
        "get_grounded_synthesizer",
        lambda: None,
    )

    monkeypatch.setattr(
        ask_ekiti,
        "retrieve",
        lambda *args, **kwargs: [],
    )

    monkeypatch.setattr(
        ask_ekiti,
        "answer_general_ekiti",
        lambda question, language: {
            "status": "answered",
            "answer": (
                "Ekiti has a strong tradition of arts and festivals."
            ),
        },
    )

    response = client.post(
        "/api/ask-ekiti",
        json={
            "question": "Tell me about arts in Ekiti.",
            "language": "en",
        },
    )

    assert response.status_code == 200

    payload = response.json()

    assert payload["answer_status"] == "answered"
    assert payload["coverage"] == "general_ai"
    assert payload["reason"] == "general_ekiti_fallback"
    assert payload["synthesis_mode"] == "general"
    assert payload["citations"] == []
    assert payload["general_ai"] is True


def test_api_rejects_irrelevant_generic_kb_hits_and_uses_fallback(
    client,
    monkeypatch,
):
    from app.api.routes import ask_ekiti

    monkeypatch.setattr(
        settings,
        "ASK_EKITI_GENERAL_FALLBACK_ENABLED",
        True,
    )

    # This test exercises the legacy/model-memory fallback behavior.
    # Web research is tested separately and must not depend on the
    # developer's active shell environment.
    monkeypatch.setattr(
        settings,
        "ASK_EKITI_WEB_RESEARCH_ENABLED",
        False,
    )

    monkeypatch.setattr(
        ask_ekiti,
        "get_grounded_synthesizer",
        lambda: None,
    )

    monkeypatch.setattr(
        ask_ekiti,
        "retrieve",
        lambda *args, **kwargs: [_creation_hit()],
    )

    monkeypatch.setattr(
        ask_ekiti,
        "answer_general_ekiti",
        lambda question, language: {
            "status": "answered",
            "answer": "Ekiti contains several geological rock formations.",
        },
    )

    response = client.post(
        "/api/ask-ekiti",
        json={
            "question": "What are the major rock types found in Ekiti State?",
            "language": "en",
        },
    )

    assert response.status_code == 200

    payload = response.json()

    assert payload["synthesis_mode"] == "general"
    assert payload["coverage"] == "general_ai"
    assert payload["reason"] == "general_ekiti_fallback"
    assert payload["citations"] == []


def test_api_current_question_requires_fresh_source(
    client,
    monkeypatch,
):
    from app.api.routes import ask_ekiti

    monkeypatch.setattr(
        settings,
        "ASK_EKITI_GENERAL_FALLBACK_ENABLED",
        True,
    )

    # This test exercises the legacy/model-memory fallback behavior.
    # Web research is tested separately and must not depend on the
    # developer's active shell environment.
    monkeypatch.setattr(
        settings,
        "ASK_EKITI_WEB_RESEARCH_ENABLED",
        False,
    )

    monkeypatch.setattr(
        ask_ekiti,
        "get_grounded_synthesizer",
        lambda: None,
    )

    def retrieval_must_not_run(*args, **kwargs):
        pytest.fail(
            "Current-information question must not use static KB retrieval"
        )

    monkeypatch.setattr(
        ask_ekiti,
        "retrieve",
        retrieval_must_not_run,
    )

    monkeypatch.setattr(
        ask_ekiti,
        "answer_general_ekiti",
        lambda question, language: {
            "status": "needs_current_source",
            "answer": (
                "This question requires a current verifiable source "
                "before it can be answered."
            ),
        },
    )

    response = client.post(
        "/api/ask-ekiti",
        json={
            "question": (
                "What major government projects are currently "
                "ongoing in Ekiti?"
            ),
            "language": "en",
        },
    )

    assert response.status_code == 200

    payload = response.json()

    assert payload["reason"] == "needs_current_source"
    assert payload["citations"] == []


def test_web_research_uses_browser_search(monkeypatch):
    from app.services.ask_synthesizer import answer_web_researched

    requests = []

    class FakeResponse:
        def __init__(self, payload):
            self._payload = payload

        def raise_for_status(self):
            return None

        def json(self):
            return self._payload

    def fake_post(url, *, headers, json, timeout):
        requests.append(json)

        # First request: browser research.
        if "tools" in json:
            return FakeResponse(
                {
                    "choices": [
                        {
                            "message": {
                                "content": "Untrusted first-pass prose.",
                                "executed_tools": [
                                    {
                                        "type": "browser.open",
                                        "search_results": {
                                            "results": [
                                                {
                                                    "title": (
                                                        "Office of the Governor"
                                                    ),
                                                    "url": (
                                                        "https://www."
                                                        "ekitistate.gov.ng/"
                                                        "governor"
                                                    ),
                                                    "content": (
                                                        "Abiodun Abayomi "
                                                        "Oyebanji is profiled "
                                                        "by the Office of the "
                                                        "Governor."
                                                    ),
                                                }
                                            ]
                                        },
                                    }
                                ],
                            }
                        }
                    ]
                }
            )

        # Second request: structured grounded synthesis.
        return FakeResponse(
            {
                "choices": [
                    {
                        "message": {
                            "content": (
                                '{"statements":['
                                '{"text":"Abiodun Abayomi Oyebanji '
                                'is profiled by the Office of the '
                                'Governor.",'
                                '"citations":[1]}]}'
                            )
                        }
                    }
                ]
            }
        )

    monkeypatch.setattr(settings, "GROQ_API_KEY", "secret")
    monkeypatch.setattr(
        "app.services.ask_synthesizer.httpx.post",
        fake_post,
    )

    result = answer_web_researched(
        "Who is Biodun Oyebanji in Ekiti?",
        "en",
    )

    assert result["status"] == "answered"
    assert "Oyebanji" in result["answer"]
    assert result["used_citations"] == [1]
    assert result["citations"][0]["source_urls"] == [
        "https://www.ekitistate.gov.ng/governor"
    ]

    assert len(requests) == 2

    browser_body = requests[0]
    grounded_body = requests[1]

    assert browser_body["tools"] == [
        {"type": "browser_search"}
    ]
    assert browser_body["tool_choice"] == "required"
    assert "response_format" not in browser_body

    # The second call must not browse again. It receives only the evidence
    # retrieved by the first call and returns structured JSON.
    assert "tools" not in grounded_body
    assert grounded_body["response_format"] == {
        "type": "json_object"
    }



def test_api_uses_web_research_when_kb_has_no_match(
    client,
    monkeypatch,
):
    from app.api.routes import ask_ekiti

    monkeypatch.setattr(
        settings,
        "ASK_EKITI_WEB_RESEARCH_ENABLED",
        True,
    )
    monkeypatch.setattr(
        settings,
        "ASK_EKITI_GENERAL_FALLBACK_ENABLED",
        True,
    )

    monkeypatch.setattr(
        ask_ekiti,
        "get_grounded_synthesizer",
        lambda: None,
    )

    monkeypatch.setattr(
        ask_ekiti,
        "retrieve",
        lambda *args, **kwargs: [],
    )

    monkeypatch.setattr(
        ask_ekiti,
        "answer_web_researched",
        lambda question, language: {
            "status": "answered",
            "answer": (
                "Web researched Ekiti answer. 〖1†L1-L4〗"
            ),
        },
    )

    response = client.post(
        "/api/ask-ekiti",
        json={
            "question": "Who is Biodun Oyebanji in Ekiti?",
            "language": "en",
        },
    )

    assert response.status_code == 200

    payload = response.json()

    assert payload["coverage"] == "web_researched"
    assert payload["reason"] == "web_research_fallback"
    assert payload["synthesis_mode"] == "web"
    assert payload["web_researched"] is True
    assert payload["general_ai"] is False
    assert payload["citations"] == []


def test_web_research_takes_priority_over_general_ai(
    client,
    monkeypatch,
):
    from app.api.routes import ask_ekiti

    monkeypatch.setattr(
        settings,
        "ASK_EKITI_WEB_RESEARCH_ENABLED",
        True,
    )
    monkeypatch.setattr(
        settings,
        "ASK_EKITI_GENERAL_FALLBACK_ENABLED",
        True,
    )

    monkeypatch.setattr(
        ask_ekiti,
        "get_grounded_synthesizer",
        lambda: None,
    )

    monkeypatch.setattr(
        ask_ekiti,
        "retrieve",
        lambda *args, **kwargs: [],
    )

    monkeypatch.setattr(
        ask_ekiti,
        "answer_web_researched",
        lambda question, language: {
            "status": "answered",
            "answer": "Fresh researched answer.",
        },
    )

    def general_must_not_run(*args, **kwargs):
        pytest.fail(
            "General model-memory fallback must not run "
            "when web research is enabled"
        )

    monkeypatch.setattr(
        ask_ekiti,
        "answer_general_ekiti",
        general_must_not_run,
    )

    response = client.post(
        "/api/ask-ekiti",
        json={
            "question": "Tell me about an Ekiti public figure.",
            "language": "en",
        },
    )

    assert response.status_code == 200
    assert response.json()["synthesis_mode"] == "web"


def test_web_source_title_uses_actual_page_title():
    from app.services.ask_synthesizer import _clean_web_source_title

    title = (
        "www.ekitistate.gov.ng - viewing lines "
        "[0 - 96] of 96"
    )

    content = (
        "L0: \n"
        "L1: URL: https://www.ekitistate.gov.ng/example\n"
        "L2: Office of the Governor – Ekiti State Government Website\n"
        "L3: \n"
        "L4: # Office of the Governor"
    )

    result = _clean_web_source_title(
        title,
        content,
        "https://www.ekitistate.gov.ng/example",
    )

    assert result == (
        "Office of the Governor – Ekiti State Government Website"
    )
