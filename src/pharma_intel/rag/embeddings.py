"""Embedding model wrapper.

Uses sentence-transformers with BAAI/bge-m3 by default (bilingual Thai+English SOTA).
For faster local dev, set EMBEDDING_MODEL env var to a smaller model like
`sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2`.
"""

from __future__ import annotations

from functools import lru_cache

from sentence_transformers import SentenceTransformer

from pharma_intel.common import logger, settings


@lru_cache(maxsize=1)
def get_embedder() -> SentenceTransformer:
    """Load embedding model (cached — first call downloads the model)."""
    logger.info(f"Loading embedding model: {settings.embedding_model}")
    logger.info(
        "First run will download the model (~2GB for bge-m3). Subsequent runs use cache."
    )
    model = SentenceTransformer(
        settings.embedding_model,
        cache_folder=str(settings.model_cache_dir),
    )
    logger.info(f"Embedding dim: {model.get_sentence_embedding_dimension()}")
    return model


def embed_texts(texts: list[str], batch_size: int = 32) -> list[list[float]]:
    """Embed a list of texts and return vectors as lists of floats."""
    model = get_embedder()
    logger.info(f"Embedding {len(texts)} texts (batch_size={batch_size})...")
    embeddings = model.encode(
        texts,
        batch_size=batch_size,
        show_progress_bar=True,
        normalize_embeddings=True,  # cosine-ready
        convert_to_numpy=True,
    )
    return embeddings.tolist()


def embed_query(query: str) -> list[float]:
    """Embed a single query (convenience wrapper)."""
    return embed_texts([query])[0]
