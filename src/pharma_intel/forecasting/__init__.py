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
from pharma_intel.forecasting.mock_data import GeneratorConfig, generate_demand_panel
from pharma_intel.forecasting.molecule_classes import ALL_CLASSES, CLASSES_BY_ID, MoleculeClass

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
    "mape",
    "smape",
    "mase",
]
