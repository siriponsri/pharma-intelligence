"""Thai FDA registration ingestion scaffold."""

from __future__ import annotations

from pathlib import Path

import polars as pl

from pharma_intel.ingestion.base import DatasetSpec, build_frame_from_csv, ensure_output_path, save_frame

SPEC = DatasetSpec(
    source_id="tfda",
    display_name="Thai FDA Registrations",
    output_name="tfda_registrations.parquet",
    schema={
        "registration_number": pl.Utf8,
        "product_name": pl.Utf8,
        "active_ingredient": pl.Utf8,
        "dosage_form": pl.Utf8,
        "license_holder": pl.Utf8,
        "approval_date": pl.Utf8,
        "status": pl.Utf8,
    },
    description="Thai FDA registration records for regulatory intelligence.",
)


def build_dataset(input_path: Path | None = None) -> pl.DataFrame:
    """Build the TFDA dataset from an optional local CSV export."""
    return build_frame_from_csv(SPEC, input_path)


def run(output_path: Path | None = None, input_path: Path | None = None) -> Path:
    """Persist the TFDA scaffold dataset."""
    target_path = ensure_output_path(output_path, SPEC.output_name)
    return save_frame(build_dataset(input_path), target_path)
