# Experiment 02: Realistic Mock Data — SARIMAX Re-evaluation

**Date:** 2026-04-22  
**Previous experiment:** `experiment_01_sarimax_baseline.md`  
**Branch:** `step-a-improve-mock-data`  
**Motivation:** Experiment 01 revealed baseline SARIMAX average MAPE of 7.1%, which was unrealistically low for monthly pharmaceutical demand. The working hypothesis was that the synthetic demand panel was too clean and too directly linked to the exogenous anchors.

## Changes to Mock Data Generator

The generator in `src/pharma_intel/forecasting/mock_data.py` was updated to make the monthly series less deterministic and more structurally realistic.

- Increased base monthly noise from 5% to 15%.
- Added per-class noise variation so each class has a distinct volatility profile.
- Added up to 2 regime shifts per class with ±20% level changes.
- Added cross-class substitution pressure so older classes lose share as newer same-area classes mature.
- Decoupled prevalence from demand by reducing elasticity to 0.5 and injecting measurement noise.
- Replaced perfectly stable seasonality with year-specific seasonal amplitude variation.
- Softened patent-cliff and COVID curves while allowing class-specific response multipliers.
- Preserved the original SARIMAX specification and random seed (`42`) to isolate the effect to the data generator only.

## Results: Before vs After

| Metric | Old (v1) | New (v2) | Change |
| --- | ---: | ---: | ---: |
| Baseline avg MAPE | 7.1% | 12.7% | +5.6 pp |
| Exog avg MAPE | 21.1% | 74.3% | +53.2 pp |
| Catastrophic exog failures (>100% MAPE) | 0 | 3 | +3 |
| Classes with MAPE < 8% (too easy) | 10 | 1 | -9 |
| Classes with MAPE > 18% (hard) | 1 | 2 | +1 |

## Per-Class Results (v2)

| Class | Baseline MAPE | Exog MAPE | Improvement % |
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
| sglt2i | 11.6% | 11.4% | 2.1% |
| statins | 8.8% | 54.3% | -520.2% |
| sulfonylureas | 14.5% | 106.1% | -629.7% |

## Interpretation

The main objective of Step A was to move the plain seasonal SARIMAX baseline into a more realistic difficulty range. On that specific target, the generator improvement worked: average baseline MAPE increased from 7.1% to 12.7%, which now falls inside the desired 12% to 20% band. The number of obviously too-easy classes also dropped sharply from 10 to 1, and the number of genuinely hard classes increased from 1 to 2.

The cost of that realism increase is that the exogenous SARIMAX specification became much less stable. The exogenous model average MAPE deteriorated from 21.1% to 74.3%, and 3 classes crossed the >100% catastrophic-failure threshold. This strongly suggests that once the synthetic data stopped being overly smooth, the current exogenous feature set became even more vulnerable to overfitting and estimation instability under only 84 training observations per class.

This result is still useful for the research pipeline. The baseline is no longer artificially flattering, so future Prophet and XGBoost comparisons will be harder to game by accident. At the same time, the exogenous SARIMAX result is now a clearer warning sign that the current exogenous design should not be treated as a strong benchmark. The next model comparisons should focus on whether Prophet or tree-based methods can absorb the increased structural noise more gracefully than SARIMAX+exog.

The most important surprise is that the generator can be made realistically hard for the plain baseline without producing a balanced exogenous benchmark. That means Step A only partially succeeded: it solved the “too clean baseline” problem but exposed an even stronger exogenous instability problem.

## Acceptance Criteria

- [x] Baseline avg MAPE in [12, 20]: PASS — 12.74%
- [x] At least 2 classes with MAPE > 18: PASS — 2 classes
- [ ] No classes with MAPE < 8: FAIL — 1 class
- [ ] No catastrophic exog failures (>100%): FAIL — 3 failures
- [x] Exog still worse than baseline (overfitting still present): PASS — 61.53 pp worse

## Artifacts

- Data: `data/processed/mock_demand_history.parquet` (regenerated, local artifact)
- Results: `data/processed/sarimax_baseline_results_v2.json`, `data/processed/sarimax_exog_results_v2.json` (local artifacts)
- Code: working tree on branch `step-a-improve-mock-data` at report generation time

## Next Steps

- [ ] Proceed to Step B — Prophet baseline
- [ ] Consider class-specific tuning of regime shift frequency or amplitude
- [ ] Revisit whether the exogenous feature set should be simplified before using it as a benchmark
