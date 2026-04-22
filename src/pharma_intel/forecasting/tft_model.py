"""Temporal Fusion Transformer scaffold for GPU-backed training."""

from __future__ import annotations

import polars as pl

from pharma_intel.forecasting.feature_engineering import build_global_features


def tft_dependencies_available() -> bool:
    """Return whether the TFT training stack is installed."""
    try:
        import lightning  # noqa: F401
        import pytorch_forecasting  # noqa: F401
        import torch  # noqa: F401
    except ImportError:
        return False
    return True


def prepare_tft_frame(df: pl.DataFrame, target_col: str = "units_kddd") -> pl.DataFrame:
    """Build a normalized TFT-ready frame with engineered features and a time index."""
    frame = build_global_features(df, target_col=target_col).sort(["class_id", "month"])
    return frame.with_columns(
        [
            (pl.col("class_id").cum_count().over("class_id") - 1).alias("time_idx"),
            pl.col("class_id").cast(pl.Utf8).alias("group_id"),
        ]
    )


def build_tft_training_config(df: pl.DataFrame, target_col: str = "units_kddd") -> dict:
    """Return a compact training configuration for the future TFT experiment."""
    if df.is_empty():
        raise ValueError("df must contain at least one row")

    prepared = prepare_tft_frame(df, target_col=target_col)
    return {
        "target_col": target_col,
        "time_idx_col": "time_idx",
        "group_id_col": "group_id",
        "n_rows": len(prepared),
        "n_groups": prepared["group_id"].n_unique(),
    }
