# Experiment 03: Realistic Mock Data — Root Cause Analysis and Overall Findings

**Date:** 2026-04-22  
**Previous experiments:** `experiment_01_sarimax_baseline.md`, Step A mock-data tuning  
**Branch:** `step-a-improve-mock-data`  
**Objective:** Identify the root cause of the unrealistically easy baseline from Experiment 01, apply realism improvements to the synthetic demand generator, and explain why the revised data improved the plain SARIMAX benchmark while destabilizing SARIMAX with exogenous variables.

## Executive Summary

The root cause of the original problem was that the synthetic demand generator was too smooth, too deterministic, and too tightly coupled to the exogenous anchor series. In the original setup, monthly demand moved in a highly predictable way because prevalence, seasonality, budget effects, and event curves were all low-noise and structurally stable. That allowed a plain seasonal SARIMAX model to reach an unrealistically low average MAPE of 7.13%.

After introducing stronger volatility, regime shifts, substitution dynamics, dampened exogenous elasticity, and less-perfect seasonality, the baseline SARIMAX difficulty moved into a more realistic range: average MAPE increased from 7.13% to 12.74%. This solves the main “too easy baseline” problem.

However, the same realism improvements exposed a second and more important modeling problem: the current SARIMAX+exog design is not robust once the series become structurally noisy. The exogenous specification deteriorated from 21.09% average MAPE to 74.27%, with 3 classes showing catastrophic failures above 100% MAPE. The evidence indicates that this is not a bug in the generator alone; it is a mismatch between the exogenous model design and the revised data-generating process.

## What Changed In The Data Generator

The tuned generator in `src/pharma_intel/forecasting/mock_data.py` now includes the following realism mechanisms.

1. Base monthly noise was increased from 0.05 to 0.15.
2. Per-class noise variation was added so each class can be materially more or less volatile than the base level.
3. Up to 2 regime shifts per class were added with ±20% level changes.
4. Cross-class substitution pressure was added so older classes lose demand share as newer same-area classes mature.
5. Prevalence linkage was weakened: demand now responds with partial elasticity and measurement noise instead of a near-1:1 prevalence ratio.
6. Seasonality is no longer identical year to year; each year has a different seasonal amplitude.
7. COVID and patent-cliff effects were softened and made class-specific.

These changes were applied while holding the model order and the random seed fixed, so the comparison isolates the effect of the synthetic data design rather than a model retune.

## Factual Results

### Before vs after

| Metric | Experiment 01 / Old | Experiment 03 / New | Change |
| --- | ---: | ---: | ---: |
| Baseline average MAPE | 7.13% | 12.74% | +5.61 pp |
| Exog average MAPE | 21.09% | 74.27% | +53.18 pp |
| Classes with MAPE < 8 | 10 | 1 | -9 |
| Classes with MAPE > 18 | 1 | 2 | +1 |
| Exog catastrophic failures > 100% MAPE | 0 | 3 | +3 |

### Classes that still reveal the remaining problems

**Still too easy in baseline**

- `acei`: 6.048% MAPE

**Hard baseline classes**

- `beta_blockers`: 18.925% MAPE
- `glp1`: 25.171% MAPE

**Catastrophic exogenous failures**

- `arbs`: 160.359% MAPE
- `ezetimibe`: 111.738% MAPE
- `sulfonylureas`: 106.126% MAPE

### Full v2 per-class results

| Class | Baseline MAPE | Exog MAPE | Relative effect of exog |
| --- | ---: | ---: | ---: |
| acei | 6.0% | 60.0% | -891.6% |
| arbs | 14.8% | 160.4% | -987.2% |
| beta_blockers | 18.9% | 82.9% | -338.2% |
| ccb | 15.2% | 45.9% | -201.4% |
| diuretics | 9.0% | 84.4% | -840.8% |
| dpp4i | 10.8% | 42.5% | -295.4% |
| ezetimibe | 13.9% | 111.7% | -704.5% |
| fibrates | 8.6% | 76.4% | -785.2% |
| glp1 | 25.2% | 59.3% | -135.6% |
| metformin | 8.3% | 70.2% | -748.8% |
| sglt2i | 11.6% | 11.4% | +2.1% |
| statins | 8.8% | 54.3% | -520.2% |
| sulfonylureas | 14.5% | 106.1% | -629.7% |

The revised data therefore fixed the global baseline difficulty but did not make the exogenous variant healthy. In fact, it made the model-design weakness more visible.

## Root Cause Of The Original Problem

The original baseline was unrealistically strong because the synthetic series were generated with too much structural regularity.

### Root cause 1: Low noise made the monthly path too easy to extrapolate

Originally the generator used low monthly noise and no per-class volatility variation. That meant classes had very smooth month-to-month paths, so a seasonal ARIMA model could extrapolate with very little penalty.

### Root cause 2: Exogenous anchors drove demand too directly

The earlier generator used prevalence factors in a much more deterministic way. In practice, real pharmaceutical demand does not move one-to-one with annual prevalence. It is filtered through diagnosis, prescribing behavior, access, formulary constraints, substitution, and supply noise. The old generator skipped much of that friction.

### Root cause 3: No structural breaks

Before Step A, the series had no explicit regime shifts. Real pharmaceutical markets do experience structural breaks from procurement changes, substitution, pricing shifts, market access changes, and shocks. A series without structural breaks is easier for a stable seasonal model.

### Root cause 4: Seasonality was too regular

The original seasonality curve was perfectly smooth and repeated with a fixed amplitude. Real annual patterns change from year to year. That fixed seasonal template made the baseline too convenient.

### Root cause 5: No competitive erosion between classes

The old generator treated each class too independently. In reality, newer classes can erode older-class share. Without substitution pressure, the demand curves remain simpler and more stationary than they should be.

## Root Cause Of The Remaining Exogenous Failure

The revised generator exposed a separate problem: the current exogenous SARIMAX design is not structurally aligned with the harder data.

### Fact 1: The exogenous model is fitted on only 84 training observations per class

The code in `src/pharma_intel/forecasting/baselines.py` trains each class on 84 months and tests on 12 months. That is a small sample for a seasonal SARIMAX `(1,1,1) × (1,1,1,12)` plus 6 exogenous regressors.

### Fact 2: The exogenous feature set is coarse and weakly aligned to the new sources of variation

The exogenous regressors are:

- `diabetes_prevalence`
- `hypertension_prevalence`
- `dyslipidemia_prevalence`
- `obesity_prevalence`
- `healthcare_budget_index`
- `stockout_days`

These variables do not directly encode the new regime shifts, substitution dynamics, or year-specific seasonality changes that now drive a larger share of the variance.

### Fact 3: Future exogenous values are not forecasted, they are simply carried forward

In `fit_sarimax`, the future exogenous matrix is created by repeating the last observed exogenous row across the full forecast horizon. That means the exogenous model is asked to forecast a more structurally unstable series while assuming the covariates remain flat in the future window.

This is especially problematic after Step A, because the generator now contains structural changes that are not represented in those repeated covariate values.

### Fact 4: The realism changes intentionally weakened the predictive strength of the anchors

The revised generator explicitly dampens prevalence elasticity and injects measurement noise. That is desirable for realism, but it also means the exogenous variables are less directly predictive of the target. In other words, the new generator is doing what it should, but the exogenous model is now relying on weaker signals.

### Fact 5: Exogenous instability is class-dependent

Only one class, `sglt2i`, still slightly benefits from exogenous features. Several others deteriorate badly, and `arbs`, `ezetimibe`, and `sulfonylureas` become catastrophic failures. This is evidence of model instability rather than a uniform data bug.

## Detailed Interpretation

The most important conclusion is that the Step A generator changes were directionally correct. They fixed the primary research problem: the baseline is no longer implausibly easy. The revised average baseline MAPE of 12.74% is much closer to a believable monthly pharma-demand benchmark.

At the same time, Step A revealed that the current exogenous SARIMAX specification is not a reliable benchmark under realistic volatility. This is not a reason to revert the realism improvements. On the contrary, it is a useful finding. A harder and more realistic synthetic environment should expose weak benchmark designs, not protect them.

The remaining baseline miss is small but real: `acei` still has MAPE below 8%. That suggests one older, high-volume hypertension class remains too smooth relative to the target realism band. However, this is now a localized issue, not a global flaw across the whole panel.

The bigger unresolved issue is exogenous overfitting. Once the target is decoupled from prevalence and budget proxies, the exogenous design no longer improves forecast quality and instead amplifies instability. That means future model comparisons should treat the current SARIMAX+exog result as evidence of mismatch, not as a gold-standard exogenous benchmark.

## Acceptance Status

| Criterion | Status | Evidence |
| --- | --- | --- |
| Baseline avg MAPE in [12, 20] | PASS | 12.74% |
| At least 2 classes with MAPE > 18 | PASS | 2 classes |
| No classes with MAPE < 8 | FAIL | `acei` at 6.048% |
| No exog catastrophic failures > 100 | FAIL | `arbs`, `ezetimibe`, `sulfonylureas` |
| Exog still worse than baseline | PASS | 74.27% vs 12.74% |

Overall status: **partial success**.

- The original root cause was found and materially fixed.
- The global realism objective for the plain baseline was achieved.
- The exogenous benchmark remains structurally unstable and is now the dominant unresolved problem.

## Implications For Next Steps

1. Proceeding to Prophet or XGBoost remains justified, because the baseline is no longer artificially easy.
2. The current SARIMAX+exog result should be interpreted as evidence of overfitting and feature-design mismatch, not as a stable exogenous benchmark.
3. If mock-data tuning is revisited later, the next most targeted adjustment is not more global noise. It is focused work on the remaining too-smooth `acei` class and on how substitution/regime effects are represented relative to exogenous proxies.
4. If exogenous modeling is revisited, the root-cause fix is likely in feature design or future-exog handling, not in changing the SARIMAX order for cosmetic improvement.

## Artifacts And Evidence

- Data artifact: `data/processed/mock_demand_history.parquet`
- Old baseline snapshot: `data/processed/sarimax_baseline_results_v1_too_easy.json`
- Old exog snapshot: `data/processed/sarimax_exog_results_v1_too_easy.json`
- New baseline results: `data/processed/sarimax_baseline_results_v2.json`
- New exog results: `data/processed/sarimax_exog_results_v2.json`
- Generator implementation: `src/pharma_intel/forecasting/mock_data.py`
- SARIMAX implementation: `src/pharma_intel/forecasting/baselines.py`
