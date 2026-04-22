"""Demand forecasting module.

Public API:
    generate_demand_panel — create synthetic demand history
    aggregate_to_class_monthly — collapse channels for class-level forecasting
    fit_sarimax — baseline SARIMAX forecaster
    evaluate_forecast — compute MAPE/sMAPE/MASE/RMSE
    ForecastResult — standardized output dataclass
    ALL_CLASSES — molecule class registry
"""

from pharma_intel.forecasting.baselines import (
    ForecastResult,
    aggregate_to_class_monthly,
    evaluate_forecast,
    fit_sarimax,
    mape,
    mase,
    smape,
)
from pharma_intel.forecasting.evaluation import diebold_mariano, rolling_origin_splits
from pharma_intel.forecasting.feature_engineering import build_global_features
from pharma_intel.forecasting.mock_data import GeneratorConfig, generate_demand_panel
from pharma_intel.forecasting.molecule_classes import ALL_CLASSES, CLASSES_BY_ID, MoleculeClass
from pharma_intel.forecasting.prophet_baseline import fit_prophet_baseline, prophet_available
from pharma_intel.forecasting.tft_model import build_tft_training_config, prepare_tft_frame, tft_dependencies_available
from pharma_intel.forecasting.xgboost_model import (
    fit_xgboost_global_model,
    infer_feature_columns,
    prepare_training_frame,
    xgboost_available,
)

__all__ = [
    # Mock data
    "generate_demand_panel",
    "GeneratorConfig",
    # Classes
    "ALL_CLASSES",
    "CLASSES_BY_ID",
    "MoleculeClass",
    # Forecasting
    "fit_sarimax",
    "aggregate_to_class_monthly",
    "ForecastResult",
    "evaluate_forecast",
    "build_global_features",
    "rolling_origin_splits",
    "diebold_mariano",
    "mape",
    "smape",
    "mase",
    "prophet_available",
    "fit_prophet_baseline",
    "xgboost_available",
    "prepare_training_frame",
    "infer_feature_columns",
    "fit_xgboost_global_model",
    "tft_dependencies_available",
    "prepare_tft_frame",
    "build_tft_training_config",
]
