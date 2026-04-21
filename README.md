# Pharma Intelligence Platform

> **Sovereign AI สำหรับ Pharmaceutical Intelligence ของ GPO**
> **ThaiLLM-powered Regulatory RAG** + **Long-term Demand Forecasting** สำหรับกลุ่มยา cardiometabolic

โครงการ M.Sc. AI for Business (KMITL SIT 2025–2026) — พร้อมแผน commercialization เป็น SaaS สำหรับอุตสาหกรรมยาไทย/SEA

## 🇹🇭 Why Sovereign Thai AI?

โครงการนี้ใช้ **ThaiLLM (OpenThaiGPT)** ของรัฐไทยเป็น default LLM provider เพื่อ:
- 🔒 **Data sovereignty** — ข้อมูลไม่ออกนอกประเทศ ตรงกับ policy หน่วยงานรัฐ
- 🤝 **Positioning** — Thai AI for Thai pharma ช่วยในการขายให้ GPO/หน่วยงานรัฐ
- 💰 **Cost** — ฟรีในระดับการใช้งานปกติ (5 req/sec, 200 req/min)
- 🔬 **Research contribution** — เปรียบเทียบ sovereign 8B model vs frontier Claude เป็นส่วนหนึ่งของ paper

**Provider abstraction:** สลับไป Claude เพื่อ benchmark ได้ผ่าน 1 environment variable

---

## 🎯 Week 1 Vertical Slice (ตอนนี้)

Scope: FDA Orange Book → parse → embed (bge-m3) → ChromaDB → **ThaiLLM** → grounded answer with citations

```bash
# 1. ติดตั้ง (ครั้งเดียว)
make setup
source .venv/bin/activate
# แก้ .env: ใส่ THAILLM_API_KEY

# 2. Download + parse FDA Orange Book
make download-orange-book

# 3. Build index (ใช้ Colab GPU แนะนำ — ดู notebooks/01_build_index_colab.ipynb)
make build-index

# 4. ถาม!
make query Q='What patents cover empagliflozin and when do they expire?'
make query Q='รายชื่อยา SGLT2 inhibitors ที่มีใน FDA Orange Book'
```

---

## 📋 Prerequisites

| Requirement | Version | Why |
|---|---|---|
| **Python** | **3.12** (แนะนำ) หรือ 3.11 | ML libs มี wheels พร้อม; 3.14 ต้อง compile บางตัว |
| **ThaiLLM API key** | — | ขอได้ที่ <http://thaillm.or.th> |
| Git | ล่าสุด | Version control |
| direnv | optional | Auto-activate venv |
| Disk | ~5GB free | Orange Book + bge-m3 (~2GB) + ChromaDB |
| RAM | ≥8GB (local) / T4 (Colab) | สำหรับ embedding 1,800+ docs |

> ⚠️ **Python 3.14 warning:** PyTorch-based libs อาจต้อง build from source — แนะนำใช้ 3.12

### การติดตั้ง Python 3.12

```bash
# macOS
brew install python@3.12

# Ubuntu/Debian
sudo apt update && sudo apt install python3.12 python3.12-venv

# Windows: ดาวน์โหลดจาก python.org
```

---

## 🚀 Setup แบบละเอียด

```bash
git clone <your-repo-url> pharma-intelligence
cd pharma-intelligence

# venv + deps
python3.12 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -e ".[dev]"

# direnv (optional)
brew install direnv          # macOS
eval "$(direnv hook zsh)"    # add to ~/.zshrc
direnv allow

# API key
cp .env.example .env
# แก้ .env ใส่ THAILLM_API_KEY

# Verify
make test
```

---

## 🧪 First Run

**Download Orange Book (~10 sec, English content):**
```bash
make download-orange-book
```

**Build index — เลือก option:**

### Option A: Local CPU (ช้า แต่ง่าย)
```bash
make build-index
```
⏱️ ครั้งแรก ~20–30 นาที (download bge-m3 + embed บน CPU)

### Option B: Colab Pro GPU (เร็ว)
1. อัพโหลด repo เข้า Colab
2. เปิด `notebooks/01_build_index_colab.ipynb`
3. รัน cells ตามลำดับ — ChromaDB จะถูก save ลง Google Drive
4. ดาวน์โหลด `chroma_db/` มาไว้ local

⏱️ รวม ~1 นาที บน T4

### Option C: ใช้ Drive mount ตรง ๆ
แก้ `.env`:
```bash
CHROMA_PERSIST_DIR=/path/to/GoogleDrive/pharma-intel/chroma_db
```
แล้วไม่ต้อง copy — query ตรงจาก Drive mount

**Query:**
```bash
# Basic
make query Q='When does empagliflozin patent expire?'

# With filters
python scripts/query_rag.py "list SGLT2 inhibitors" --k 10 --area diabetes

# Override provider (benchmarking)
python scripts/query_rag.py "..." --provider anthropic
```

---

## 🔀 LLM Provider Switching

**Default:** ThaiLLM (sovereign)
```bash
# .env
LLM_PROVIDER=thaillm
THAILLM_API_KEY=xxx
```

**Benchmark mode:** Claude for comparison
```bash
# .env
LLM_PROVIDER=anthropic
ANTHROPIC_API_KEY=sk-ant-xxx
```

**Per-call override:**
```bash
python scripts/query_rag.py "..." --provider anthropic
```

**Run full benchmark (both providers, same questions):**
```bash
# Create questions file (see tests/sample_questions.json for format)
python scripts/benchmark_providers.py \
    --questions data/test_questions.json \
    --out data/benchmark_results.json \
    --providers thaillm,anthropic
```

---

## 📁 โครงสร้างโปรเจกต์

```
pharma-intelligence/
├── src/pharma_intel/
│   ├── common/              # config, logging, drug constants
│   ├── ingestion/           # FDA, TFDA parsers
│   ├── rag/
│   │   ├── embeddings.py    # bge-m3
│   │   ├── vectorstore.py   # ChromaDB
│   │   ├── indexer.py       # glue
│   │   ├── query.py         # RAG engine
│   │   └── llm/             # ★ Provider abstraction
│   │       ├── base.py
│   │       ├── thaillm_provider.py      (primary)
│   │       ├── anthropic_provider.py    (benchmark)
│   │       └── factory.py
│   └── forecasting/         # IS2 phase (placeholder)
│
├── scripts/                 # typer CLI
│   ├── download_orange_book.py
│   ├── build_index.py
│   ├── query_rag.py
│   └── benchmark_providers.py  ★ for paper
│
├── notebooks/
│   └── 01_build_index_colab.ipynb   ★ GPU indexing
│
├── tests/
├── data/ (gitignored)
├── chroma_db/ (gitignored)
│
├── pyproject.toml
├── Makefile
├── .env.example
├── .envrc
└── .gitignore
```

---

## 🛠️ คำสั่งที่ใช้บ่อย

```bash
make help                   # แสดงคำสั่งทั้งหมด
make setup                  # setup ครั้งแรก
make install-dev            # dev deps
make install-all            # + forecasting
make test                   # pytest
make lint                   # ruff + mypy
make format                 # black + ruff --fix
make clean                  # ล้าง cache

# Pipeline
make download-orange-book
make build-index
make query Q='question'

# Advanced
python scripts/query_rag.py "q" --k 10 --area diabetes --provider thaillm
python scripts/build_index.py --reset
python scripts/benchmark_providers.py --questions ... --out ...
```

---

## ⚙️ Configuration

### LLM Provider
```bash
LLM_PROVIDER=thaillm              # thaillm | anthropic
```

### ThaiLLM
```bash
THAILLM_API_KEY=xxx
THAILLM_BASE_URL=http://thaillm.or.th/api/v1
THAILLM_MODEL=openthaigpt-thaillm-8b-instruct-v7.2
```

⚠️ **Security:** ThaiLLM endpoint ใช้ HTTP (ไม่ใช่ HTTPS) — API key ส่งแบบ plaintext อย่าใช้บน public WiFi, rotate key บ่อย ๆ

### Claude (optional)
```bash
ANTHROPIC_API_KEY=sk-ant-xxx
CLAUDE_MODEL=claude-sonnet-4-6   # or claude-haiku-4-5-20251001
```

### Embedding model
```bash
EMBEDDING_MODEL=BAAI/bge-m3                                           # SOTA bilingual (2GB)
# EMBEDDING_MODEL=sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2   # faster (400MB)
```
⚠️ เปลี่ยน model ต้อง rebuild: `python scripts/build_index.py --reset`

### Google Drive mount
```bash
DATA_DIR=/Volumes/GoogleDrive/pharma-intel/data
CHROMA_PERSIST_DIR=/Volumes/GoogleDrive/pharma-intel/chroma_db
MODEL_CACHE_DIR=/Volumes/GoogleDrive/pharma-intel/.cache/models
```

---

## 🧭 Roadmap

### ✅ Week 1 — FDA Orange Book slice (DONE)
- [x] Repo scaffolding, logging, config
- [x] Orange Book download + parse
- [x] Cardiometabolic filter (~50 drugs)
- [x] Drug monograph generation
- [x] bge-m3 + ChromaDB
- [x] **LLM provider abstraction (ThaiLLM default, Claude optional)**
- [x] Colab GPU indexing notebook
- [x] Benchmark script for paper

### 🔲 Week 2 — Evaluation framework
- [ ] Test set (100+ bilingual Q&A pairs, pharmacist-validated)
- [ ] RAGAS integration (faithfulness, precision, recall, answer relevance)
- [ ] Custom metric: citation accuracy
- [ ] **First benchmark: ThaiLLM vs Claude** (early signal for paper)

### 🔲 Week 3 — Thai sources (key differentiator)
- [ ] TFDA drug registration scraper
- [ ] ราชกิจจานุเบกษา PDF + typhoon-ocr
- [ ] NLEM essential medicines list parser
- [ ] PyThaiNLP preprocessing

### 🔲 Week 4 — ClinicalTrials + PubMed
- [ ] ClinicalTrials.gov API
- [ ] PubMed E-utilities
- [ ] Hybrid retrieval (BM25 + dense + cross-encoder reranker)

### 🔲 Week 5–8 — Forecasting foundation
- [ ] Mock demand data generator (anchored to HDC public stats)
- [ ] SARIMAX baseline
- [ ] XGBoost with engineered features

### 🔲 Week 9–14 — TFT on Vast AI
- [ ] Exogenous feature pipeline (patents, regulations → forecast features)
- [ ] Global TFT training
- [ ] Ablation study
- [ ] Diebold-Mariano significance tests

### 🔲 Week 15+ — Integration + paper
- [ ] Streamlit dashboard
- [ ] GPO stakeholder user study
- [ ] Paper: "Sovereign Thai LLM for Pharmaceutical Intelligence"
- [ ] IS1/IS2 writing

---

## 🔬 Research Contribution

Paper angles opened by this architecture:

1. **Sovereign vs Frontier Benchmark** — Can 8B OpenThaiGPT match Claude Sonnet on bilingual pharmaceutical regulatory QA?
2. **Bilingual RAG** — How does bge-m3 + Thai LLM perform on code-switched queries (Thai question, English source)?
3. **Long-horizon exogenous forecasting** — Does RAG-extracted regulatory signal improve 3–5 yr TFT forecasts?

---

## 🔧 Troubleshooting

**Problem:** `pip install` เจอ PyTorch/hnswlib error
**Solution:** Python version — ใช้ 3.12

**Problem:** `ModuleNotFoundError: pharma_intel`
**Solution:** `make install-dev`

**Problem:** `THAILLM_API_KEY not set` / `ANTHROPIC_API_KEY not set`
**Solution:** `cp .env.example .env` + แก้ใส่ key, direnv `direnv allow`

**Problem:** ThaiLLM ตอบช้า / timeout
**Solution:**
- Service rate limit (5 req/sec) — ถ้าชน ลอง sleep
- Service downtime — fallback ไป Claude ชั่วคราว: `--provider anthropic`

**Problem:** bge-m3 download ช้าบน local
**Solution:** สลับเป็น MiniLM-L12-v2 หรือใช้ Colab notebook

**Problem:** ChromaDB `sqlite3` version error
**Solution:** `pip install pysqlite3-binary` + monkey-patch

**Problem:** FDA URL เปลี่ยน
**Solution:** แก้ `ORANGE_BOOK_URL` ใน `src/pharma_intel/ingestion/fda_orange_book.py`

---

## 🔐 Security & IP

- **`.env` อยู่ใน `.gitignore`** — ห้าม commit API keys
- **ThaiLLM HTTP endpoint** — ไม่ encrypt, อย่าใช้ public WiFi
- **GPO internal data** — ห้ามเข้า git ใช้ DVC/external storage
- **Commercial model** — train/fine-tune บน non-GPO data only (IS Plan §10)

---

## 📚 References

- ThaiLLM / OpenThaiGPT: <http://thaillm.or.th>
- FDA Orange Book: <https://www.fda.gov/drugs/drug-approvals-and-databases/orange-book-data-files>
- BAAI bge-m3: <https://huggingface.co/BAAI/bge-m3>
- Anthropic Claude: <https://docs.claude.com/>
- LlamaIndex: <https://docs.llamaindex.ai>
- PyThaiNLP: <https://pythainlp.org>

---

## 📝 License

Proprietary. IP clearance with GPO required before commercial deployment.

---

**Author:** Siripon Srihangpiboon
**Program:** M.Sc. AI for Business, KMITL SIT (2025–2026)
**Contact:** srihangpiboon.siri@gmail.com
