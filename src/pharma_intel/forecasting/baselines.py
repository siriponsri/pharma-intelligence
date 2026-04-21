"""SARIMAX baseline forecaster.

This is the statistical baseline against which TFT will be compared.
Per-class univariate model with exogenous features.

Why SARIMAX baseline:
    - Interpretable (committee likes this)
    - Fast to fit and evaluate
    - Handles exogenous regressors natively → fair comparison with TFT
    - Standard benchmark in pharmaceutical forecasting literature
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import polars as pl

from pharma_intel.common import logger


@dataclass
class ForecastResult:
    """Standardized forecast output across all baseline/ML/DL models."""

    class_id: str
    model_name: str
    train_end: str  # last date used for training
    horizon_months: int
    forecast_dates: list[str]
    forecast_mean: list[float]
    forecast_lower_95: list[float]
    forecast_upper_95: list[float]
    fitted_params: dict | None = None


def aggregate_to_class_monthly(df: pl.DataFrame, target_col: str = "units_kddd") -> pl.DataFrame:
    """Collapse channel dimension — forecast at class × month level.

    Input: long panel with (month, class_id, channel, ...)
    Output: wide-ish with (month, class_id, units_kddd_total, ...features)
    """
    # Aggregate target by class × month, take first exogenous value per group
    # (exogenous values are identical across channels by construction)
    aggregated = (
        df.group_by(["month", "class_id", "therapeutic_area"])
        .agg(
            [
                pl.col(target_col).sum().alias(target_col),
                pl.col("revenue_thb_million").sum().alias("revenue_thb_million"),
                pl.col("stockout_days").max().alias("stockout_days"),
                pl.col("competitor_launch_flag").any().alias("competitor_launch_flag"),
                pl.col("patent_cliff_flag").any().alias("patent_cliff_flag"),
                pl.col("regulation_change_flag").any().alias("regulation_change_flag"),
                pl.col("diabetes_prevalence").first().alias("diabetes_prevalence"),
                pl.col("hypertension_prevalence").first().alias("hypertension_prevalence"),
                pl.col("dyslipidemia_prevalence").first().alias("dyslipidemia_prevalence"),
                pl.col("obesity_prevalence").first().alias("obesity_prevalence"),
                pl.col("healthcare_budget_index").first().alias("healthcare_budget_index"),
            ]
        )
        .sort(["class_id", "month"])
    )
    return aggregated


def fit_sarimax(
    class_df: pl.DataFrame,
    target_col: str = "units_kddd",
    exog_cols: list[str] | None = None,
    order: tuple[int, int, int] = (1, 1, 1),
    seasonal_order: tuple[int, int, int, int] = (1, 1, 1, 12),
    horizon_months: int = 24,
) -> ForecastResult:
    """Fit SARIMAX on a single class time series.

    Args:
        class_df: Filtered DataFrame for one class, sorted by month
        target_col: Column to forecast
        exog_cols: Exogenous regressor columns (None = endogenous-only)
        order: (p, d, q) for SARIMA
        seasonal_order: (P, D, Q, s) for seasonal component (s=12 for monthly)
        horizon_months: How many months to forecast ahead

    Returns:
        ForecastResult with point estimates + 95% CIs
    """
    try:
        from statsmodels.tsa.statespace.sarimax import SARIMAX
    except ImportError as e:
        raise ImportError(
            "statsmodels required for SARIMAX. "
            "Install with: pip install statsmodels"
        ) from e

    # Extract arrays
    pdf = class_df.to_pandas()
    pdf = pdf.sort_values("month").reset_index(drop=True)
    y = pdf[target_col].to_numpy()

    if exog_cols:
        exog = pdf[exog_cols].astype(float).to_numpy()
    else:
        exog = None

    class_id = pdf["class_id"].iloc[0]
    train_end = str(pdf["month"].iloc[-1])
    logger.info(
        f"Fitting SARIMAX for {class_id}: n={len(y)}, "
        f"order={order}, seasonal={seasonal_order}, exog={exog_cols or 'none'}"
    )

    model = SARIMAX(
        y,
        exog=exog,
        order=order,
        seasonal_order=seasonal_order,
        enforce_stationarity=False,
        enforce_invertibility=False,
    )
    fitted = model.fit(disp=False, maxiter=200)

    # Build future exog (simple extrapolation — carry forward last observed)
    if exog is not None:
        last_exog = exog[-1:]
        future_exog = np.tile(last_exog, (horizon_months, 1))
    else:
        future_exog = None

    forecast = fitted.get_forecast(steps=horizon_months, exog=future_exog)
    mean = forecast.predicted_mean
    ci = forecast.conf_int(alpha=0.05)

    # Generate future dates
    last_month = pdf["month"].iloc[-1]
    future_dates = _future_months(last_month, horizon_months)

    return ForecastResult(
        class_id=class_id,
        model_name="SARIMAX" + ("+exog" if exog_cols else ""),
        train_end=train_end,
        horizon_months=horizon_months,
        forecast_dates=[str(d) for d in future_dates],
        forecast_mean=mean.tolist(),
        forecast_lower_95=ci[:, 0].tolist() if hasattr(ci, "shape") else list(ci.iloc[:, 0]),
        forecast_upper_95=ci[:, 1].tolist() if hasattr(ci, "shape") else list(ci.iloc[:, 1]),
        fitted_params={"aic": float(fitted.aic), "bic": float(fitted.bic)},
    )


def _future_months(last_month, n: int) -> list:
    """Generate n months starting after last_month."""
    import datetime as dt

    if isinstance(last_month, dt.date):
        current = last_month
    elif hasattr(last_month, "to_pydatetime"):
        current = last_month.to_pydatetime().date()
    else:
        current = dt.date.fromisoformat(str(last_month)[:10])

    out = []
    for _ in range(n):
        if current.month == 12:
            current = dt.date(current.year + 1, 1, 1)
        else:
            current = dt.date(current.year, current.month + 1, 1)
        out.append(current)
    return out


# ======================================================================
# Evaluation metrics
# ======================================================================


def mape(y_true: np.ndarray, y_pred: np.ndarray, eps: float = 1e-6) -> float:
    """Mean Absolute Percentage Error."""
    y_true = np.asarray(y_true, dtype=float)
    y_pred = np.asarray(y_pred, dtype=float)
    return float(np.mean(np.abs((y_true - y_pred) / (np.abs(y_true) + eps))) * 100)


def smape(y_true: np.ndarray, y_pred: np.ndarray, eps: float = 1e-6) -> float:
    """Symmetric Mean Absolute Percentage Error."""
    y_true = np.asarray(y_true, dtype=float)
    y_pred = np.asarray(y_pred, dtype=float)
    denominator = (np.abs(y_true) + np.abs(y_pred)) / 2 + eps
    return float(np.mean(np.abs(y_true - y_pred) / denominator) * 100)


def mase(y_true: np.ndarray, y_pred: np.ndarray, y_train: np.ndarray, season: int = 12) -> float:
    """Mean Absolute Scaled Error (scaled against seasonal naive on training)."""
    y_true = np.asarray(y_true, dtype=float)
    y_pred = np.asarray(y_pred, dtype=float)
    y_train = np.asarray(y_train, dtype=float)

    if len(y_train) <= season:
        return float("nan")
    scale = np.mean(np.abs(y_train[season:] - y_train[:-season]))
    if scale < 1e-9:
        return float("nan")
    return float(np.mean(np.abs(y_true - y_pred)) / scale)


def evaluate_forecast(
    actual: list[float] | np.ndarray,
    forecast: ForecastResult,
    y_train: list[float] | np.ndarray | None = None,
) -> dict:
    """Compute all metrics for a forecast against held-out actuals."""
    y_true = np.asarray(actual)
    y_pred = np.asarray(forecast.forecast_mean)
    n = min(len(y_true), len(y_pred))
    y_true, y_pred = y_true[:n], y_pred[:n]

    metrics = {
        "mape": mape(y_true, y_pred),
        "smape": smape(y_true, y_pred),
        "rmse": float(np.sqrt(np.mean((y_true - y_pred) ** 2))),
        "mae": float(np.mean(np.abs(y_true - y_pred))),
    }
    if y_train is not None:
        metrics["mase"] = mase(y_true, y_pred, np.asarray(y_train))
    return metrics
