"""OpenAI-compatible client adapter for the portfolio Multi-LLM AI Gateway."""

from __future__ import annotations

import json
import os
from typing import Any
from urllib import error, request


class OpenAICompatibleGatewayClient:
    """Callable adapter accepted by SemanticAnalyzer.

    The gateway owns provider routing, fallback, authentication, cost governance and
    provider abstraction. This client only submits the evidence-filtered ETL context.
    """

    def __init__(
        self,
        base_url: str | None = None,
        api_key: str | None = None,
        model: str | None = None,
        timeout_seconds: float = 30.0,
    ):
        self.base_url = (base_url or os.getenv("ETL_AI_GATEWAY_URL") or "").rstrip("/")
        self.api_key = api_key or os.getenv("ETL_AI_GATEWAY_API_KEY")
        self.model = model or os.getenv("ETL_AI_MODEL") or "mock:etl-intelligence"
        self.timeout_seconds = timeout_seconds
        if not self.base_url:
            raise ValueError("ETL_AI_GATEWAY_URL or base_url is required")

    def __call__(self, system_prompt: str, context: dict[str, Any]) -> dict[str, Any]:
        payload = {
            "model": self.model,
            "stream": False,
            "response_format": {"type": "json_object"},
            "messages": [
                {"role": "system", "content": system_prompt},
                {
                    "role": "user",
                    "content": json.dumps(context, ensure_ascii=False, sort_keys=True),
                },
            ],
        }
        headers = {"Content-Type": "application/json"}
        if self.api_key:
            headers["X-API-Key"] = self.api_key
        req = request.Request(
            f"{self.base_url}/v1/chat/completions",
            data=json.dumps(payload).encode("utf-8"),
            headers=headers,
            method="POST",
        )
        try:
            with request.urlopen(req, timeout=self.timeout_seconds) as response:
                body = json.loads(response.read().decode("utf-8"))
        except (error.URLError, TimeoutError, json.JSONDecodeError) as exc:
            raise RuntimeError(f"AI Gateway request failed: {type(exc).__name__}") from exc

        try:
            content = body["choices"][0]["message"]["content"]
            return json.loads(content)
        except (KeyError, IndexError, TypeError, json.JSONDecodeError) as exc:
            raise ValueError("AI Gateway returned an invalid structured response") from exc
