"""RAG query engine — retrieve from vector store, generate answer via LLM provider.

The LLM backend is pluggable — see `pharma_intel.rag.llm` for available providers.
Default is ThaiLLM (sovereign), with Claude available for benchmarking.
"""

from __future__ import annotations

from dataclasses import dataclass

from pharma_intel.common import logger
from pharma_intel.rag.embeddings import embed_query
from pharma_intel.rag.llm import LLMProvider, get_llm
from pharma_intel.rag.vectorstore import RetrievedChunk, VectorStore

# System prompt — bilingual, since queries may come in Thai or English and
# context (currently FDA Orange Book) is English.
SYSTEM_PROMPT = """You are a pharmaceutical regulatory intelligence assistant for Thai pharma \
R&D teams (คุณเป็นผู้ช่วย intelligence ด้านการกำกับยาสำหรับทีม R&D เภสัชกรไทย).

Your role: answer questions about FDA-approved drugs, patents, market exclusivity, \
and implications for Thai generic drug strategy.

RULES:
1. Answer ONLY from the provided context. If the context doesn't contain the answer, \
say so explicitly — never make up drug names, dates, or patent numbers. \
(ถ้าข้อมูลไม่มีใน context ให้ตอบตรง ๆ ว่าไม่พบ — ห้ามเดา)
2. Always cite sources using [doc_id] inline notation after each factual claim.
3. Be precise with dates (use YYYY-MM-DD if possible) and patent numbers.
4. When relevant, highlight business implications for Thai generic manufacturers \
(e.g., "patent expires 2026 → generic opportunity window opens").
5. Structure answers clearly with bullet points for lists of patents or products.
6. Respond in the same language as the question (Thai for Thai questions, \
English for English questions). Mixed-language questions: respond primarily in Thai."""


@dataclass
class RAGAnswer:
    """Output of a RAG query."""

    question: str
    answer: str
    retrieved: list[RetrievedChunk]
    model: str
    provider: str
    input_tokens: int | None = None
    output_tokens: int | None = None


class RAGEngine:
    """Retrieves relevant drug monographs and generates grounded answers.

    The LLM backend is injected via `llm` parameter or resolved from settings.
    """

    def __init__(
        self,
        collection_name: str = "cardiometabolic_drugs",
        top_k: int = 5,
        llm: LLMProvider | None = None,
    ):
        self.store = VectorStore(collection_name=collection_name)
        self.top_k = top_k
        self.llm: LLMProvider = llm or get_llm()
        logger.info(
            f"RAGEngine ready — collection='{collection_name}', "
            f"llm={self.llm.provider_name}/{self.llm.model_name}"
        )

    def retrieve(
        self,
        query: str,
        k: int | None = None,
        where: dict | None = None,
    ) -> list[RetrievedChunk]:
        """Embed query and fetch top-k chunks."""
        k = k or self.top_k
        query_emb = embed_query(query)
        chunks = self.store.query(query_embedding=query_emb, k=k, where=where)
        if chunks:
            logger.info(
                f"Retrieved {len(chunks)} chunks (top score: {chunks[0].score:.3f})"
            )
        else:
            logger.warning("No chunks retrieved")
        return chunks

    def build_context(self, chunks: list[RetrievedChunk]) -> str:
        """Format retrieved chunks as numbered context blocks."""
        blocks = []
        for i, chunk in enumerate(chunks, 1):
            header = (
                f"[{chunk.doc_id}] "
                f"Ingredient: {chunk.metadata.get('ingredient', 'N/A')} | "
                f"Trade: {chunk.metadata.get('trade_name', 'N/A')} | "
                f"TA: {chunk.metadata.get('therapeutic_area', 'N/A')}"
            )
            blocks.append(f"--- Source {i} ---\n{header}\n\n{chunk.text}")
        return "\n\n".join(blocks)

    def answer(
        self,
        question: str,
        k: int | None = None,
        where: dict | None = None,
        max_tokens: int = 1500,
        temperature: float = 0.3,
    ) -> RAGAnswer:
        """Retrieve + generate."""
        chunks = self.retrieve(question, k=k, where=where)

        if not chunks:
            return RAGAnswer(
                question=question,
                answer="No relevant documents found in the knowledge base. "
                "(ไม่พบเอกสารที่เกี่ยวข้องในฐานข้อมูล)",
                retrieved=[],
                model=self.llm.model_name,
                provider=self.llm.provider_name,
            )

        context = self.build_context(chunks)
        user_message = (
            f"CONTEXT:\n{context}\n\n"
            f"QUESTION: {question}\n\n"
            "Answer the question using only the context above. "
            "Cite sources as [doc_id] inline."
        )

        response = self.llm.complete(
            system=SYSTEM_PROMPT,
            user=user_message,
            max_tokens=max_tokens,
            temperature=temperature,
        )

        return RAGAnswer(
            question=question,
            answer=response.text,
            retrieved=chunks,
            model=response.model,
            provider=self.llm.provider_name,
            input_tokens=response.input_tokens,
            output_tokens=response.output_tokens,
        )
