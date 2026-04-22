"""HDC prevalence ingestion scaffold."""

from __future__ import annotations

from pathlib import Path

import polars as pl

from pharma_intel.ingestion.base import (
    DatasetSpec,
    build_frame_from_source,
    ensure_output_path,
    resolve_input_path,
    save_frame,
    write_quality_report,
)

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

COLUMN_ALIASES = {
    "year": ("fiscal_year", "report_year", "budget_year", "ปี", "ปีงบประมาณ"),
    "province": ("province_name", "changwat", "จังหวัด", "จังหวัดที่รักษา"),
    "age_group": ("age_band", "age_range", "ช่วงอายุ", "กลุ่มอายุ"),
    "disease_code": ("icd10", "icd_10", "diagnosis_code", "รหัสโรค", "icd10tm"),
    "gender": ("sex", "patient_gender", "เพศ"),
    "prevalence_per_1000": (
        "prevalence_rate",
        "rate_per_1000",
        "prevalence",
        "อัตราป่วยต่อพันประชากร",
        "อัตราความชุกต่อพันประชากร",
    ),
}

GENDER_MAP = {
    "m": "male",
    "male": "male",
    "ชาย": "male",
    "f": "female",
    "female": "female",
    "หญิง": "female",
}


def build_dataset(input_path: Path | None = None) -> pl.DataFrame:
    """Build the HDC dataset from a local raw export."""
    frame = build_frame_from_source(SPEC, input_path=input_path, column_aliases=COLUMN_ALIASES)
    return frame.with_columns(
        [
            pl.col("year").cast(pl.Int64, strict=False).alias("year"),
            pl.col("province").cast(pl.Utf8).str.strip_chars().alias("province"),
            pl.col("age_group").cast(pl.Utf8).str.strip_chars().alias("age_group"),
            pl.col("disease_code").cast(pl.Utf8).str.strip_chars().str.to_uppercase().alias("disease_code"),
            pl.col("gender")
            .cast(pl.Utf8)
            .str.strip_chars()
            .str.to_lowercase()
            .replace_strict(GENDER_MAP, default=None)
            .alias("gender"),
            pl.col("prevalence_per_1000")
            .cast(pl.Utf8)
            .str.replace_all(",", "")
            .cast(pl.Float64, strict=False)
            .alias("prevalence_per_1000"),
        ]
    )


def run(output_path: Path | None = None, input_path: Path | None = None) -> Path:
    """Persist the normalized HDC dataset and a quality report."""
    target_path = ensure_output_path(output_path, SPEC.output_name)
    resolved_input = resolve_input_path(input_path, SPEC.source_id)
    frame = build_dataset(resolved_input)
    written_path = save_frame(frame, target_path)
    write_quality_report(frame, SPEC, written_path, resolved_input)
    return written_path
