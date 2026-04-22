"""ClinicalTrials.gov ingestion scaffold."""

from __future__ import annotations

from pathlib import Path

import polars as pl

from pharma_intel.ingestion.base import DatasetSpec, build_frame_from_csv, ensure_output_path, save_frame

SPEC = DatasetSpec(
    source_id="clinicaltrials",
    display_name="ClinicalTrials.gov",
    output_name="clinicaltrials_cardiometabolic.parquet",
    schema={
        "nct_id": pl.Utf8,
        "brief_title": pl.Utf8,
        "phase": pl.Utf8,
        "overall_status": pl.Utf8,
        "condition": pl.Utf8,
        "intervention_name": pl.Utf8,
        "sponsor": pl.Utf8,
        "last_update_date": pl.Utf8,
    },
    description="Global clinical trial pipeline signals for cardiometabolic drugs.",
)


def build_dataset(input_path: Path | None = None) -> pl.DataFrame:
    """Build the ClinicalTrials.gov dataset from an optional local CSV export."""
    return build_frame_from_csv(SPEC, input_path)


def run(output_path: Path | None = None, input_path: Path | None = None) -> Path:
    """Persist the ClinicalTrials.gov scaffold dataset."""
    target_path = ensure_output_path(output_path, SPEC.output_name)
    return save_frame(build_dataset(input_path), target_path)
