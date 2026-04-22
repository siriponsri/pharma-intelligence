"""ChromaDB vector store wrapper.

Persistent local store. For production, swap to Qdrant or Pinecone.
"""

from __future__ import annotations

from dataclasses import dataclass

import chromadb
from chromadb.config import Settings as ChromaSettings

from pharma_intel.common import logger, settings


@dataclass
class RetrievedChunk:
    """A retrieved document chunk with metadata and similarity score."""

    doc_id: str
    text: str
    metadata: dict
    score: float  # cosine similarity (higher = better)


class VectorStore:
    """Thin wrapper around ChromaDB collection."""

    def __init__(self, collection_name: str = "cardiometabolic_drugs"):
        self.collection_name = collection_name
        self.client = chromadb.PersistentClient(
            path=str(settings.chroma_persist_dir),
            settings=ChromaSettings(anonymized_telemetry=False),
        )
        self.collection = self.client.get_or_create_collection(
            name=collection_name,
            metadata={"hnsw:space": "cosine"},
        )
        logger.info(
            f"VectorStore ready — collection='{collection_name}', "
            f"count={self.collection.count()}"
        )

    def add(
        self,
        ids: list[str],
        embeddings: list[list[float]],
        documents: list[str],
        metadatas: list[dict],
    ) -> None:
        """Add documents to the collection. Replaces existing docs with same IDs."""
        assert len(ids) == len(embeddings) == len(documents) == len(metadatas)

        # Chroma doesn't support list/None in metadata — coerce
        clean_meta = [_clean_metadata(m) for m in metadatas]
        max_batch_size = self.client.get_max_batch_size()

        # Upsert pattern — delete existing then add
        existing = self.collection.get(ids=ids)
        if existing["ids"]:
            self.collection.delete(ids=existing["ids"])

        for start in range(0, len(ids), max_batch_size):
            end = start + max_batch_size
            self.collection.add(
                ids=ids[start:end],
                embeddings=embeddings[start:end],
                documents=documents[start:end],
                metadatas=clean_meta[start:end],
            )

        logger.info(f"Indexed {len(ids)} documents (total in collection: {self.collection.count()})")

    def query(
        self,
        query_embedding: list[float],
        k: int = 5,
        where: dict | None = None,
    ) -> list[RetrievedChunk]:
        """Query the collection by embedding. Optional metadata filter."""
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=k,
            where=where,
        )

        chunks: list[RetrievedChunk] = []
        for i in range(len(results["ids"][0])):
            # Chroma returns distance (lower = better for cosine). Convert to similarity.
            distance = results["distances"][0][i]
            similarity = 1.0 - distance
            chunks.append(
                RetrievedChunk(
                    doc_id=results["ids"][0][i],
                    text=results["documents"][0][i],
                    metadata=results["metadatas"][0][i],
                    score=similarity,
                )
            )
        return chunks

    def reset(self) -> None:
        """Drop and recreate the collection."""
        self.client.delete_collection(self.collection_name)
        self.collection = self.client.get_or_create_collection(
            name=self.collection_name,
            metadata={"hnsw:space": "cosine"},
        )
        logger.warning(f"Reset collection '{self.collection_name}'")


def _clean_metadata(meta: dict) -> dict:
    """Ensure all metadata values are Chroma-compatible (str, int, float, bool)."""
    out: dict = {}
    for k, v in meta.items():
        if v is None:
            continue
        if isinstance(v, (str, int, float, bool)):
            out[k] = v
        else:
            out[k] = str(v)
    return out
