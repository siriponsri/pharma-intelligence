"""Royal Gazette ingestion scaffold."""

from __future__ import annotations

from pathlib import Path

import polars as pl

from pharma_intel.ingestion.base import DatasetSpec, build_frame_from_csv, ensure_output_path, save_frame

SPEC = DatasetSpec(
    source_id="ratchakitcha",
    display_name="Royal Gazette",
    output_name="ratchakitcha_announcements.parquet",
    schema={
        "publication_date": pl.Utf8,
        "document_title": pl.Utf8,
        "announcement_type": pl.Utf8,
        "issuing_agency": pl.Utf8,
        "related_drug": pl.Utf8,
        "summary": pl.Utf8,
        "source_url": pl.Utf8,
    },
    description="Royal Gazette announcements relevant to pharmaceutical regulation.",
)


def build_dataset(input_path: Path | None = None) -> pl.DataFrame:
    """Build the Royal Gazette dataset from an optional local CSV export."""
    return build_frame_from_csv(SPEC, input_path)


def run(output_path: Path | None = None, input_path: Path | None = None) -> Path:
    """Persist the Royal Gazette scaffold dataset."""
    target_path = ensure_output_path(output_path, SPEC.output_name)
    return save_frame(build_dataset(input_path), target_path)
