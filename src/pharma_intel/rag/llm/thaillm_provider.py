"""ThaiLLM provider (OpenThaiGPT / thaillm.or.th).

Thailand's sovereign LLM service. OpenAI-compatible chat completions endpoint
but uses 'apikey' header instead of 'Authorization: Bearer'.

Docs: http://thaillm.or.th (as of 2026-04)
Rate limits: 5 req/sec, 200 req/min (per issued API key)

⚠️ SECURITY NOTE: The documented endpoint uses HTTP (not HTTPS), meaning
API keys are transmitted in plaintext. For production deployment:
    - Never use over public/untrusted networks
    - Rotate keys frequently
    - Monitor for any HTTPS-enabled endpoint the service may publish
"""

from __future__ import annotations

import httpx

from pharma_intel.common import logger
from pharma_intel.rag.llm.base import LLMProvider, LLMResponse

DEFAULT_BASE_URL = "http://thaillm.or.th/api/v1"
DEFAULT_MODEL = "openthaigpt-thaillm-8b-instruct-v7.2"


class ThaiLLMProvider(LLMProvider):
    """Provider for the Thai government ThaiLLM service (OpenThaiGPT)."""

    def __init__(
        self,
        api_key: str,
        base_url: str = DEFAULT_BASE_URL,
        model: str = DEFAULT_MODEL,
        timeout: float = 60.0,
    ):
        if not api_key:
            raise ValueError("ThaiLLM API key is required")
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")
        self.model = model
        self.timeout = timeout
        self._client = httpx.Client(timeout=timeout)

        if base_url.startswith("http://"):
            logger.warning(
                "ThaiLLM endpoint uses HTTP (not HTTPS). "
                "API key will be transmitted unencrypted. "
                "Do not use on untrusted networks."
            )

    @property
    def model_name(self) -> str:
        return self.model

    @property
    def provider_name(self) -> str:
        return "thaillm"

    def complete(
        self,
        system: str,
        user: str,
        max_tokens: int = 1500,
        temperature: float = 0.3,
    ) -> LLMResponse:
        """Call ThaiLLM chat completions endpoint."""
        url = f"{self.base_url}/chat/completions"
        headers = {
            "Content-Type": "application/json",
            "apikey": self.api_key,
        }
        body = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
            "max_tokens": max_tokens,
            "temperature": temperature,
        }

        logger.info(f"Calling ThaiLLM model={self.model}")
        response = self._client.post(url, headers=headers, json=body)

        if response.status_code >= 400:
            logger.error(
                f"ThaiLLM API error {response.status_code}: {response.text[:500]}"
            )
            response.raise_for_status()

        data = response.json()

        # Standard OpenAI response shape
        try:
            text = data["choices"][0]["message"]["content"]
        except (KeyError, IndexError) as e:
            logger.error(f"Unexpected ThaiLLM response shape: {data}")
            raise RuntimeError(f"Could not parse ThaiLLM response: {e}") from e

        usage = data.get("usage", {})
        return LLMResponse(
            text=text,
            model=self.model,
            input_tokens=usage.get("prompt_tokens"),
            output_tokens=usage.get("completion_tokens"),
            raw=data,
        )

    def list_models(self) -> list[str]:
        """Query available models via GET /models (OpenAI-compatible)."""
        url = f"{self.base_url}/models"
        headers = {"apikey": self.api_key}
        response = self._client.get(url, headers=headers)
        response.raise_for_status()
        data = response.json()
        return [m.get("id", "") for m in data.get("data", [])]

    def __del__(self):
        try:
            self._client.close()
        except Exception:
            pass
