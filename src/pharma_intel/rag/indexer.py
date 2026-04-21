"""Indexer — embeds drug monographs and persists them in the vector store."""

from __future__ import annotations

from pharma_intel.common import logger
from pharma_intel.ingestion.fda_orange_book import DrugMonograph
from pharma_intel.rag.embeddings import embed_texts
from pharma_intel.rag.vectorstore import VectorStore


def index_monographs(
    monographs: list[DrugMonograph],
    collection_name: str = "cardiometabolic_drugs",
    batch_size: int = 32,
) -> VectorStore:
    """Embed and index a list of DrugMonograph.

    Returns the VectorStore for immediate querying.
    """
    if not monographs:
        raise ValueError("No monographs provided — did the ingestion pipeline run?")

    logger.info(f"Indexing {len(monographs)} monographs into '{collection_name}'")

    texts = [m.text for m in monographs]
    ids = [m.doc_id for m in monographs]
    metadatas = [
        {
            "appl_no": m.appl_no,
            "product_no": m.product_no,
            "ingredient": m.ingredient,
            "trade_name": m.trade_name,
            "applicant": m.applicant,
            "strength": m.strength,
            "dosage_form_route": m.dosage_form_route,
            "approval_date": m.approval_date or "",
            "therapeutic_area": m.therapeutic_area,
            "num_patents": len(m.patents),
            "num_exclusivities": len(m.exclusivities),
            "source": "fda_orange_book",
        }
        for m in monographs
    ]

    # Embed in batches
    embeddings = embed_texts(texts, batch_size=batch_size)

    # Store
    store = VectorStore(collection_name=collection_name)
    store.add(ids=ids, embeddings=embeddings, documents=texts, metadatas=metadatas)
    return store
