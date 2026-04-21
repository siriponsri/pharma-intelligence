"""LLM provider abstraction — swap backends via LLM_PROVIDER env var."""

from pharma_intel.rag.llm.base import LLMProvider, LLMResponse
from pharma_intel.rag.llm.factory import get_llm

__all__ = ["LLMProvider", "LLMResponse", "get_llm"]
