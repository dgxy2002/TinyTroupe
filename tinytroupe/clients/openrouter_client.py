import os

import httpx
from openai import OpenAI

from tinytroupe import config_manager
from tinytroupe.clients.openai_client import OpenAIClient


class OpenRouterClient(OpenAIClient):
    """OpenAI-compatible client configured for the OpenRouter API."""

    @config_manager.config_defaults(timeout="timeout", base_url="base_url")
    def _setup_from_config(self, timeout=None, base_url=None):
        api_key = os.getenv("OPENROUTER_API_KEY")
        if not api_key:
            raise ValueError(
                "OPENROUTER_API_KEY is required when API_TYPE is 'openrouter'."
            )

        httpx_client = httpx.Client(
            timeout=httpx.Timeout(
                timeout=timeout,
                connect=10.0,
                read=timeout,
                write=10.0,
                pool=5.0,
            )
        )

        default_headers = {}
        if site_url := os.getenv("OPENROUTER_SITE_URL"):
            default_headers["HTTP-Referer"] = site_url
        if app_name := os.getenv("OPENROUTER_APP_NAME"):
            default_headers["X-Title"] = app_name

        client_options = {
            "api_key": api_key,
            "base_url": base_url or "https://openrouter.ai/api/v1",
            "max_retries": 0,
            "http_client": httpx_client,
        }
        if default_headers:
            client_options["default_headers"] = default_headers

        self.client = OpenAI(**client_options)
