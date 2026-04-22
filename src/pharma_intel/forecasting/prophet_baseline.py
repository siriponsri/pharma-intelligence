"""Prophet baseline wrapper for class-level monthly demand forecasting."""

from __future__ import annotations

import polars as pl

from pharma_intel.forecasting.baselines import ForecastResult


def prophet_available() -> bool:
    """Return whether Prophet is installed in the current environment."""
    try:
        import prophet  # noqa: F401
    except ImportError:
        return False
    return True


def fit_prophet_baseline(
    class_df: pl.DataFrame,
    target_col: str = "units_kddd",
    exog_cols: list[str] | None = None,
    horizon_months: int = 24,
) -> ForecastResult:
    """Fit Prophet on one class time series and return the standardized forecast result."""
    if not prophet_available():
        raise RuntimeError("Prophet is not installed. Install the forecasting extra to run this baseline.")

    from prophet import Prophet

    pdf = class_df.to_pandas().sort_values("month").reset_index(drop=True)
    if pdf.empty:
        raise ValueError("class_df must contain at least one row")

    regressors = exog_cols or []
    model = Prophet(yearly_seasonality=True, weekly_seasonality=False, daily_seasonality=False)
    for regressor in regressors:
        model.add_regressor(regressor)

    train_frame = pdf.rename(columns={"month": "ds", target_col: "y"})
    model.fit(train_frame[["ds", "y", *regressors]])

    future = model.make_future_dataframe(periods=horizon_months, freq="MS")
    for regressor in regressors:
        future[regressor] = train_frame[regressor].iloc[-1]

    forecast_pdf = model.predict(future).tail(horizon_months)
    future_dates = forecast_pdf["ds"].astype(str).tolist()
    class_id = str(pdf["class_id"].iloc[0])

    return ForecastResult(
        class_id=class_id,
        model_name="Prophet" + ("+exog" if regressors else ""),
        train_end=str(train_frame["ds"].iloc[-1]),
        horizon_months=horizon_months,
        forecast_dates=future_dates,
        forecast_mean=forecast_pdf["yhat"].astype(float).tolist(),
        forecast_lower_95=forecast_pdf["yhat_lower"].astype(float).tolist(),
        forecast_upper_95=forecast_pdf["yhat_upper"].astype(float).tolist(),
        fitted_params={"n_train_rows": int(len(train_frame)), "n_regressors": len(regressors)},
    )
