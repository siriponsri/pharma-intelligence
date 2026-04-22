# Master Plan: Pharmaceutical Intelligence Platform for GPO

**ชื่อโครงการ:** Cardiometabolic Drug Intelligence Platform (CDIP)
**ผู้รับผิดชอบ:** Siripon Srihangpiboon (Pharmacist, GPO + M.Sc. AI for Business, KMITL SIT)
**วันที่จัดทำแผน:** 22 เมษายน 2026
**สถานะ:** Living document — v1.0 (synthesis after Week 2 experiments)
**ระยะเวลาโครงการ:** 18 เดือน (พ.ค. 2026 – ต.ค. 2027)

---

## สารบัญ

1. [Executive Summary](#1-executive-summary)
2. [ที่มาและความสำคัญ](#2-ที่มาและความสำคัญ)
3. [Objectives และ Deliverables](#3-objectives-และ-deliverables)
4. [สถานะปัจจุบัน: สิ่งที่ทำแล้ว](#4-สถานะปัจจุบัน-สิ่งที่ทำแล้ว)
5. [บทเรียนจาก Week 1–2](#5-บทเรียนจาก-week-1-2)
6. [System Architecture](#6-system-architecture)
7. [แผนการทำงาน 6 Phase](#7-แผนการทำงาน-6-phase)
8. [Data Strategy](#8-data-strategy)
9. [Tech Stack และ Infrastructure](#9-tech-stack-และ-infrastructure)
10. [Timeline และ Milestones](#10-timeline-และ-milestones)
11. [Risks และ Mitigation](#11-risks-และ-mitigation)
12. [Success Criteria](#12-success-criteria)
13. [Budget Estimate](#13-budget-estimate)
14. [IS1 / IS2 Mapping](#14-is1--is2-mapping)
15. [Commercialization Path](#15-commercialization-path)
16. [Decision Log](#16-decision-log)

---

## 1. Executive Summary

### ปัญหาที่แก้
องค์การเภสัชกรรม (GPO) เผชิญ pain points 2 เรื่องในกระบวนการ R&D:
- **R&D cycle ยาวเกินไป** — ยาออกตลาดช้า ไม่ตรงความต้องการ ลงทุนผิด
- **ไม่มีระบบ intelligence** — ติดตามยาใหม่, คู่แข่ง, regulation ด้วยมือ ไม่ scalable

### สิ่งที่เราสร้าง
ระบบ AI สองเครื่องยนต์ที่ทำงานร่วมกัน:
- **Engine A (Forecasting):** ทำนายความต้องการยา cardiometabolic 3–5 ปีล่วงหน้า
- **Engine B (Intelligence):** RAG system ติดตาม regulatory changes, patents, trials

### Positioning
- 🇹🇭 **Sovereign AI** — ใช้ ThaiLLM (OpenThaiGPT) เป็น default
- 📊 **Therapeutic focus** — cardiometabolic (DM + HTN + Dyslipidemia) 13 molecule classes
- 🎓 **Academic rigor** — M.Sc. thesis (IS1 + IS2) + conference paper
- 💼 **Business-ready** — prototype for GPO, potential SaaS for Thai/SEA pharma

### Current status (22 เม.ย. 2026)
- ✅ Repo scaffolding + tech stack locked
- ✅ Engine B (RAG): FDA Orange Book pipeline ทำงานได้
- ✅ Engine A (Forecasting): Mock data generator + SARIMAX baseline + 3 experiment reports
- 🎯 **Next critical milestone:** เพิ่ม real public data (Phase 2) เพื่อเตรียม GPO demo

---

## 2. ที่มาและความสำคัญ

### 2.1 Business Pain Points (จาก GPO)

| Pain Point | ผลกระทบปัจจุบัน | คาด impact หลังแก้ |
|---|---|---|
| R&D cycle 3–5 ปี ไม่ align กับ market demand | ลงทุน R&D ในยาที่ไม่ตรงความต้องการ | Hit rate generic launch สูงขึ้น ≥20% |
| Manual regulatory monitoring | RA team ใช้เวลาหลายวัน/สัปดาห์ | ลดเวลาเหลือหลักชั่วโมง |
| ไม่เห็น competitor movement | โดนตัดหน้าตลาด | Early warning 12–18 เดือนก่อน launch |
| ไม่มี patent cliff tracking | พลาดโอกาส generic window | Identify cliff 24 เดือนล่วงหน้า |

### 2.2 Therapeutic Area: Cardiometabolic

**เหตุผลเลือก:**
- Data availability สูงสุด (NHES, HDC, สปสช. open data)
- GPO portfolio ครอบคลุมอยู่แล้ว
- NCDs คิดเป็น ~40–50% ของยาที่ใช้ใน รพ.รัฐ
- Patent cliff density สูงในช่วง 2025–2030
- Policy relevance สูง (NCDs เป็นปัญหาชาติ)

**Scope:**
- 13 molecule classes
- Diabetes: metformin, sulfonylureas, DPP-4i, SGLT2i, GLP-1 RA
- Hypertension: ACEi, ARBs, CCB, beta-blockers, diuretics
- Dyslipidemia: statins, ezetimibe, fibrates

### 2.3 Research Gap ที่ address

ไม่มีงานวิจัยที่:
1. ทำ long-horizon (3–5 yr) forecasting สำหรับ Thai pharmaceutical demand ด้วย exogenous signals
2. Benchmark sovereign Thai LLM vs frontier LLMs บน bilingual pharmaceutical regulatory QA
3. Integrate RAG-extracted regulatory signals เป็น forecasting features (cross-engine approach)

---

## 3. Objectives และ Deliverables

### 3.1 Research Objectives (สำหรับ IS1 + IS2 + paper)

**RO1 (Forecasting):** Evaluate whether classical (SARIMAX, Prophet), ML (XGBoost), and DL (TFT) models differ significantly in long-horizon pharmaceutical demand forecasting, and whether exogenous regulatory/patent signals provide meaningful improvement.

**RO2 (Intelligence):** Evaluate bilingual RAG architecture for Thai–English pharmaceutical regulatory documents using sovereign ThaiLLM vs frontier Claude, measuring retrieval accuracy, faithfulness, and citation quality.

**RO3 (Integration):** Quantify the value of cross-engine feedback — does feeding RAG-extracted event signals improve downstream forecasting?

### 3.2 Business Objectives (สำหรับ GPO pitch)

**BO1:** Reduce time-to-decision for R&D pipeline selection from weeks → hours.
**BO2:** Automate regulatory scanning currently done manually by RA team.
**BO3:** Provide 3–5 year demand forecasts with uncertainty intervals for strategic planning.

### 3.3 Academic Deliverables

| Deliverable | Target Venue | Timeline |
|---|---|---|
| IS1 Report + defense | KMITL SIT | End of Semester 1 |
| IS2 Report + defense | KMITL SIT | End of Semester 2 |
| Conference paper | IEEE JCSSE / NCIT / KICSS | After IS2 |

### 3.4 Business Deliverables

| Deliverable | Target Audience | Timeline |
|---|---|---|
| RAG demo (Engine B) | GPO RA team | Phase 3 end |
| Methodology demo (Engine A) | GPO Strategic Planning | Phase 4 end |
| Integrated dashboard | GPO Executive | Phase 5 end |
| Pilot deployment proposal | GPO leadership | Phase 6 |

---

## 4. สถานะปัจจุบัน: สิ่งที่ทำแล้ว

### 4.1 Infrastructure ✅
- Repository scaffolding: monorepo with `src/pharma_intel/` subpackages
- Development environment: Python 3.12 + pyproject.toml + pip venv
- CI standards: ruff, black, mypy, pytest
- Configuration system: pydantic-settings + loguru
- Git workflow: conventional commits, feature branches

### 4.2 Engine B — RAG (partial) ✅
- **Ingestion:** FDA Orange Book download + parse (1,800+ cardiometabolic monographs)
- **Embedding:** BAAI/bge-m3 wrapper (bilingual Thai + English)
- **Vector store:** ChromaDB with metadata filtering
- **Query engine:** retrieve + generate with citations
- **LLM abstraction:** ThaiLLM default + Claude benchmark (provider pattern)

### 4.3 Engine A — Forecasting (Week 2) ✅
- **Molecule class registry:** 13 classes with metadata (patent expiry, launch year, driver)
- **Anchors module:** Thai public health statistics (prevalence, market shares, budget index)
- **Mock data generator:** synthetic monthly demand 2018–2025, 4 channels
- **SARIMAX baseline:** with and without exogenous features
- **Evaluation framework:** MAPE, sMAPE, MASE, RMSE

### 4.4 Documentation ✅
- `docs/project_scope.md` — 1-pager for advisor alignment
- `docs/next_steps.md` — human-readable roadmap
- `docs/experiment_01_sarimax_baseline.md` — first results
- `docs/experiment_02_realistic_mock.md` — mock data iteration
- `docs/experiment_03_realistic_mock.md` — root cause analysis
- `.github/copilot-instructions.md` — AI assistant guardrails
- `docs/prompts/` — Copilot Agent prompt library

### 4.5 สิ่งที่ยัง**ไม่ได้**ทำ ❌
- Real public data integration (HDC, e-GP, สปสช.)
- Thai regulatory scrapers (TFDA, ราชกิจจา, NLEM)
- Prophet baseline (Step B prompt พร้อมแล้ว แต่ยังไม่ execute)
- XGBoost + feature engineering
- TFT (Temporal Fusion Transformer)
- ClinicalTrials.gov + PubMed integration
- RAG evaluation set (100+ bilingual Q&A)
- Streamlit dashboard
- GPO formal engagement

---

## 5. บทเรียนจาก Week 1–2

### 5.1 Technical Lessons

**บทเรียน 1: Mock data is a research tool, not a product tool**
- Week 1 พยายามใช้ mock เป็น proxy ของความจริง → ไม่เวิร์ค
- Week 2 experiment 02–03 เจอ SARIMAX baseline 7.1% → 12.7% → ระเบิด
- **สรุป:** mock data มีไว้ validate methodology เท่านั้น ไม่ใช่ demo business value

**บทเรียน 2: SARIMAX + high-dim exog + small sample = catastrophic failure**
- 84 obs × 12 params = 7 obs/param < safe ratio 15
- ต้อง regularization (Prophet) หรือ feature engineering (XGBoost) เท่านั้นที่ handle ได้
- **Paper contribution opportunity:** "Failure modes of classical statistical forecasters under realistic pharmaceutical volatility"

**บทเรียน 3: Root cause analysis > quick fixes**
- Experiment 03 แยกแยะได้ว่าปัญหามี 5 สาเหตุต่างกัน
- บางสาเหตุเป็น data issue, บางสาเหตุเป็น model issue
- **ต้อง diagnose ก่อนแก้ ไม่ใช่ tune random parameters**

### 5.2 Process Lessons

**บทเรียน 4: Build-first, write-later ใช้ได้ผลจริง**
- Week 2 มี artifacts พร้อมใช้ 13 modules + 3 experiment reports
- Paper draft จะเขียนง่ายมากเพราะมีหลักฐานครบ

**บทเรียน 5: Copilot Agent ต้องมี guardrails**
- Anti-patterns สำคัญกว่าที่คิด (เช่น "ห้าม tune SARIMAX order")
- Decision trees ป้องกัน infinite retry loop
- Scientific honesty clause = เขียนลงไปใน prompt ไม่ใช่ assume

**บทเรียน 6: Windows dev environment มีข้อจำกัดที่ต้องจัดการ**
- Long path issue, `make` ไม่มี, Prophet install ยาก
- แนะนำ short project path, เตรียม fallback, document workarounds

### 5.3 Business/Strategic Lessons

**บทเรียน 7: Mock data ≠ demo-ready**
- ถ้า demo ด้วย mock data โดยไม่ label ชัดเจน → credibility พัง
- Framing ต้องเป็น **"methodology demo"** ไม่ใช่ **"product demo"**

**บทเรียน 8: Need real public data anchor before GPO demo**
- HDC, e-GP, สปสช. public data ต้องมี**บางส่วน**ใน demo
- Mix real + synthetic with clear labels → credibility สูง

**บทเรียน 9: GPO engagement ต้อง informal-first**
- ก่อน formal proposal → ต้อง informal chat ก่อนว่าหัวหน้าสนใจมั้ย
- ก่อน data access → ต้องมี prototype ให้เห็นก่อน
- Sequence: informal → demo → NDA → data → production

---

## 6. System Architecture

### 6.1 High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│          User Interface Layer                               │
│  ┌─────────────────────┐  ┌────────────────────────────┐  │
│  │  Streamlit Dashboard │  │  RAG Chat Interface        │  │
│  │  (forecasts, alerts) │  │  (ThaiLLM / Claude)        │  │
│  └──────────┬───────────┘  └──────────────┬─────────────┘  │
└─────────────┼──────────────────────────────┼────────────────┘
              │                              │
    ┌─────────▼────────────┐      ┌──────────▼───────────────┐
    │  Engine A:           │      │  Engine B:               │
    │  Forecasting         │◄─────┤  Intelligence (RAG)      │
    │                      │      │                          │
    │  - SARIMAX baseline  │      │  - Document ingestion    │
    │  - Prophet baseline  │      │  - Embedding (bge-m3)    │
    │  - XGBoost (main ML) │      │  - Vector DB (Chroma)    │
    │  - TFT (main DL)     │      │  - Hybrid retrieval      │
    │                      │      │  - LLM generation        │
    │  Output:             │      │                          │
    │  - Demand forecast   │      │  Output:                 │
    │  - Uncertainty CIs   │      │  - Grounded answers      │
    │  - Feature importance│      │  - Citations             │
    └──────────┬───────────┘      │  - Event extraction      │
               │                  └──────────┬───────────────┘
               │                             │
               └───────────┬─────────────────┘
                           │
                ┌──────────▼──────────────────┐
                │  Shared Feature Store       │
                │                             │
                │  Exogenous features for     │
                │  Engine A from Engine B:    │
                │  - Patent cliff signals     │
                │  - Regulation events        │
                │  - Competitor launches      │
                │  - Clinical trial phase     │
                │  - Epidemiological proj.    │
                └─────────────────────────────┘
                           │
┌──────────────────────────┴──────────────────────────────────┐
│                Data Ingestion Layer                         │
│                                                             │
│  Public (free):                 Gov/Regulated:              │
│  - FDA Orange Book ✅            - e-GP (Thai procurement)  │
│  - ClinicalTrials.gov            - สปสช. Open Data         │
│  - PubMed                        - HDC prevalence          │
│  - USPTO patents                 - TFDA registrations      │
│  - WHO EML                       - ราชกิจจานุเบกษา         │
│                                  - NLEM                     │
│                                                             │
│  Internal (GPO, phase 6+, under NDA):                       │
│  - Historical sales                                         │
│  - Production volumes                                       │
│  - Pipeline status                                          │
└─────────────────────────────────────────────────────────────┘
```

### 6.2 Design Principles

1. **"ML for numbers, LLM for language"** — Forecasting = ML/DL, Intelligence = RAG
2. **Sovereign-first** — ThaiLLM default, Claude optional
3. **Provider abstraction** — swap LLMs via config, ไม่ rewrite code
4. **Real + synthetic data hybrid** — label ชัดเจน, never mix without transparency
5. **Reproducibility** — random seeds locked, experiments versioned in git
6. **Scientific honesty** — bad results are valuable findings, document them

---

## 7. แผนการทำงาน 6 Phase

**ภาพรวมแต่ละ phase:**

| Phase | ชื่อ | ระยะเวลา | สถานะ |
|---|---|---|---|
| 1 | Foundation | Week 1–2 | ✅ Done |
| 2 | Real Public Data Integration | Week 3–8 | 🎯 Current |
| 3 | Engine B Completion (RAG) | Week 6–14 | Planned |
| 4 | Engine A Completion (Forecasting) | Week 10–22 | Planned |
| 5 | Integration + Dashboard + GPO Demo | Week 20–32 | Planned |
| 6 | Pilot Deployment + Paper | Week 28–52+ | Planned |

---

## Phase 1: Foundation ✅ DONE

### 1.1 สิ่งที่ต้องการ (Inputs)
- ความชัดเจนเรื่อง scope (therapeutic area, horizon, users)
- Tech stack decision
- IP policy decision (ThaiLLM default)

### 1.2 ผลลัพธ์ที่ได้ (Outputs) ✅
- [x] Repo scaffolding ด้วย 4 subpackages
- [x] Config + logging + drug constants
- [x] FDA Orange Book ingestion pipeline
- [x] Mock demand generator
- [x] SARIMAX baseline + metrics
- [x] LLM provider abstraction
- [x] 3 experiment reports
- [x] Copilot prompt library

### 1.3 วิธีทำ (How)
ทำด้วยตนเอง + AI pair programming — ใช้เวลารวม ~2 สัปดาห์

---

## Phase 2: Real Public Data Integration 🎯 CURRENT

### 2.1 วัตถุประสงค์ (Why)
เปลี่ยนจาก "100% mock" → "real anchor + synthetic supplement" เพื่อ:
- ให้ demo GPO มี credibility (real numbers)
- Validate methodology กับข้อมูลจริง
- เตรียม data pipeline สำหรับ production

### 2.2 สิ่งที่ต้องการ (Inputs)
- Internet connection (public APIs)
- ไม่ต้องการ GPO internal data ใน phase นี้
- Legal check: ทุก source เป็น public domain / open license

### 2.3 ผลลัพธ์ที่ต้องได้ (Outputs)

**Data artifacts:**
- `data/processed/hdc_ncd_prevalence.parquet` — NCD prevalence รายปี 2015–2025
- `data/processed/egp_cardiometabolic_procurement.parquet` — e-GP procurement monthly
- `data/processed/nhso_utilization.parquet` — UC drug utilization
- `data/processed/orange_book_monographs.parquet` — ✅ already done
- `data/processed/clinicaltrials_cardiometabolic.parquet` — global trials
- `data/processed/pubmed_abstracts.parquet` — recent literature

**Code artifacts:**
- `src/pharma_intel/ingestion/hdc_scraper.py`
- `src/pharma_intel/ingestion/egp_scraper.py`
- `src/pharma_intel/ingestion/nhso_scraper.py`
- `src/pharma_intel/ingestion/clinicaltrials_api.py`
- `src/pharma_intel/ingestion/pubmed_api.py`
- Unified `src/pharma_intel/ingestion/pipeline.py`

**Documentation:**
- `docs/data_sources.md` — แต่ละ source, field mapping, update frequency, licensing
- `docs/experiment_04_real_data_integration.md`

### 2.4 วิธีทำ (How)

**Step 2.1 — HDC NCD Prevalence (Week 3)**
```
Priority: HIGH (easiest + highest value)
Source: https://hdcservice.moph.go.th
Method: Manual CSV download initially → automate scraper if API available
Target fields:
  - year, province, age_group, disease_code
  - prevalence_per_1000
  - gender breakdown
Validation: compare against NHES reports for sanity check
```

**Step 2.2 — e-GP Drug Procurement (Week 3–4)**
```
Priority: HIGH (closest to GPO's world)
Source: https://www.gprocurement.go.th
Method: Web scraping with Playwright (JS-heavy site)
Target: government drug procurement records by month × drug × hospital
Challenges:
  - Anti-bot protection → rotate UA, add delays
  - Thai drug names need mapping to RxNorm/ATC
Validation: sample 50 records, manually verify against source
```

**Step 2.3 — สปสช. Open Data (Week 4–5)**
```
Priority: MEDIUM
Source: https://opendata.nhso.go.th
Method: CSV/API download
Target: UC scheme drug utilization monthly aggregates
Benefit: closest proxy to actual consumption demand
```

**Step 2.4 — ClinicalTrials.gov Integration (Week 5)**
```
Priority: MEDIUM
Source: https://clinicaltrials.gov (official API)
Method: REST API with rate limiting
Target: all Phase II–IV trials for cardiometabolic drugs
Value: leading indicator for new drug demand 2–4 years ahead
```

**Step 2.5 — PubMed Literature (Week 6)**
```
Priority: LOW-MEDIUM
Source: NCBI E-utilities API
Method: Query per drug + date range
Target: recent (last 5 yr) abstracts per molecule class
Value: research activity signal for demand forecasting
```

**Step 2.6 — Unified Data Pipeline (Week 6–7)**
```
Create: src/pharma_intel/ingestion/pipeline.py
Responsibilities:
  - Schedule all scrapers (Prefect or GitHub Actions cron)
  - Version data (DVC or timestamped Parquet)
  - Data quality checks (completeness, freshness)
  - Monitor + alert on failures
```

**Step 2.7 — Data Quality Report (Week 7–8)**
```
Create: docs/experiment_04_real_data_integration.md
Include:
  - Coverage analysis per source (years, classes, completeness %)
  - Comparison: real data trends vs mock data anchors
  - Known gaps and limitations
  - Recommendations for production use
```

### 2.5 Acceptance Criteria
- [ ] อย่างน้อย 3 จาก 5 sources ทำงานได้ end-to-end
- [ ] มี data coverage ย้อนหลังอย่างน้อย 5 ปีทุก source
- [ ] Data quality report เสร็จ
- [ ] สามารถ refresh data ได้ด้วย 1 command
- [ ] Real prevalence numbers ใกล้เคียง mock anchors (sanity check)

### 2.6 Risks และ Mitigation
| Risk | Mitigation |
|---|---|
| e-GP scraping blocked | Manual quarterly download as fallback; contact กรมบัญชีกลางเป็น official |
| HDC API rate limits | Cache aggressively; update monthly ไม่ต้อง real-time |
| Thai drug name → RxNorm mapping ยาก | Build custom Thai drug dictionary incrementally |
| Data licensing unclear | Document each source's license; consult advisor if uncertain |

### 2.7 Timeline: Week 3–8 (6 สัปดาห์)

---

## Phase 3: Engine B Completion (RAG System)

### 3.1 วัตถุประสงค์ (Why)
สร้าง regulatory intelligence system ที่ใช้งานได้จริงกับ**ข้อมูลไทย** ไม่ใช่แค่ FDA Orange Book

### 3.2 สิ่งที่ต้องการ (Inputs)
- Phase 2 outputs (Thai data sources)
- ThaiLLM API key
- (Optional) Anthropic API key for benchmarking

### 3.3 ผลลัพธ์ที่ต้องได้ (Outputs)

**Code:**
- `src/pharma_intel/ingestion/tfda_scraper.py` — Thai FDA drug registrations
- `src/pharma_intel/ingestion/ratchakitcha_scraper.py` — Royal Gazette
- `src/pharma_intel/ingestion/nlem_scraper.py` — Essential Medicines List
- `src/pharma_intel/rag/hybrid_retrieval.py` — BM25 + dense + reranker
- `src/pharma_intel/rag/event_extractor.py` — LLM-based entity extraction
- `src/pharma_intel/rag/evaluator.py` — RAGAS integration

**Data:**
- `chroma_db/` — unified index with Thai + English documents
- `data/processed/regulatory_events.parquet` — extracted structured events

**Evaluation:**
- `data/eval/rag_test_set.jsonl` — 100–200 Q&A pairs (bilingual)
- `data/processed/rag_benchmark_results.json` — ThaiLLM vs Claude comparison

**Documentation:**
- `docs/experiment_05_thai_rag.md`
- `docs/experiment_06_rag_evaluation.md`
- `docs/experiment_07_llm_benchmark.md`

### 3.4 วิธีทำ (How)

**Step 3.1 — TFDA Scraper (Week 6–7)**
```
Source: https://www.fda.moph.go.th
Method: requests + BeautifulSoup (mostly static HTML)
Target: new drug registrations, recalls, safety alerts
Parse: Thai text via PyThaiNLP normalization
Output: structured JSON per record
```

**Step 3.2 — ราชกิจจานุเบกษา Scraper (Week 7–8)**
```
Source: https://ratchakitcha.soc.go.th
Method: Daily RSS + PDF download
Parse: PDF extraction (typhoon-ocr for scanned) + keyword filter
Target: กฎหมาย/ประกาศ/คำสั่ง related to drugs
Challenges:
  - Scanned PDFs need OCR
  - Legal Thai is dense, needs careful chunking
Output: classified document store
```

**Step 3.3 — NLEM Parser (Week 8)**
```
Source: http://ndi.fda.moph.go.th
Method: Annual PDF download + parse
Target: current Thailand Essential Medicines List
Value: signals "which drugs are covered" — huge demand driver
Output: structured drug list with tier (A/B/C/D/E)
```

**Step 3.4 — Hybrid Retrieval (Week 9–10)**
```
Replace simple dense retrieval with:
  1. BM25 (rank_bm25) for keyword match
  2. Dense (bge-m3) for semantic
  3. Reciprocal Rank Fusion
  4. Cross-encoder rerank (BAAI/bge-reranker-v2-m3)
Expected: Context Precision > 0.80, Recall > 0.85
```

**Step 3.5 — Event Extraction (Week 10–11)**
```
Create LLM pipeline:
  Input: regulatory document
  Output: structured event
    {
      event_type: approval|recall|nlem_change|law|...,
      affected_drugs: [ATC codes],
      effective_date: date,
      impact_level: low|medium|high,
      summary_thai: str,
      summary_english: str
    }
Use ThaiLLM for extraction + classification
Feed output → Engine A as exogenous features
```

**Step 3.6 — Evaluation Set Creation (Week 11–12)**
```
Create 100–200 Q&A pairs manually (you, as pharmacist):
  - 40 fact retrieval ("When was X approved in Thailand?")
  - 30 regulatory interpretation ("Which class does this law affect?")
  - 20 cross-document synthesis
  - 10 temporal queries
  - Mix Thai (40%), English (40%), code-switched (20%)
Store as JSONL with: {question, answer_ground_truth, source_docs}
```

**Step 3.7 — RAGAS Evaluation (Week 12–13)**
```
Metrics:
  - Context Precision, Context Recall
  - Faithfulness, Answer Relevancy
  - Citation Accuracy (custom)
Run on ThaiLLM + Claude benchmarks
Compare: does language-specialized Thai LLM beat frontier EN LLM on Thai queries?
```

**Step 3.8 — Research Report (Week 13–14)**
```
Write paper section:
  - Methodology: bilingual RAG architecture
  - Results: retrieval metrics + generation quality
  - Finding: where ThaiLLM wins/loses vs Claude
  - Implication for sovereign AI in pharma context
```

### 3.5 Acceptance Criteria
- [ ] TFDA, ราชกิจจา, NLEM scrapers ทำงานได้
- [ ] Hybrid retrieval: Context Precision > 0.80
- [ ] Faithfulness > 0.90 (both LLMs)
- [ ] Citation accuracy > 0.95
- [ ] Bilingual performance gap < 15%
- [ ] Event extraction works on sample of 50 documents
- [ ] RAG can answer "ยาเบาหวานที่ NLEM categoryA มีอะไรบ้าง" correctly

### 3.6 Risks
| Risk | Mitigation |
|---|---|
| Thai OCR quality poor | Use typhoon-ocr + manual spot check top 100 docs |
| Evaluation set bias (you wrote it) | Have 1 colleague review; use diverse question types |
| ThaiLLM rate limit (5 req/sec) | Batch + cache; run benchmark overnight |
| LLM cost overrun | Monitor tokens; use Haiku for bulk; batch API |

### 3.7 Timeline: Week 6–14 (ขนาน Phase 2 ปลายทาง + ต่อ)

---

## Phase 4: Engine A Completion (Forecasting System)

### 4.1 วัตถุประสงค์ (Why)
Complete forecasting pipeline: add models beyond SARIMAX, run proper ablation studies, produce publishable results.

### 4.2 สิ่งที่ต้องการ (Inputs)
- Phase 2 real data (anchor for realistic mock + validation)
- Phase 3 RAG-extracted events (for exogenous features)
- Vast AI GPU access (for TFT)

### 4.3 ผลลัพธ์ที่ต้องได้ (Outputs)

**Code:**
- `src/pharma_intel/forecasting/prophet_baseline.py` — 2nd baseline
- `src/pharma_intel/forecasting/feature_engineering.py` — lag, rolling, encoding
- `src/pharma_intel/forecasting/xgboost_model.py` — main ML
- `src/pharma_intel/forecasting/tft_model.py` — main DL
- `src/pharma_intel/forecasting/evaluation.py` — Diebold-Mariano + backtesting

**Experiments:**
- `docs/experiment_08_prophet.md`
- `docs/experiment_09_xgboost.md`
- `docs/experiment_10_tft.md`
- `docs/experiment_11_ablation_study.md`
- `docs/experiment_12_final_benchmark.md`

**Results:**
- `data/processed/benchmarks/final_results.parquet` — all models × all classes × all horizons

### 4.4 วิธีทำ (How)

**Step 4.1 — Prophet Baseline (Week 10–11)**
```
Already have prompt ready (docs/prompts/step_B_prophet_baseline.md)
Run: after Phase 2 data integration to have real anchors
Test hypothesis: Prophet's Bayesian regularization fixes SARIMAX+exog instability
Expected: Prophet+exog MAPE ~10-18% (stable, no catastrophic failures)
```

**Step 4.2 — Feature Engineering Module (Week 12–13)**
```
Create: src/pharma_intel/forecasting/feature_engineering.py
Features:
  Endogenous:
    - lag (1, 3, 6, 12, 24 months)
    - rolling mean, std, min, max (3, 6, 12 windows)
    - YoY growth
    - Calendar (month, quarter, Thai fiscal position)
  Exogenous from Engine B:
    - days_to_nearest_patent_expiry_in_class
    - regulatory_event_count_last_6mo
    - nlem_status (A/B/C/D/E)
    - competitor_launch_flag
  Static per-class:
    - atc_level_1, atc_level_3, route
    - years_since_first_launch_global
    - gpo_manufactured_flag
```

**Step 4.3 — XGBoost Global Model (Week 13–15)**
```
Design:
  - Single model across all 13 classes (global learning)
  - class_id as categorical feature
  - Recursive multi-step forecasting for long horizons
Tuning:
  - Optuna 50-trial hyperparameter search
  - Time-series split (no data leakage)
Evaluation:
  - MAPE per class × horizon (12, 24, 36 months)
  - Feature importance (SHAP values)
Expected: beat Prophet by ≥5% relative MAPE
```

**Step 4.4 — TFT Implementation (Week 15–19)**
```
Use pytorch-forecasting library
Dataset:
  - 13 classes × 84 months = manageable
  - Encoder: 24 months, Decoder: 12–36 months
Training:
  - On Vast AI T4 or A100
  - Early stopping on validation loss
  - ~4-8 hours per major experiment
Experiments:
  E1: TFT endogenous-only (baseline)
  E2: TFT + prevalence features
  E3: TFT + patent/regulation features
  E4: TFT + all exogenous
  E5: Ensemble TFT + Prophet
```

**Step 4.5 — Ablation Study (Week 19–20)**
```
Systematic comparison across:
  - 5 models (Naive, SARIMAX, Prophet, XGBoost, TFT)
  - 2 feature sets (endog-only, +exog)
  - 3 horizons (12, 24, 36 months)
  - 13 classes
Statistical test: Diebold-Mariano per pair
Output: comprehensive benchmark table
```

**Step 4.6 — Final Benchmark + Paper Draft (Week 20–22)**
```
Write IS1 paper section 4 "Baseline Evaluation" and section 5 "Deep Learning":
  - Methodology (data, splits, metrics)
  - Results tables
  - Ablation analysis
  - Discussion on exogenous feature value
  - Limitations
```

### 4.5 Acceptance Criteria
- [ ] Prophet baseline MAPE 10–18% (realistic)
- [ ] XGBoost beats Prophet by ≥5% relative
- [ ] TFT beats XGBoost by ≥3% relative (at least at longer horizons)
- [ ] Exogenous features help TFT/XGBoost (Diebold-Mariano p<0.05)
- [ ] Forecasts have uncertainty intervals (prediction intervals, not point)
- [ ] All 13 classes included, no cherry-picking

### 4.6 Risks
| Risk | Mitigation |
|---|---|
| TFT doesn't converge | Try DeepAR fallback; reduce complexity; longer training |
| Vast AI instance loss | Save checkpoints to Google Drive; resume-able training |
| Hyperparameter search overfitting | Separate validation set; use TS cross-validation |
| Exogenous features overfit XGBoost too | Built-in regularization; feature selection |

### 4.7 Timeline: Week 10–22 (ต้องจบก่อน end of semester 1 สำหรับ IS1)

---

## Phase 5: Integration + Dashboard + GPO Demo

### 5.1 วัตถุประสงค์ (Why)
Integrate both engines, build user-facing dashboard, prepare professional demo for GPO stakeholders.

### 5.2 สิ่งที่ต้องการ (Inputs)
- Phase 3 + 4 outputs (RAG + Forecasting both working)
- GPO stakeholder buy-in from informal engagement
- Streamlit deployment option

### 5.3 ผลลัพธ์ที่ต้องได้ (Outputs)

**Code:**
- `app/streamlit_app.py` — main dashboard
- `app/pages/1_pipeline_recommender.py`
- `app/pages/2_regulatory_feed.py`
- `app/pages/3_drug_deep_dive.py`
- `app/pages/4_ask_ai.py`

**Documents:**
- Executive summary 1-page (Thai)
- Demo script (step-by-step)
- Pitch deck (10–12 slides)
- FAQ document (prepare for GPO questions)

### 5.4 วิธีทำ (How)

**Step 5.1 — Dashboard Development (Week 20–24)**
```
Pages:
  1. Home
     - KPI overview
     - Next alerts
     - Drug spotlight of the week
  
  2. Pipeline Recommender
     - Score drugs for R&D priority
     - Combine: demand forecast + patent window + competitive landscape
     - Output: ranked list with rationale
  
  3. Regulatory Feed
     - Filterable stream of new events (TFDA, ราชกิจจา, FDA)
     - LLM-generated Thai summaries
     - Impact classification
  
  4. Drug Deep-Dive
     - Per-drug view
     - Historical demand + forecast with CI
     - Patent timeline
     - Competitor launches
     - Related regulations
  
  5. Ask AI
     - RAG chat interface
     - Bilingual
     - Citations
```

**Step 5.2 — Demo Preparation (Week 24–26)**
```
Create materials:
  - Executive summary (1 page Thai)
    * Problem statement
    * Solution overview
    * Expected value
    * Ask (what we need from GPO)
  
  - Demo script (30-min session)
    * Opening (2 min): problem context
    * Demo Part 1: RAG for regulation (8 min)
    * Demo Part 2: Forecasting methodology (10 min)
    * Integration: cross-engine value (5 min)
    * The Ask (3 min): data access + pilot
    * Q&A (2 min)
  
  - Pitch deck (bilingual)
  
  - FAQ document (anticipate tough questions):
    * "How accurate is the forecast?"
    * "Where did the data come from?"
    * "What do you need from us?"
    * "What's the cost?"
    * "Who owns the IP?"
    * "Can this replace our RA team?" (answer: no, augment)
```

**Step 5.3 — Demo with GPO (Week 26–28)**
```
Sequence:
  1. Informal coffee chat with supervisor (week 26)
  2. Present to immediate team (week 27)
  3. If positive: present to department head (week 27–28)
  4. If positive: formal pitch to executives (week 28+)
Goal: Get LOI or data access agreement
```

**Step 5.4 — Feedback Integration (Week 28–32)**
```
Capture GPO feedback systematically:
  - What resonated
  - What didn't
  - What questions were asked
  - What features they requested
Adjust roadmap based on feedback
```

### 5.5 Acceptance Criteria
- [ ] Dashboard deploys and runs without errors
- [ ] All 5 pages functional
- [ ] Demo can be run end-to-end in 30 minutes
- [ ] At least 3 GPO stakeholders see demo
- [ ] Captured feedback documented
- [ ] Decision from GPO: pilot / not-pilot / need-more-info

### 5.6 Risks
| Risk | Mitigation |
|---|---|
| Demo breaks during presentation | Pre-record backup video; practice 3+ times |
| Hard questions from executives | FAQ document + honest "I don't know, will find out" |
| Political resistance from GPO | Start with individual champions, build grassroots |
| Demo data not convincing | Mix real public data + clearly-labeled synthetic |

### 5.7 Timeline: Week 20–32

---

## Phase 6: Pilot Deployment + Paper + Commercialization

### 6.1 วัตถุประสงค์ (Why)
- Academic: defend IS1+IS2, publish paper
- Business: deploy pilot, learn in production
- Long-term: commercial spin-off or GPO internal system

### 6.2 สิ่งที่ต้องการ (Inputs)
- Phase 5 success (GPO interest confirmed)
- IS1 + IS2 thesis committee approval
- Time: thesis + pilot = 6–12 months

### 6.3 ผลลัพธ์ที่ต้องได้ (Outputs)

**Academic:**
- IS1 thesis submitted + defended
- IS2 thesis submitted + defended
- Conference paper accepted (JCSSE / NCIT / KICSS) or journal submission

**Business:**
- GPO pilot deployment (under NDA, with internal data)
- Updated forecasts with real GPO historical sales
- Usage analytics (who uses what, how often)
- Business case for ongoing internal deployment

**Commercial (optional):**
- Separate codebase for commercialization (non-GPO data only)
- LOIs from 2–3 other Thai pharma companies
- Startup registration / corporate entity
- Seed funding or grant application

### 6.4 วิธีทำ (How)

**Step 6.1 — Thesis Writing (Week 28–44)**
```
IS1 (Forecasting-focused):
  - Chapter 1: Introduction
  - Chapter 2: Literature Review
  - Chapter 3: Methodology
  - Chapter 4: Data
  - Chapter 5: Results (Prophet, XGBoost, TFT, ablation)
  - Chapter 6: Discussion
  - Chapter 7: Conclusion + Future Work

IS2 (RAG-focused):
  - Similar structure
  - Focus on bilingual RAG + LLM benchmarking + integration
```

**Step 6.2 — Paper Submission (Week 36–44)**
```
Target venues (Thai/SEA first, then international):
  - IEEE JCSSE (annual, deadline typically Oct)
  - NCIT Thailand (deadline varies)
  - KICSS (international ASEAN)
  - iSAI-NLP (NLP-focused if IS2)
Process:
  1. Draft
  2. Advisor review
  3. Submit
  4. Respond to reviews
  5. Camera-ready
```

**Step 6.3 — GPO Pilot Deployment (Week 30–52)**
```
Assuming GPO agreed in Phase 5:
  1. NDA signed (week 30–32)
  2. Data handover + integration (week 32–36)
  3. Retrain models on real data (week 36–40)
  4. Deploy dashboard on internal infrastructure (week 40–44)
  5. User training (week 44–46)
  6. Production monitoring (week 46+)
  7. Iteration based on usage (ongoing)
```

**Step 6.4 — Commercial Spin-off (Week 44+, optional)**
```
Only if:
  - IP with GPO is clear (written clearance)
  - Demand from non-GPO Thai pharma is validated
  - Personal bandwidth available
Steps:
  1. Separate non-GPO codebase + data
  2. Build MVP for 2nd customer segment (local Thai pharma)
  3. LOIs from 3+ potential customers
  4. Registered company
  5. Seed fundraising or grant (NIA, BUCA, depa)
```

### 6.5 Acceptance Criteria (Academic)
- [ ] IS1 defense passed
- [ ] IS2 defense passed
- [ ] At least 1 paper submitted
- [ ] Thesis documents archived at KMITL

### 6.6 Acceptance Criteria (Business)
- [ ] GPO pilot deployed (or clearly documented why not)
- [ ] Usage data collected for ≥3 months
- [ ] ROI analysis completed

### 6.7 Risks
| Risk | Mitigation |
|---|---|
| Paper rejected | Revise based on reviews; try 2nd venue; journal later |
| GPO pulls pilot | Document lessons learned; apply to other pharma |
| IP dispute with GPO | Written agreement upfront (ยังไม่ได้ข้าม phase นี้ถ้า IP ยังไม่ชัด) |
| Personal burnout | Milestone checkpoints; don't sprint 12 months straight |

### 6.8 Timeline: Week 28–52+ (ยืดหยุ่นตาม thesis timeline จริง)

---

## 8. Data Strategy

### 8.1 Data Tiers

**Tier 1: Public (free, fully usable)**
- FDA Orange Book ✅
- ClinicalTrials.gov
- PubMed
- USPTO patents
- WHO Essential Medicines
- ราชกิจจานุเบกษา (archive)

**Tier 2: Public Thai Government (free but fragile)**
- TFDA drug registrations
- HDC prevalence
- สปสช. open data
- e-GP procurement

**Tier 3: Synthetic (generated, must label)**
- Mock demand panel (current)
- Augmented training data (future)

**Tier 4: GPO Internal (requires NDA, Phase 6)**
- Historical sales
- Production volumes
- R&D pipeline

### 8.2 Data Governance Rules

1. **Labeling:** Every data artifact must indicate tier in metadata
2. **Isolation:** Tier 4 data NEVER enters git history
3. **Commercial:** Commercial fork uses Tier 1–3 only
4. **Versioning:** Each tier has its own refresh cadence
5. **Provenance:** Every processed file must cite source + date

### 8.3 Refresh Cadence

| Source | Cadence | Method |
|---|---|---|
| FDA Orange Book | Monthly | Scheduled scraper |
| ClinicalTrials.gov | Weekly | Scheduled scraper |
| TFDA registrations | Weekly | Scheduled scraper |
| ราชกิจจา | Daily | Scheduled scraper |
| HDC prevalence | Quarterly | Manual download |
| e-GP procurement | Monthly | Scheduled scraper |
| Mock data | On demand | `python scripts/generate_mock_demand.py` |

---

## 9. Tech Stack และ Infrastructure

### 9.1 Development
- Python 3.12, pip + venv
- VS Code + Copilot Agent
- Git + GitHub (private repo, project branch for IS)
- Windows 11 + PowerShell (primary) + Git Bash (fallback)

### 9.2 Compute
- Local: CPU for dev + small experiments
- Colab Pro: GPU for embedding + medium training
- Vast AI: dedicated GPU for TFT training (on-demand)
- Google Drive 5TB: data + model storage

### 9.3 Data Stack
- polars (primary), pandas (stats libs)
- DuckDB (ad-hoc SQL)
- Parquet (storage)
- ChromaDB (vectors)

### 9.4 Modeling Stack
- statsmodels (SARIMAX)
- prophet (Bayesian)
- xgboost (main ML)
- pytorch-forecasting (TFT)
- sentence-transformers (embeddings)
- anthropic SDK + httpx (LLM)

### 9.5 Application Stack
- Streamlit (dashboard)
- typer + rich (CLI)
- pydantic (validation)
- loguru (logging)

### 9.6 Observability
- MLflow (experiment tracking) — Phase 4+
- Weights & Biases (alternative) — if needed
- Manual git commits for smaller experiments

---

## 10. Timeline และ Milestones

### 10.1 Gantt Overview

```
Week:  1  2  3  4  5  6  7  8  9 10 11 12 13 14 15 16 17 18 19 20 21 22 23 24 25 26 27 28 29 30 ...
P1:    ■■
P2:          ■■■■■■■■■■■■
P3:                   ■■■■■■■■■■■■■■■■■■
P4:                               ■■■■■■■■■■■■■■■■■■■■■■■■
P5:                                                 ■■■■■■■■■■■■■■■■■■■■■■■■
P6:                                                                   ■■■■■■■■■■■...
```

### 10.2 Key Milestones

| Week | Milestone | Deliverable |
|---|---|---|
| 2 | ✅ Foundation | Repo, mock data, SARIMAX baseline |
| 8 | Phase 2 complete | Real public data integrated |
| 14 | Phase 3 complete | Thai RAG working + evaluated |
| 22 | Phase 4 complete | TFT + full ablation study |
| 26 | First GPO demo | Dashboard + pitch ready |
| 32 | Phase 5 complete | GPO decision on pilot |
| 44 | IS1 defense | Thesis accepted |
| 52 | IS2 defense + paper submitted | Second thesis + conference paper |

### 10.3 Weekly Cadence (ข้อเสนอ)
- **Monday:** Planning + priority setting
- **Tue–Thu:** Deep work (coding, writing)
- **Friday:** Experiment runs + report writing
- **Weekend:** Rest or buffer

---

## 11. Risks และ Mitigation

### 11.1 Technical Risks

| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| TFT ไม่ converge หรือ GPU memory issues | Medium | High | Start with small config; N-BEATS fallback; more checkpoints |
| Thai OCR คุณภาพแย่ | High | Medium | typhoon-ocr + manual spot check |
| ChromaDB scale issues | Low | Medium | Qdrant ready as production swap |
| Long Windows paths | Medium | Low | Short project paths; document workaround |
| Package install failures | Medium | Medium | pin versions; conda-forge fallback |

### 11.2 Data Risks

| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| e-GP scraping blocked | Medium | High | Manual quarterly download fallback |
| GPO data access denied | High | High | Use public + mock; delay commercial phase |
| Licensing issues on some sources | Low | Medium | Legal check per source; document |
| Data quality poor (Thai sources) | High | Medium | Validation + completeness reports |

### 11.3 Academic Risks

| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| Advisor pivot mid-project | Low | High | Lock scope early; written agreement |
| Paper rejected | High | Medium | Multiple venue targets; revision cycle |
| IS timeline slip | Medium | High | Build-first strategy; parallel work |
| Committee unfamiliar with TFT | Medium | Low | Start with Prophet/SARIMAX; progress to TFT |

### 11.4 Business/IP Risks

| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| GPO IP dispute | Medium | Critical | Written clearance before any commercial work |
| Competitor copies approach | Low | Medium | Move fast; publish; first-mover |
| Founder burnout | High | Critical | Realistic milestones; rest; delegate if possible |
| ThaiLLM service discontinued | Low | High | Provider abstraction; Claude fallback ready |

### 11.5 Process Risks

| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| Scope creep | High | High | Written scope; advisor check-ins; say no |
| Too ambitious timeline | High | High | Built-in buffer; mini-milestones |
| Lost git commits | Low | Medium | Frequent commits; remote backup |
| Key person illness/absence | Medium | High | Document everything; version control |

---

## 12. Success Criteria

### 12.1 Minimum Viable Success
(ถ้าทำได้แค่นี้ก็ถือว่าสำเร็จ)
- IS1 passed
- IS2 passed
- RAG system demonstrably working on Thai+English
- Forecasting baseline beaten by at least 1 ML model

### 12.2 Target Success
(เป้าหมายหลัก)
- Above + paper published at Tier 2+ conference
- GPO LOI for pilot
- TFT implemented + beats XGBoost

### 12.3 Stretch Success
(ถ้าได้เพิ่ม ถือว่าเกินคาด)
- Above + GPO pilot deployed
- 2nd pharma company LOI
- Commercial entity registered
- Seed funding secured

### 12.4 Metrics Summary

**Academic:**
- IS1 + IS2 defense passed ✓
- Paper acceptance at chosen venue
- Citations (later)

**Technical:**
- Forecasting MAPE: realistic range (12–20%) baseline, ML ≥5% better
- RAG: Faithfulness >0.90, Citation accuracy >0.95
- Dashboard: uptime >99%

**Business:**
- GPO stakeholders exposed: ≥5
- Demo completions: ≥3
- LOI/agreement: ≥1
- Pilot usage: ≥3 months if deployed

---

## 13. Budget Estimate

### 13.1 Direct Costs (per month)

| Item | Est. cost (THB) | Notes |
|---|---|---|
| Colab Pro | 400 | Dev + embedding on GPU |
| Vast AI (Phase 4 only) | 2,000–5,000 | TFT training ~2–4 weeks total |
| Anthropic API (benchmarking) | 500–2,000 | Lower if use batch + Haiku |
| ThaiLLM API | 0 | Free tier sufficient |
| Domain + hosting (Phase 5+) | 500 | Dashboard deployment |
| Total (avg) | **~3,000–8,000** | Depends on phase |

### 13.2 One-time Costs
- Python 3.12 setup: 0
- VS Code + extensions: 0
- GitHub Copilot: $10/month ($120/year) optional but recommended
- Conference attendance (paper): ~10,000–20,000 THB per event

### 13.3 Total 18-month Budget
- Compute + API: 60,000–150,000 THB
- Conference: 10,000–40,000 THB
- **Grand total: ~70,000–190,000 THB**

### 13.4 Potential Funding Sources
- KMITL research grant (check eligibility)
- NIA / depa startup grants (Phase 6+)
- BUCA / สกว. research fund
- GPO R&D budget (if pilot moves forward)

---

## 14. IS1 / IS2 Mapping

### 14.1 IS1: Forecasting Track

**Working title:** *"Exogenous Regulatory and Patent Signals for Long-horizon Pharmaceutical Demand Forecasting: A Case Study on Thai Cardiometabolic Generics"*

**Phases primarily covered:**
- Phase 1 (Foundation)
- Phase 2 partial (data relevant to forecasting: HDC, e-GP, สปสช.)
- Phase 4 complete (forecasting models)

**IS1 chapter mapping:**
- Ch 1 Intro: Phase 1 scope
- Ch 2 Literature: state of pharma forecasting
- Ch 3 Methodology: Phase 4 model design
- Ch 4 Data: Phase 2 integration
- Ch 5 Results: Phase 4 experiments (experiment_08–12)
- Ch 6 Discussion: implications
- Ch 7 Conclusion + Future Work (→ IS2)

### 14.2 IS2: Intelligence Track

**Working title:** *"Sovereign Thai LLM for Bilingual Pharmaceutical Regulatory Intelligence: Monitoring, Extraction, and Integration with Forecasting Systems"*

**Phases primarily covered:**
- Phase 2 partial (regulatory sources: TFDA, ราชกิจจา, NLEM)
- Phase 3 complete (RAG system)
- Phase 5 partial (integration)

**IS2 chapter mapping:**
- Ch 1 Intro: Phase 1 scope + IS1 summary
- Ch 2 Literature: state of RAG + Thai NLP
- Ch 3 Methodology: Phase 3 architecture
- Ch 4 Data: Phase 2 regulatory data
- Ch 5 Results: Phase 3 experiments (experiment_05–07)
- Ch 6 Integration: cross-engine study (Phase 5)
- Ch 7 Discussion + Future Work

---

## 15. Commercialization Path

### 15.1 Decision: When to Commercialize?

**Go/No-go criteria (after Phase 5):**
- [ ] GPO pilot confirmed or declined (either way, have signal)
- [ ] Written IP clearance (can you commercialize without GPO blocking?)
- [ ] Demand validation from ≥2 non-GPO pharma
- [ ] Founder bandwidth available (1,000+ hours/year)
- [ ] Financial runway (need ~500k–2M THB for 12 months)

### 15.2 If Go: Structure

**Option A: SaaS Product**
- Thai/SEA pharma intelligence platform
- Monthly subscription: 50–300k THB/month per customer
- Target: 10+ customers = 5–30M THB/year revenue potential

**Option B: Service + Consulting**
- Consulting-first: bespoke analysis
- Lower scale, higher margin
- Less tech debt

**Option C: Government / NGO**
- Sell to Thai MOH as national tool
- Single large contract
- Slower sales cycle but stable

### 15.3 If No-Go: Graceful Exit
- IS1 + IS2 complete = academic success
- Open source the non-GPO components
- Pivot to different research or career

### 15.4 IP Strategy

**Before any commercial activity:**
1. Written IP clearance from GPO in writing
2. Clear that thesis IP belongs to student (KMITL policy check)
3. Any code/data touched by GPO = separated from commercial
4. Trademark the product name if viable

---

## 16. Decision Log

| Date | Decision | Reason |
|---|---|---|
| 2026-04 | Chose cardiometabolic TA | Data availability + policy relevance |
| 2026-04 | ThaiLLM default | Sovereign AI positioning |
| 2026-04 | Molecule-class forecast unit | Match decision granularity |
| 2026-04 | IS1 = Forecasting, IS2 = Intelligence | Leverage RAG work from Week 1 |
| 2026-04 | TFT as main model | Publishable novelty |
| 2026-04 | Python 3.12 over 3.14 | ML wheels availability |
| 2026-04 | Copilot Agent with guardrails | Accelerate dev with safety |
| 2026-04 | Move from 100% mock to real+synthetic hybrid | Demo credibility |
| 2026-04 | SARIMAX+exog failure is a finding, not a bug | Research honesty |
| 2026-04 | Phase 2 (real data) before Phase 3/4 | Better anchor for everything downstream |

---

## 📎 Appendix A: File Inventory

**Documentation:**
- `docs/project_scope.md` — 1-pager for advisor
- `docs/master_plan.md` — this file
- `docs/next_steps.md` — immediate roadmap
- `docs/data_sources.md` — Phase 2 deliverable
- `docs/experiment_01.md` through `docs/experiment_12.md`

**Code:**
- `src/pharma_intel/common/` — config, logging, constants
- `src/pharma_intel/ingestion/` — scrapers per source
- `src/pharma_intel/rag/` — retrieval + generation
- `src/pharma_intel/forecasting/` — models + evaluation

**Scripts:**
- `scripts/download_*.py`, `scripts/build_*.py`
- `scripts/generate_*.py`, `scripts/run_*.py`
- `scripts/benchmark_*.py`

**Configuration:**
- `pyproject.toml`, `Makefile`
- `.env.example`, `.envrc`
- `.github/copilot-instructions.md`

---

## 📎 Appendix B: Glossary

- **ATC code** — Anatomical Therapeutic Chemical classification (WHO)
- **bge-m3** — BAAI General Embedding, multilingual model
- **DDD** — Defined Daily Dose (WHO unit for drug consumption)
- **Diebold-Mariano** — Statistical test for forecast comparison
- **e-GP** — ระบบจัดซื้อจัดจ้างภาครัฐ (Thai government procurement)
- **HDC** — Health Data Center, กสธ.
- **MAPE** — Mean Absolute Percentage Error
- **NLEM** — National List of Essential Medicines (บัญชียาหลัก)
- **NCD** — Non-Communicable Disease
- **RAG** — Retrieval-Augmented Generation
- **SARIMAX** — Seasonal ARIMA with eXogenous variables
- **สปสช.** — สำนักงานหลักประกันสุขภาพแห่งชาติ (NHSO)
- **TFDA** — Thai FDA (อย.)
- **TFT** — Temporal Fusion Transformer
- **ThaiLLM / OpenThaiGPT** — Thai sovereign LLM from SCB 10X / NECTEC

---

## 📎 Appendix C: Quick Reference — Commands

```powershell
# Setup
python -m venv .venv
.venv\Scripts\activate
pip install -e ".[dev,forecasting]"

# Phase 1 (done)
pytest -v

# Phase 2 (current)
python scripts\download_hdc.py --input <path-to-hdc-export>
python scripts\download_nhso.py --input <path-to-nhso-export>
python scripts\download_clinicaltrials.py --input <path-to-clinicaltrials-export>

# Phase 3 (upcoming)
python scripts\download_tfda.py --input <path-to-tfda-export>
python scripts\build_index.py
python scripts\evaluate_rag.py

# Phase 4 (upcoming)
python scripts\generate_mock_demand.py
python scripts\run_sarimax_baseline.py
python scripts\run_prophet_baseline.py
python scripts\run_xgboost_baseline.py
python scripts\run_tft_experiment.py

# Phase 5 (upcoming)
streamlit run app\streamlit_app.py

# All phases
git add -A
git commit -m "<conventional commit>"
git push
```

---

**End of Master Plan**

*This document is a living artifact. Update after every phase completion, after advisor meetings, after GPO interactions, and whenever strategic pivots are made. Keep version history in git.*

**Next Review Date:** End of Phase 2 (~Week 8)
**Version Control:** This is v1.0 — commit to `docs/master_plan.md` as baseline.
