"""Tests for Phase 4 forecasting scaffolds."""

from __future__ import annotations

import numpy as np
import polars as pl

from pharma_intel.forecasting import GeneratorConfig, aggregate_to_class_monthly, generate_demand_panel
from pharma_intel.forecasting.evaluation import diebold_mariano, rolling_origin_splits
from pharma_intel.forecasting.feature_engineering import build_global_features
from pharma_intel.forecasting.prophet_baseline import prophet_available
from pharma_intel.forecasting.tft_model import build_tft_training_config, prepare_tft_frame, tft_dependencies_available
from pharma_intel.forecasting.xgboost_model import prepare_training_frame, xgboost_available


class TestForecastingScaffolds:
    def test_feature_engineering_adds_expected_columns(self):
        panel = generate_demand_panel(
            config=GeneratorConfig(start_date="2020-01-01", end_date="2022-12-31", random_seed=42)
        )
        class_month = aggregate_to_class_monthly(panel)

        features = build_global_features(class_month)

        assert {"lag_1", "lag_12", "rolling_mean_3", "yoy_growth", "thai_fiscal_quarter"} <= set(features.columns)
        assert len(features) == len(class_month)

    def test_training_frame_keeps_rows_after_lag_filter(self):
        panel = generate_demand_panel(
            config=GeneratorConfig(start_date="2019-01-01", end_date="2023-12-31", random_seed=42)
        )
        class_month = aggregate_to_class_monthly(panel)

        training_frame = prepare_training_frame(class_month)

        assert len(training_frame) > 0
        assert "lag_12" in training_frame.columns

    def test_rolling_origin_splits_returns_windows(self):
        frame = pl.DataFrame({"month": list(range(12)), "value": list(range(12))})

        splits = rolling_origin_splits(frame, min_train_rows=6, test_rows=2, step_rows=2)

        assert len(splits) == 3
        assert len(splits[0][0]) == 6
        assert len(splits[0][1]) == 2

    def test_diebold_mariano_returns_valid_probability(self):
        result = diebold_mariano(np.array([1.0, 2.0, 3.0, 4.0]), np.array([1.5, 2.5, 3.5, 4.5]))

        assert isinstance(result["dm_stat"], float)
        assert 0.0 <= result["p_value"] <= 1.0

    def test_optional_model_surfaces_are_import_safe(self):
        assert isinstance(prophet_available(), bool)
        assert isinstance(xgboost_available(), bool)
        assert isinstance(tft_dependencies_available(), bool)

    def test_tft_config_builds_without_gpu_runtime(self):
        panel = generate_demand_panel(
            config=GeneratorConfig(start_date="2020-01-01", end_date="2022-12-31", random_seed=42)
        )
        class_month = aggregate_to_class_monthly(panel)

        prepared = prepare_tft_frame(class_month)
        config = build_tft_training_config(class_month)

        assert "time_idx" in prepared.columns
        assert config["n_rows"] == len(prepared)
        assert config["n_groups"] > 0