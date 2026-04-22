"""Model-comparison and backtesting utilities."""

from __future__ import annotations

import math

import numpy as np
import polars as pl


def rolling_origin_splits(
    df: pl.DataFrame,
    min_train_rows: int,
    test_rows: int,
    step_rows: int | None = None,
) -> list[tuple[pl.DataFrame, pl.DataFrame]]:
    """Create rolling-origin train/test splits for a sorted time series frame."""
    if min_train_rows <= 0 or test_rows <= 0:
        raise ValueError("min_train_rows and test_rows must be positive")

    step = step_rows or test_rows
    if step <= 0:
        raise ValueError("step_rows must be positive")

    splits: list[tuple[pl.DataFrame, pl.DataFrame]] = []
    for train_end in range(min_train_rows, len(df) - test_rows + 1, step):
        train = df.slice(0, train_end)
        test = df.slice(train_end, test_rows)
        splits.append((train, test))
    return splits


def diebold_mariano(loss_model_a: np.ndarray, loss_model_b: np.ndarray, horizon: int = 1) -> dict[str, float]:
    """Compute a simple Diebold-Mariano comparison using normal approximation."""
    errors_a = np.asarray(loss_model_a, dtype=float)
    errors_b = np.asarray(loss_model_b, dtype=float)
    if errors_a.shape != errors_b.shape:
        raise ValueError("Loss arrays must have the same shape")
    if len(errors_a) < 3:
        raise ValueError("At least 3 observations are required")

    differential = errors_a - errors_b
    mean_differential = float(np.mean(differential))
    centered = differential - mean_differential

    gamma_0 = float(np.dot(centered, centered) / (len(differential) - 1))
    variance = gamma_0
    for lag in range(1, max(horizon, 1)):
        covariance = float(np.dot(centered[lag:], centered[:-lag]) / (len(differential) - 1))
        variance += 2.0 * covariance

    variance = max(variance / len(differential), 1e-12)
    statistic = mean_differential / math.sqrt(variance)
    p_value = math.erfc(abs(statistic) / math.sqrt(2.0))
    return {"dm_stat": float(statistic), "p_value": float(p_value), "mean_loss_diff": mean_differential}
