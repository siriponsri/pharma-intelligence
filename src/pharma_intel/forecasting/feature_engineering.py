"""Feature engineering utilities for global forecasting models."""

from __future__ import annotations

import polars as pl


def _normalize_month_column(frame: pl.DataFrame) -> pl.DataFrame:
    """Ensure the month column is represented as a date."""
    month_dtype = frame.schema.get("month")
    if month_dtype == pl.Utf8:
        return frame.with_columns(pl.col("month").str.to_date(strict=False).alias("month"))
    if month_dtype == pl.Datetime:
        return frame.with_columns(pl.col("month").dt.date().alias("month"))
    return frame


def build_global_features(df: pl.DataFrame, target_col: str = "units_kddd") -> pl.DataFrame:
    """Add lag, rolling, growth, and calendar features to a class-month panel."""
    frame = _normalize_month_column(df).sort(["class_id", "month"])

    return frame.with_columns(
        [
            pl.col(target_col).shift(1).over("class_id").alias("lag_1"),
            pl.col(target_col).shift(3).over("class_id").alias("lag_3"),
            pl.col(target_col).shift(6).over("class_id").alias("lag_6"),
            pl.col(target_col).shift(12).over("class_id").alias("lag_12"),
            pl.col(target_col).shift(24).over("class_id").alias("lag_24"),
            pl.col(target_col).rolling_mean(window_size=3).over("class_id").alias("rolling_mean_3"),
            pl.col(target_col).rolling_mean(window_size=6).over("class_id").alias("rolling_mean_6"),
            pl.col(target_col).rolling_mean(window_size=12).over("class_id").alias("rolling_mean_12"),
            pl.col(target_col).rolling_std(window_size=3).over("class_id").alias("rolling_std_3"),
            pl.col(target_col).rolling_std(window_size=6).over("class_id").alias("rolling_std_6"),
            pl.col(target_col).rolling_std(window_size=12).over("class_id").alias("rolling_std_12"),
            ((pl.col(target_col) / pl.col(target_col).shift(12).over("class_id")) - 1.0).alias("yoy_growth"),
            pl.col("month").dt.month().alias("calendar_month"),
            pl.col("month").dt.quarter().alias("calendar_quarter"),
            pl.when(pl.col("month").dt.month().is_between(10, 12))
            .then(pl.lit(1))
            .when(pl.col("month").dt.month().is_between(1, 3))
            .then(pl.lit(2))
            .when(pl.col("month").dt.month().is_between(4, 6))
            .then(pl.lit(3))
            .otherwise(pl.lit(4))
            .alias("thai_fiscal_quarter"),
        ]
    )
