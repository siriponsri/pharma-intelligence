# Experiment Registry

This file is the top-level experiment ledger for the project. Use it to trace why an experiment was run, which method was used, how it was evaluated, where the artifacts were written, and which report or slide deck should cite it.

## Rules

- One experiment ID per report file under `docs/`.
- Keep raw outputs in `data/processed/` or `notebooks/results/` and summarize them here.
- Update the `Status`, `Artifacts`, and `Summary` columns immediately after each run.
- Never overwrite historical conclusions; add a new experiment file if the question changes materially.

## Registry

| ID | Phase | Engine | Title | Primary Method | Main Evaluation | Status | Report |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 01 | 1 | Forecasting | SARIMAX baseline | Seasonal SARIMAX, with and without exog | MAPE, sMAPE, MASE, RMSE | Complete | `docs/experiment_01_sarimax_baseline.md` |
| 02 | 1 | Forecasting | Realistic mock data iteration | Synthetic demand redesign + SARIMAX rerun | Baseline difficulty shift, hard/easy class counts | Complete | `docs/experiment_02_realistic_mock.md` |
| 03 | 1 | Forecasting | Realistic mock root cause analysis | Evidence review across generator and SARIMAX behavior | Root cause analysis, acceptance review | Complete | `docs/experiment_03_realistic_mock.md` |
| 04 | 2 | Shared Data | Real public data integration | Public-source ingestion, mapping, validation | Completeness, sanity checks, field coverage | Planned | `docs/experiment_04_real_data_integration.md` |
| 05 | 3 | RAG | Thai regulatory RAG build | Thai-source ingestion + bilingual retrieval | Retrieval quality, citation quality, latency | Planned | `docs/experiment_05_thai_rag.md` |
| 06 | 3 | RAG | RAG evaluation set | Structured bilingual QA benchmark | Faithfulness, groundedness, retrieval metrics | Complete (Orange Book slice) | `docs/experiment_06_rag_evaluation.md` |
| 07 | 3 | RAG | LLM benchmark | ThaiLLM vs Claude on identical retrieval context | Answer quality, citation quality, language match | Planned | `docs/experiment_07_llm_benchmark.md` |
| 08 | 4 | Forecasting | Prophet baseline | Prophet with tuned seasonality and regressors | MAPE, sMAPE, MASE, RMSE | Planned | `docs/experiment_08_prophet.md` |
| 09 | 4 | Forecasting | XGBoost baseline | Tabular gradient boosting with engineered features | Backtest metrics, feature importance | Planned | `docs/experiment_09_xgboost.md` |
| 10 | 4 | Forecasting | TFT benchmark | Temporal Fusion Transformer | Backtest metrics, calibration, uncertainty | Planned | `docs/experiment_10_tft.md` |
| 11 | 4 | Forecasting | Ablation study | Remove groups of features and signals | Delta in metrics, contribution analysis | Planned | `docs/experiment_11_ablation_study.md` |
| 12 | 4 | Forecasting | Final benchmark | Unified comparison across all forecasting methods | Final benchmark table and significance checks | Planned | `docs/experiment_12_final_benchmark.md` |

## Slide Mapping

| Use Case | Recommended Source |
| --- | --- |
| Advisor progress update | `docs/master_plan.md`, `docs/next_steps.md`, this registry |
| Thesis chapter methods | `docs/experiment_template.md` plus per-experiment methodology sections |
| Thesis chapter results | Experiment reports 01-12 |
| GPO demo deck | Experiment 04-07 for intelligence, 08-12 for forecasting |
