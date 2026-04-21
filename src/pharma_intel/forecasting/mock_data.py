"""Mock demand data generator.

Generates realistic-looking monthly demand time series for cardiometabolic
molecule classes in Thailand. Anchored to public prevalence/budget statistics
so that the SHAPE of the data is defensible, even though specific values
are synthetic.

Output schema (long format):
    month: date (first of month)
    class_id: str — molecule class identifier
    therapeutic_area: str
    channel: str — gpo_direct | hospital_public | hospital_private | retail
    units_kddd: float — thousand defined daily doses
    revenue_thb_million: float — approximate revenue
    stockout_days: int — supply disruption proxy
    competitor_launch_flag: bool — new competitor launched this month
    patent_cliff_flag: bool — patent cliff event within 6mo window
    regulation_change_flag: bool — NLEM/TFDA change this month
    diabetes_prevalence: float
    hypertension_prevalence: float
    dyslipidemia_prevalence: float
    obesity_prevalence: float
    healthcare_budget_index: float

Usage:
    from pharma_intel.forecasting.mock_data import generate_demand_panel
    df = generate_demand_panel(start="2018-01-01", end="2025-12-31")
    df.write_parquet("data/processed/mock_demand.parquet")
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime, timedelta

import numpy as np
import polars as pl

from pharma_intel.common import logger
from pharma_intel.forecasting.anchors import (
    ANNUAL_MARKET_SIZE_KDDD,
    CLASS_MARKET_SHARE_BY_AREA,
    HEALTHCARE_BUDGET_INDEX_TH,
    get_prevalence,
)
from pharma_intel.forecasting.molecule_classes import ALL_CLASSES, MoleculeClass

# Channel mix for typical Thai cardiometabolic generic
CHANNEL_MIX = {
    "gpo_direct": 0.15,  # direct GPO sales to gov hospitals
    "hospital_public": 0.45,  # other public hospitals procurement
    "hospital_private": 0.25,
    "retail": 0.15,  # pharmacy retail
}

# Approximate revenue per thousand-DDD by class (THB thousands/kDDD)
# Higher for new patent-protected, lower for old generics
REVENUE_PER_KDDD_THB = {
    "metformin": 800,
    "sulfonylureas": 900,
    "dpp4i": 6_500,  # branded, expensive
    "sglt2i": 9_000,  # still branded
    "glp1": 18_000,  # very expensive biologic-ish
    "acei": 1_200,
    "arbs": 2_200,
    "ccb": 1_500,
    "beta_blockers": 1_100,
    "diuretics": 700,
    "statins": 1_800,  # atorvastatin/simvastatin cheap, rosuvastatin pricier
    "ezetimibe": 5_500,
    "fibrates": 1_600,
}


@dataclass
class GeneratorConfig:
    """Configuration for mock data generation."""

    start_date: str = "2018-01-01"
    end_date: str = "2025-12-31"
    random_seed: int = 42

    # Noise parameters
    monthly_noise_sigma: float = 0.05  # ~5% monthly variance
    seasonality_amplitude: float = 0.08  # 8% peak-to-trough

    # Class-level correlation (same class moves together across channels)
    class_correlation: float = 0.75

    # Event probabilities
    stockout_prob_per_month: float = 0.03  # 3% chance per month
    regulation_change_prob: float = 0.015  # 1.5% chance per month

    # Inject COVID shock 2020-03 to 2020-09
    inject_covid_shock: bool = True
    covid_impact: float = -0.15  # -15% during worst months

    # Patent cliff effect: when patent expires, class demand jumps
    patent_cliff_boost: float = 0.35  # +35% within 18 months of expiry
    patent_cliff_window_months: int = 18


# ======================================================================
# Core generator
# ======================================================================


def generate_demand_panel(
    start: str | None = None,
    end: str | None = None,
    config: GeneratorConfig | None = None,
) -> pl.DataFrame:
    """Generate monthly demand panel for all cardiometabolic molecule classes.

    Returns a long-format DataFrame with one row per (month, class, channel).
    """
    cfg = config or GeneratorConfig()
    if start:
        cfg.start_date = start
    if end:
        cfg.end_date = end

    rng = np.random.default_rng(cfg.random_seed)
    months = _month_range(cfg.start_date, cfg.end_date)
    logger.info(
        f"Generating mock demand: {len(months)} months × "
        f"{len(ALL_CLASSES)} classes × {len(CHANNEL_MIX)} channels = "
        f"{len(months) * len(ALL_CLASSES) * len(CHANNEL_MIX):,} rows"
    )

    rows: list[dict] = []
    for molecule_class in ALL_CLASSES:
        series = _generate_class_series(molecule_class, months, cfg, rng)
        rows.extend(series)

    df = pl.DataFrame(rows)
    logger.info(f"Generated {len(df):,} rows")
    return df


def _generate_class_series(
    cls: MoleculeClass,
    months: list[date],
    cfg: GeneratorConfig,
    rng: np.random.Generator,
) -> list[dict]:
    """Generate monthly series for one molecule class, all channels."""
    area = cls.therapeutic_area
    annual_total_kddd = ANNUAL_MARKET_SIZE_KDDD[area]
    class_share = CLASS_MARKET_SHARE_BY_AREA[area].get(cls.class_id, 0.05)

    # Monthly base (annual total / 12)
    monthly_base_kddd = (annual_total_kddd * class_share) / 12

    # Class-specific shocks (shared across channels via correlation)
    class_shock = rng.normal(0, cfg.monthly_noise_sigma, size=len(months))

    rows: list[dict] = []
    for idx, month in enumerate(months):
        # 1. Trend from prevalence
        year = month.year
        prevalence = get_prevalence(cls.growth_driver, year)
        # Normalize: 2019 prevalence = baseline 1.0
        prev_2019 = get_prevalence(cls.growth_driver, 2019)
        prevalence_factor = prevalence / prev_2019 if prev_2019 > 0 else 1.0

        # 2. Launch ramp — if class is new to Thai market, gradual ramp up
        years_since_launch = year - cls.first_launch_th_year
        launch_factor = 1.0 if years_since_launch >= 10 else _sigmoid_ramp(years_since_launch)

        # 3. Seasonality — public hospital Q4 budget spike + flu season
        month_num = month.month
        seasonality = 1.0 + cfg.seasonality_amplitude * np.cos(
            2 * np.pi * (month_num - 10) / 12  # peak in October (Q4 budget)
        )

        # 4. Budget effect
        budget_idx = HEALTHCARE_BUDGET_INDEX_TH.get(year, 100)
        budget_2019 = HEALTHCARE_BUDGET_INDEX_TH[2019]
        budget_factor = (budget_idx / budget_2019) ** 0.5  # sqrt dampening

        # 5. COVID shock
        covid_factor = 1.0
        if cfg.inject_covid_shock:
            covid_factor = _covid_shock(month, cfg.covid_impact)

        # 6. Patent cliff effect
        patent_cliff_flag = False
        cliff_factor = 1.0
        for expiry_year in cls.key_patent_expiries.values():
            months_to_expiry = (expiry_year - year) * 12 + (1 - month_num)
            if abs(months_to_expiry) <= cfg.patent_cliff_window_months:
                patent_cliff_flag = True
                # Ramp up demand as patent approaches and after expiry
                cliff_factor *= 1 + cfg.patent_cliff_boost * _cliff_curve(
                    months_to_expiry, cfg.patent_cliff_window_months
                )

        # 7. Random events
        stockout_days = 0
        if rng.random() < cfg.stockout_prob_per_month:
            stockout_days = int(rng.integers(3, 14))

        competitor_launch_flag = bool(
            rng.random() < 0.01 + (0.005 if patent_cliff_flag else 0)
        )
        regulation_change_flag = bool(rng.random() < cfg.regulation_change_prob)

        # Stockout reduces observed demand
        stockout_factor = 1.0 - (stockout_days / 30) * 0.5

        # 8. Combine all factors
        total_factor = (
            prevalence_factor
            * launch_factor
            * seasonality
            * budget_factor
            * covid_factor
            * cliff_factor
            * stockout_factor
        )

        # 9. Noise (class-correlated + channel-specific)
        class_noise = class_shock[idx]

        # Per-channel split
        for channel, channel_share in CHANNEL_MIX.items():
            channel_noise = rng.normal(0, cfg.monthly_noise_sigma * 0.5)
            # Weighted combination of class + channel noise
            combined_noise = (
                cfg.class_correlation * class_noise
                + (1 - cfg.class_correlation) * channel_noise
            )

            units = max(
                0,
                monthly_base_kddd * channel_share * total_factor * (1 + combined_noise),
            )
            revenue = (units * REVENUE_PER_KDDD_THB[cls.class_id]) / 1_000  # THB millions

            # Prevalences (same for all rows at same month)
            rows.append(
                {
                    "month": month,
                    "class_id": cls.class_id,
                    "therapeutic_area": area,
                    "channel": channel,
                    "units_kddd": round(units, 2),
                    "revenue_thb_million": round(revenue, 2),
                    "stockout_days": stockout_days,
                    "competitor_launch_flag": competitor_launch_flag,
                    "patent_cliff_flag": patent_cliff_flag,
                    "regulation_change_flag": regulation_change_flag,
                    "diabetes_prevalence": round(get_prevalence("diabetes_prevalence", year), 2),
                    "hypertension_prevalence": round(
                        get_prevalence("hypertension_prevalence", year), 2
                    ),
                    "dyslipidemia_prevalence": round(
                        get_prevalence("dyslipidemia_prevalence", year), 2
                    ),
                    "obesity_prevalence": round(get_prevalence("obesity_prevalence", year), 2),
                    "healthcare_budget_index": float(budget_idx),
                }
            )

    return rows


# ======================================================================
# Helpers
# ======================================================================


def _month_range(start: str, end: str) -> list[date]:
    """Generate list of first-of-month dates between start and end inclusive."""
    start_dt = datetime.strptime(start, "%Y-%m-%d").date()
    end_dt = datetime.strptime(end, "%Y-%m-%d").date()

    months = []
    current = date(start_dt.year, start_dt.month, 1)
    while current <= end_dt:
        months.append(current)
        # Advance by one month
        if current.month == 12:
            current = date(current.year + 1, 1, 1)
        else:
            current = date(current.year, current.month + 1, 1)
    return months


def _sigmoid_ramp(years: int) -> float:
    """Smooth ramp-up for newly launched drug classes. Returns 0..1."""
    if years < 0:
        return 0.05  # pre-launch tiny baseline
    # Logistic curve: reaches ~90% by year 6
    return 1 / (1 + np.exp(-0.8 * (years - 3)))


def _covid_shock(month: date, impact: float) -> float:
    """Return multiplicative factor for COVID-era disruption."""
    shock_start = date(2020, 3, 1)
    shock_peak = date(2020, 6, 1)
    shock_end = date(2020, 10, 1)

    if month < shock_start or month > shock_end:
        return 1.0

    # Triangular shape
    if month <= shock_peak:
        days_in = (month - shock_start).days
        peak_days = (shock_peak - shock_start).days
        intensity = days_in / peak_days if peak_days > 0 else 0
    else:
        days_out = (shock_end - month).days
        recovery_days = (shock_end - shock_peak).days
        intensity = days_out / recovery_days if recovery_days > 0 else 0

    return 1.0 + impact * intensity


def _cliff_curve(months_to_expiry: int, window: int) -> float:
    """Shape of patent cliff effect.

    Before expiry: build-up (generic manufacturers preparing)
    At expiry: peak
    After expiry: sustained elevation declining slowly
    """
    if months_to_expiry > 0:
        # Approaching expiry — ramp up
        return (1 - months_to_expiry / window) ** 2
    else:
        # After expiry — decay back over twice the window
        return max(0, 1 - abs(months_to_expiry) / (window * 2))


# ======================================================================
# Convenience wrappers
# ======================================================================


def generate_and_save(
    output_path: str | None = None,
    config: GeneratorConfig | None = None,
) -> pl.DataFrame:
    """Generate demand panel and save to Parquet."""
    from pharma_intel.common import settings

    settings.ensure_dirs()

    df = generate_demand_panel(config=config)

    if output_path is None:
        output_path = str(settings.processed_dir / "mock_demand_history.parquet")

    df.write_parquet(output_path)
    logger.info(f"Saved mock demand panel to {output_path}")
    return df
