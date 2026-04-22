"""Shared helpers for ingestion source scaffolds."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

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


def empty_frame(spec: DatasetSpec) -> pl.DataFrame:
    """Return an empty DataFrame with the declared schema."""
    return pl.DataFrame(schema=spec.schema)


def ensure_output_path(output_path: Path | None, output_name: str, base_dir: Path | None = None) -> Path:
    """Resolve and create the target output path."""
    settings.ensure_dirs()
    target_dir = base_dir or settings.processed_dir
    target_dir.mkdir(parents=True, exist_ok=True)
    return output_path or (target_dir / output_name)


def build_frame_from_csv(spec: DatasetSpec, input_path: Path | None = None) -> pl.DataFrame:
    """Load a CSV into the declared schema, or return an empty frame when unavailable."""
    if input_path is None:
        return empty_frame(spec)

    if not input_path.exists():
        logger.warning(f"Input path does not exist for {spec.source_id}: {input_path}")
        return empty_frame(spec)

    frame = pl.read_csv(input_path)
    for column_name, data_type in spec.schema.items():
        if column_name not in frame.columns:
            frame = frame.with_columns(pl.lit(None, dtype=data_type).alias(column_name))

    return frame.select(
        [pl.col(column_name).cast(data_type, strict=False).alias(column_name) for column_name, data_type in spec.schema.items()]
    )


def save_frame(frame: pl.DataFrame, output_path: Path) -> Path:
    """Persist a parquet artifact and log a short summary."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    frame.write_parquet(output_path)
    logger.info(f"Saved {len(frame):,} rows to {output_path}")
    return output_path
