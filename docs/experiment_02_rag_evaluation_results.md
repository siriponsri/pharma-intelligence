# Experiment 02: RAG Evaluation Results

## Objective

This experiment evaluated the current bilingual Retrieval-Augmented Generation workflow built on the FDA Orange Book slice. The goal was to verify that the Colab notebook can build the index successfully and to measure early retrieval, grounding, citation, bilingual-response, and abstention behavior.

## Data and Run Context

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

This confirms that the Experiment 02 notebook pipeline is operational and reproducible on Colab. The remaining issues are concentrated in model quality rather than in the ingestion or indexing pipeline.

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

The following queries were executed in the notebook evaluation cell.

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

The first 10 queries were designed as core factual checks. The last 2 were stress tests designed to measure abstention quality on out-of-scope questions.

## Metrics Used

This experiment used a mix of automatic metrics produced directly by the notebook and manual metrics intended for later reviewer scoring.

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
| Citation count | Number of inline citation tokens found in an answer | Count of regex matches on `[...]` |
| Input tokens | Provider-reported prompt token count when available | Read from `result.input_tokens` |
| Output tokens | Provider-reported generation token count when available | Read from `result.output_tokens` |

### Heuristics used by the notebook

The notebook used simple heuristics rather than formal benchmark labels.

- Response language detection: the evaluation cell classified an answer as Thai when Thai Unicode characters were sufficiently dominant; otherwise it classified the answer as English.
- Citation extraction: citations were extracted with a bracket pattern matching inline references such as `[OB-212614-001]`.
- Abstention detection: answers were marked as abstentions when they contained phrases such as `not available`, `not found in the context`, `ไม่พบ`, or `ไม่มีข้อมูล`.
- Citation support check: an answer passed the automatic citation support check only when every extracted citation existed in that query's retrieved `doc_id` list.

### Manual metrics intended for detailed review

The notebook also wrote blank reviewer columns into the CSV so the run can be scored manually.

| Manual field | Purpose | Recommended interpretation |
| --- | --- | --- |
| `manual_retrieval_relevance` | Judge whether the retrieved top-k sources actually match the user question | `Pass`, `Partial`, or `Fail` |
| `manual_answer_grounding` | Judge whether the answer is supported by the retrieved text without unsupported additions | `Pass`, `Partial`, or `Fail` |
| `manual_citation_quality` | Judge whether citations are present, specific, and traceable to the right claims | `Pass`, `Partial`, or `Fail` |
| `manual_notes` | Capture observed errors, ambiguity, hallucinations, or useful comments | Free-text notes |

## How To Evaluate In Detail

The following process should be used when reviewing the Experiment 02 outputs in detail.

### Step 1. Open the saved artifacts

Use these files as the source of truth.

- `notebooks/results/01_notebook_result/data/processed/experiment_02_eval_results.csv`
- `notebooks/results/01_notebook_result/data/processed/experiment_02_eval_results.json`
- `notebooks/results/01_notebook_result/data/processed/orange_book_cardiometabolic.parquet`

### Step 2. Review retrieval relevance

For each query:

1. Read `retrieved_doc_ids`, `retrieved_ingredients`, and `retrieved_scores`.
2. Check whether the top-k retrieved documents are relevant to the requested ingredient, product family, exclusivity topic, or business question.
3. Score `manual_retrieval_relevance`:

- `Pass`: top retrieved items clearly support the question intent.
- `Partial`: at least one relevant document is present, but ranking is noisy or mixed with irrelevant results.
- `Fail`: the retrieved items do not materially support the question.

### Step 3. Review answer grounding

For each query:

1. Read the generated `answer`.
2. Compare the factual claims in the answer against the retrieved documents only.
3. Watch for unsupported dates, patent numbers, manufacturers, market facts, or extra world knowledge not present in the retrieved evidence.
4. Score `manual_answer_grounding`:

- `Pass`: the answer is fully supported by the retrieved context.
- `Partial`: the answer is mostly supported but includes extrapolation, weak phrasing, or incompleteness.
- `Fail`: the answer includes invented or unsupported claims.

### Step 4. Review citation quality

For each query:

1. Check whether the answer includes citations after factual claims.
2. Verify that the cited IDs are actual retrieved `doc_id` values.
3. Verify that each citation supports the specific sentence or bullet where it appears.
4. Score `manual_citation_quality`:

- `Pass`: citations are present, accurate, and specific.
- `Partial`: citations exist but are overly broad, incomplete, or attached loosely.
- `Fail`: citations are absent, invalid, or do not support the associated claim.

### Step 5. Review bilingual behavior

For each query:

1. Compare `language` with `response_language`.
2. Check whether English questions receive English answers and Thai questions receive Thai answers.
3. Record mismatches or awkward mixed-language behavior in `manual_notes`.

### Step 6. Review abstention quality

For stress-test queries and any low-confidence response:

1. Check whether the system clearly states that the answer is unavailable in the current Orange Book context.
2. Verify that the model does not continue with unsupported external facts after abstaining.
3. Record whether the refusal is clean, partial, or unsafe in `manual_notes`.

### Step 7. Summarize final experiment status

After all rows are scored:

1. Count the number of `Pass`, `Partial`, and `Fail` labels for retrieval, grounding, and citation quality.
2. Separate results by English versus Thai queries and by core versus no-answer queries.
3. Report the main failure patterns, such as wrong answer language, irrelevant retrieval, unsupported external knowledge, weak abstention, or placeholder citations.
4. Use both the notebook's automatic metrics and the manual labels when writing the final narrative.

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

## Real Query Outcomes

### Better-performing cases

**Metformin manufacturer comparison (`EN03`, `TH03`)**

- Retrieval was clean and focused on `METFORMIN HYDROCHLORIDE` documents.
- Citations were present.
- The cited document IDs came from the retrieved set.
- The answer content was materially aligned with the Orange Book records.

**Empagliflozin combination products (`EN05`, `TH04`)**

- Retrieval mostly returned empagliflozin and empagliflozin-metformin combination products.
- Citation support was stronger than the run average.
- This indicates that the current retrieval stack works better on explicit ingredient queries than on broader therapeutic-class prompts.

### Partial cases

**Empagliflozin patent coverage (`EN01`)**

- Retrieval was directionally relevant and focused on empagliflozin combination-product records.
- The answer returned a large patent list.
- However, the answer language was wrong for the English prompt, and citation attachment was too broad.

**Atorvastatin dosage form and route (`TH05`)**

- One atorvastatin record was retrieved, but several simvastatin records ranked above it.
- The answer was still partly usable, but this reflects ranking noise and weak ingredient precision.

### Failure cases

**SGLT2 inhibitor listing (`EN02`, `TH02`)**

- Retrieval failed materially, returning glyburide and spironolactone instead of SGLT2 products.
- The English answer then mixed abstention with unsupported external knowledge.
- This is the clearest hallucination pattern in the saved run.

**Dapagliflozin exclusivities (`EN04`)**

- Retrieval was ingredient-relevant.
- The answer used placeholder citations such as `[source1, source2]` instead of actual `doc_id` references.
- That makes the answer non-traceable even if the underlying content is directionally plausible.

**Out-of-scope stress tests (`ST01`, `ST02`)**

- Both stress tests should have produced strict abstentions.
- The system abstained inconsistently and still attached weak or irrelevant retrieval context.
- This indicates that current refusal behavior is not fully reliable.

## Main Findings

### 1. Infrastructure passed

The Colab workflow successfully built the corpus, generated the vector index, wrote the evaluation artifacts, and exported a verified Chroma archive. Experiment 02 is therefore no longer blocked by notebook execution or data-pipeline stability.

### 2. English response behavior failed

All English queries were answered in Thai according to the saved run output. This is a direct failure against the intended bilingual-response behavior.

### 3. Citation quality remains weak

Citation presence was acceptable at 0.75 overall, but only 0.333 of answers had citations fully supported by the retrieved document set. The run showed over-citation, placeholder citation formats, and citations attached to weakly grounded answers.

### 4. Retrieval quality is uneven

The system performs better when the prompt names a specific ingredient, such as metformin or empagliflozin. It performs poorly for class-level questions such as `SGLT2 inhibitors` and some formulation-oriented questions.

### 5. Generation control still needs work

Several saved answers exposed `<think>` traces. This should not appear in user-facing output and indicates a response-formatting or provider-control problem.

### 6. Abstention is not yet safe enough

The model sometimes acknowledges missing context but still continues with unsupported external facts. This weakens trust and should be treated as a blocking quality issue.

## Conclusion

Experiment 02 should be considered a successful technical run but only a partial quality pass.

- Notebook execution: pass
- Index construction: pass
- Export workflow: pass
- Ingredient-focused retrieval: partial pass
- English/Thai response control: fail
- Citation grounding: fail
- Abstention discipline: fail
- Class-level retrieval: fail

The saved results are strong enough to demonstrate that the RAG pipeline works operationally, but not yet strong enough to claim robust bilingual answer quality or production-ready grounding behavior.

## Recommended Next Actions

1. Remove or suppress `<think>` traces before presenting answers to users.
2. Enforce response-language matching for English prompts.
3. Restrict final citations to retrieved `doc_id` values only.
4. Add a guardrail that blocks unsupported external facts after an abstention.
5. Improve retrieval for therapeutic-class prompts using metadata-aware reranking or ingredient normalization.
6. Complete the manual review columns in the saved CSV for formal scoring of retrieval relevance, grounding, and hallucination.

## Source Artifacts

The following files were used as the source of truth for this summary.

- `notebooks/results/01_notebook_result/data/processed/orange_book_cardiometabolic.parquet`
- `notebooks/results/01_notebook_result/data/processed/experiment_02_eval_results.csv`
- `notebooks/results/01_notebook_result/data/processed/experiment_02_eval_results.json`
- `notebooks/results/01_notebook_result/data/processed/experiment_02_eval_summary.md`