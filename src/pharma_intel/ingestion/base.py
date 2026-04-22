"""Shared helpers for ingestion source scaffolds."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
import re
from zipfile import ZipFile

import pandas as pd
import polars as pl

from pharma_intel.common import logger, settings


@dataclass(frozen=True)
class DatasetSpec:
    """Declarative definition of one ingestion dataset."""

    source_id: str
    display_name: str
    output_name: str
    schema: dict[str, pl.DataType]
    description: str


SUPPORTED_INPUT_EXTENSIONS = (".csv", ".tsv", ".parquet", ".json", ".jsonl", ".xlsx", ".xls", ".zip")


def empty_frame(spec: DatasetSpec) -> pl.DataFrame:
    """Return an empty DataFrame with the declared schema."""
    return pl.DataFrame(schema=spec.schema)


def normalize_column_name(column_name: str) -> str:
    """Convert source column names to a canonical snake_case form."""
    normalized = re.sub(r"\W+", "_", column_name, flags=re.UNICODE).strip("_").lower()
    return re.sub(r"_+", "_", normalized)


def ensure_output_path(output_path: Path | None, output_name: str, base_dir: Path | None = None) -> Path:
    """Resolve and create the target output path."""
    settings.ensure_dirs()
    target_dir = base_dir or settings.processed_dir
    target_dir.mkdir(parents=True, exist_ok=True)
    return output_path or (target_dir / output_name)


def resolve_input_path(input_path: Path | None, source_id: str) -> Path | None:
    """Return the explicit input path or discover the newest raw export for a source."""
    if input_path is not None:
        return input_path

    source_dir = settings.raw_dir / source_id
    if not source_dir.exists():
        return None

    candidates = [
        path
        for path in source_dir.rglob("*")
        if path.is_file() and path.suffix.lower() in SUPPORTED_INPUT_EXTENSIONS
    ]
    if not candidates:
        return None

    return max(candidates, key=lambda path: path.stat().st_mtime)


def read_input_frame(input_path: Path) -> pl.DataFrame:
    """Load a raw export into a Polars DataFrame."""
    suffix = input_path.suffix.lower()

    if suffix == ".csv":
        return pl.read_csv(input_path)
    if suffix == ".tsv":
        return pl.read_csv(input_path, separator="\t")
    if suffix == ".parquet":
        return pl.read_parquet(input_path)
    if suffix == ".json":
        return pl.read_json(input_path)
    if suffix == ".jsonl":
        return pl.read_ndjson(input_path)
    if suffix in {".xlsx", ".xls"}:
        return pl.from_pandas(pd.read_excel(input_path))
    if suffix == ".zip":
        return _read_zipped_frame(input_path)

    raise ValueError(f"Unsupported input file type: {input_path.suffix}")


def _read_zipped_frame(input_path: Path) -> pl.DataFrame:
    with ZipFile(input_path) as archive:
        members = sorted(
            member
            for member in archive.namelist()
            if Path(member).suffix.lower() in {".csv", ".tsv", ".json", ".jsonl", ".xlsx", ".xls"}
        )
        if not members:
            raise ValueError(f"No supported dataset file found in archive: {input_path}")

        member_name = members[0]
        suffix = Path(member_name).suffix.lower()
        with archive.open(member_name) as handle:
            if suffix == ".csv":
                return pl.read_csv(handle)
            if suffix == ".tsv":
                return pl.read_csv(handle, separator="\t")
            if suffix == ".json":
                return pl.read_json(handle)
            if suffix == ".jsonl":
                return pl.read_ndjson(handle)
            if suffix in {".xlsx", ".xls"}:
                return pl.from_pandas(pd.read_excel(handle))

    raise ValueError(f"Unable to load dataset archive: {input_path}")


def normalize_frame_columns(
    frame: pl.DataFrame,
    spec: DatasetSpec,
    column_aliases: dict[str, tuple[str, ...]] | None = None,
) -> pl.DataFrame:
    """Map source-specific column names into the declared schema."""
    alias_map = column_aliases or {}
    normalized_columns = {normalize_column_name(column_name): column_name for column_name in frame.columns}
    expressions: list[pl.Expr] = []

    for column_name, data_type in spec.schema.items():
        candidate_names = (column_name, *alias_map.get(column_name, ()))
        source_column = next(
            (
                normalized_columns.get(normalize_column_name(candidate_name))
                for candidate_name in candidate_names
                if normalized_columns.get(normalize_column_name(candidate_name)) is not None
            ),
            None,
        )
        if source_column is None:
            expressions.append(pl.lit(None, dtype=data_type).alias(column_name))
            continue

        expressions.append(pl.col(source_column).alias(column_name))

    return frame.select(expressions)


def cast_frame_to_schema(frame: pl.DataFrame, spec: DatasetSpec) -> pl.DataFrame:
    """Cast a normalized frame into the declared schema."""
    return frame.select(
        [pl.col(column_name).cast(data_type, strict=False).alias(column_name) for column_name, data_type in spec.schema.items()]
    )


def build_frame_from_source(
    spec: DatasetSpec,
    input_path: Path | None = None,
    column_aliases: dict[str, tuple[str, ...]] | None = None,
) -> pl.DataFrame:
    """Load a source export into the declared schema, or return an empty frame when unavailable."""
    resolved_path = resolve_input_path(input_path, spec.source_id)
    if resolved_path is None:
        logger.warning(f"No raw export found for {spec.source_id}; returning an empty frame")
        return empty_frame(spec)

    if not resolved_path.exists():
        logger.warning(f"Input path does not exist for {spec.source_id}: {resolved_path}")
        return empty_frame(spec)

    logger.info(f"Loading {spec.source_id} export from {resolved_path}")
    frame = read_input_frame(resolved_path)
    normalized_frame = normalize_frame_columns(frame, spec, column_aliases=column_aliases)
    return cast_frame_to_schema(normalized_frame, spec)


def build_frame_from_csv(spec: DatasetSpec, input_path: Path | None = None) -> pl.DataFrame:
    """Backwards-compatible wrapper for source loading with exact column names."""
    return build_frame_from_source(spec, input_path=input_path)


def default_report_path(spec: DatasetSpec, report_path: Path | None = None) -> Path:
    """Return the default data-quality report path for a dataset."""
    settings.ensure_dirs()
    return report_path or (settings.interim_dir / f"{Path(spec.output_name).stem}_quality.json")


def write_quality_report(
    frame: pl.DataFrame,
    spec: DatasetSpec,
    output_path: Path,
    input_path: Path | None,
    report_path: Path | None = None,
) -> Path:
    """Write a lightweight data-quality report for a dataset."""
    target_path = default_report_path(spec, report_path=report_path)
    target_path.parent.mkdir(parents=True, exist_ok=True)
    report = {
        "source_id": spec.source_id,
        "display_name": spec.display_name,
        "input_path": str(input_path) if input_path is not None else None,
        "output_path": str(output_path),
        "row_count": frame.height,
        "column_count": frame.width,
        "columns": frame.columns,
        "null_counts": frame.null_count().to_dicts()[0] if frame.width else {},
    }
    target_path.write_text(json.dumps(report, indent=2), encoding="utf-8")
    logger.info(f"Saved {spec.source_id} quality report to {target_path}")
    return target_path


def save_frame(frame: pl.DataFrame, output_path: Path) -> Path:
    """Persist a parquet artifact and log a short summary."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    frame.write_parquet(output_path)
    logger.info(f"Saved {len(frame):,} rows to {output_path}")
    return output_path
