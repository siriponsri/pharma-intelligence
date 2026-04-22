"""PubMed ingestion scaffold."""

from __future__ import annotations

from pathlib import Path

import polars as pl

from pharma_intel.ingestion.base import DatasetSpec, build_frame_from_csv, ensure_output_path, save_frame

SPEC = DatasetSpec(
    source_id="pubmed",
    display_name="PubMed Abstracts",
    output_name="pubmed_abstracts.parquet",
    schema={
        "pmid": pl.Utf8,
        "title": pl.Utf8,
        "abstract": pl.Utf8,
        "journal": pl.Utf8,
        "publication_date": pl.Utf8,
        "query_term": pl.Utf8,
    },
    description="Literature activity signals and evidence context from PubMed.",
)


def build_dataset(input_path: Path | None = None) -> pl.DataFrame:
    """Build the PubMed dataset from an optional local CSV export."""
    return build_frame_from_csv(SPEC, input_path)


def run(output_path: Path | None = None, input_path: Path | None = None) -> Path:
    """Persist the PubMed scaffold dataset."""
    target_path = ensure_output_path(output_path, SPEC.output_name)
    return save_frame(build_dataset(input_path), target_path)
