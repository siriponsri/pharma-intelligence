# Copilot Agent Prompt — Step B: Prophet Baseline

> **Prerequisites:** Step A must be complete and merged. Verify with `git log --oneline -10` that `fix(mock): increase realism...` commit exists.
> **Instructions for the human:** Copy this entire file into Copilot Agent after Step A is reviewed and merged.
> **Mode:** Autonomous — Copilot executes all commands and commits changes.

---

## 🎯 Mission

Add a Prophet forecasting baseline as a second comparator to SARIMAX. Prophet's Bayesian prior should prevent the catastrophic overfitting we saw with SARIMAX+exogenous.

**Expected outcome:** Prophet with exogenous regressors stays stable (avg MAPE ~10–18%), unlike SARIMAX+exog which overfit badly. This establishes the paper's argument that classical statistical models are brittle with exog features, motivating ML/DL methods.

**Budget:** Up to 25 tool invocations. Stop if exceeded.

---

## 📋 Required Context — READ BEFORE STARTING

1. **Re-read `.github/copilot-instructions.md`** — anti-patterns apply.
2. **Read `docs/experiment_02_realistic_mock.md`** — know the current SARIMAX numbers.
3. **Read `src/pharma_intel/forecasting/baselines.py`** — this is the SARIMAX pattern you'll mirror for Prophet.
4. **Read `scripts/run_sarimax_baseline.py`** — Prophet script will mirror this structure.
5. **Read `src/pharma_intel/forecasting/__init__.py`** — know what's currently exported.

---

## ✅ Before You Start

### Task 0 — Planning phase (DO NOT execute)

After reading, write a plan addressing:

1. **Module structure** — propose where Prophet code goes (should be a NEW file `prophet_baseline.py`, not mixed into `baselines.py`)
2. **API shape** — what the `fit_prophet()` function signature will look like (match `fit_sarimax()` as closely as possible)
3. **Exog handling** — how you'll pass exog columns to Prophet's `add_regressor`
4. **Future exog** — how you'll extend exog values for the forecast window (same carry-forward strategy as SARIMAX)
5. **Known issues** — Prophet requires pandas DataFrames with specific column names (`ds`, `y`); address this cleanly

**STOP and wait for my "go."**

---

## 🔧 Task 1 — Branching

```powershell
git checkout main
git pull  # if remote exists; otherwise skip
git checkout -b step-b-prophet-baseline
git status   # expect clean

# Verify Step A results are in place
ls data\processed\sarimax_baseline_results_v2.json
ls data\processed\sarimax_exog_results_v2.json
```

**STOP condition:** If v2 result files are missing, stop — Step A wasn't completed.

---

## 🔧 Task 2 — Verify Prophet is installed

Prophet was added to the `forecasting` optional extra. Verify:

```powershell
python -c "from prophet import Prophet; print('Prophet version:', Prophet.__module__)"
```

**If import fails:** Prophet install can be tricky on Windows (requires cmdstanpy backend). Run:
```powershell
pip install prophet
python -c "from prophet import Prophet; m = Prophet(); print('Prophet OK')"
```

If still fails, STOP and report — may need system-level compiler setup.

---

## 🔧 Task 3 — Create `prophet_baseline.py`

Create new file `src/pharma_intel/forecasting/prophet_baseline.py`:

```python
"""Prophet baseline forecaster.

Second baseline alongside SARIMAX. Prophet uses an additive decomposable
model (trend + seasonality + holidays + exog) with Bayesian priors on
changepoints — this regularization is hypothesized to prevent the
catastrophic overfitting observed when SARIMAX is combined with exogenous
features.

Reference: Taylor & Letham (2018), "Forecasting at Scale"
"""

from __future__ import annotations

import warnings

import numpy as np
import pandas as pd
import polars as pl

from pharma_intel.common import logger
from pharma_intel.forecasting.baselines import ForecastResult, _future_months

# Silence Prophet's verbose cmdstanpy logging
import logging as _logging
_logging.getLogger("cmdstanpy").setLevel(_logging.WARNING)
_logging.getLogger("prophet").setLevel(_logging.WARNING)


def fit_prophet(
    class_df: pl.DataFrame,
    target_col: str = "units_kddd",
    exog_cols: list[str] | None = None,
    horizon_months: int = 24,
    seasonality_mode: str = "multiplicative",
    changepoint_prior_scale: float = 0.05,
) -> ForecastResult:
    """Fit Prophet on a single class time series.

    Args:
        class_df: Filtered DataFrame for one class, sorted by month.
        target_col: Column to forecast.
        exog_cols: Exogenous regressor columns (None = endogenous-only).
        horizon_months: How many months to forecast ahead.
        seasonality_mode: 'multiplicative' or 'additive'. Multiplicative is
            typical for demand data where seasonal effects scale with level.
        changepoint_prior_scale: Prior on changepoint magnitude. Lower =
            more regularization. Default 0.05 (Prophet default is 0.05).

    Returns:
        ForecastResult with point estimates + 95% CIs.
    """
    from prophet import Prophet

    pdf = class_df.to_pandas().sort_values("month").reset_index(drop=True)
    class_id = pdf["class_id"].iloc[0]

    # Prophet requires columns named 'ds' (date) and 'y' (target)
    prophet_df = pdf[["month", target_col]].rename(
        columns={"month": "ds", target_col: "y"}
    )
    prophet_df["ds"] = pd.to_datetime(prophet_df["ds"])

    # Add exog columns if present
    if exog_cols:
        for col in exog_cols:
            prophet_df[col] = pdf[col].astype(float).values

    train_end = str(pdf["month"].iloc[-1])
    logger.info(
        f"Fitting Prophet for {class_id}: n={len(prophet_df)}, "
        f"mode={seasonality_mode}, exog={exog_cols or 'none'}"
    )

    # Fit
    model = Prophet(
        seasonality_mode=seasonality_mode,
        changepoint_prior_scale=changepoint_prior_scale,
        yearly_seasonality=True,
        weekly_seasonality=False,  # monthly data
        daily_seasonality=False,
        interval_width=0.95,
    )
    if exog_cols:
        for col in exog_cols:
            model.add_regressor(col)

    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        model.fit(prophet_df)

    # Build future dataframe
    future_dates = _future_months(pdf["month"].iloc[-1], horizon_months)
    future_df = pd.DataFrame({"ds": pd.to_datetime(future_dates)})

    if exog_cols:
        # Carry forward last observed exog values (same strategy as SARIMAX)
        last_exog = pdf[exog_cols].iloc[-1]
        for col in exog_cols:
            future_df[col] = last_exog[col]

    forecast = model.predict(future_df)

    return ForecastResult(
        class_id=class_id,
        model_name="Prophet" + ("+exog" if exog_cols else ""),
        train_end=train_end,
        horizon_months=horizon_months,
        forecast_dates=[str(d) for d in future_dates],
        forecast_mean=forecast["yhat"].tolist(),
        forecast_lower_95=forecast["yhat_lower"].tolist(),
        forecast_upper_95=forecast["yhat_upper"].tolist(),
        fitted_params={
            "seasonality_mode": seasonality_mode,
            "changepoint_prior_scale": changepoint_prior_scale,
            "n_changepoints": int(len(model.changepoints)),
        },
    )
```

**Critical:** `_future_months` is imported from `baselines.py` — do NOT duplicate it.

---

## 🔧 Task 4 — Update `forecasting/__init__.py`

Add Prophet exports. Modify `src/pharma_intel/forecasting/__init__.py`:

```python
# Add to imports:
from pharma_intel.forecasting.prophet_baseline import fit_prophet

# Add to __all__:
__all__ = [
    # ... existing ...
    "fit_prophet",
]
```

---

## 🔧 Task 5 — Create `scripts/run_prophet_baseline.py`

Mirror `scripts/run_sarimax_baseline.py` closely. Create `scripts/run_prophet_baseline.py`:

```python
"""Fit Prophet baseline on mock demand and evaluate forecast quality.

Usage:
    python scripts\run_prophet_baseline.py
    python scripts\run_prophet_baseline.py --class-id sglt2i --horizon 24
    python scripts\run_prophet_baseline.py --with-exog
"""

from __future__ import annotations

import json
from pathlib import Path

import polars as pl
import typer
from rich.console import Console
from rich.table import Table

from pharma_intel.common import logger, settings
from pharma_intel.forecasting import (
    CLASSES_BY_ID,
    aggregate_to_class_monthly,
    evaluate_forecast,
    fit_prophet,
)

app = typer.Typer(add_completion=False)
console = Console()

EXOG_FEATURES = [
    "diabetes_prevalence",
    "hypertension_prevalence",
    "dyslipidemia_prevalence",
    "obesity_prevalence",
    "healthcare_budget_index",
    "stockout_days",
]


@app.command()
def main(
    class_id: str | None = typer.Option(None, "--class-id"),
    input_path: Path | None = typer.Option(None, "--input"),
    horizon: int = typer.Option(24, "--horizon"),
    test_months: int = typer.Option(12, "--test-months"),
    with_exog: bool = typer.Option(False, "--with-exog"),
    output: Path | None = typer.Option(None, "--output"),
):
    """Fit Prophet, forecast, and evaluate on held-out data."""
    settings.ensure_dirs()
    input_path = input_path or (settings.processed_dir / "mock_demand_history.parquet")

    if not input_path.exists():
        console.print(f"[red]Error:[/red] {input_path} not found")
        raise typer.Exit(1)

    logger.info(f"Loading demand panel from {input_path}")
    df = pl.read_parquet(input_path)
    class_df = aggregate_to_class_monthly(df)

    target_classes = [class_id] if class_id else sorted(class_df["class_id"].unique().to_list())
    exog_cols = EXOG_FEATURES if with_exog else None
    model_label = "Prophet+exog" if with_exog else "Prophet"

    results: list[dict] = []

    for cid in target_classes:
        if cid not in CLASSES_BY_ID:
            logger.warning(f"Unknown class '{cid}', skipping")
            continue

        class_data = class_df.filter(pl.col("class_id") == cid).sort("month")
        if len(class_data) < 36:
            logger.warning(f"{cid}: insufficient history")
            continue

        train = class_data.head(len(class_data) - test_months)
        test = class_data.tail(test_months)

        try:
            forecast = fit_prophet(
                train,
                target_col="units_kddd",
                exog_cols=exog_cols,
                horizon_months=test_months,
            )
        except Exception as e:
            logger.error(f"{cid}: fit failed — {e}")
            continue

        metrics = evaluate_forecast(
            actual=test["units_kddd"].to_list(),
            forecast=forecast,
            y_train=train["units_kddd"].to_list(),
        )

        results.append(
            {
                "class_id": cid,
                "display_name": CLASSES_BY_ID[cid].display_name,
                "model": model_label,
                "n_train": len(train),
                "n_test": len(test),
                "horizon_months": test_months,
                **{k: round(v, 3) for k, v in metrics.items()},
            }
        )

    # Display table
    table = Table(title=f"{model_label} Forecast Evaluation ({test_months}-month held-out)")
    table.add_column("Class", style="cyan")
    table.add_column("MAPE %", justify="right", style="yellow")
    table.add_column("sMAPE %", justify="right")
    table.add_column("MASE", justify="right")
    table.add_column("RMSE", justify="right")

    for r in sorted(results, key=lambda x: x.get("mape", 999)):
        table.add_row(
            r["class_id"],
            f"{r['mape']:.1f}",
            f"{r['smape']:.1f}",
            f"{r.get('mase', float('nan')):.2f}",
            f"{r['rmse']:,.0f}",
        )
    console.print(table)

    if results:
        avg_mape = sum(r["mape"] for r in results) / len(results)
        console.print(f"\n[bold]Average MAPE: {avg_mape:.2f}%[/bold]")

    if output:
        output.write_text(json.dumps(results, indent=2, ensure_ascii=False), encoding="utf-8")
        console.print(f"\n[green]✓ Saved to {output}[/green]")


if __name__ == "__main__":
    app()
```

---

## 🔧 Task 6 — Add tests

Create `tests/test_prophet.py`:

```python
"""Smoke tests for Prophet baseline."""
from __future__ import annotations

import pytest


class TestProphetBaseline:
    def test_import(self):
        """Prophet and our wrapper must import."""
        from pharma_intel.forecasting import fit_prophet  # noqa: F401

    def test_fit_smoke(self):
        """Tiny fit run — verify end-to-end works without crashing."""
        pytest.importorskip("prophet")
        import polars as pl
        from datetime import date
        from pharma_intel.forecasting import fit_prophet

        # Small synthetic series — 36 months, single class
        months = [date(2020 + i // 12, i % 12 + 1, 1) for i in range(36)]
        df = pl.DataFrame({
            "month": months,
            "class_id": ["test_class"] * 36,
            "therapeutic_area": ["diabetes"] * 36,
            "units_kddd": [100 + i * 2 + (i % 12) * 5 for i in range(36)],
            "diabetes_prevalence": [10.0] * 36,
            "stockout_days": [0] * 36,
        })

        result = fit_prophet(
            df,
            target_col="units_kddd",
            exog_cols=None,
            horizon_months=6,
        )

        assert result.class_id == "test_class"
        assert result.model_name == "Prophet"
        assert len(result.forecast_mean) == 6
        assert len(result.forecast_lower_95) == 6
        assert len(result.forecast_upper_95) == 6
        # Prophet should produce positive forecasts here
        assert all(v > 0 for v in result.forecast_mean)

    def test_fit_with_exog(self):
        pytest.importorskip("prophet")
        import polars as pl
        from datetime import date
        from pharma_intel.forecasting import fit_prophet

        months = [date(2020 + i // 12, i % 12 + 1, 1) for i in range(36)]
        df = pl.DataFrame({
            "month": months,
            "class_id": ["test_class"] * 36,
            "therapeutic_area": ["diabetes"] * 36,
            "units_kddd": [100 + i * 2 for i in range(36)],
            "diabetes_prevalence": [10.0 + i * 0.01 for i in range(36)],
        })

        result = fit_prophet(
            df,
            exog_cols=["diabetes_prevalence"],
            horizon_months=6,
        )
        assert result.model_name == "Prophet+exog"
        assert len(result.forecast_mean) == 6
```

Run tests:
```powershell
pytest tests\test_prophet.py -v
pytest -v   # full suite — ensure no regressions
```

**STOP condition:** If any test fails, stop and report. Do NOT modify tests to make them pass.

---

## 🔧 Task 7 — Run Prophet baselines

```powershell
# Prophet endogenous only
python scripts\run_prophet_baseline.py --output data\processed\prophet_baseline_results.json

# Prophet with exog
python scripts\run_prophet_baseline.py --with-exog --output data\processed\prophet_exog_results.json
```

Expected runtime: 3–5 minutes total (Prophet is slower to fit than SARIMAX, especially first run).

---

## ✅ Task 8 — Validate and compare

Run this validation script:

```powershell
python -c "
import json

# Load all 4 result sets (2 SARIMAX + 2 Prophet)
s_base = json.load(open('data/processed/sarimax_baseline_results_v2.json'))
s_exog = json.load(open('data/processed/sarimax_exog_results_v2.json'))
p_base = json.load(open('data/processed/prophet_baseline_results.json'))
p_exog = json.load(open('data/processed/prophet_exog_results.json'))

def avg_mape(rs): return sum(r['mape'] for r in rs) / len(rs)
def catastrophic(rs, thresh=100): return sum(1 for r in rs if r['mape'] > thresh)

print(f'{\"Model\":<20} {\"Avg MAPE\":>10} {\"# catastrophic (>100%)\":>22}')
print('-' * 55)
print(f'{\"SARIMAX\":<20} {avg_mape(s_base):>9.1f}% {catastrophic(s_base):>22}')
print(f'{\"SARIMAX+exog\":<20} {avg_mape(s_exog):>9.1f}% {catastrophic(s_exog):>22}')
print(f'{\"Prophet\":<20} {avg_mape(p_base):>9.1f}% {catastrophic(p_base):>22}')
print(f'{\"Prophet+exog\":<20} {avg_mape(p_exog):>9.1f}% {catastrophic(p_exog):>22}')
print()

# Acceptance criteria
p_base_range = 10 <= avg_mape(p_base) <= 22
p_exog_stable = catastrophic(p_exog) == 0
p_exog_not_terrible = avg_mape(p_exog) <= avg_mape(p_base) * 2

print(f'Prophet baseline avg in [10, 22]: {p_base_range}')
print(f'Prophet+exog has no catastrophic failures: {p_exog_stable}')
print(f'Prophet+exog <= 2x Prophet baseline: {p_exog_not_terrible}')
"
```

### Acceptance criteria

- Prophet baseline avg MAPE in [10%, 22%] — realistic range
- Prophet+exog has zero catastrophic failures (>100% MAPE)
- Prophet+exog MAPE ≤ 2× Prophet baseline (shows regularization is working, even if exog adds some noise)

### Decision tree

**If all pass:** Continue to Task 9.

**If Prophet baseline > 22% (unexpectedly high):**
- Check if Prophet converged — look at warnings in log
- Try `seasonality_mode='additive'` and rerun
- Max 1 retry — if still high, report honestly

**If Prophet+exog shows catastrophic failure (rare but possible):**
- Check Prophet version — older versions handle regressors differently
- Try `changepoint_prior_scale=0.01` (stronger regularization)
- Max 1 retry

**If tests fail:** STOP. Don't modify tests.

---

## 🔧 Task 9 — Write experiment report

Create `docs/experiment_08_prophet.md`:

```markdown
# Experiment 08: Prophet Baseline vs SARIMAX

**Date:** [today YYYY-MM-DD]
**Previous:** `experiment_02_realistic_mock.md` (SARIMAX on calibrated mock)
**Branch:** step-b-prophet-baseline
**Goal:** Introduce second baseline (Prophet) to test hypothesis that Bayesian regularization prevents the overfitting catastrophe seen with SARIMAX+exog.

## Results Summary

| Model | Avg MAPE | # Catastrophic (>100%) | Notes |
| --- | ---: | ---: | --- |
| SARIMAX | [X]% | [X] | From experiment 02 |
| SARIMAX+exog | [X]% | [X] | Overfitting expected |
| Prophet | [X]% | [X] | Bayesian additive |
| Prophet+exog | [X]% | [X] | Regularized regressors |

## Per-Class Results — Prophet

| Class | Prophet MAPE | Prophet+exog MAPE | Improvement |
| --- | ---: | ---: | ---: |
[Full table for all 13 classes]

## Key Finding

[1–2 paragraphs. The key narrative should be something like:
"SARIMAX+exog suffers catastrophic overfitting on [N] classes (MAPE >100%),
while Prophet+exog maintains stability (worst class: X%). This supports our
hypothesis that Prophet's Bayesian changepoint prior regularizes the exog
coefficients, whereas SARIMAX's maximum likelihood estimation over-commits
to spurious correlations in the 84-observation training window."]

## Statistical vs ML Comparison (Qualitative)

| Property | SARIMAX | Prophet |
| --- | --- | --- |
| Parameter estimation | Maximum likelihood | Bayesian (Stan) |
| Exog regularization | None | Implicit via changepoint prior |
| Handles missing data | Poorly | Gracefully |
| Convergence issues observed | Yes (exog run) | No |
| Training time per class | ~1s | ~10-20s |
| Interpretability | High (ARIMA coeffs) | High (decomposition) |

## Acceptance Criteria

- [ ] Prophet baseline avg MAPE in [10, 22]: [PASS/FAIL — X%]
- [ ] Prophet+exog zero catastrophic failures: [PASS/FAIL — X failures]
- [ ] Prophet+exog ≤ 2x baseline: [PASS/FAIL]
- [ ] All pytest tests pass: [PASS/FAIL — N/M]

## Open Questions

[Any oddities observed. E.g.:
- Prophet showed unexpected negative forecasts on class X — investigate
- Changepoint prior may need per-class tuning
- Yearly seasonality may be too aggressive given only 7 years of data]

## Next Steps

- [ ] Step C: XGBoost with feature engineering (richer feature space, tree regularization)
- [ ] After XGBoost: TFT on Vast AI GPU
- [ ] Diebold-Mariano test for significance (introduced in Step D)

## Artifacts

- Code: `src/pharma_intel/forecasting/prophet_baseline.py`
- Script: `scripts/run_prophet_baseline.py`
- Tests: `tests/test_prophet.py`
- Results: `data/processed/prophet_baseline_results.json`, `data/processed/prophet_exog_results.json`
- Commit: [hash]
```

Fill in all brackets with actual values.

---

## 🔧 Task 10 — Commit and report

```powershell
git add -A

git commit -m "feat(is1): add Prophet baseline with exogenous regressor support

- New module: src/pharma_intel/forecasting/prophet_baseline.py
- New script: scripts/run_prophet_baseline.py
- Tests: tests/test_prophet.py (3 smoke tests)
- Exports: fit_prophet added to forecasting.__init__

Result: Prophet baseline avg MAPE [X]%, Prophet+exog [Y]%
Key finding: Prophet's Bayesian regularization prevents the SARIMAX+exog
catastrophic overfitting ([Z] failures -> 0 failures).
Refs: docs/experiment_08_prophet.md"

git log --oneline -5
git diff main --stat
```

### Final report

```
## Step B Completion Report

### New files
- src/pharma_intel/forecasting/prophet_baseline.py
- scripts/run_prophet_baseline.py
- tests/test_prophet.py
- docs/experiment_08_prophet.md

### Key results
- SARIMAX+exog avg MAPE: [X]% ([N] catastrophic failures)
- Prophet+exog avg MAPE: [Y]% ([M] catastrophic failures)
- Hypothesis supported: [YES/NO — explain]

### Acceptance
- All criteria: [PASS/FAIL]
- Unit tests: [N/M passed]

### Ready for
Step C (XGBoost) — awaiting your approval to proceed.
```

---

## 🚫 Anti-patterns (reminder)

- ❌ Do NOT tune `changepoint_prior_scale` beyond 1 retry to make results prettier
- ❌ Do NOT remove classes with bad MAPE
- ❌ Do NOT duplicate `_future_months` or `mape`/`smape`/`mase` functions — import from `baselines.py`
- ❌ Do NOT write Prophet-specific metrics — reuse existing ones
- ❌ Do NOT modify SARIMAX code
- ❌ Do NOT modify mock data generator
- ❌ Do NOT modify `anchors.py` or `molecule_classes.py`

---

## ❓ Common issues

- **Prophet install fails on Windows:** Needs C++ compiler. If `pip install prophet` fails, stop and ask me.
- **Prophet is very slow:** First fit can take 30+ seconds. This is normal. Total for 13 classes × 2 configs = ~10 minutes worst case.
- **Negative forecasts:** Prophet can produce negative values for low-demand classes. This is a Prophet limitation — document it, don't hack around it.
- **cmdstanpy warnings:** Normal, already silenced in the module.

---

**When complete, say:**

```
✅ Step B complete. Report: [final report]
Awaiting approval for Step C (XGBoost).
```
