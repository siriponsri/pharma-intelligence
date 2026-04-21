# Project Scope: Pharmaceutical Intelligence Platform for GPO

**Author:** Siripon Srihangpiboon
**Program:** M.Sc. AI for Business, KMITL SIT (2025–2026)
**Document version:** 1.0 — Living document, update after advisor meetings
**Status:** Draft for advisor alignment

---

## 1. Problem Statement

**Government Pharmaceutical Organization (GPO)** ซึ่งเป็นผู้ผลิตยาของรัฐไทย เผชิญ pain points 2 เรื่องในกระบวนการ R&D:

1. **R&D cycle ยาวเกินไป** — กว่ายาจะออกสู่ตลาด ความต้องการเปลี่ยนไปแล้ว ทำให้ยาไม่ตรงกับตลาด
2. **ไม่มีระบบ monitoring** สำหรับยาใหม่, ความเคลื่อนไหวคู่แข่ง, และ regulation ที่เปลี่ยนแปลงแบบ real-time

**Business consequence:** GPO เสียโอกาสทางการตลาดและลงทุน R&D ในยาที่อาจจะไม่เป็นที่ต้องการเมื่อ launch

---

## 2. Users & Stakeholders

| User Role | Primary Need | Output ที่ต้องการ |
|---|---|---|
| **R&D / Strategic Planning** | ตัดสินใจว่าควรลงทุนพัฒนายาตัวไหน | Demand forecast 3–5 ปี + pipeline recommendation |
| **Regulatory Affairs (RA)** | ติดตามกฎระเบียบที่กระทบ portfolio | Real-time alert + Thai summary ของ regulation ใหม่ |
| **Marketing** | เข้าใจ competitive landscape | Competitor launch tracker + market share projection |
| **Executive (CEO/CTO)** | Big picture decisions | Executive summary dashboard รายสัปดาห์ |

**Primary user for MVP:** R&D / Strategic Planning team (ตัดสินใจ pipeline)

---

## 3. Scope & Deliverables

### 3.1 Therapeutic Area (Locked)
**Cardiometabolic drugs** ครอบคลุม:
- Diabetes Mellitus (DM)
- Hypertension (HTN)
- Dyslipidemia

**เหตุผล:** Data availability สูงสุด, GPO portfolio ครอบคลุม, patent cliff 2025–2030 หนาแน่น, NCD policy relevance สูง

**ขอบเขตกว้างพอ:** ~50 molecule names, ~1,800 FDA-approved products — เพียงพอสำหรับ cross-series learning ใน TFT

### 3.2 Forecast Unit
**Molecule-class level** (ไม่ใช่ SKU-level) เช่น:
- SGLT2 inhibitors (รวม empagliflozin, dapagliflozin, canagliflozin)
- DPP-4 inhibitors
- ARBs
- Statins

**เหตุผล:** SKU-level noisy เกินไป; class-level เป็น decision unit ที่ R&D ใช้จริง

### 3.3 Forecast Horizon
- **IS1 MVP:** 12–24 months (validate methodology ก่อน)
- **IS1 final:** ขยายเป็น 36–60 months (3–5 ปี ตาม business requirement)

### 3.4 Geographic Scope
- **Primary:** ประเทศไทย (GPO's market)
- **Reference:** US (Orange Book), EU (EMA), Global (WHO) — ใช้เป็น leading indicator เท่านั้น

---

## 4. System Architecture (Two Engines)

```
┌─────────────────────────────────────────────────┐
│         Streamlit Dashboard + RAG Chat          │
└────────────┬────────────────────┬───────────────┘
             │                    │
  ┌──────────▼─────────┐  ┌───────▼──────────────┐
  │  Engine A:         │  │  Engine B:           │
  │  Forecasting (IS1) │◄─┤  Intelligence (IS2)  │
  │                    │  │                      │
  │  • SARIMAX base    │  │  • FDA Orange Book   │
  │  • Prophet         │  │  • TFDA registrations│
  │  • XGBoost         │  │  • ราชกิจจา          │
  │  • TFT (main)      │  │  • ClinicalTrials    │
  │                    │  │  • ThaiLLM RAG       │
  └──────────┬─────────┘  └───────┬──────────────┘
             │                    │
             └────────┬───────────┘
                      ▼
         ┌────────────────────────┐
         │  Exogenous Features:   │
         │  • Patent cliff signal │
         │  • Regulation events   │
         │  • Competitor launches │
         │  • Epi prevalence      │
         └────────────────────────┘
```

**สำคัญ:** Engine B's outputs (extracted events) = Engine A's inputs (exogenous features)
→ Integration เป็น technical contribution หลัก

### 4.1 Principle: "ML for numbers, LLM for language"
- **Forecasting** = classical/deep time-series models (ไม่ใช่ LLM)
- **Event extraction + summarization + classification** = ThaiLLM
- **Q&A over regulatory corpus** = RAG with ThaiLLM

**เหตุผล:** LLM ทำ numeric forecasting ได้แย่กว่าและ defend ใน paper ยาก

---

## 5. IS1 / IS2 Split

### IS1 (Semester 1): Long-term Demand Forecasting
**Working title:** *"Exogenous Regulatory and Patent Signals for Long-horizon Pharmaceutical Demand Forecasting: A Case Study on Thai Cardiometabolic Generics"*

**Deliverables:**
- Mock demand dataset (anchored to public Thai stats)
- Baseline models: SARIMAX, Prophet
- ML model: XGBoost with engineered features
- Deep learning model: Temporal Fusion Transformer (main contribution)
- Ablation study: with/without exogenous features
- Paper draft for IEEE JCSSE / NCIT / KICSS

**Research question:**
> Do external signals (patent expiry, regulatory changes, epi projections) significantly improve long-horizon (36+ month) pharmaceutical demand forecasting over endogenous-only models?

**Evaluation:**
- Metrics: MAPE, sMAPE, MASE, weighted quantile loss
- Statistical test: Diebold-Mariano (p<0.05)
- Backtesting: rolling origin, 3 folds

### IS2 (Semester 2): ThaiLLM Regulatory Intelligence + Integration
**Working title:** *"Sovereign Thai LLM for Bilingual Pharmaceutical Regulatory Intelligence: Monitoring, Extraction, and Integration with Forecasting Systems"*

**Deliverables:**
- Scrapers: TFDA, ราชกิจจา, ClinicalTrials, PubMed
- Event extraction pipeline (LLM-based)
- Bilingual RAG with ThaiLLM
- Integration with IS1 forecasting engine
- Streamlit dashboard
- GPO stakeholder user study

**Research question:**
> Can a sovereign 8B Thai LLM (OpenThaiGPT) match frontier models (Claude Sonnet) on bilingual pharmaceutical regulatory QA, and what is the cost/performance trade-off for government deployment?

---

## 6. Data Strategy

### 6.1 Real Public Data (use immediately)
| Source | Data | Used in |
|---|---|---|
| **FDA Orange Book** | Patent expiry, approvals | IS1 feature, IS2 RAG |
| **NLEM (Thailand)** | Essential medicines list | IS1 feature, IS2 RAG |
| **HDC (กสธ.)** | NCD prevalence trends | IS1 anchor for mock |
| **e-GP (กรมบัญชีกลาง)** | Government drug procurement | IS1 volume validation |
| **สปสช. Open Data** | Reimbursement utilization | IS1 demand proxy |
| **TFDA drug registrations** | Thai approvals | IS2 RAG |
| **ราชกิจจานุเบกษา** | Laws, announcements | IS2 RAG |
| **ClinicalTrials.gov** | Global trials | IS2 signal |

### 6.2 Mock Data (when internal GPO data unavailable)
**Principle:** Anchor to real public aggregates. Mock structure realistic but specific values synthetic.

Mock datasets:
- `mock_demand_history.csv` — monthly sales by molecule-class, 60+ months
- `mock_drug_events.csv` — event table (approvals, recalls, launches)
- `mock_regulation_docs.csv` — synthetic regulation documents

### 6.3 GPO Internal Data (if granted)
- Historical sales (≥5 yr) — replace mock for final validation
- Production volumes
- R&D pipeline

**Legal requirement:** Written IP clearance from GPO BEFORE using any internal data in commercial context

---

## 7. Tech Stack

| Layer | Choice | Rationale |
|---|---|---|
| Language | Python 3.12 | Standard ML |
| LLM | **ThaiLLM (OpenThaiGPT)** default + Claude benchmark | Sovereign AI positioning |
| Embedding | `BAAI/bge-m3` | Bilingual Thai+English SOTA |
| Vector DB | ChromaDB | Free, self-host |
| Forecasting | pytorch-forecasting, darts, statsforecast | TFT + baselines |
| Compute | Colab Pro (dev) + Vast AI (TFT training) | Budget-friendly |
| Dashboard | Streamlit | Fast MVP |

---

## 8. Timeline (High-level)

```
IS1 (Sem 1, ~16 weeks) — Forecasting
├── W1-2  Scope + scaffolding + FDA data (✅ DONE)
├── W3-4  Mock demand generator + exploratory analysis
├── W5-7  Baselines (SARIMAX, Prophet, XGBoost)
├── W8-10 TFT on Vast AI
├── W11-12 Ablation study + significance tests
├── W13-14 Dashboard + writing
└── W15-16 IS1 defense + paper submission

IS2 (Sem 2, ~16 weeks) — Intelligence
├── W1-4  Thai scrapers (TFDA, ราชกิจจา)
├── W5-7  Event extraction + Thai summary
├── W8-10 RAG evaluation (ThaiLLM vs Claude benchmark)
├── W11-12 Integration with IS1 forecaster
├── W13-14 GPO user study + dashboard polish
└── W15-16 IS2 defense + commercial pitch
```

---

## 9. Success Criteria

### IS1 Research Success
- TFT with exogenous features reduces MAPE ≥5% vs SARIMAX baseline (Diebold-Mariano p<0.05)
- Forecast MAPE <20% at 24-month horizon, <30% at 60-month
- Paper accepted at Tier 2+ Thai/SEA conference

### IS2 Research Success
- ThaiLLM achieves ≥85% of Claude performance on Thai pharmaceutical QA
- RAG retrieval: Context Precision >0.75, Faithfulness >0.90
- Citation Accuracy >0.95

### Business Success
- GPO signs LOI for pilot deployment (IS2 end)
- At least 1 non-GPO Thai pharma interested
- Unit economics validated (CAC < 3x ARPU)

---

## 10. Key Risks

| Risk | Mitigation |
|---|---|
| GPO doesn't grant internal data access | Use mock anchored to public stats + real FDA data |
| Mock data challenged at defense | Strong anchoring methodology + sensitivity analysis |
| Advisor unfamiliar with TFT | Pre-lit-review meeting, start with interpretable baselines |
| ThaiLLM service downtime | Fallback to Claude via provider abstraction |
| IP dispute w/ GPO if commercialized | Written clearance before any commercial work; train commercial model on non-GPO data only |

---

## 11. Open Questions for Advisor

1. Preferred methodology lean: time-series **forecasting** vs **NLP/IR**?
2. Target conference for IS1 paper?
3. Is co-authorship with committee possible?
4. GPO as case study: is formal partnership required or informal is OK?
5. Budget for Vast AI training (~THB 2k–5k/month during TFT phase)?

---

## 12. Decision Log

| Date | Decision | Rationale |
|---|---|---|
| 2026-04 | Chose cardiometabolic TA | Data availability + policy relevance |
| 2026-04 | ThaiLLM as default LLM | Sovereign AI positioning for gov deployment |
| 2026-04 | Molecule-class forecast unit | Match decision-making granularity, reduce noise |
| 2026-04 | Forecasting = IS1, Intelligence = IS2 | Forecasting more paper-friendly; leverage RAG work already done as exogenous feature source |
| 2026-04 | TFT as main model | Handles exogenous + categorical + long horizon; publishable novelty vs Prophet/SARIMAX |
