import configparser
from types import SimpleNamespace
from unittest.mock import patch

import pytest

from tinytroupe.clients.openrouter_client import OpenRouterClient
from tinytroupe.utils.config import _apply_environment_overrides


def _base_config():
    config = configparser.ConfigParser()
    config["OpenAI"] = {
        "API_TYPE": "openai",
        "MODEL": "gpt-4o",
        "EMBEDDING_MODEL": "text-embedding-3-small",
    }
    return config


def test_openrouter_environment_overrides(monkeypatch):
    monkeypatch.setenv("TINY_TROUPE_API_TYPE", "openrouter")
    monkeypatch.setenv("OPENROUTER_MODEL", "openai/gpt-5-mini")
    monkeypatch.setenv(
        "OPENROUTER_EMBEDDING_MODEL", "openai/text-embedding-3-small"
    )

    config = _apply_environment_overrides(_base_config())

    assert config["OpenAI"]["API_TYPE"] == "openrouter"
    assert config["OpenAI"]["MODEL"] == "openai/gpt-5-mini"
    assert config["OpenAI"]["EMBEDDING_MODEL"] == "openai/text-embedding-3-small"
    assert config["OpenAI"]["BASE_URL"] == "https://openrouter.ai/api/v1"


@patch("tinytroupe.clients.openrouter_client.OpenAI")
def test_openrouter_client_uses_key_endpoint_and_headers(mock_openai, monkeypatch):
    monkeypatch.setenv("OPENROUTER_API_KEY", "test-key")
    monkeypatch.setenv("OPENROUTER_SITE_URL", "https://example.test")
    monkeypatch.setenv("OPENROUTER_APP_NAME", "TinyTroupe Test")
    client = OpenRouterClient(cache_api_calls=False)

    client._setup_from_config(
        timeout=30, base_url="https://openrouter.ai/api/v1"
    )

    options = mock_openai.call_args.kwargs
    assert options["api_key"] == "test-key"
    assert options["base_url"] == "https://openrouter.ai/api/v1"
    assert options["max_retries"] == 0
    assert options["default_headers"] == {
        "HTTP-Referer": "https://example.test",
        "X-Title": "TinyTroupe Test",
    }


def test_openrouter_client_requires_key(monkeypatch):
    monkeypatch.delenv("OPENROUTER_API_KEY", raising=False)
    client = OpenRouterClient(cache_api_calls=False)

    with pytest.raises(ValueError, match="OPENROUTER_API_KEY"):
        client._setup_from_config(timeout=30)


def test_openrouter_client_tracks_per_call_tokens_cost_and_latency():
    openrouter = OpenRouterClient(cache_api_calls=False)
    response = SimpleNamespace(
        id="generation-123",
        model="openai/gpt-5-mini",
        usage=SimpleNamespace(
            prompt_tokens=100,
            completion_tokens=25,
            total_tokens=125,
            cost=0.00125,
            completion_tokens_details=SimpleNamespace(reasoning_tokens=7),
        ),
    )

    openrouter._record_response(
        response,
        kind="chat",
        requested_model="openai/gpt-5-mini",
        local_latency_ms=42.5,
    )

    records = openrouter.get_call_records()
    assert records == [
        {
            "sequence": 0,
            "generation_id": "generation-123",
            "kind": "chat",
            "requested_model": "openai/gpt-5-mini",
            "response_model": "openai/gpt-5-mini",
            "input_tokens": 100,
            "output_tokens": 25,
            "reasoning_tokens": 7,
            "total_tokens": 125,
            "local_latency_ms": 42.5,
            "cost_usd": 0.00125,
            "provider_name": None,
            "provider_latency_ms": None,
            "metadata_status": "cost_from_response",
            "metadata_error": None,
            "request_status": "completed",
            "call_error": None,
        }
    ]

    records[0]["input_tokens"] = 0
    assert openrouter.get_call_records()[0]["input_tokens"] == 100

    openrouter.reset_usage_tracking()
    assert openrouter.get_call_records() == []


def test_openrouter_client_tracks_billed_response_when_parser_raises():
    openrouter = OpenRouterClient(cache_api_calls=False)
    response = SimpleNamespace(
        id="generation-length-limited",
        model="openai/gpt-5-mini",
        usage=SimpleNamespace(
            prompt_tokens=50,
            completion_tokens=100,
            total_tokens=150,
            cost=0.004,
            completion_tokens_details=SimpleNamespace(reasoning_tokens=90),
        ),
    )

    class BilledParserError(Exception):
        def __init__(self):
            self.completion = response
            super().__init__("length limit reached")

    with patch(
        "tinytroupe.clients.openrouter_client.OpenAIClient._raw_model_call",
        side_effect=BilledParserError(),
    ):
        with pytest.raises(BilledParserError):
            openrouter._raw_model_call("openai/gpt-5-mini", {})

    record = openrouter.get_call_records()[0]
    assert record["request_status"] == "failed"
    assert record["cost_usd"] == 0.004
    assert record["reasoning_tokens"] == 90
    assert "length limit reached" in record["call_error"]
    assert openrouter.get_cost_stats()["total_tokens"] == 150
