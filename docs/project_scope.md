# Project Scope: Pharmaceutical Intelligence Platform for GPO

**Author:** Siripon Srihangpiboon  
**Program:** M.Sc. AI for Business, KMITL School of Information Technology  
**Academic Period:** 2025-2026  
**Document Version:** 2.0  
**Status:** Working scope document for academic planning, technical implementation, and advisor alignment

## 1. Executive Summary

This project proposes a pharmaceutical intelligence platform designed to support the strategic planning, regulatory monitoring, and product development activities of the Government Pharmaceutical Organization (GPO) in Thailand. The platform is organized into two integrated workstreams:

- IS1: long-horizon demand forecasting for cardiometabolic molecule classes
- IS2: bilingual pharmaceutical regulatory intelligence using retrieval-augmented generation with ThaiLLM

The central research thesis is that pharmaceutical forecasting can be materially improved when structured external signals such as patent expiry, regulatory events, epidemiological trends, and competitor activity are incorporated into the modeling pipeline. In this architecture, the regulatory intelligence engine is not only an end-user question-answering system but also a feature-generation layer for the forecasting engine.

The project is intended to serve both academic and applied objectives. Academically, it supports publishable research in forecasting, bilingual regulatory intelligence, and the use of sovereign Thai language models in a pharmaceutical context. Operationally, it provides a foundation for a deployable system that can assist GPO and similar organizations in portfolio planning, opportunity identification, and monitoring of the competitive and regulatory environment.

## 2. Problem Statement

Pharmaceutical R&D and strategic planning functions operate under long product-development cycles, uncertain future demand, and rapidly changing regulatory conditions. In the GPO context, two operational gaps are especially significant.

First, product development cycles are long enough that the market conditions assumed at project initiation may no longer hold by the time a product is launched. This creates the risk of allocating capital and scientific resources to products that are no longer aligned with real market demand.

Second, pharmaceutical intelligence is typically dispersed across multiple sources, including approval databases, patent registers, regulatory notices, procurement signals, and clinical pipeline information. Without a structured monitoring system, organizations face delays in identifying competitor actions, regulatory changes, and emerging generic opportunities.

The business consequences include misallocated R&D investment, slower response to market opportunities, reduced situational awareness regarding patents and exclusivities, and limited ability to defend portfolio decisions with data.

## 3. Project Objectives

The project has four primary objectives.

1. Develop a forecasting framework that estimates medium- to long-horizon demand for cardiometabolic molecule classes relevant to the Thai market.
2. Build a bilingual regulatory intelligence system capable of answering pharmaceutical questions grounded in structured document sources.
3. Convert regulatory and competitive intelligence into structured exogenous signals that can be incorporated into forecasting workflows.
4. Produce a technically defensible platform suitable for academic evaluation and future extension toward operational deployment.

## 4. Stakeholders and Target Users

The project is primarily designed for decision-support rather than consumer use. The intended stakeholders are listed below.

| Stakeholder Group | Primary Need | Expected Output |
| --- | --- | --- |
| R&D and Strategic Planning | Decide which molecule classes or product areas should receive development investment | Long-horizon demand outlook, opportunity prioritization, pipeline recommendations |
| Regulatory Affairs | Monitor changes that affect market entry, approvals, labeling, and exclusivity | Searchable regulatory intelligence, grounded summaries, alerts |
| Marketing and Business Strategy | Understand competitor activity and therapeutic-area opportunity | Competitive landscape summaries, manufacturer comparisons, market timing signals |
| Executive Leadership | Assess portfolio direction and strategic risk at a high level | Executive summaries, evidence-backed scenario views |

The primary minimum viable product user is the R&D and strategic planning team, as this group most directly benefits from integrating forecast outputs with patent and regulatory intelligence.

## 5. Scope Definition

### 5.1 Therapeutic Scope

The project scope is limited to cardiometabolic therapeutics. This includes:

- Diabetes mellitus
- Hypertension
- Dyslipidemia
- Relevant combination products crossing these categories

This scope is intentionally constrained. It is broad enough to provide a meaningful portfolio view while remaining feasible for data ingestion, model evaluation, and domain interpretation within the project timeline.

### 5.2 Forecasting Unit of Analysis

The forecasting unit is the molecule-class level rather than the SKU level. Representative examples include:

- SGLT2 inhibitors
- DPP-4 inhibitors
- ARBs
- Statins

This choice reflects the actual decision level at which strategic pharmaceutical planning is often performed and avoids the instability and sparsity associated with SKU-level demand modeling.

### 5.3 Geographic Scope

The primary market of interest is Thailand. However, several non-Thai data sources are included as leading indicators or reference signals, especially where Thai public data is incomplete. The geographic treatment is therefore:

- Primary market: Thailand
- Reference markets and evidence sources: United States, Europe, and selected global public datasets

### 5.4 Time Horizon

The project distinguishes between methodological validation and long-horizon strategic application.

- IS1 minimum viable validation horizon: 12 to 24 months
- IS1 strategic target horizon: 36 to 60 months

The shorter horizon is used to validate methods and benchmark baselines, while the longer horizon corresponds to the actual business need for early R&D portfolio planning.

## 6. System Concept and Architecture

The platform is structured around two integrated engines.

### 6.1 Engine A: Forecasting

The forecasting engine estimates future demand trajectories for cardiometabolic molecule classes. It is intended to support strategic decisions such as whether a therapeutic area should be prioritized, expanded, or deprioritized.

Representative model families include:

- SARIMAX baselines
- Prophet
- XGBoost with engineered exogenous features
- Temporal Fusion Transformer as a primary advanced model candidate

Representative forecasting features include:

- Historical demand trends
- Epidemiological prevalence
- Budget and utilization proxies
- Patent expiry signals
- Regulatory events
- Competitor launch indicators

### 6.2 Engine B: Regulatory Intelligence

The intelligence engine ingests pharmaceutical regulatory sources, builds searchable structured artifacts, and supports grounded bilingual question answering. It is intended both as an end-user capability and as a feature extraction layer for the forecasting workstream.

Representative intelligence functions include:

- Data ingestion and parsing
- Monograph generation and document normalization
- Embedding and vector indexing
- Retrieval-augmented generation in Thai and English
- Event extraction and summarization for downstream analytics

### 6.3 Integration Logic

The project is based on the following methodological division of labor:

- Statistical and machine-learning models are used for numerical forecasting.
- LLMs are used for language-heavy tasks such as retrieval, summarization, classification, and event extraction.

The key integration hypothesis is that outputs from the intelligence engine can be transformed into structured exogenous features that improve the forecasting engine.

## 7. Workstream Structure

### 7.1 IS1: Long-Horizon Demand Forecasting

**Working Title:** Exogenous Regulatory and Patent Signals for Long-Horizon Pharmaceutical Demand Forecasting: A Case Study on Thai Cardiometabolic Generics

#### Primary Deliverables

- Mock demand dataset anchored to public-sector evidence
- Baseline forecasting models
- Comparative evaluation of endogenous-only and exogenous-feature models
- Experimental record suitable for academic reporting
- Draft conference or journal submission

#### Research Question

Do external signals such as patent expiry, regulatory changes, and epidemiological projections significantly improve long-horizon pharmaceutical demand forecasting relative to endogenous-only baselines?

#### Evaluation Framework

- Metrics: MAPE, sMAPE, MASE, and related forecast-error measures
- Validation design: rolling-origin or comparable backtesting strategy
- Statistical comparison: Diebold-Mariano testing where appropriate

### 7.2 IS2: Bilingual Regulatory Intelligence

**Working Title:** Sovereign Thai LLM for Bilingual Pharmaceutical Regulatory Intelligence: Monitoring, Extraction, and Integration with Forecasting Systems

#### Primary Deliverables

- Ingestion pipelines for regulatory and reference sources
- Bilingual RAG system with grounded answers and citations
- Event extraction and structured intelligence outputs
- Benchmarking of ThaiLLM against an external frontier model
- Integration pathway into IS1 exogenous features

#### Research Question

Can a sovereign Thai LLM deliver sufficiently reliable bilingual pharmaceutical question answering and structured intelligence extraction for regulatory use cases, and how does its quality-cost trade-off compare with an external benchmark model?

## 8. Data Strategy

### 8.1 Public Data Sources

The project prioritizes public or publicly accessible data sources to reduce dependency on proprietary datasets during early phases.

| Source | Intended Role |
| --- | --- |
| FDA Orange Book | Patents, approvals, product and exclusivity intelligence |
| Thai National List of Essential Medicines | Policy and reimbursement relevance |
| HDC and comparable public health sources | Prevalence and disease-burden anchors |
| Government procurement data | Demand validation and public market signals |
| TFDA registrations | Thai regulatory events and approvals |
| Royal Gazette publications | Legal and regulatory announcements |
| ClinicalTrials.gov and related databases | Early pipeline and development signals |

### 8.2 Mock Data Strategy

Where internal GPO data is unavailable, the project uses synthetic but structured datasets anchored to real-world public statistics. The goal is not to fabricate precise commercial truth, but to create a defensible experimental environment in which model design, feature engineering, and evaluation workflows can be tested.

Mock data will be considered acceptable only when:

- The generation logic is documented
- Key assumptions are tied to public signals where possible
- Sensitivity analysis is possible
- The limitations of synthetic data are explicitly stated in reporting

### 8.3 Internal Data Contingency

If internal GPO data becomes available, it should be used only under explicit permission and documented governance. Any commercial or publication use of such data requires formal clearance consistent with institutional and partner constraints.

## 9. Technical Stack

The current project stack reflects a balance between research flexibility and implementation speed.

| Layer | Current Choice | Rationale |
| --- | --- | --- |
| Programming language | Python 3.12 | Mature scientific and NLP ecosystem |
| LLM provider | ThaiLLM by default, Anthropic optional | Sovereign deployment alignment with optional benchmark comparison |
| Embeddings | BAAI/bge-m3 | Strong multilingual retrieval performance |
| Vector store | ChromaDB | Lightweight local persistence and experimentation |
| Forecasting libraries | statsmodels, scikit-learn, forecasting extensions | Baselines and future advanced modeling support |
| Notebook acceleration | Colab GPU | Practical solution for large embedding workloads |
| Application layer | Streamlit, planned | Suitable for internal demonstration and prototyping |

## 10. Methodological Principles

The project adopts the following principles.

1. Use interpretable baselines before advanced models.
2. Keep the distinction clear between forecasting tasks and language tasks.
3. Evaluate retrieval quality and answer faithfulness separately from user-facing fluency.
4. Treat public regulatory sources as evidence, not merely text to be summarized.
5. Prefer traceable, citation-backed outputs whenever claims are generated for end users.

## 11. Success Criteria

### 11.1 Academic Success

- A technically coherent and defensible forecasting methodology
- A functioning bilingual RAG system with grounded citations
- Clear evidence regarding whether exogenous intelligence improves forecast performance
- At least one submission-ready research artifact

### 11.2 Technical Success

- Reproducible ingestion and indexing pipeline
- Stable local and Colab-based execution paths
- Verifiable model and retrieval evaluation outputs
- Clear failure reporting and documented experimental runs

### 11.3 Practical Success

- Useful portfolio-level insights for strategic planning
- Search and retrieval that reduces time spent on regulatory lookup
- A foundation that can be extended to Thai regulatory sources and stakeholder dashboards

## 12. Risks and Constraints

| Risk | Description | Mitigation |
| --- | --- | --- |
| Limited access to proprietary demand data | Final validation may be constrained if internal GPO data is unavailable | Use public anchors and clearly documented mock data methodology |
| Data-source schema change | Regulatory source formats may change unexpectedly | Implement defensive parsing, schema normalization, and validation checks |
| Model overfitting on synthetic data | Synthetic structure may not represent future real-world behavior | Use conservative claims, sensitivity analysis, and later real-data validation where available |
| LLM service instability or limits | Provider rate limits or downtime can interrupt evaluation | Support provider abstraction and controlled retry policy |
| Scope expansion risk | Too many data sources or objectives may reduce research quality | Keep cardiometabolic and two-engine scope locked during core phases |

## 13. Timeline

### Phase 1: Foundation and Validation

- Repository scaffolding and environment setup
- FDA Orange Book ingestion
- Mock demand generation
- Baseline forecasting validation

### Phase 2: Forecasting Expansion

- Additional forecasting baselines
- Exogenous feature engineering
- More rigorous backtesting and comparison
- Preparation of forecasting-focused academic output

### Phase 3: Intelligence Expansion

- Thai regulatory source ingestion
- Structured event extraction
- RAG evaluation and provider benchmarking
- Integration of intelligence outputs into forecasting experiments

### Phase 4: Integration and Demonstration

- Dashboard or reporting interface
- Stakeholder-oriented summaries
- Consolidated documentation and academic submission outputs

## 14. Open Questions for Advisor Review

The following questions remain important for advisor alignment.

1. Should the primary research contribution emphasize forecasting methodology, intelligence methodology, or the integration between the two?
2. Which publication venue should guide methodological depth and evaluation rigor?
3. What level of external stakeholder involvement is appropriate during the research timeline?
4. Under what conditions can internal or partner data be used in research outputs?
5. How should the project balance academic rigor against prototype delivery speed?

## 15. Decision Log

| Date | Decision | Rationale |
| --- | --- | --- |
| 2026-04 | Cardiometabolic therapeutics selected as the initial scope | High policy relevance, manageable scope, and strong public-data availability |
| 2026-04 | Molecule-class forecasting chosen over SKU-level forecasting | Better alignment with strategic planning decisions and lower noise |
| 2026-04 | ThaiLLM selected as the default LLM provider | Supports sovereign AI positioning and government-aligned deployment use cases |
| 2026-04 | Two-engine architecture adopted | Keeps forecasting and language-intelligence concerns methodologically separate while enabling integration |
| 2026-04 | Colab GPU path added for indexing | Makes large multilingual embedding workflows practical during development |

## 16. Scope Boundary Statement

The project does not currently aim to deliver the following within the core scope:

- A production-hardened enterprise deployment
- Full Thai regulatory coverage across all product categories
- SKU-level commercial forecasting at launch
- Clinical decision support or medical advice functionality
- Autonomous decision-making without human review

These may become future extensions, but they are intentionally excluded from the current scope to preserve methodological clarity and delivery feasibility.