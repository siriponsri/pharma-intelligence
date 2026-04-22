# Experiment 08: Prophet Baseline

**Status:** Notebook-ready  
**Phase:** 4  
**Engine:** Forecasting

## Objective

Benchmark Prophet against the SARIMAX baseline on the cardiometabolic class-month panel using the same 12-month holdout structure and the same evaluation metrics.

## Execution Path

- Colab notebook: `notebooks/02_forecasting_baselines_colab.ipynb`
- Script entry point: `scripts/run_prophet_baseline.py`
- Main artifacts:
	- `data/processed/prophet_baseline_results_colab.json`
	- `data/processed/prophet_baseline_results_colab.csv`

## Notebook Contract

The Colab workflow runs two Prophet variants:

- endogenous only
- Prophet with the current exogenous feature set

The notebook saves per-class metrics and a compact summary covering:

- MAPE
- sMAPE
- MASE
- RMSE

## Next Update

Replace this placeholder with the measured results after executing the Colab notebook and preserve the reported numbers exactly as produced.
