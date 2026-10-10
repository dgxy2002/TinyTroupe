import configparser
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
