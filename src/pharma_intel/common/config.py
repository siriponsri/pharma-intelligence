"""Centralized config loaded from environment variables via pydantic-settings."""

from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Global settings. Values come from .env or OS environment."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # ============ LLM provider selection ============
    # Supported: 'thaillm' (default, sovereign) | 'anthropic' (benchmark)
    llm_provider: str = Field(default="thaillm", alias="LLM_PROVIDER")

    # ThaiLLM (OpenThaiGPT) — primary
    thaillm_api_key: str = Field(default="", alias="THAILLM_API_KEY")
    thaillm_base_url: str = Field(
        default="http://thaillm.or.th/api/v1", alias="THAILLM_BASE_URL"
    )
    thaillm_model: str = Field(
        default="openthaigpt-thaillm-8b-instruct-v7.2", alias="THAILLM_MODEL"
    )

    # Anthropic Claude — optional for benchmarking
    anthropic_api_key: str = Field(default="", alias="ANTHROPIC_API_KEY")
    claude_model: str = Field(default="claude-sonnet-4-6", alias="CLAUDE_MODEL")

    # ============ Paths ============
    data_dir: Path = Field(default=Path("./data"), alias="DATA_DIR")
    chroma_persist_dir: Path = Field(default=Path("./chroma_db"), alias="CHROMA_PERSIST_DIR")
    model_cache_dir: Path = Field(default=Path("./.cache/models"), alias="MODEL_CACHE_DIR")

    # ============ Embedding model ============
    embedding_model: str = Field(default="BAAI/bge-m3", alias="EMBEDDING_MODEL")

    # ============ Logging ============
    log_level: str = Field(default="INFO", alias="LOG_LEVEL")

    @property
    def raw_dir(self) -> Path:
        return self.data_dir / "raw"

    @property
    def processed_dir(self) -> Path:
        return self.data_dir / "processed"

    @property
    def interim_dir(self) -> Path:
        return self.data_dir / "interim"

    def ensure_dirs(self) -> None:
        """Create all data directories if they don't exist."""
        for d in [self.raw_dir, self.processed_dir, self.interim_dir, self.chroma_persist_dir]:
            d.mkdir(parents=True, exist_ok=True)


# Singleton instance — import this everywhere
settings = Settings()
