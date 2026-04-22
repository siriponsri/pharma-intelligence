"""NHSO utilization ingestion scaffold."""

from __future__ import annotations

from pathlib import Path

import polars as pl

from pharma_intel.ingestion.base import DatasetSpec, build_frame_from_csv, ensure_output_path, save_frame

SPEC = DatasetSpec(
    source_id="nhso",
    display_name="NHSO Open Data Utilization",
    output_name="nhso_utilization.parquet",
    schema={
        "service_month": pl.Utf8,
        "scheme": pl.Utf8,
        "drug_class": pl.Utf8,
        "claims_count": pl.Int64,
        "units_dispensed": pl.Float64,
        "reimbursement_thb": pl.Float64,
    },
    description="Public claims and utilization aggregates from NHSO open data.",
)


def build_dataset(input_path: Path | None = None) -> pl.DataFrame:
    """Build the NHSO dataset from an optional local CSV export."""
    return build_frame_from_csv(SPEC, input_path)


def run(output_path: Path | None = None, input_path: Path | None = None) -> Path:
    """Persist the NHSO scaffold dataset."""
    target_path = ensure_output_path(output_path, SPEC.output_name)
    return save_frame(build_dataset(input_path), target_path)
