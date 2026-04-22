# GitHub Copilot Instructions — pharma-intelligence

> This file is automatically loaded by GitHub Copilot for every chat in this repository.
> It defines project context, coding standards, and behavioral rules for Copilot.
> **Keep this file up to date as the project evolves.**

---

## 🎯 Project Overview

**pharma-intelligence** is a dual-engine AI system for the Thai Government Pharmaceutical Organization (GPO):

- **Engine A (IS1 / Forecasting):** Long-term (3–5 year) demand forecasting for cardiometabolic generic drugs using time-series ML (SARIMAX → Prophet → XGBoost → TFT)
- **Engine B (IS2 / Intelligence):** Bilingual Thai–English RAG for regulatory monitoring (FDA Orange Book, TFDA, ราชกิจจานุเบกษา, ClinicalTrials.gov)

**Academic context:** Master's thesis (IS1 + IS2) at KMITL SIT, M.Sc. AI for Business (2025–2026)
**Business context:** Prototype for GPO, with potential commercialization as Thai/SEA pharma intelligence SaaS
**Primary LLM:** ThaiLLM (OpenThaiGPT) — sovereign Thai AI — with Claude as optional benchmark

---

## 📁 Repository Structure

```
src/pharma_intel/
  common/          # Config (pydantic-settings), logging (loguru), drug constants
  ingestion/       # FDA Orange Book, future: TFDA, ราชกิจจา, ClinicalTrials
  rag/             # Embeddings (bge-m3), ChromaDB, query engine
    llm/           # Provider abstraction (ThaiLLM default, Claude benchmark)
  forecasting/     # Mock data, molecule classes, anchors, SARIMAX baseline

scripts/           # Typer CLI entry points (download, build-index, query, generate-mock, sarimax)
tests/             # pytest suites
docs/              # Scope docs, experiment reports, prompt files
notebooks/         # Colab-oriented notebooks (GPU indexing)
data/              # raw/, interim/, processed/ (all gitignored)
chroma_db/         # Vector store persistence (gitignored)
```

Every command has a Python script equivalent — on Windows PowerShell, prefer `python scripts\xxx.py` over `make xxx`.

---

## 🛠️ Tech Stack

| Layer | Choice | Notes |
|---|---|---|
| Python | 3.12 | 3.13/3.14 have ML wheel issues |
| Data | polars (primary), pandas (when stats libs require) | polars is preferred |
| Stats | statsmodels (SARIMAX) | |
| ML | scikit-learn, xgboost, lightgbm | |
| Deep Learning | PyTorch, pytorch-forecasting (TFT) — Phase 3 | Vast AI for training |
| Time-series | prophet, statsforecast, darts | |
| RAG | ChromaDB, sentence-transformers (bge-m3), LlamaIndex (no LangChain) | |
| LLM | anthropic SDK; httpx for ThaiLLM (OpenAI-compatible but custom `apikey` header) | |
| CLI | typer + rich for tables and panels | |
| Validation | pydantic v2 | |
| Logging | loguru (NEVER print() — always `from pharma_intel.common import logger`) | |

---

## ✍️ Coding Standards

### Style
- **Line length:** 100
- **Formatter:** `black` with target `py312`
- **Linter:** `ruff` (select E, F, I, N, W, UP, B, C4, SIM)
- **Type checker:** `mypy` — but `disallow_untyped_defs=false` for flexibility
- **Imports:** isort-compatible (handled by ruff)

### Patterns
- **Configuration:** Always load via `from pharma_intel.common import settings` (pydantic-settings singleton). Never hardcode paths, API keys, or model names.
- **Logging:** Use `from pharma_intel.common import logger` (loguru). Use `logger.info()` for normal flow, `logger.warning()` for recoverable issues, `logger.error()` for failures before raising.
- **DataFrames:** Prefer `polars.DataFrame`. Convert to pandas only when a downstream lib requires it (e.g., statsmodels).
- **Random seeds:** All random operations must accept a `random_seed` parameter, default 42, stored in the output for reproducibility.
- **Paths:** Use `pathlib.Path`, not string concatenation. Use `settings.processed_dir`, `settings.raw_dir` etc.
- **Dataclasses:** Use `@dataclass(frozen=True)` for value objects, regular `@dataclass` for mutable ones.
- **Errors:** Raise specific exceptions (`ValueError`, `RuntimeError`, `KeyError`). Never swallow exceptions silently.

### File organization
- One module = one responsibility. Don't mix SARIMAX and Prophet in the same file — separate modules under `forecasting/`.
- New baseline models go in `src/pharma_intel/forecasting/` with matching test file in `tests/`.
- New CLI scripts go in `scripts/` using typer. Match pattern of existing scripts.
- New experiment reports go in `docs/experiment_XX_description.md`.

---

## 🧪 Testing Discipline

- **Before changing code:** Run `pytest -v` to establish baseline. Note which tests pass.
- **When adding features:** Write at least 1 smoke test per new module.
- **When fixing bugs:** Write a regression test first (must fail), then fix, then test passes.
- **Test naming:** `test_<module>.py` at repo root `tests/`. Class `Test<Thing>`, methods `test_<behavior>`.

---

## 📊 Research Discipline (CRITICAL)

**This is a thesis project.** Every experiment result must be:

1. **Reproducible** — committed to git with data seed + config + script + output file
2. **Documented** — `docs/experiment_XX_<name>.md` with date, config, results table, interpretation
3. **Honest** — bad results are valuable findings. NEVER tune code to make numbers look better.

### 🚫 Anti-patterns — Copilot must never do these

- ❌ **Never edit the mock data generator to make a failing baseline look successful.** If SARIMAX with exog shows overfitting, that IS the finding. Document it, don't hide it.
- ❌ **Never tune SARIMAX order (p,d,q) without documenting the grid search.** Document the full search procedure and alternatives tried.
- ❌ **Never silently change random seeds to get "better" results.** Seeds are locked to 42 unless I explicitly request a different value (e.g., for variance analysis).
- ❌ **Never remove classes from ALL_CLASSES to improve average metrics.** All 13 classes must be in every experiment run.
- ❌ **Never delete or modify previous experiment reports.** Create new reports with higher numbers (experiment_02, experiment_03...).
- ❌ **Never hardcode API keys or credentials** in committed code. Use `.env` (gitignored) and `settings`.

### ✅ What Copilot should do

- ✅ Report numbers exactly as produced. Round only to the decimal places specified in the prompt.
- ✅ Explain WHY a result is what it is (e.g., "exogenous features hurt because of overfitting — 84 obs, 12 params").
- ✅ Propose next steps as hypotheses to test, not conclusions.
- ✅ When changing shared config (e.g., noise_sigma), warn that old experiments must be rerun.
- ✅ When in doubt, STOP and ASK.

---

## 🔒 Security & Compliance

- **.env is gitignored.** Never commit `.env`. If you see keys in code, flag it immediately.
- **ThaiLLM HTTP endpoint:** The documented `thaillm.or.th/api/v1` uses HTTP (not HTTPS). Never log API keys. Never use on untrusted networks. Document this caveat when relevant.
- **GPO internal data:** If ever granted, must be gitignored and stored outside the repo (DVC or external storage). Never enters git history.
- **Commercial fork:** If this codebase is ever split for commercial use, training/fine-tuning must use non-GPO data only.

---

## 💻 Platform Notes

- **Primary dev OS:** Windows 11 with PowerShell + VS Code
- **`make` is not available on Windows PowerShell by default** — use `python scripts\xxx.py` directly
- **Long path limit:** Windows 260-char MAX_PATH can break pip installs with deeply nested packages (e.g., jupyter labextensions). Prefer short project paths like `C:\dev\pi\` over `C:\Users\name\Desktop\my_project\pharma-intelligence\`.
- **Jupyter is optional** — moved to `[notebook]` extra in pyproject.toml. Use Colab for notebooks instead of local Jupyter.

---

## 🧭 Current Project State (update as work progresses)

**Last updated:** 2026-04-21

### ✅ Completed
- Repository scaffolding (config, logging, constants, tests)
- FDA Orange Book ingestion pipeline (download, parse, filter, monograph generation)
- bge-m3 embedding + ChromaDB vector store
- RAG query engine with LLM provider abstraction (ThaiLLM default, Claude benchmark)
- Mock demand data generator (13 cardiometabolic classes, 2018–2025, 4 channels)
- SARIMAX baseline forecaster with evaluation metrics (MAPE, sMAPE, MASE, RMSE)
- First experiment: `docs/experiment_01_sarimax_baseline.md`

### ⚠️ Known issues (as of 2026-04-21)
- **Mock data too easy:** SARIMAX baseline MAPE = 7.1% average — suspiciously low vs pharma literature (10–20% expected)
- **SARIMAX + exog overfits:** Average MAPE worsens to 21.1%. Catastrophic failures on fibrates (-931%), ccb (-925%), diuretics (-724%). Convergence warnings observed. Rule-of-thumb violated: 84 obs / 12 params = 7 obs/param < recommended 15.

### 🔜 Next milestones
1. **Step A** — Improve mock data realism (inject more noise, regime shifts, cross-class substitution) so baseline MAPE lands in 12–20% range
2. **Step B** — Add Prophet baseline with Bayesian regularization for exog features
3. **Step C** — Add XGBoost with proper feature engineering (future)
4. **Step D** — TFT on Vast AI (future)

---

## 📝 Commit Message Convention

Use conventional commits with optional scope:

```
<type>(<scope>): <subject>

[optional body explaining why]
[optional footer: refs to experiment docs or issues]
```

**Types:**
- `feat` — new feature
- `fix` — bug fix
- `exp` — experiment run (data produced, not code)
- `docs` — documentation only
- `refactor` — code restructuring without behavior change
- `test` — test additions/changes
- `chore` — tooling, dependencies

**Scopes for this project:**
- `is1` — IS1 / forecasting engine
- `is2` — IS2 / RAG engine
- `mock` — mock data generator
- `ingestion` — data scrapers
- `llm` — LLM providers
- `infra` — build, CI, deps

**Examples:**
```
feat(is1): add Prophet baseline with exogenous regularization
fix(mock): increase noise sigma to match realistic pharma volatility
exp(is1): rerun SARIMAX after mock data fix — MAPE 15.3% (was 7.1%)
docs: add experiment 02 findings on Prophet vs SARIMAX
```

---

## 🗣️ Communication Style

When Copilot presents results to the user:

- **Lead with the number or result.** Don't bury the headline.
- **Use tables** when comparing 2+ models, classes, or configurations.
- **Flag surprises** — if a result is unexpected (e.g., too good, too bad, wrong direction), call it out.
- **Suggest next steps as questions**, not directives.
- **Thai or English** — respond in the language used in the question. Technical terms stay English.

---

## 🎓 User Background

The user (Siripon) is:
- A **pharmacist** at GPO with 9 years of pharma domain experience
- An AI/ML **student** currently learning (Super AI Engineer Season 6)
- Comfortable with Python, PyTorch, basic MLOps
- **Does not use LangChain** — prefer LlamaIndex or direct SDK calls
- Working primarily on **Windows 11 + PowerShell + VS Code**

Assume intermediate ML knowledge but novice-level research methodology — explain statistical subtleties (e.g., why Diebold-Mariano, what overfitting looks like in time-series) when they come up.
