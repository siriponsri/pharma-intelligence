# Experiment 09: XGBoost Baseline

**Status:** Notebook-ready  
**Phase:** 4  
**Engine:** Forecasting

## Objective

Evaluate whether the feature-engineered XGBoost global model handles the current volatility and exogenous structure better than the classical baselines.

## Execution Path

- Colab notebook: `notebooks/02_forecasting_baselines_colab.ipynb`
- Script entry point: `scripts/run_xgboost_baseline.py`
- Main artifacts:
	- `data/processed/xgboost_baseline_results_colab.json`
	- `data/processed/xgboost_predictions_colab.csv`
	- `data/processed/xgboost_feature_importance_colab.csv`

## Notebook Contract

The Colab workflow:

- prepares the engineered feature frame
- uses the last 12 months as holdout
- trains the global XGBoost regressor
- saves overall MAE, RMSE, and MAPE
- saves per-class metrics and feature importance

## Next Update

Replace this placeholder with the measured results after executing the Colab notebook and preserve the reported numbers exactly as produced.
