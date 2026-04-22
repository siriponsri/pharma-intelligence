"""NHSO utilization ingestion scaffold."""

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

COLUMN_ALIASES = {
    "service_month": (
        "month",
        "service_date",
        "claim_month",
        "เดือนบริการ",
        "เดือนรับบริการ",
        "ปีเดือน",
    ),
    "scheme": ("benefit_scheme", "insurance_scheme", "สิทธิการรักษา", "กองทุน"),
    "drug_class": ("atc_class", "medicine_group", "กลุ่มยา", "หมวดยา"),
    "claims_count": ("claim_count", "visits", "จำนวนรายการ", "จำนวนเคลม", "จำนวนครั้งบริการ"),
    "units_dispensed": ("dispensed_units", "quantity", "จำนวนหน่วย", "จำนวนยาที่จ่าย"),
    "reimbursement_thb": ("reimbursed_amount", "paid_amount", "ยอดชดเชย", "ยอดชดเชยบาท", "มูลค่าชดเชย(บาท)"),
}


def _normalize_service_month() -> pl.Expr:
    raw_month = (
        pl.col("service_month")
        .cast(pl.Utf8)
        .str.strip_chars()
        .str.replace_all(r"[./]", "-")
    )
    return (
        pl.when(raw_month.str.contains(r"^\d{4}-\d{2}$"))
        .then(raw_month)
        .when(raw_month.str.contains(r"^\d{6}$"))
        .then(raw_month.str.slice(0, 4) + pl.lit("-") + raw_month.str.slice(4, 2))
        .when(raw_month.str.contains(r"^\d{2}-\d{4}$"))
        .then(raw_month.str.slice(3, 4) + pl.lit("-") + raw_month.str.slice(0, 2))
        .when(raw_month.str.contains(r"^\d{4}-\d{2}-\d{2}$"))
        .then(raw_month.str.slice(0, 7))
        .otherwise(None)
        .alias("service_month")
    )


def build_dataset(input_path: Path | None = None) -> pl.DataFrame:
    """Build the NHSO dataset from a local raw export."""
    frame = build_frame_from_source(SPEC, input_path=input_path, column_aliases=COLUMN_ALIASES)
    return frame.with_columns(
        [
            _normalize_service_month(),
            pl.col("scheme").cast(pl.Utf8).str.strip_chars().str.to_uppercase().alias("scheme"),
            pl.col("drug_class").cast(pl.Utf8).str.strip_chars().alias("drug_class"),
            pl.col("claims_count")
            .cast(pl.Utf8)
            .str.replace_all(",", "")
            .cast(pl.Int64, strict=False)
            .alias("claims_count"),
            pl.col("units_dispensed")
            .cast(pl.Utf8)
            .str.replace_all(",", "")
            .cast(pl.Float64, strict=False)
            .alias("units_dispensed"),
            pl.col("reimbursement_thb")
            .cast(pl.Utf8)
            .str.replace_all(",", "")
            .cast(pl.Float64, strict=False)
            .alias("reimbursement_thb"),
        ]
    )


def run(output_path: Path | None = None, input_path: Path | None = None) -> Path:
    """Persist the normalized NHSO dataset and a quality report."""
    target_path = ensure_output_path(output_path, SPEC.output_name)
    resolved_input = resolve_input_path(input_path, SPEC.source_id)
    frame = build_dataset(resolved_input)
    written_path = save_frame(frame, target_path)
    write_quality_report(frame, SPEC, written_path, resolved_input)
    return written_path
