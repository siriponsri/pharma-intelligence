"""Factory that returns the configured LLM provider based on environment settings.

Use:
    from pharma_intel.rag.llm import get_llm
    llm = get_llm()
    response = llm.complete(system="...", user="...")

Switch providers by setting LLM_PROVIDER in .env:
    LLM_PROVIDER=thaillm    (default — sovereign Thai LLM)
    LLM_PROVIDER=anthropic  (Claude, for benchmarking)
"""

from __future__ import annotations

from pharma_intel.common import logger, settings
from pharma_intel.rag.llm.base import LLMProvider


def get_llm(override: str | None = None) -> LLMProvider:
    """Return an LLMProvider instance based on config or explicit override.

    Args:
        override: Force a specific provider regardless of settings.
                  Useful for benchmarking scripts that want to run both.
    """
    provider = (override or settings.llm_provider).lower().strip()
    logger.info(f"Initializing LLM provider: {provider}")

    if provider == "thaillm":
        from pharma_intel.rag.llm.thaillm_provider import ThaiLLMProvider

        return ThaiLLMProvider(
            api_key=settings.thaillm_api_key,
            base_url=settings.thaillm_base_url,
            model=settings.thaillm_model,
        )

    if provider == "anthropic":
        from pharma_intel.rag.llm.anthropic_provider import AnthropicProvider

        return AnthropicProvider(
            api_key=settings.anthropic_api_key,
            model=settings.claude_model,
        )

    raise ValueError(
        f"Unknown LLM provider: '{provider}'. "
        f"Supported: 'thaillm', 'anthropic'. "
        f"Set LLM_PROVIDER in .env."
    )
