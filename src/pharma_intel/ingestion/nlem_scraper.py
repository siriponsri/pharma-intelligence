"""NLEM ingestion scaffold."""

from __future__ import annotations

from pathlib import Path

import polars as pl

from pharma_intel.ingestion.base import DatasetSpec, build_frame_from_csv, ensure_output_path, save_frame

SPEC = DatasetSpec(
    source_id="nlem",
    display_name="National List of Essential Medicines",
    output_name="nlem_updates.parquet",
    schema={
        "update_date": pl.Utf8,
        "medicine_name": pl.Utf8,
        "nlem_category": pl.Utf8,
        "action": pl.Utf8,
        "reason": pl.Utf8,
        "source_url": pl.Utf8,
    },
    description="Policy and formulary changes from the Thai essential medicines list.",
)


def build_dataset(input_path: Path | None = None) -> pl.DataFrame:
    """Build the NLEM dataset from an optional local CSV export."""
    return build_frame_from_csv(SPEC, input_path)


def run(output_path: Path | None = None, input_path: Path | None = None) -> Path:
    """Persist the NLEM scaffold dataset."""
    target_path = ensure_output_path(output_path, SPEC.output_name)
    return save_frame(build_dataset(input_path), target_path)
