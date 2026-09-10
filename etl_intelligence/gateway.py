"""OpenAI-compatible client adapter for the portfolio Multi-LLM AI Gateway."""

from __future__ import annotations

import copy
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
        self.model = model or os.getenv("ETL_AI_MODEL") or "default"
        self.timeout_seconds = timeout_seconds
        self._observations: list[dict[str, Any]] = []
        if not self.base_url:
            raise ValueError("ETL_AI_GATEWAY_URL or base_url is required")

    def usage_observations(self) -> list[dict[str, Any]]:
        """Return Gateway usage/cost evidence without changing the analyzer callable contract."""
        return copy.deepcopy(self._observations)

    def clear_usage_observations(self) -> None:
        self._observations.clear()

    def __call__(
        self,
        system_prompt: str,
        context: str | dict[str, Any],
    ) -> dict[str, Any]:
        user_content = (
            context
            if isinstance(context, str)
            else json.dumps(context, ensure_ascii=False, sort_keys=True)
        )
        payload = {
            "model": self.model,
            "stream": False,
            "response_format": {"type": "json_object"},
            "messages": [
                {"role": "system", "content": system_prompt},
                {
                    "role": "user",
                    "content": user_content,
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

        self._observations.append(
            {
                "usage": copy.deepcopy(body.get("usage")) if isinstance(body, dict) else None,
                "gateway": copy.deepcopy(body.get("gateway")) if isinstance(body, dict) else None,
            }
        )

        try:
            content = body["choices"][0]["message"]["content"]
            return json.loads(content)
        except (KeyError, IndexError, TypeError, json.JSONDecodeError) as exc:
            raise ValueError("AI Gateway returned an invalid structured response") from exc
