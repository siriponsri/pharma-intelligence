# Experiment 06: RAG Evaluation On The Orange Book Slice

**Date:** 2026-04-22  
**Phase:** 3  
**Engine:** RAG  
**Status:** Complete for the FDA Orange Book slice

## Objective

Evaluate the current bilingual Retrieval-Augmented Generation workflow built on the FDA Orange Book slice, focusing on retrieval quality, grounding, citation behavior, bilingual response quality, and abstention on out-of-scope questions.

## Data And Run Context

The reported results are based on the saved notebook run in `notebooks/results/01_notebook_result`.

- Corpus source: FDA Orange Book cardiometabolic slice
- Total monographs indexed: 5479
- Unique ingredients: 150
- Unique applicants: 398
- Therapeutic area mix: 3632 hypertension, 921 diabetes, 857 dyslipidemia, 69 combination products
- Embedding/index environment: Google Colab T4 GPU
- LLM provider: `thaillm`
- Model: `openthaigpt-thaillm-8b-instruct-v7.2`
- Retrieval depth: top-5

## Operational Results

The notebook completed successfully end-to-end.

- Orange Book monographs built: 5479
- Index build time: 224.3 seconds
- Final Chroma collection size: 5479
- Verified zip export size: 44.7 MB

This confirms that the notebook pipeline is operational and reproducible on Colab. The remaining issues are concentrated in model quality rather than ingestion or indexing stability.

## Evaluation Set

The notebook evaluated a 12-query bilingual sanity set.

- Total queries: 12
- Core factual queries: 10
- No-answer stress tests: 2
- English queries: 6
- Thai queries: 6

The tested prompts covered:

- empagliflozin patents
- SGLT2 inhibitor listing
- metformin generic manufacturers
- dapagliflozin exclusivities
- empagliflozin combination products
- atorvastatin dosage-form questions
- out-of-scope Thailand procurement and market-share questions

## Queries Used

| Query ID | Language | Category | Expected focus | Query |
| --- | --- | --- | --- | --- |
| EN01 | EN | core | empagliflozin | What patents cover empagliflozin and when do they expire? |
| EN02 | EN | core | SGLT2 inhibitors | List SGLT2 inhibitors approved by FDA with their manufacturers. |
| EN03 | EN | core | metformin | Compare generic manufacturers of metformin. |
| EN04 | EN | core | dapagliflozin | What exclusivities are listed for dapagliflozin products? |
| EN05 | EN | core | empagliflozin | Show FDA-approved combination products that include empagliflozin. |
| TH01 | TH | core | dapagliflozin | สิทธิบัตรของ dapagliflozin หมดเมื่อไหร่ |
| TH02 | TH | core | SGLT2 inhibitors | มียา SGLT2 inhibitors ตัวใดบ้างที่ได้รับอนุมัติจาก FDA และผู้ผลิตคือใคร |
| TH03 | TH | core | metformin | เปรียบเทียบผู้ผลิตยาสามัญของ metformin |
| TH04 | TH | core | empagliflozin | มีผลิตภัณฑ์ผสมใดบ้างที่มี empagliflozin |
| TH05 | TH | core | atorvastatin | รูปแบบยาและวิธีใช้ของ atorvastatin ที่พบใน Orange Book คืออะไร |
| ST01 | EN | no-answer | out-of-scope Thailand procurement | What does the Orange Book say about Thai hospital procurement of empagliflozin? |
| ST02 | TH | no-answer | out-of-scope Thailand market share | ส่วนแบ่งตลาดในประเทศไทยปี 2025 ของยา SGLT2 inhibitors แต่ละตัวคืออะไร |

## Metrics Used

### Automatic metrics used in the notebook

| Metric | Definition | How it was computed |
| --- | --- | --- |
| Mean latency | Average end-to-end answer time per query | Mean of `latency_seconds` across all evaluated queries |
| P95 latency | Tail latency for slower queries | 95th percentile of `latency_seconds` |
| Citation presence rate | Share of answers containing at least one citation | Mean of boolean `citation_present` |
| Citation supported-by-retrieval rate | Share of answers whose extracted citations are all contained in the retrieved `doc_id` set | Mean of boolean `citations_supported_by_retrieval` |
| Heuristic language match rate | Share of answers whose detected answer language matches the query language | Mean of boolean `language_match_heuristic` |
| Abstention rate | Share of answers that appear to refuse or acknowledge missing context | Mean of boolean `looks_like_abstention` |
| Mean top retrieval score | Average similarity score of the top-ranked retrieved chunk | Mean of `top_score` |

### Manual metrics intended for detailed review

| Manual field | Purpose | Recommended interpretation |
| --- | --- | --- |
| `manual_retrieval_relevance` | Judge whether the retrieved top-k sources actually match the user question | `Pass`, `Partial`, or `Fail` |
| `manual_answer_grounding` | Judge whether the answer is supported by the retrieved text without unsupported additions | `Pass`, `Partial`, or `Fail` |
| `manual_citation_quality` | Judge whether citations are present, specific, and traceable to the right claims | `Pass`, `Partial`, or `Fail` |
| `manual_notes` | Capture observed errors, ambiguity, hallucinations, or useful comments | Free-text notes |

## Measured Results

### Overall metrics

| Metric | Result |
| --- | ---: |
| Mean latency | 6.135 s |
| P95 latency | 10.879 s |
| Citation presence rate | 0.750 |
| Citation supported-by-retrieval rate | 0.333 |
| Heuristic language match rate | 0.500 |
| Abstention rate | 0.333 |
| Mean top retrieval score | 0.549 |

### Core-query metrics

| Metric | Result |
| --- | ---: |
| Core queries | 10 |
| Citation presence rate | 0.800 |
| Citation supported-by-retrieval rate | 0.400 |
| Heuristic language match rate | 0.500 |
| Abstention rate | 0.200 |
| Mean top retrieval score | 0.574 |

### By query language

| Query language | Queries | Mean latency | Language match | Citation presence | Citation supported | Abstention |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| English | 6 | 5.824 s | 0.000 | 0.833 | 0.333 | 0.333 |
| Thai | 6 | 6.446 s | 1.000 | 0.667 | 0.333 | 0.333 |

## Interpretation

The current Orange Book slice is operational but not yet robust enough to count as the final Thai regulatory RAG benchmark. It is strong enough to support indexed retrieval and initial bilingual QA, but its evaluation results show three visible weaknesses: weak English-language matching, incomplete citation discipline, and ingredient-ranking errors on broader class-level questions.

This means the experiment is still useful and should be preserved, but it should be interpreted as an early-phase benchmark on the FDA slice rather than the final Phase 3 evaluation target. The next RAG work should improve retrieval ranking and citation formatting, then rerun the same evaluation structure on the Thai-source corpus.

## Artifacts

- `notebooks/results/01_notebook_result/data/processed/experiment_02_eval_results.csv`
- `notebooks/results/01_notebook_result/data/processed/experiment_02_eval_results.json`
- `notebooks/results/01_notebook_result/data/processed/orange_book_cardiometabolic.parquet`

