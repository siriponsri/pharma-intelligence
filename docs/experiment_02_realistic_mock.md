# Experiment 02: Realistic Mock Data Iteration

**Date:** 2026-04-22  
**Phase:** 1  
**Engine:** Forecasting  
**Motivation:** Experiment 01 showed that the original synthetic monthly demand was too easy for seasonal SARIMAX, producing an average baseline MAPE of 7.13%.

## Objective

Increase the realism of the synthetic demand panel so the plain SARIMAX baseline lands closer to a believable monthly pharmaceutical forecasting range.

## Method Changes

- Increased base monthly noise and added per-class volatility variation.
- Added regime shifts to create structural breaks.
- Added cross-class substitution pressure.
- Reduced direct prevalence elasticity and injected measurement noise.
- Added year-specific seasonality variation.
- Softened and randomized COVID and patent-cliff effects.

## Results

| Metric | Old | New | Change |
| --- | ---: | ---: | ---: |
| Baseline avg MAPE | 7.13% | 12.74% | +5.61 pp |
| Exog avg MAPE | 21.09% | 74.27% | +53.18 pp |
| Classes with MAPE < 8 | 10 | 1 | -9 |
| Classes with MAPE > 18 | 1 | 2 | +1 |

## Interpretation

The realism objective for the plain baseline succeeded. The data are materially harder and closer to the intended benchmark range. However, the exogenous SARIMAX benchmark became much less stable under the revised series, which indicates that the original exogenous design depended on overly clean signal structure.

## Evaluation

- Primary metrics: MAPE, sMAPE, MASE, RMSE
- Acceptance criteria used:
  - baseline average MAPE in `[12, 20]`
  - at least 2 hard classes with MAPE `> 18`
  - no classes below `8%` MAPE
  - no catastrophic exog failures above `100%` MAPE

## Artifacts

- `data/processed/mock_demand_history.parquet`
- `data/processed/sarimax_baseline_results_v2.json`
- `data/processed/sarimax_exog_results_v2.json`
- Follow-up analysis: `docs/experiment_03_realistic_mock.md`
