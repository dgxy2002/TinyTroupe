import copy
import os
import threading
import time

import httpx
from openai import OpenAI

from tinytroupe import config_manager
from tinytroupe.clients.openai_client import OpenAIClient


class OpenRouterClient(OpenAIClient):
    """OpenAI-compatible client configured for the OpenRouter API."""

    def __init__(self, *args, **kwargs):
        self._call_records = []
        self._call_records_lock = threading.RLock()
        self._openrouter_base_url = "https://openrouter.ai/api/v1"
        super().__init__(*args, **kwargs)

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

        self._openrouter_base_url = (
            base_url or "https://openrouter.ai/api/v1"
        ).rstrip("/")
        client_options = {
            "api_key": api_key,
            "base_url": self._openrouter_base_url,
            "max_retries": 0,
            "http_client": httpx_client,
        }
        if default_headers:
            client_options["default_headers"] = default_headers

        self.client = OpenAI(**client_options)

    def _raw_model_call(self, model, chat_api_params):
        """Make a chat call and retain its server-reported usage metadata."""

        started = time.perf_counter()
        try:
            response = super()._raw_model_call(model, chat_api_params)
        except Exception as exc:
            # Structured-output parsers can raise after OpenRouter has already
            # completed and billed the generation (for example, when the model
            # reaches its length limit). Preserve that response so failed
            # attempts are included in experiment cost and token totals.
            failed_response = getattr(exc, "completion", None)
            if failed_response is not None:
                self._record_response(
                    failed_response,
                    kind="chat",
                    requested_model=model,
                    local_latency_ms=(time.perf_counter() - started) * 1000,
                    call_error=f"{type(exc).__name__}: {exc}",
                )
                self._update_cost_stats(failed_response, was_cached=False)
            raise
        self._record_response(
            response,
            kind="chat",
            requested_model=model,
            local_latency_ms=(time.perf_counter() - started) * 1000,
        )
        return response

    def _raw_embedding_model_call(self, text, model):
        """Set up OpenRouter for standalone embedding calls and track usage."""

        self._setup_from_config()
        started = time.perf_counter()
        response = self.client.embeddings.create(input=[text], model=model)
        self._record_response(
            response,
            kind="embedding",
            requested_model=model,
            local_latency_ms=(time.perf_counter() - started) * 1000,
        )
        # OpenAIClient.get_embedding does not update its aggregate counters.
        self._update_cost_stats(response, was_cached=False)
        return response

    @staticmethod
    def _attribute(value, name, default=None):
        if value is None:
            return default
        if isinstance(value, dict):
            return value.get(name, default)
        return getattr(value, name, default)

    def _record_response(
        self,
        response,
        *,
        kind,
        requested_model,
        local_latency_ms,
        call_error=None,
    ):
        usage = self._attribute(response, "usage")
        completion_details = self._attribute(usage, "completion_tokens_details")
        output_details = self._attribute(usage, "output_tokens_details")
        input_tokens = self._attribute(
            usage, "prompt_tokens", self._attribute(usage, "input_tokens", 0)
        ) or 0
        output_tokens = self._attribute(
            usage, "completion_tokens", self._attribute(usage, "output_tokens", 0)
        ) or 0
        reasoning_tokens = self._attribute(
            completion_details,
            "reasoning_tokens",
            self._attribute(output_details, "reasoning_tokens", 0),
        ) or 0
        direct_cost = self._attribute(usage, "cost")
        record = {
            "sequence": 0,
            "generation_id": self._attribute(response, "id"),
            "kind": kind,
            "requested_model": requested_model,
            "response_model": self._attribute(response, "model"),
            "input_tokens": int(input_tokens),
            "output_tokens": int(output_tokens),
            "reasoning_tokens": int(reasoning_tokens),
            "total_tokens": int(
                self._attribute(usage, "total_tokens", input_tokens + output_tokens)
                or 0
            ),
            "local_latency_ms": round(local_latency_ms, 3),
            "cost_usd": float(direct_cost) if direct_cost is not None else None,
            "provider_name": None,
            "provider_latency_ms": None,
            "metadata_status": (
                "cost_from_response" if direct_cost is not None else "pending"
            ),
            "metadata_error": None,
            "request_status": "failed" if call_error else "completed",
            "call_error": call_error,
        }
        with self._call_records_lock:
            record["sequence"] = len(self._call_records)
            self._call_records.append(record)

    def get_call_records(self, start=0, end=None):
        """Return a defensive copy of per-call resource records."""

        with self._call_records_lock:
            return copy.deepcopy(self._call_records[slice(start, end)])

    def reset_call_records(self):
        with self._call_records_lock:
            self._call_records.clear()

    def restore_call_records(self, records):
        """Restore previously checkpointed usage records for a resumed run."""

        restored = copy.deepcopy(list(records))
        for sequence, record in enumerate(restored):
            if not isinstance(record, dict):
                raise TypeError("Each restored OpenRouter call record must be a dict.")
            record["sequence"] = sequence
        with self._call_records_lock:
            self._call_records = restored

    def reset_usage_tracking(self):
        """Reset both legacy aggregate counters and detailed call records."""

        self.reset_cost_stats()
        self.reset_call_records()

    def enrich_call_records(self, start=0, end=None, *, max_attempts=3):
        """Fetch exact cost/provider metadata from OpenRouter's generation API.

        OpenRouter may need a short interval before generation metadata is
        queryable, so incomplete records are retried. Failures are recorded and
        returned rather than hiding missing billing observations.
        """

        api_key = os.getenv("OPENROUTER_API_KEY")
        if not api_key:
            raise ValueError("OPENROUTER_API_KEY is required to fetch generation metadata.")

        with self._call_records_lock:
            upper = len(self._call_records) if end is None else min(end, len(self._call_records))
            indexes = list(range(start, upper))

        headers = {"Authorization": f"Bearer {api_key}"}
        endpoint = f"{self._openrouter_base_url}/generation"
        with httpx.Client(timeout=30.0, headers=headers) as metadata_client:
            for index in indexes:
                with self._call_records_lock:
                    generation_id = self._call_records[index].get("generation_id")
                    already_complete = (
                        self._call_records[index].get("metadata_status") == "complete"
                    )
                if already_complete:
                    continue
                if not generation_id:
                    self._set_metadata_error(index, "missing_generation_id")
                    continue

                error = None
                data = None
                for attempt in range(max_attempts):
                    try:
                        response = metadata_client.get(
                            endpoint, params={"id": generation_id}
                        )
                        response.raise_for_status()
                        payload = response.json()
                        data = payload.get("data", payload)
                        if data:
                            break
                        error = "empty_metadata_response"
                    except Exception as exc:  # metadata must not erase a valid run
                        error = f"{type(exc).__name__}: {exc}"
                    if attempt + 1 < max_attempts:
                        time.sleep(0.5 * (attempt + 1))

                if not data:
                    self._set_metadata_error(index, error or "metadata_unavailable")
                    continue

                native_input = data.get("native_tokens_prompt")
                native_output = data.get("native_tokens_completion")
                native_reasoning = data.get("native_tokens_reasoning")
                latency = data.get("latency")
                with self._call_records_lock:
                    record = self._call_records[index]
                    if native_input is not None:
                        record["input_tokens"] = int(native_input)
                    if native_output is not None:
                        record["output_tokens"] = int(native_output)
                    if native_reasoning is not None:
                        record["reasoning_tokens"] = int(native_reasoning)
                    record["total_tokens"] = (
                        record["input_tokens"] + record["output_tokens"]
                    )
                    if data.get("total_cost") is not None:
                        record["cost_usd"] = float(data["total_cost"])
                    record["provider_name"] = data.get("provider_name")
                    record["provider_latency_ms"] = (
                        float(latency) if latency is not None else None
                    )
                    record["metadata_status"] = (
                        "complete" if record["cost_usd"] is not None else "partial"
                    )
                    record["metadata_error"] = None

        return self.get_call_records(start, end)

    def _set_metadata_error(self, index, error):
        with self._call_records_lock:
            self._call_records[index]["metadata_status"] = "unavailable"
            self._call_records[index]["metadata_error"] = error
