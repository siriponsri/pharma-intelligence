"""Tests for forecasting module."""

from __future__ import annotations

import numpy as np
import polars as pl
import pytest


class TestMoleculeClasses:
    def test_all_classes_registered(self):
        from pharma_intel.forecasting.molecule_classes import ALL_CLASSES

        assert len(ALL_CLASSES) >= 10

    def test_diabetes_classes_exist(self):
        from pharma_intel.forecasting.molecule_classes import classes_for_area

        dm = classes_for_area("diabetes")
        ids = [c.class_id for c in dm]
        assert "metformin" in ids
        assert "sglt2i" in ids
        assert "dpp4i" in ids
        assert "glp1" in ids

    def test_all_members_are_strings(self):
        from pharma_intel.forecasting.molecule_classes import ALL_CLASSES

        for cls in ALL_CLASSES:
            assert all(isinstance(m, str) for m in cls.members)

    def test_get_class_invalid(self):
        from pharma_intel.forecasting.molecule_classes import get_class

        with pytest.raises(KeyError):
            get_class("nonexistent")

    def test_get_class_valid(self):
        from pharma_intel.forecasting.molecule_classes import get_class

        c = get_class("sglt2i")
        assert c.therapeutic_area == "diabetes"


class TestAnchors:
    def test_prevalence_lookup(self):
        from pharma_intel.forecasting.anchors import get_prevalence

        # Known year
        val = get_prevalence("diabetes_prevalence", 2020)
        assert 8 < val < 15

    def test_prevalence_extrapolation(self):
        from pharma_intel.forecasting.anchors import get_prevalence

        # Future year — should extrapolate
        val = get_prevalence("diabetes_prevalence", 2030)
        # Should be increasing trend
        assert val > get_prevalence("diabetes_prevalence", 2025)

    def test_market_shares_sum_reasonable(self):
        from pharma_intel.forecasting.anchors import CLASS_MARKET_SHARE_BY_AREA

        for area, shares in CLASS_MARKET_SHARE_BY_AREA.items():
            total = sum(shares.values())
            # Should be ≤1.0 (remainder allowed for other classes)
            assert 0.7 <= total <= 1.0, f"{area}: {total}"


class TestMockDataGeneration:
    @pytest.fixture(scope="class")
    def df(self) -> pl.DataFrame:
        from pharma_intel.forecasting import GeneratorConfig, generate_demand_panel

        cfg = GeneratorConfig(
            start_date="2020-01-01",
            end_date="2021-12-31",
            random_seed=42,
        )
        return generate_demand_panel(config=cfg)

    def test_output_is_dataframe(self, df):
        assert isinstance(df, pl.DataFrame)
        assert len(df) > 0

        cvs = []
        for class_id in df["class_id"].unique().to_list():
            class_data = df.filter(pl.col("class_id") == class_id)["units_kddd"]
            cvs.append(class_data.std() / class_data.mean())
        assert min(cvs) > 0

    def test_required_columns(self, df):
        required = {
            "month",
            "class_id",
            "therapeutic_area",
            "channel",
            "units_kddd",
            "revenue_thb_million",
            "diabetes_prevalence",
            "hypertension_prevalence",
            "healthcare_budget_index",
        }
        assert required.issubset(set(df.columns))

    def test_no_negative_demand(self, df):
        assert df["units_kddd"].min() >= 0

    def test_all_classes_present(self, df):
        from pharma_intel.forecasting.molecule_classes import ALL_CLASSES

        expected_ids = {c.class_id for c in ALL_CLASSES}
        actual_ids = set(df["class_id"].unique())
        assert expected_ids == actual_ids

    def test_reproducibility(self):
        from pharma_intel.forecasting import GeneratorConfig, generate_demand_panel

        cfg = GeneratorConfig(
            start_date="2020-01-01",
            end_date="2020-06-30",
            random_seed=123,
        )
        df1 = generate_demand_panel(config=cfg)
        df2 = generate_demand_panel(config=cfg)
        assert df1.equals(df2)

    def test_realistic_noise_level(self, df):
        """Generated data should show class-level variation within the tuned realism band."""
        for class_id in df["class_id"].unique().to_list():
            class_data = df.filter(pl.col("class_id") == class_id)["units_kddd"]
            cv = class_data.std() / class_data.mean()
            assert 0.45 <= cv <= 0.60, f"{class_id}: CV={cv:.3f} out of realistic range"


class TestMetrics:
    def test_mape_perfect_forecast(self):
        from pharma_intel.forecasting import mape

        y = np.array([100, 200, 300])
        assert mape(y, y) == pytest.approx(0.0)

    def test_mape_constant_error(self):
        from pharma_intel.forecasting import mape

        y_true = np.array([100.0, 100.0, 100.0])
        y_pred = np.array([110.0, 110.0, 110.0])
        assert mape(y_true, y_pred) == pytest.approx(10.0, abs=0.1)

    def test_smape_symmetric(self):
        from pharma_intel.forecasting import smape

        y_true = np.array([100.0, 200.0])
        y_pred = np.array([90.0, 220.0])
        # Symmetric, should be positive
        v1 = smape(y_true, y_pred)
        v2 = smape(y_pred, y_true)
        assert v1 == pytest.approx(v2, abs=0.1)

    def test_mase_needs_sufficient_training(self):
        from pharma_intel.forecasting import mase

        y_true = np.array([100.0, 105.0])
        y_pred = np.array([102.0, 107.0])
        # Training too short → NaN
        y_train = np.array([100.0, 101.0])  # only 2 points, season=12
        result = mase(y_true, y_pred, y_train, season=12)
        assert np.isnan(result)
