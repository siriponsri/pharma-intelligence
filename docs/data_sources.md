# Data Sources

This document tracks the real and synthetic data sources referenced in the master plan. It is intended to support Phase 2 data integration, evaluation traceability, and later reporting.

## Source Inventory

| Source | Type | Phase | Current Status | Intended Use | Key Fields / Signals | Update Frequency | Licensing / Access |
| --- | --- | --- | --- | --- | --- | --- | --- |
| FDA Orange Book | Public regulatory | 1-3 | Implemented | RAG grounding, patent / exclusivity evidence | ingredient, applicant, approval date, exclusivities, patents | Periodic download | Public |
| Thailand HDC | Public epidemiology | 2 | Planned | Forecasting anchors and validation | prevalence, incidence, diagnosis counts | Annual / periodic | Public |
| NHSO open data | Public claims / utilization | 2 | Planned | Demand anchor and service utilization signals | utilization, reimbursement, case volume | Periodic | Public |
| Thai e-GP procurement | Public procurement | 2 | Planned | Demand validation and government purchasing signals | tender, price, quantity, hospital buyer | Periodic | Public |
| TFDA registrations | Public regulatory | 2-3 | Planned | Thai regulatory RAG and launch monitoring | registration, holder, dosage form, approval date | Periodic | Public |
| Royal Gazette | Public legal / regulatory | 2-3 | Planned | Regulatory event extraction | announcement, publication date, policy type | Periodic | Public |
| NLEM updates | Public policy | 2-3 | Planned | Formulary and policy change signals | medicine, status, update date | Irregular | Public |
| ClinicalTrials.gov | Public clinical | 2-3 | Planned | Pipeline / competitor event extraction | phase, sponsor, indication, status | Periodic | Public |
| PubMed | Public literature | 2-3 | Planned | Evidence retrieval and context enrichment | title, abstract, keywords | Continuous | Public |
| GPO internal sales | Internal | 6 | Planned | Pilot production forecasting | sales, volume, date, channel | Internal cadence | NDA required |
| GPO pipeline status | Internal | 6 | Planned | Integrated planning support | project stage, target product, timing | Internal cadence | NDA required |
| Mock demand panel | Synthetic | 1 | Implemented | Methodology validation only | units, channel, prevalence anchors, shocks | Generated as needed | Internal synthetic |

## Usage Rules

- Label synthetic sources clearly in every experiment report.
- Do not mix internal GPO data into public artifacts without approval.
- When a source is first integrated, create or update the matching experiment report in `docs/`.
- Record sanity checks and known limitations before using any source in a benchmark.
