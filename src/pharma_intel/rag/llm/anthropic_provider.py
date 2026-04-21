"""Anthropic Claude provider.

Optional backend, used for benchmarking ThaiLLM performance in the research
paper. Not required for normal operation.
"""

from __future__ import annotations

import anthropic

from pharma_intel.common import logger
from pharma_intel.rag.llm.base import LLMProvider, LLMResponse


class AnthropicProvider(LLMProvider):
    """Provider for Anthropic's Claude models."""

    def __init__(self, api_key: str, model: str = "claude-sonnet-4-6"):
        if not api_key:
            raise ValueError("Anthropic API key is required")
        self._client = anthropic.Anthropic(api_key=api_key)
        self.model = model

    @property
    def model_name(self) -> str:
        return self.model

    @property
    def provider_name(self) -> str:
        return "anthropic"

    def complete(
        self,
        system: str,
        user: str,
        max_tokens: int = 1500,
        temperature: float = 0.3,
    ) -> LLMResponse:
        logger.info(f"Calling Claude model={self.model}")
        response = self._client.messages.create(
            model=self.model,
            max_tokens=max_tokens,
            temperature=temperature,
            system=system,
            messages=[{"role": "user", "content": user}],
        )

        text = "\n".join(
            block.text for block in response.content if block.type == "text"
        )
        return LLMResponse(
            text=text,
            model=self.model,
            input_tokens=response.usage.input_tokens,
            output_tokens=response.usage.output_tokens,
            raw=None,
        )
