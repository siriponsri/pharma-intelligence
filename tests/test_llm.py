"""Tests for LLM provider abstraction (no network calls)."""

from __future__ import annotations

import pytest

from pharma_intel.rag.llm.base import LLMProvider, LLMResponse


class TestLLMResponse:
    def test_response_construction(self):
        r = LLMResponse(text="hello", model="test-model")
        assert r.text == "hello"
        assert r.model == "test-model"
        assert r.input_tokens is None
        assert r.output_tokens is None

    def test_response_with_usage(self):
        r = LLMResponse(
            text="hello",
            model="test-model",
            input_tokens=10,
            output_tokens=5,
        )
        assert r.input_tokens == 10
        assert r.output_tokens == 5


class TestThaiLLMProvider:
    def test_requires_api_key(self):
        from pharma_intel.rag.llm.thaillm_provider import ThaiLLMProvider

        with pytest.raises(ValueError, match="API key"):
            ThaiLLMProvider(api_key="")

    def test_provider_metadata(self):
        from pharma_intel.rag.llm.thaillm_provider import ThaiLLMProvider

        p = ThaiLLMProvider(
            api_key="fake-key",
            base_url="https://example.com/api/v1",  # https so no warning in tests
            model="test-model",
        )
        assert p.provider_name == "thaillm"
        assert p.model_name == "test-model"


class TestAnthropicProvider:
    def test_requires_api_key(self):
        from pharma_intel.rag.llm.anthropic_provider import AnthropicProvider

        with pytest.raises(ValueError, match="API key"):
            AnthropicProvider(api_key="")


class TestFactory:
    def test_invalid_provider_raises(self, monkeypatch):
        # Force an invalid provider via override
        from pharma_intel.rag.llm import get_llm

        with pytest.raises(ValueError, match="Unknown LLM provider"):
            get_llm(override="nonexistent")

    def test_returns_llmprovider_instance(self, monkeypatch):
        from pharma_intel.rag.llm import get_llm

        # Set fake key so factory doesn't error on missing key
        monkeypatch.setenv("THAILLM_API_KEY", "fake-key")
        monkeypatch.setenv("THAILLM_BASE_URL", "https://example.com/api/v1")

        # Re-import settings to pick up env change
        from importlib import reload

        from pharma_intel.common import config

        reload(config)

        llm = get_llm(override="thaillm")
        assert isinstance(llm, LLMProvider)
        assert llm.provider_name == "thaillm"
