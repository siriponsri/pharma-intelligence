"""Tests for Phase 3 RAG scaffolds."""

from __future__ import annotations

from pharma_intel.rag.evaluator import batch_evaluate_answers, evaluate_rag_answer
from pharma_intel.rag.event_extractor import events_to_frame, extract_events_from_chunks
from pharma_intel.rag.hybrid_retrieval import rerank_dense_candidates
from pharma_intel.rag.vectorstore import RetrievedChunk


def _fake_chunks() -> list[RetrievedChunk]:
    return [
        RetrievedChunk(
            doc_id="doc-1",
            text="Empagliflozin patent expires on 2026-05-01 and supports diabetes treatment.",
            metadata={"ingredient": "empagliflozin", "therapeutic_area": "diabetes"},
            score=0.80,
        ),
        RetrievedChunk(
            doc_id="doc-2",
            text="Losartan was approved earlier and is widely used for hypertension.",
            metadata={"ingredient": "losartan", "therapeutic_area": "hypertension"},
            score=0.82,
        ),
    ]


class TestRagScaffolds:
    def test_reranker_prefers_query_overlap(self):
        reranked = rerank_dense_candidates("empagliflozin patent", _fake_chunks(), top_k=1)

        assert reranked[0].doc_id == "doc-1"

    def test_event_extraction_returns_structured_rows(self):
        events = extract_events_from_chunks(_fake_chunks())
        frame = events_to_frame(events)

        assert len(events) == 2
        assert "event_type" in frame.columns
        assert frame["event_date"].to_list()[0] == "2026-05-01"

    def test_rag_evaluator_reports_citations_and_language(self):
        record = evaluate_rag_answer(
            question="When does empagliflozin patent expire?",
            answer="The patent expires on 2026-05-01 [doc-1].",
            retrieved=_fake_chunks(),
        )

        assert record.has_citations is True
        assert record.language_match is True
        assert record.retrieved_count == 2

    def test_batch_evaluation_builds_table(self):
        frame = batch_evaluate_answers(
            [("ถามเรื่อง empagliflozin", "ไม่พบข้อมูล [doc-1]", _fake_chunks())]
        )

        assert frame.height == 1
        assert frame["citation_count"].item() == 1