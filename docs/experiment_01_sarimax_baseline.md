# Experiment 01: SARIMAX Baseline Results

**Date:** 2026-04-21  
**Dataset:** Mock demand, 2018-01 to 2025-12, 13 cardiometabolic classes  
**Models compared:** SARIMAX vs SARIMAX+exogenous features  
**Test horizon:** 12 months held-out

## Summary
Adding the current exogenous feature set did not help overall forecasting accuracy. Average MAPE worsened from 7.1% for the plain SARIMAX baseline to 21.1% for SARIMAX with exogenous features, which is a 195.7% relative increase in error.

## Results Table
| Class | Baseline MAPE | Exog MAPE | Improvement |
| --- | ---: | ---: | ---: |
| acei | 4.6% | 13.6% | -196.0% |
| arbs | 4.3% | 10.4% | -141.1% |
| beta_blockers | 3.4% | 15.7% | -367.1% |
| ccb | 4.2% | 43.1% | -925.1% |
| diuretics | 6.1% | 50.4% | -723.9% |
| dpp4i | 13.4% | 8.9% | 33.5% |
| ezetimibe | 3.5% | 5.7% | -62.6% |
| fibrates | 5.5% | 56.5% | -931.2% |
| glp1 | 24.7% | 16.8% | 31.8% |
| metformin | 4.1% | 25.1% | -507.3% |
| sglt2i | 8.8% | 11.5% | -30.8% |
| statins | 6.1% | 6.5% | -8.1% |
| sulfonylureas | 4.0% | 9.8% | -143.9% |
| AVERAGE | 7.1% | 21.1% | -195.7% |

## Per-Class Observations
- Best performing class: beta_blockers (lowest observed MAPE: 3.4% in baseline SARIMAX)
- Worst performing class: fibrates (highest observed MAPE: 56.5% in SARIMAX+exogenous)
- Classes where exog helped most: dpp4i (+33.5%), glp1 (+31.8%); no third class improved
- Classes where exog hurt performance: fibrates (-931.2%), ccb (-925.1%), diuretics (-723.9%), metformin (-507.3%), beta_blockers (-367.1%), acei (-196.0%), sulfonylureas (-143.9%), arbs (-141.1%), ezetimibe (-62.6%), sglt2i (-30.8%), statins (-8.1%)

## Interpretation
The plain seasonal SARIMAX baseline is substantially more stable on this synthetic monthly panel than the version with the current exogenous regressors. With only 84 training observations per class and several correlated external features, the exogenous specification appears to add noise and estimation instability rather than signal; this is consistent with the convergence warning observed during the exogenous run.

## Next Steps
- [ ] Try Prophet baseline for comparison
- [ ] Add XGBoost with richer feature engineering
- [ ] Longer horizon test (24 and 36 months)
- [ ] Run Diebold-Mariano test for statistical significance