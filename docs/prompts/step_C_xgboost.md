# Copilot Agent Prompt — Step C: XGBoost with Feature Engineering (PLACEHOLDER)

> **Status:** PLANNED — not ready to execute yet.
> **Prerequisites:** Steps A and B must be complete and merged. Prophet baseline must show realistic, non-catastrophic behavior.
> **When ready:** I will update this file with the full prompt. Do NOT run this prompt in its current form.

---

## Why this is a placeholder

Step C introduces substantially more code complexity:

1. **Feature engineering module** — lag features, rolling windows, calendar features, categorical encoding for class_id
2. **Train/test split strategy** — must handle global model (all classes in one model) carefully
3. **Hyperparameter tuning** — need to decide on search strategy (Optuna? random search? manual?)
4. **Evaluation at multiple horizons** — 12, 24, 36 months (not just 12)
5. **Feature importance reporting** — needed for the paper

I want to design this carefully with input from the Steps A and B results before committing to the full prompt.

---

## Expected scope (for planning purposes only)

After Step B reveals how Prophet compares to SARIMAX, Step C will address:

- Can a tree-based model with richer features beat Prophet?
- Which exogenous features are most important?
- Does using class_id as a categorical feature (global model) help over per-class models?
- What happens at longer horizons (24, 36 months)?

---

## Research angle for paper

Step C sets up the argument for Step D (TFT):

> *"XGBoost with lag features achieves X% MAPE at 24 months. However, it treats each horizon prediction independently and cannot capture the temporal dependency structure that a sequence-aware model (TFT) exploits."*

This motivates TFT as the final model.

---

## Placeholder structure (subject to revision)

When activated, Step C will likely include:

- Task 0: Planning
- Task 1: Branching
- Task 2: Create `feature_engineering.py` module
- Task 3: Create `xgboost_baseline.py` module
- Task 4: Create `scripts/run_xgboost_baseline.py`
- Task 5: Add tests
- Task 6: Run experiments (endog, exog, per-horizon)
- Task 7: Feature importance report
- Task 8: Write `experiment_09_xgboost.md`
- Task 9: Commit

Estimated budget: 40–50 tool invocations (larger than Steps A/B due to feature engineering complexity)

---

**Do not execute until explicitly activated.**

If Copilot Agent is asked to run this file as-is, respond with:

> "This prompt is a placeholder. Step C is not ready. Please request the updated version after reviewing Step B results."
