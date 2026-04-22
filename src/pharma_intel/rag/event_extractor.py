"""Regulatory event extraction helpers for retrieved RAG evidence."""

from __future__ import annotations

from dataclasses import asdict, dataclass
import re

import polars as pl

from pharma_intel.rag.vectorstore import RetrievedChunk

DATE_PATTERN = re.compile(r"\b\d{4}-\d{2}-\d{2}\b")
EVENT_KEYWORDS = {
    "patent": ("patent", "สิทธิบัตร"),
    "exclusivity": ("exclusivity", "exclusive"),
    "approval": ("approved", "approval", "อนุมัติ"),
    "registration": ("registration", "registered", "ขึ้นทะเบียน"),
    "policy": ("nlem", "gazette", "policy", "บัญชียาหลัก"),
}


@dataclass(frozen=True)
class RegulatoryEvent:
    """A compact structured event extracted from one evidence chunk."""

    source_id: str
    event_type: str
    molecule: str
    event_date: str | None
    summary: str
    evidence_text: str


def infer_event_type(text: str) -> str:
    """Assign a coarse event type using keyword matches."""
    normalized = text.lower()
    for event_type, keywords in EVENT_KEYWORDS.items():
        if any(keyword in normalized for keyword in keywords):
            return event_type
    return "other"


def extract_events_from_chunks(chunks: list[RetrievedChunk]) -> list[RegulatoryEvent]:
    """Create one structured event per retrieved chunk."""
    events: list[RegulatoryEvent] = []
    for chunk in chunks:
        match = DATE_PATTERN.search(chunk.text)
        molecule = (
            chunk.metadata.get("ingredient")
            or chunk.metadata.get("trade_name")
            or chunk.metadata.get("product_name")
            or "unknown"
        )
        summary = chunk.text.split(".\n", 1)[0].split("\n", 1)[0][:220]
        events.append(
            RegulatoryEvent(
                source_id=chunk.doc_id,
                event_type=infer_event_type(f"{summary} {molecule}"),
                molecule=str(molecule),
                event_date=match.group(0) if match else None,
                summary=summary,
                evidence_text=chunk.text[:500],
            )
        )
    return events


def events_to_frame(events: list[RegulatoryEvent]) -> pl.DataFrame:
    """Convert extracted events to a tabular artifact."""
    return pl.DataFrame([asdict(event) for event in events]) if events else pl.DataFrame(
        schema={
            "source_id": pl.Utf8,
            "event_type": pl.Utf8,
            "molecule": pl.Utf8,
            "event_date": pl.Utf8,
            "summary": pl.Utf8,
            "evidence_text": pl.Utf8,
        }
    )
