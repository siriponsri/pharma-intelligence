"""Lightweight RAG evaluation helpers for batch experiments."""

from __future__ import annotations

from dataclasses import asdict, dataclass
import re

import polars as pl

from pharma_intel.rag.vectorstore import RetrievedChunk

CITATION_PATTERN = re.compile(r"\[[^\]]+\]")
THAI_CHAR_PATTERN = re.compile(r"[ก-๙]")
ABSTENTION_MARKERS = (
    "no relevant documents found",
    "not found in the knowledge base",
    "ไม่พบ",
    "ไม่มีข้อมูล",
)


@dataclass(frozen=True)
class RAGEvaluationRecord:
    """One evaluation row for a RAG answer."""

    question: str
    answer_language: str
    question_language: str
    citation_count: int
    has_citations: bool
    retrieved_count: int
    avg_retrieval_score: float
    language_match: bool
    abstained: bool


def detect_language(text: str) -> str:
    """Classify text as Thai, English, mixed, or empty."""
    if not text.strip():
        return "empty"
    has_thai = bool(THAI_CHAR_PATTERN.search(text))
    has_latin = bool(re.search(r"[A-Za-z]", text))
    if has_thai and has_latin:
        return "mixed"
    if has_thai:
        return "thai"
    if has_latin:
        return "english"
    return "other"


def evaluate_rag_answer(
    question: str,
    answer: str,
    retrieved: list[RetrievedChunk],
) -> RAGEvaluationRecord:
    """Compute simple retrieval and answer-quality heuristics for one response."""
    citation_count = len(CITATION_PATTERN.findall(answer))
    question_language = detect_language(question)
    answer_language = detect_language(answer)
    avg_retrieval_score = sum(chunk.score for chunk in retrieved) / len(retrieved) if retrieved else 0.0
    normalized_answer = answer.lower()
    abstained = any(marker in normalized_answer for marker in ABSTENTION_MARKERS)

    return RAGEvaluationRecord(
        question=question,
        answer_language=answer_language,
        question_language=question_language,
        citation_count=citation_count,
        has_citations=citation_count > 0,
        retrieved_count=len(retrieved),
        avg_retrieval_score=avg_retrieval_score,
        language_match=question_language in {answer_language, "mixed"} or answer_language == "mixed",
        abstained=abstained,
    )


def batch_evaluate_answers(rows: list[tuple[str, str, list[RetrievedChunk]]]) -> pl.DataFrame:
    """Evaluate a list of question-answer-retrieval triples."""
    records = [asdict(evaluate_rag_answer(question, answer, retrieved)) for question, answer, retrieved in rows]
    return pl.DataFrame(records)
