"""Thai e-GP procurement ingestion scaffold."""

from __future__ import annotations

from pathlib import Path

import polars as pl

from pharma_intel.ingestion.base import DatasetSpec, build_frame_from_csv, ensure_output_path, save_frame

SPEC = DatasetSpec(
    source_id="egp",
    display_name="Thai e-GP Procurement",
    output_name="egp_cardiometabolic_procurement.parquet",
    schema={
        "procurement_month": pl.Utf8,
        "hospital_name": pl.Utf8,
        "drug_name": pl.Utf8,
        "quantity": pl.Float64,
        "unit_price": pl.Float64,
        "total_value": pl.Float64,
        "province": pl.Utf8,
    },
    description="Government procurement records for cardiometabolic medicines.",
)


def build_dataset(input_path: Path | None = None) -> pl.DataFrame:
    """Build the e-GP dataset from an optional local CSV export."""
    return build_frame_from_csv(SPEC, input_path)


def run(output_path: Path | None = None, input_path: Path | None = None) -> Path:
    """Persist the e-GP scaffold dataset."""
    target_path = ensure_output_path(output_path, SPEC.output_name)
    return save_frame(build_dataset(input_path), target_path)
