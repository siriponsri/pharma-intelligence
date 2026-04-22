"""HDC prevalence ingestion scaffold."""

from __future__ import annotations

from pathlib import Path

import polars as pl

from pharma_intel.ingestion.base import DatasetSpec, build_frame_from_csv, ensure_output_path, save_frame

SPEC = DatasetSpec(
    source_id="hdc",
    display_name="Thailand HDC NCD Prevalence",
    output_name="hdc_ncd_prevalence.parquet",
    schema={
        "year": pl.Int64,
        "province": pl.Utf8,
        "age_group": pl.Utf8,
        "disease_code": pl.Utf8,
        "gender": pl.Utf8,
        "prevalence_per_1000": pl.Float64,
    },
    description="Public epidemiology anchor data from the Ministry of Public Health HDC service.",
)


def build_dataset(input_path: Path | None = None) -> pl.DataFrame:
    """Build the HDC dataset from an optional local CSV export."""
    return build_frame_from_csv(SPEC, input_path)


def run(output_path: Path | None = None, input_path: Path | None = None) -> Path:
    """Persist the HDC scaffold dataset."""
    target_path = ensure_output_path(output_path, SPEC.output_name)
    return save_frame(build_dataset(input_path), target_path)
