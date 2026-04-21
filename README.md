# Pharma Intelligence Platform

Pharma Intelligence Platform is a research and product development repository for pharmaceutical intelligence focused on the Government Pharmaceutical Organization (GPO) context in Thailand. The project combines two complementary workstreams:

- IS1: demand forecasting for cardiometabolic molecule classes
- IS2: bilingual regulatory intelligence and retrieval-augmented generation (RAG) using ThaiLLM

The repository supports an M.Sc. AI for Business research program at KMITL SIT and is structured to evolve into a production-oriented platform for Thai and Southeast Asian pharmaceutical use cases.

## Table of Contents

- Project Overview
- Research Scope
- Current Status
- System Architecture
- Repository Structure
- Prerequisites
- Installation
- Configuration
- IS1 Forecasting Workflow
- IS2 Regulatory Intelligence Workflow
- Colab GPU Workflow for Indexing
- Development Commands
- Testing and Quality Checks
- Troubleshooting
- Roadmap
- License and Usage

## Project Overview

The platform addresses two operational problems commonly faced by pharmaceutical R&D and strategic planning teams:

1. Long product development cycles can cause demand assumptions to become outdated before launch.
2. Regulatory, patent, and competitor intelligence is often fragmented and difficult to monitor continuously.

To address these issues, the repository contains:

- A forecasting pipeline for long-horizon demand estimation at the molecule-class level
- A regulatory intelligence pipeline that ingests FDA Orange Book data and supports bilingual Thai and English question answering
- A common configuration, logging, and experimentation framework for research iteration

The initial therapeutic focus is cardiometabolic drugs, covering diabetes, hypertension, dyslipidemia, and relevant combination products.

## Research Scope

### IS1: Forecasting

The forecasting workstream focuses on molecule-class level demand forecasting rather than SKU-level prediction. This aligns better with strategic R&D decisions and reduces noise relative to product-level demand series.

Current forecasting components include:

- Mock demand generation anchored to public-health and market assumptions
- SARIMAX baseline models
- SARIMAX with exogenous regulatory and market features
- A foundation for later extension to Prophet, XGBoost, and Temporal Fusion Transformer workflows

### IS2: Regulatory Intelligence

The regulatory intelligence workstream focuses on bilingual retrieval and grounded question answering over pharmaceutical regulatory data sources. The current implemented slice is centered on FDA Orange Book ingestion and document indexing.

Current intelligence components include:

- FDA Orange Book download and parsing
- Cardiometabolic product filtering
- Natural-language monograph generation for each approved product
- Dense embedding with multilingual models
- Persistent ChromaDB vector indexing
- Bilingual question answering with ThaiLLM by default and Anthropic as an optional benchmark provider

## Current Status

The repository currently includes a working vertical slice for both IS1 and IS2.

Completed or verified items include:

- Project setup and dependency installation on Python 3.12
- Smoke tests and unit tests passing locally
- Mock demand generation and SARIMAX baseline evaluation
- Orange Book ingestion with updated parser handling for current FDA schema changes
- Colab notebook support for GPU-based bge-m3 indexing
- ThaiLLM provider integration and bilingual RAG query pipeline

Recent verified forecasting result:

- Plain SARIMAX outperformed SARIMAX with the current exogenous feature set on the mock dataset
- Experiment output is documented in `docs/experiment_01_sarimax_baseline.md`

## System Architecture

The platform is designed around two coordinated engines.

### Engine A: Forecasting

Forecasting is responsible for estimating medium- to long-horizon demand at the molecule-class level. The core principle is to use forecasting models for quantitative prediction rather than LLMs.

Representative inputs include:

- Historical demand series
- Epidemiological prevalence trends
- Budget and healthcare utilization proxies
- Regulatory and patent-derived exogenous signals

Representative outputs include:

- Forecasts by molecule class
- Comparative model metrics
- Feature-ablation findings

### Engine B: Intelligence

The intelligence engine is responsible for collecting, structuring, retrieving, and summarizing regulatory information.

Representative inputs include:

- FDA Orange Book records
- Future planned Thai sources such as TFDA and Royal Gazette publications
- Patent and exclusivity metadata

Representative outputs include:

- Grounded answers with citations
- Structured regulatory event signals
- Evidence inputs for downstream forecasting features

### Integration Principle

The core methodological principle of the project is:

- Machine learning for numerical forecasting
- LLMs for language understanding, extraction, and grounded summarization

This separation keeps forecasting defensible from a modeling perspective while still exploiting LLM capabilities for document-heavy pharmaceutical intelligence tasks.

## Repository Structure

```text
pharma-intelligence/
├── data/
│   ├── raw/
│   ├── interim/
│   └── processed/
├── docs/
├── notebooks/
├── scripts/
├── src/
│   └── pharma_intel/
│       ├── common/
│       ├── forecasting/
│       ├── ingestion/
│       └── rag/
├── tests/
├── chroma_db/
├── Makefile
├── pyproject.toml
└── README.md
```

Key areas:

- `src/pharma_intel/common`: configuration, constants, and logging
- `src/pharma_intel/forecasting`: mock data generation, anchors, baselines, and molecule-class definitions
- `src/pharma_intel/ingestion`: Orange Book ingestion and monograph creation
- `src/pharma_intel/rag`: embeddings, vector store, query engine, and LLM provider abstraction
- `scripts`: CLI entry points for ingestion, indexing, querying, forecasting, and benchmarking
- `notebooks`: notebook-based workflows, including Colab GPU indexing
- `docs`: experiment writeups and scope documentation

## Prerequisites

The following environment is recommended:

- Python 3.12
- Git
- Approximately 5 GB of free disk space for model cache, processed data, and ChromaDB artifacts
- At least 8 GB RAM for local development
- A ThaiLLM API key for the default LLM workflow

Optional but recommended:

- Google Drive for persisting large model and vector index artifacts
- Colab GPU runtime for faster embedding and indexing

### Python Version Guidance

Supported Python range is defined in `pyproject.toml` as `>=3.11,<3.15`. Python 3.12 is the recommended version because the repository and its current dependency set have already been validated in that environment.

## Installation

### 1. Clone the Repository

```bash
git clone https://github.com/siriponsri/pharma-intelligence.git
cd pharma-intelligence
```

### 2. Create and Activate a Virtual Environment

#### Windows PowerShell

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
```

#### macOS or Linux

```bash
python3.12 -m venv .venv
source .venv/bin/activate
```

### 3. Install Dependencies

For the validated local development setup used in this repository:

```bash
pip install --upgrade pip
pip install -e ".[dev,forecasting]"
```

Optional dependency sets:

- `.[dev]`: testing and code quality tools only
- `.[dev,notebook]`: add Jupyter support
- `.[dev,notebook,forecasting]`: full local environment

### 4. Create the Environment File

```bash
cp .env.example .env
```

On Windows PowerShell, if `cp` is not available:

```powershell
Copy-Item .env.example .env
```

Then update `.env` with at least:

```env
THAILLM_API_KEY=your_key_here
```

### 5. Verify the Setup

```bash
pytest -v --tb=short
```

## Configuration

The repository uses environment-based configuration through `.env` and `pydantic-settings`.

### Core Settings

```env
LLM_PROVIDER=thaillm
THAILLM_API_KEY=
THAILLM_BASE_URL=http://thaillm.or.th/api/v1
THAILLM_MODEL=openthaigpt-thaillm-8b-instruct-v7.2

ANTHROPIC_API_KEY=
CLAUDE_MODEL=claude-sonnet-4-6

DATA_DIR=./data
CHROMA_PERSIST_DIR=./chroma_db
MODEL_CACHE_DIR=./.cache/models

EMBEDDING_MODEL=BAAI/bge-m3
LOG_LEVEL=INFO
```

### Embedding Model Options

Default model:

```env
EMBEDDING_MODEL=BAAI/bge-m3
```

Faster local development alternative:

```env
EMBEDDING_MODEL=sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2
```

If the embedding model changes, rebuild the vector index.

### Security Note

The current ThaiLLM endpoint uses HTTP rather than HTTPS. Treat the API key as sensitive, avoid untrusted networks when possible, and rotate credentials periodically.

## IS1 Forecasting Workflow

### Generate the Mock Demand Panel

```bash
python scripts/generate_mock_demand.py
```

Generated outputs include:

- `data/processed/mock_demand_history.parquet`
- `data/processed/mock_demand_history.csv`

### Run the SARIMAX Baseline

```bash
python scripts/run_sarimax_baseline.py --output data/processed/sarimax_baseline_results.json
```

### Run SARIMAX with Exogenous Features

```bash
python scripts/run_sarimax_baseline.py --with-exog --output data/processed/sarimax_exog_results.json
```

### Current Experiment Notes

The current experiment shows that the present exogenous feature specification does not improve forecasting accuracy on the mock dataset. This is documented in:

- `docs/experiment_01_sarimax_baseline.md`

## IS2 Regulatory Intelligence Workflow

### Step 1: Download and Process FDA Orange Book Data

```bash
python scripts/download_orange_book.py
```

This pipeline:

- Downloads the Orange Book archive
- Parses product, patent, and exclusivity files
- Filters cardiometabolic products
- Generates monograph text suitable for indexing
- Writes processed parquet output

Primary processed artifact:

- `data/processed/orange_book_cardiometabolic.parquet`

### Step 2: Build the Vector Index

```bash
python scripts/build_index.py
```

This command embeds monograph text and stores the persistent collection in ChromaDB.

Expected behavior:

- Local CPU with `BAAI/bge-m3` is slow on first run
- First run downloads a large model cache
- Colab GPU is recommended for production-sized indexing workflows

### Step 3: Query the RAG System

```bash
python scripts/query_rag.py "What patents cover empagliflozin and when do they expire?"
python scripts/query_rag.py "List SGLT2 inhibitors approved by FDA with their manufacturers" --k 10
python scripts/query_rag.py "สิทธิบัตรของ dapagliflozin หมดเมื่อไหร่"
```

The query engine:

- Retrieves top-k chunks from ChromaDB
- Builds a grounded context block
- Uses the configured LLM provider to answer in the question language
- Returns source citations inline using document identifiers

### Provider Override Example

```bash
python scripts/query_rag.py "Compare generic manufacturers of metformin" --provider anthropic
```

## Colab GPU Workflow for Indexing

For `BAAI/bge-m3`, Colab GPU is the recommended indexing path.

Notebook:

- `notebooks/01_build_index_colab.ipynb`

Recommended workflow:

1. Open the notebook in Colab
2. Set runtime to a T4 GPU or better
3. Mount Google Drive
4. Clone the repository from GitHub
5. Install dependencies
6. Load `THAILLM_API_KEY` via Colab Secrets
7. Run ingestion and indexing cells
8. Persist `chroma_db` to Google Drive
9. Reuse that persisted index for local querying

This notebook has been updated to clone the repository directly from:

```text
https://github.com/siriponsri/pharma-intelligence.git
```

## Development Commands

The repository includes a `Makefile`, but note that it is oriented toward POSIX shells. On Windows, direct `python` and `pip` commands are often more reliable than invoking `make`.

### Common Make Targets

```bash
make help
make install-dev
make install-notebook
make install-all
make test
make lint
make format
make download-orange-book
make build-index
make generate-mock
make sarimax-baseline
make sarimax-exog
```

### Windows-Friendly Direct Commands

```powershell
pytest -v
python scripts\download_orange_book.py
python scripts\build_index.py
python scripts\generate_mock_demand.py
python scripts\run_sarimax_baseline.py --output data\processed\sarimax_baseline_results.json
python scripts\query_rag.py "What patents cover empagliflozin and when do they expire?"
```

## Testing and Quality Checks

Run the automated tests:

```bash
pytest -v --tb=short
```

Run linting and type checks:

```bash
ruff check src tests scripts
mypy src
```

Apply formatting:

```bash
black src tests scripts
ruff check --fix src tests scripts
```

## Troubleshooting

### Windows and `make`

The provided `Makefile` uses Unix-oriented shell commands. On Windows PowerShell, prefer the direct `python`, `pip`, and `pytest` commands shown in this README.

### Orange Book Schema Changes

The FDA source files may change column naming conventions over time. The current parser already handles the observed `DF;Route` versus `DF_Route` schema variation and null text fields found in recent Orange Book data.

### Slow Local Indexing

If local indexing with `BAAI/bge-m3` is too slow:

- Use the Colab GPU notebook
- Or temporarily switch to `sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2` for faster local iteration

### Large Model Download Behavior

The first embedding run downloads model artifacts and may take significant time. Reuse `MODEL_CACHE_DIR` across runs where possible.

### ChromaDB Persistence

If querying fails after indexing, verify:

- `CHROMA_PERSIST_DIR` points to the expected `chroma_db` folder
- The same embedding model is used consistently
- The collection exists and contains documents

### ThaiLLM Rate Limits

ThaiLLM enforces rate limits. If the provider returns a rate-limit error during evaluation, wait briefly and retry once.

## Roadmap

### Near-Term

- Add a formal bilingual evaluation set for RAG
- Add Anthropic benchmark comparisons for answer quality and citation behavior
- Extend forecasting baselines to Prophet and tree-based methods
- Add additional Thai regulatory data sources

### Medium-Term

- Integrate regulatory event extraction into exogenous forecasting features
- Expand dashboard and stakeholder-facing reporting
- Run longer-horizon forecasting experiments with stronger validation design

### Long-Term

- Train and evaluate richer forecasting models such as TFT
- Build production-grade ingestion for TFDA, Royal Gazette, and clinical trial sources
- Conduct stakeholder evaluation with GPO or comparable institutions

## License and Usage

This project is marked as proprietary in `pyproject.toml`. Do not assume open-source usage rights unless the repository owner provides explicit licensing terms.