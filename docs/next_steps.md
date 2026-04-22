# Next Steps Roadmap — Post Experiment 01

**Status as of:** 2026-04-21
**Current phase:** IS1 — Forecasting engine development
**Last experiment:** `docs/experiment_01_sarimax_baseline.md`

This document is for **humans** (you, advisor, future self). The matching machine-executable prompts for Copilot Agent are in `docs/prompts/`.

---

## 📊 Where We Are

Experiment 01 revealed two critical findings:

1. **Baseline MAPE = 7.1%** — suspiciously low. Pharmaceutical forecasting literature typically reports 10–20% for monthly molecule-class demand. Our mock data appears too "clean" — signal-to-noise ratio is unrealistically high.
2. **SARIMAX + exogenous MAPE = 21.1%** — catastrophic overfitting, not a finding about "exog doesn't help." Some classes exploded to -900% improvement (fibrates, ccb, diuretics) with convergence warnings.

### Root causes
- Noise sigma = 5% is too low for real pharma demand
- Prevalence trends are near-linear → SARIMAX fits trivially
- 84 training observations vs 12 parameters = 7 obs/param (rule of thumb: ≥15)
- Exogenous features are too correlated with target (prevalence drives demand directly in our generator)
- No cross-class substitution dynamics (real pharma: SGLT2i uptake reduces DPP4i share)

### Why this is actually good news
This is a **valid and publishable failure mode**. The paper can discuss:
> *"Classical statistical forecasters (SARIMAX) with exogenous regressors are highly sensitive to the signal-to-noise ratio and observation-to-parameter ratio. In realistic pharmaceutical monthly demand settings, this motivates using ML/DL methods (Prophet, XGBoost, TFT) with built-in regularization."*

This is section 4.1 "Baseline failure modes" in the paper. Don't erase it — build on it.

---

## 🎯 Next 2 Steps (Scope 2)

### Step A — Improve mock data realism
**Goal:** Baseline SARIMAX MAPE should land in **12–20%** range (realistic for monthly pharma demand)

**What changes:**
- Increase `monthly_noise_sigma` from 0.05 → default 0.12, with per-class variation
- Add **regime shifts** — 1–2 structural breaks per class (new formulary inclusion, supply disruption) not explainable by exog features alone
- Add **cross-class substitution** — when a new class launches, older same-area classes see gradual share loss
- **Decouple** exog from target — don't use prevalence directly; use a delayed, noisy version
- Add **holiday/budget-cycle spikes** that are irregular year-to-year (not perfect sinusoids)
- Keep patent cliff and COVID shock but soften into more gradual curves

**Validation criteria (Copilot must verify after change):**
- Rerun SARIMAX baseline → average MAPE ∈ [12%, 20%]
- At least 2 classes should have MAPE > 18% (hard cases)
- No class should have MAPE < 8% (too easy)
- Rerun SARIMAX + exog → should still be **worse** than baseline (overfitting confirmed), but not catastrophic (no class > 100% MAPE)

**Deliverables:**
- Updated `src/pharma_intel/forecasting/mock_data.py`
- New `docs/experiment_02_realistic_mock.md` with before/after comparison
- Updated data files in `data/processed/`

---

### Step B — Add Prophet baseline
**Goal:** Establish second baseline with different modeling philosophy (additive Bayesian vs SARIMA state-space)

**What's new:**
- Module `src/pharma_intel/forecasting/prophet_baseline.py`
- Script `scripts/run_prophet_baseline.py`
- Prophet accepts exog via `add_regressor()` with built-in regularization → should NOT overfit like SARIMAX did

**Expected outcomes:**
- Prophet endogenous MAPE: 10–18%
- Prophet + exog MAPE: should be close to or slightly better than Prophet endogenous
- Thesis: "Prophet's Bayesian prior prevents the catastrophic overfitting observed in SARIMAX+exog"

**Deliverables:**
- `src/pharma_intel/forecasting/prophet_baseline.py` (fit_prophet + ForecastResult)
- `scripts/run_prophet_baseline.py` (CLI mirroring sarimax script)
- Updated `src/pharma_intel/forecasting/__init__.py` (export new functions)
- `tests/test_prophet.py` (smoke tests — don't require real training)
- `docs/experiment_08_prophet.md` with comparison table

---

## 🗓️ Realistic Timeline

| Phase | Duration | Owner | Output |
|---|---|---|---|
| Step A (Copilot Agent) | 2–4 hours | Copilot autonomous + you review diff | Updated mock + rerun + experiment_02 doc |
| You review Step A | 30 min | You | Approve or request changes |
| Step B (Copilot Agent) | 3–5 hours | Copilot autonomous + you review diff | Prophet module + rerun + experiment_03 doc |
| You review Step B | 30 min | You | Approve or request changes |
| Paper draft — failure modes section | 1 hour | You | 1-page draft |

Total: roughly 1 working day, split across two sessions.

---

## 📋 How to Execute (for the human)

### Before starting Copilot Agent for Step A

1. Make sure you're on a clean git branch:
```powershell
git checkout -b step-a-improve-mock-data
git status   # should be clean
```

2. Confirm `pytest -v` passes on current main:
```powershell
pytest -v
```

3. Open Copilot Agent in VS Code (💬 icon → select "Agent" from top dropdown)

4. Paste the contents of `docs/prompts/step_A_fix_mock_data.md` into the Agent chat

5. Review the plan Copilot proposes BEFORE giving approval to proceed

### After Step A completes

1. Review the diff:
```powershell
git diff main
```

2. Verify acceptance criteria in the experiment doc
3. If happy, merge:
```powershell
git checkout main
git merge step-a-improve-mock-data
```

4. Tag the state:
```powershell
git tag -a v0.2.0-step-a -m "Realistic mock data; SARIMAX baseline calibrated"
```

5. Repeat for Step B.

---

## 🚧 Things that are OUT of scope for this round

- XGBoost with feature engineering (Step C — next round)
- TFT implementation (Step D — after Step C)
- Thai scrapers (TFDA, ราชกิจจา) — IS2 territory
- RAG evaluation framework — IS2 territory
- Streamlit dashboard — final integration phase
- GPO data access negotiations — parallel human task

Do NOT let Copilot drift into these. The prompts are designed to STOP if Copilot tries.

---

## 📚 References for Methodology Review

When writing experiment reports, cite these concepts:

- **Overfitting in time-series with exogenous features:** Hyndman & Athanasopoulos, *Forecasting: Principles and Practice* (3rd ed), Ch. 9
- **Realistic pharma forecasting benchmarks:** IQVIA and McKinsey publish 10–20% MAPE norms for monthly molecule-level demand
- **Observation-to-parameter ratio:** Box-Jenkins literature; general rule ≥15 obs per estimated parameter
- **Prophet's regularization:** Taylor & Letham (2018), "Forecasting at Scale" — prior on changepoints and seasonality
- **Diebold-Mariano test:** For pairwise forecast comparison, we'll introduce this in Step D

---

## ✅ Success Criteria for This Round

After Steps A + B are complete, you should be able to say in a paragraph:

> *"We generate synthetic monthly demand for 13 cardiometabolic molecule classes anchored to Thai public health statistics. Our baseline SARIMAX achieves X% average MAPE at 12-month horizon. Adding exogenous features (prevalence, budget, stockout) causes overfitting under SARIMAX (avg MAPE Y%) but is stable under Prophet (avg MAPE Z%). This motivates our use of ML/DL methods that scale to higher-dimensional feature spaces."*

Where X, Y, Z are actual numbers from your experiments.

That paragraph alone is the foundation of paper Section 4 "Baseline Evaluation."
