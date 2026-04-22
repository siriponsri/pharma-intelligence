"""Hybrid retrieval utilities built on top of the dense vector store."""

from __future__ import annotations

import re

from pharma_intel.rag.embeddings import embed_query
from pharma_intel.rag.vectorstore import RetrievedChunk, VectorStore


def _tokenize(text: str) -> set[str]:
    """Convert text into a normalized token set."""
    return set(re.findall(r"[\w-]+", text.lower()))


def lexical_overlap_score(query: str, text: str) -> float:
    """Score a document by normalized token overlap with the query."""
    query_tokens = _tokenize(query)
    if not query_tokens:
        return 0.0
    text_tokens = _tokenize(text)
    return len(query_tokens & text_tokens) / len(query_tokens)


def rerank_dense_candidates(
    query: str,
    candidates: list[RetrievedChunk],
    top_k: int = 5,
    dense_weight: float = 0.7,
) -> list[RetrievedChunk]:
    """Combine dense similarity with lexical overlap over the retrieved candidates."""
    reranked: list[RetrievedChunk] = []
    for chunk in candidates:
        metadata_text = " ".join(str(value) for value in chunk.metadata.values())
        lexical_score = lexical_overlap_score(query, f"{chunk.text} {metadata_text}")
        hybrid_score = (dense_weight * chunk.score) + ((1.0 - dense_weight) * lexical_score)
        reranked.append(
            RetrievedChunk(
                doc_id=chunk.doc_id,
                text=chunk.text,
                metadata=chunk.metadata,
                score=hybrid_score,
            )
        )
    return sorted(reranked, key=lambda chunk: chunk.score, reverse=True)[:top_k]


def hybrid_retrieve(
    query: str,
    top_k: int = 5,
    dense_k: int = 12,
    where: dict | None = None,
    store: VectorStore | None = None,
    collection_name: str = "cardiometabolic_drugs",
) -> list[RetrievedChunk]:
    """Retrieve dense candidates and rerank them with lexical overlap."""
    vector_store = store or VectorStore(collection_name=collection_name)
    dense_candidates = vector_store.query(
        query_embedding=embed_query(query),
        k=dense_k,
        where=where,
    )
    return rerank_dense_candidates(query, dense_candidates, top_k=top_k)
