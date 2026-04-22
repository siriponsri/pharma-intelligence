"""XGBoost global-model scaffold for class-level forecasting."""

from __future__ import annotations

import polars as pl

from pharma_intel.forecasting.feature_engineering import build_global_features

NUMERIC_DTYPES = {
    pl.Int8,
    pl.Int16,
    pl.Int32,
    pl.Int64,
    pl.UInt8,
    pl.UInt16,
    pl.UInt32,
    pl.UInt64,
    pl.Float32,
    pl.Float64,
    pl.Boolean,
}


def xgboost_available() -> bool:
    """Return whether XGBoost is installed in the current environment."""
    try:
        import xgboost  # noqa: F401
    except ImportError:
        return False
    return True


def prepare_training_frame(df: pl.DataFrame, target_col: str = "units_kddd") -> pl.DataFrame:
    """Build the global model frame with engineered features and complete lag history."""
    frame = build_global_features(df, target_col=target_col)
    return frame.drop_nulls(subset=["lag_1", "lag_12"])


def infer_feature_columns(df: pl.DataFrame, target_col: str = "units_kddd") -> list[str]:
    """Infer numeric feature columns suitable for XGBoost training."""
    excluded = {"month", "class_id", "therapeutic_area", target_col}
    return sorted(
        column_name
        for column_name, data_type in df.schema.items()
        if column_name not in excluded and data_type in NUMERIC_DTYPES
    )


def fit_xgboost_global_model(
    train_df: pl.DataFrame,
    target_col: str = "units_kddd",
    feature_cols: list[str] | None = None,
) -> dict:
    """Fit a simple global XGBoost regressor and return model metadata."""
    if not xgboost_available():
        raise RuntimeError("XGBoost is not installed. Install the forecasting extra to run this baseline.")
    if train_df.is_empty():
        raise ValueError("train_df must contain at least one row")

    from xgboost import XGBRegressor

    chosen_features = feature_cols or infer_feature_columns(train_df, target_col=target_col)
    if not chosen_features:
        raise ValueError("No numeric features available for training")

    features = train_df.select(
        [pl.col(column_name).cast(pl.Float64, strict=False).fill_null(0.0).alias(column_name) for column_name in chosen_features]
    )
    target = train_df.select(pl.col(target_col).cast(pl.Float64)).to_numpy().ravel()

    model = XGBRegressor(
        n_estimators=300,
        max_depth=6,
        learning_rate=0.05,
        subsample=0.9,
        colsample_bytree=0.9,
        objective="reg:squarederror",
        random_state=42,
    )
    model.fit(features.to_numpy(), target)

    return {
        "model": model,
        "feature_columns": chosen_features,
        "n_rows": len(train_df),
        "target_col": target_col,
    }
