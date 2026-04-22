# Copilot Agent Prompt — Step A: Improve Mock Data Realism

> **Instructions for the human:** Copy this entire file's contents into the Copilot Agent chat in VS Code. Agent mode must be selected (top dropdown of chat panel).
> **Mode:** Autonomous — Copilot executes all commands and commits changes. You review diffs afterwards via `git log` / `git diff`.

---

## 🎯 Mission

The current mock demand generator produces data that is too "clean" — SARIMAX baseline achieves 7.1% MAPE on average, which is unrealistically low for monthly pharmaceutical demand. This invalidates downstream comparisons (baseline vs exog, baseline vs ML, baseline vs TFT).

**Your task:** Modify the mock data generator to produce more realistic demand series, then rerun SARIMAX baselines to verify the fix. Document everything in a new experiment report.

**Budget:** Up to 30 tool invocations (file edits + terminal runs combined). Stop if exceeded and ask.

---

## 📋 Required Context — READ BEFORE STARTING

1. **Read `.github/copilot-instructions.md`** — this contains project standards, anti-patterns, and research discipline rules. They are non-negotiable.
2. **Read `docs/experiment_01_sarimax_baseline.md`** — understand the previous results you are improving on.
3. **Read `src/pharma_intel/forecasting/mock_data.py`** — the current generator.
4. **Read `src/pharma_intel/forecasting/anchors.py`** — prevalence and market share anchors.
5. **Read `src/pharma_intel/forecasting/molecule_classes.py`** — molecule class definitions with patent expiry metadata.

When you have read all 5 files, begin with Task 0.

---

## ✅ Before You Start

### Task 0 — Planning phase (DO NOT execute anything yet)

After reading the files above, write a plan in the chat that includes:

1. **Your diagnosis** — in 3–5 bullets, explain why you think the current mock data is too easy
2. **Your proposed changes** — list specifically which parameters and mechanisms you will modify
3. **Your validation strategy** — how you will verify the fix worked
4. **Open questions** — anything ambiguous you want me to clarify

**STOP after writing this plan and wait for my "go" before proceeding.**

If I say "go," continue to Task 1. If I give feedback, revise the plan and re-confirm.

---

## 🔧 Task 1 — Branching and baseline snapshot

```powershell
# Create feature branch
git checkout -b step-a-improve-mock-data

# Verify clean state
git status   # expect: clean working tree

# Run existing tests to confirm we're starting from green
pytest -v

# Snapshot current baseline results (copy experiment_01 output to a reference location)
Copy-Item data\processed\sarimax_baseline_results.json data\processed\sarimax_baseline_results_v1_too_easy.json
Copy-Item data\processed\sarimax_exog_results.json data\processed\sarimax_exog_results_v1_too_easy.json
```

**STOP condition:** If `pytest` fails on any existing test, STOP and report. Do NOT proceed with changes on a broken baseline.

---

## 🔧 Task 2 — Update `mock_data.py`

Modify `src/pharma_intel/forecasting/mock_data.py` to address the over-cleanliness. Apply ALL of these changes:

### 2.1 Increase base noise and add per-class variation

In `GeneratorConfig`:
- Change `monthly_noise_sigma: float = 0.05` to `monthly_noise_sigma: float = 0.12`
- Add new field `per_class_noise_variation: float = 0.5` (documentation: "some classes have up to ±50% more or less noise than base")

In `_generate_class_series`, derive a class-specific sigma:
```python
# Each class gets a slightly different noise level — deterministic from seed
class_sigma_multiplier = 1.0 + rng.uniform(
    -cfg.per_class_noise_variation, cfg.per_class_noise_variation
)
class_sigma = cfg.monthly_noise_sigma * class_sigma_multiplier
```
Use `class_sigma` wherever `cfg.monthly_noise_sigma` currently generates class-level noise.

### 2.2 Add regime shifts

Add new field to `GeneratorConfig`:
- `regime_shift_count: int = 2` (each class gets ~2 structural breaks over 8-year window)
- `regime_shift_magnitude: float = 0.15` (±15% level change)

In `_generate_class_series`, before the monthly loop:
```python
# Choose regime shift months (not tied to events — truly structural)
n_shifts = rng.integers(1, cfg.regime_shift_count + 1)
shift_months = sorted(rng.choice(range(12, len(months) - 6), size=n_shifts, replace=False))
shift_magnitudes = rng.uniform(
    -cfg.regime_shift_magnitude, cfg.regime_shift_magnitude, size=n_shifts
)

# Cumulative level adjustment per month index
regime_levels = np.ones(len(months))
for shift_idx, magnitude in zip(shift_months, shift_magnitudes):
    regime_levels[shift_idx:] *= (1 + magnitude)
```
Then inside the loop, multiply total_factor by `regime_levels[idx]`.

### 2.3 Add cross-class substitution dynamics

Add helper function (before `_generate_class_series`):
```python
def _substitution_factor(
    cls: MoleculeClass,
    year: int,
) -> float:
    """Older drug classes lose share when newer in-area classes launch.

    Simple rule: for each class, reduce demand by 2% per year for each
    newer class in the same therapeutic area (launched ≥5 years ago).
    """
    from pharma_intel.forecasting.molecule_classes import ALL_CLASSES
    newer_classes = [
        c for c in ALL_CLASSES
        if c.therapeutic_area == cls.therapeutic_area
        and c.first_launch_th_year > cls.first_launch_th_year
        and year - c.first_launch_th_year >= 5  # newer class has had time to gain share
    ]
    return max(0.5, 1.0 - 0.02 * len(newer_classes) * (year - cls.first_launch_th_year) / 10)
```
In the monthly loop, multiply total_factor by `_substitution_factor(cls, year)`.

### 2.4 Decouple exogenous signals from target

The prevalence values currently drive demand too deterministically. Weaken the linkage:

In `_generate_class_series`, replace:
```python
prevalence_factor = prevalence / prev_2019 if prev_2019 > 0 else 1.0
```
with:
```python
# Use a noisy, partial version — real world: demand responds to diagnosed cases
# (lagged, with measurement noise), not raw prevalence
raw_ratio = prevalence / prev_2019 if prev_2019 > 0 else 1.0
# Dampen elasticity — 1% prevalence change → 0.5% demand change, not 1:1
dampened = 1.0 + (raw_ratio - 1.0) * 0.5
# Add measurement noise on top
prevalence_factor = dampened * (1 + rng.normal(0, 0.03))
```

### 2.5 Make seasonality less perfect

Replace the smooth cosine seasonality:
```python
seasonality = 1.0 + cfg.seasonality_amplitude * np.cos(
    2 * np.pi * (month_num - 10) / 12
)
```
with a version that has year-specific variation:
```python
# Year-specific seasonal amplitude — some years stronger Q4 spike than others
year_seasonal_mult = 1.0 + rng.normal(0, 0.3) if idx == 0 else year_seasonal_mult  # hack: preserve per-year
# Better: compute once per year
```

Actually, implement it cleanly like this:
```python
# Before the monthly loop, pre-compute per-year seasonal amplitude
unique_years = sorted({m.year for m in months})
year_amp = {y: cfg.seasonality_amplitude * (1 + rng.normal(0, 0.3)) for y in unique_years}

# In the loop:
amp = year_amp[year]
seasonality = 1.0 + amp * np.cos(2 * np.pi * (month_num - 10) / 12)
```

### 2.6 Soften patent cliff and COVID curves

Current curves are too sharp. Make them:
- Patent cliff: reduce `patent_cliff_boost` from 0.35 to 0.20
- COVID: reduce `covid_impact` from -0.15 to -0.10
- Add random variation: each class responds slightly differently. Multiply both by a per-class factor `1 + rng.normal(0, 0.4)` (clamped ≥0).

### 2.7 Update docstring

Update the module docstring to list the new parameters and the rationale ("Calibrated to produce MAPE 12–20% on seasonal SARIMAX baseline").

---

## 🔧 Task 3 — Regenerate data and rerun baselines

```powershell
# Regenerate mock data with new parameters
python scripts\generate_mock_demand.py --output data\processed\mock_demand_history.parquet

# Rerun SARIMAX baseline (no exog)
python scripts\run_sarimax_baseline.py --output data\processed\sarimax_baseline_results_v2.json

# Rerun SARIMAX + exog
python scripts\run_sarimax_baseline.py --with-exog --output data\processed\sarimax_exog_results_v2.json
```

---

## ✅ Task 4 — Validate acceptance criteria

Run this validation script and report the output:

```powershell
python -c "
import json

baseline_v1 = json.load(open('data/processed/sarimax_baseline_results_v1_too_easy.json'))
baseline_v2 = json.load(open('data/processed/sarimax_baseline_results_v2.json'))
exog_v2 = json.load(open('data/processed/sarimax_exog_results_v2.json'))

avg_b1 = sum(r['mape'] for r in baseline_v1) / len(baseline_v1)
avg_b2 = sum(r['mape'] for r in baseline_v2) / len(baseline_v2)
avg_e2 = sum(r['mape'] for r in exog_v2) / len(exog_v2)

hard_classes = sum(1 for r in baseline_v2 if r['mape'] > 18)
too_easy = sum(1 for r in baseline_v2 if r['mape'] < 8)
catastrophic = sum(1 for r in exog_v2 if r['mape'] > 100)

print(f'Baseline v1 (old) avg MAPE: {avg_b1:.2f}%')
print(f'Baseline v2 (new) avg MAPE: {avg_b2:.2f}%')
print(f'Exog v2 (new) avg MAPE:    {avg_e2:.2f}%')
print()
print(f'Classes with MAPE > 18 (hard): {hard_classes}')
print(f'Classes with MAPE < 8 (too easy): {too_easy}')
print(f'Exog classes with MAPE > 100 (catastrophic): {catastrophic}')
print()

# Acceptance criteria
ok_range = 12 <= avg_b2 <= 20
ok_hard = hard_classes >= 2
ok_easy = too_easy == 0
ok_not_catastrophic = catastrophic == 0
ok_exog_still_worse = avg_e2 > avg_b2

all_pass = ok_range and ok_hard and ok_easy and ok_not_catastrophic and ok_exog_still_worse
print(f'Baseline avg in [12, 20]: {ok_range}')
print(f'At least 2 hard classes: {ok_hard}')
print(f'No too-easy classes: {ok_easy}')
print(f'No catastrophic exog failures: {ok_not_catastrophic}')
print(f'Exog still worse than baseline: {ok_exog_still_worse}')
print()
print(f'ALL ACCEPTANCE CRITERIA: {\"PASS\" if all_pass else \"FAIL\"}')
"
```

### Decision tree based on output

**If ALL criteria PASS:** Continue to Task 5.

**If baseline avg MAPE < 12% (still too easy):** The changes were not strong enough.
- Try increasing `monthly_noise_sigma` to 0.15
- Try increasing `regime_shift_magnitude` to 0.20
- Rerun Tasks 3 and 4

**If baseline avg MAPE > 20% (too noisy now):**
- Reduce `monthly_noise_sigma` to 0.10
- Reduce `regime_shift_magnitude` to 0.10
- Rerun Tasks 3 and 4

**If some classes still catastrophic in exog (MAPE > 100):**
- The optimizer is likely still unstable. This is OK if only 1–2 classes. Report it honestly.
- Do NOT try to "fix" by changing SARIMAX itself.

**If `pytest` starts failing:**
- STOP. Do not proceed. Report which tests fail.

**Max retry loops:** 2. If still failing after 2 retries, stop and explain what's happening.

---

## 🔧 Task 5 — Update tests

Update `tests/test_forecasting.py`:

1. In `TestMockDataGeneration`, update the `test_output_is_dataframe` or equivalent to also assert:
   - Generated DataFrame has CV (coefficient of variation) within a realistic range per class
   - Add new test:
     ```python
     def test_realistic_noise_level(self, df):
         """Generated data should have per-class CV between 0.08 and 0.35."""
         import polars as pl
         for class_id in df["class_id"].unique():
             class_data = df.filter(pl.col("class_id") == class_id)["units_kddd"]
             cv = class_data.std() / class_data.mean()
             assert 0.08 <= cv <= 0.35, f"{class_id}: CV={cv:.3f} out of realistic range"
     ```

2. Run `pytest -v` and ensure ALL tests pass (including the new one).

---

## 🔧 Task 6 — Write experiment report

Create `docs/experiment_02_realistic_mock.md` with this structure:

```markdown
# Experiment 02: Realistic Mock Data — SARIMAX Re-evaluation

**Date:** [today's date YYYY-MM-DD]
**Previous experiment:** `experiment_01_sarimax_baseline.md`
**Branch:** step-a-improve-mock-data
**Motivation:** Experiment 01 revealed MAPE 7.1% baseline — suspiciously low vs literature norm (10–20%). Hypothesis: mock data too clean.

## Changes to Mock Data Generator

[Bulleted list of the 6 changes applied — link to commit hash]

## Results: Before vs After

| Metric | Old (v1) | New (v2) | Change |
| --- | ---: | ---: | ---: |
| Baseline avg MAPE | 7.1% | [X]% | [+Y] pp |
| Exog avg MAPE | 21.1% | [X]% | [+Y] pp |
| Catastrophic exog failures (>100% MAPE) | 3 | [X] | — |
| Classes with MAPE < 8% (too easy) | [X] | [X] | — |
| Classes with MAPE > 18% (hard) | [X] | [X] | — |

## Per-Class Results (v2)

[Full table with class_id, baseline MAPE, exog MAPE, improvement %]

## Interpretation

[2–4 paragraphs discussing:
1. Whether the baseline now lands in realistic range
2. Whether exog overfitting is reduced or still present
3. What this implies for the comparison with Prophet and XGBoost to come
4. Any surprises]

## Acceptance Criteria

- [ ] Baseline avg MAPE in [12, 20]: [PASS/FAIL — X%]
- [ ] At least 2 classes with MAPE > 18: [PASS/FAIL — X classes]
- [ ] No classes with MAPE < 8: [PASS/FAIL]
- [ ] No catastrophic exog failures (>100%): [PASS/FAIL — X failures]
- [ ] Exog still worse than baseline (overfitting still present): [PASS/FAIL — diff X pp]

## Artifacts

- Data: `data/processed/mock_demand_history.parquet` (regenerated)
- Results: `data/processed/sarimax_baseline_results_v2.json`, `data/processed/sarimax_exog_results_v2.json`
- Code: commit hash [will be filled at commit time]

## Next Steps

- [ ] Proceed to Step B — Prophet baseline
- [ ] Consider whether regime_shift_count should be tuned per-class
```

Replace bracketed placeholders with actual values.

---

## 🔧 Task 7 — Commit and report

```powershell
# Stage all changes
git add -A

# Commit with conventional message
git commit -m "fix(mock): increase realism — noise, regime shifts, substitution, decoupled exog

- Increased monthly_noise_sigma 0.05 -> 0.12 with per-class variation
- Added 1-2 regime shifts per class (structural breaks)
- Added cross-class substitution dynamics (newer classes erode older share)
- Decoupled prevalence from demand (0.5 elasticity + measurement noise)
- Year-specific seasonality amplitude variation
- Softened patent cliff and COVID impact curves

Result: SARIMAX baseline MAPE now realistic at [X]%, SARIMAX+exog at [Y]%.
Refs: docs/experiment_02_realistic_mock.md"

# Show the log
git log --oneline -5

# Show the diff stat
git diff main --stat
```

### Final report to the user

At the end, output a concise summary:

```
## Step A Completion Report

### What changed
- Modified files: [list with line counts changed]
- New files: docs/experiment_02_realistic_mock.md

### Key results
- Baseline SARIMAX avg MAPE: 7.1% → [X]%
- Exog SARIMAX avg MAPE: 21.1% → [X]%
- Catastrophic failures: 3 → [X]

### Acceptance
- All criteria: [PASS/FAIL]
- Unit tests: [N/M passed]

### Next
Ready for Step B? See docs/prompts/step_B_prophet_baseline.md
```

---

## 🚫 Anti-patterns — DO NOT DO THESE

These are taken from `.github/copilot-instructions.md` but called out specifically:

- ❌ **Do NOT tune SARIMAX order** (currently (1,1,1) × (1,1,1,12)) to improve results. The hypothesis is about data, not the model.
- ❌ **Do NOT remove classes** from ALL_CLASSES or skip classes with high MAPE.
- ❌ **Do NOT change random seed** to one that gives prettier numbers. Seed stays 42.
- ❌ **Do NOT delete or modify `experiment_01_sarimax_baseline.md`** — it's a historical record.
- ❌ **Do NOT modify `anchors.py`** unless I explicitly approve — prevalence numbers must stay realistic.
- ❌ **Do NOT modify `molecule_classes.py`** — class definitions are locked.
- ❌ **Do NOT add new LLM calls, scrapers, or RAG changes** — Step A is forecasting-only.
- ❌ **Do NOT create new Python scripts** unless absolutely necessary for validation.
- ❌ **Do NOT try to "debug" convergence warnings from SARIMAX** — they're expected and valuable signal.

---

## 🎓 Scientific honesty clause

If the validation criteria fail even after 2 retry loops:
1. STOP iterating
2. Write the experiment report with the actual (failing) numbers
3. Document clearly what you tried
4. Surface this as an open question for me

**A failed experiment honestly documented is more valuable than a "successful" one that's been over-tuned.**

---

## ❓ Open questions you might have

If any of these are unclear during execution, STOP and ask:

- Should the COVID shock affect all classes equally, or be class-specific?
- Is the CV range [0.08, 0.35] in the new test too tight/loose?
- Should regime shifts be gitignored-deterministic (seeded) or truly random per run?
- Is it OK to delete `sarimax_baseline_results.json` (v1) now that we renamed it?

Default answer if I don't respond: pick the safer/more conservative option.

---

**When all 7 tasks complete successfully, respond with:**

```
✅ Step A complete. Report: [paste final report]
Ready for Step B — say "proceed to Step B" to continue.
```
