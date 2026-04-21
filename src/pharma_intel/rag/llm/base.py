"""Abstract LLM provider interface.

All LLM backends (ThaiLLM, Claude, Typhoon, etc.) implement this interface
so the rest of the codebase can swap providers without changing business logic.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass
class LLMResponse:
    """Standardized response from any LLM provider."""

    text: str
    model: str
    input_tokens: int | None = None
    output_tokens: int | None = None
    raw: dict | None = None  # provider-specific raw response (for debugging)


class LLMProvider(ABC):
    """Abstract base for all LLM backends."""

    @property
    @abstractmethod
    def model_name(self) -> str:
        """Human-readable model identifier used in logs and output."""

    @property
    @abstractmethod
    def provider_name(self) -> str:
        """Short provider label: 'thaillm', 'anthropic', 'typhoon', etc."""

    @abstractmethod
    def complete(
        self,
        system: str,
        user: str,
        max_tokens: int = 1500,
        temperature: float = 0.3,
    ) -> LLMResponse:
        """Generate a completion given system + user messages.

        Implementations must:
            - Respect max_tokens and temperature
            - Raise on non-2xx HTTP responses
            - Populate input_tokens/output_tokens when the API provides them
        """
