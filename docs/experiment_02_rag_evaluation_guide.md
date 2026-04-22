# Experiment 02: RAG Evaluation Guide

## Purpose

This document defines a practical evaluation guide for the bilingual pharmaceutical regulatory intelligence workflow. It is intended to support structured testing of retrieval quality, answer grounding, citation quality, bilingual handling, and operational robustness after the Orange Book index has been built.

The guide is designed for the current FDA Orange Book slice and can be extended later when TFDA, Royal Gazette, ClinicalTrials.gov, or other sources are added.

## Evaluation Objectives

The current RAG evaluation should answer five questions.

1. Does the system retrieve documents that are relevant to the user question?
2. Is the generated answer grounded in the retrieved context rather than invented?
3. Are citations present and traceable to the retrieved records?
4. Does the system handle English and Thai questions consistently?
5. Is the overall behavior acceptable for pharmaceutical intelligence use cases?

## Recommended Test Set Structure

Build a small manual sanity-check set first, then extend to a larger benchmark later.

Suggested phases:

- Phase 1: 10 to 15 manually reviewed questions for smoke testing
- Phase 2: 30 to 50 bilingual questions with expected evidence references
- Phase 3: 100 or more questions for a formal evaluation set

Each test item should record:

- Query language
- Question text
- Expected information type
- Expected relevant product or ingredient
- Expected source or document family when known
- Actual retrieved sources
- Actual answer
- Manual assessment notes

## Example English Prompts

These prompts are appropriate for the current FDA Orange Book slice.

1. What patents cover empagliflozin and when do they expire?
2. List SGLT2 inhibitors approved by FDA with their manufacturers.
3. Compare generic manufacturers of metformin.
4. Which statin has the latest FDA approval date?
5. What exclusivities are listed for dapagliflozin products?
6. Which applicants are associated with sitagliptin-containing products?
7. Show FDA-approved combination products that include empagliflozin.
8. What is the dosage form and route for major atorvastatin products?
9. Which ARB products appear in the Orange Book and who are their applicants?
10. What patents are associated with linagliptin combination products?

## Example Thai Prompts

These prompts test bilingual retrieval and answer generation while the underlying corpus remains primarily English.

1. สิทธิบัตรของ dapagliflozin หมดเมื่อไหร่
2. มียา SGLT2 inhibitors ตัวใดบ้างที่ได้รับอนุมัติจาก FDA และผู้ผลิตคือใคร
3. เปรียบเทียบผู้ผลิตยาสามัญของ metformin
4. statin ตัวไหนมีวันที่อนุมัติจาก FDA ล่าสุด
5. มีผลิตภัณฑ์ผสมใดบ้างที่มี empagliflozin
6. สิทธิผูกขาดทางการตลาดของผลิตภัณฑ์ที่มี linagliptin มีอะไรบ้าง
7. รูปแบบยาและวิธีใช้ของ atorvastatin ที่พบใน Orange Book คืออะไร
8. ผลิตภัณฑ์ที่มี sitagliptin มีผู้ยื่นคำขอรายใดบ้าง
9. ถามเฉพาะข้อมูลที่มีใน Orange Book เกี่ยวกับ canagliflozin
10. ยากลุ่ม ARB ใน Orange Book มีผู้ผลิตหรือผู้ยื่นคำขอรายใดบ้าง

## Stress-Test Prompts

These prompts are useful for probing edge cases and failure modes.

### No-Answer Cases

1. What does the Orange Book say about Thai hospital procurement of empagliflozin?
2. Which GPO factories manufacture dapagliflozin today?
3. What was the 2025 Thailand market share of each SGLT2 inhibitor?

Expected behavior:

- The system should explicitly say the information is not available in the current context.
- It should not invent market-share, procurement, or Thailand-specific facts that are absent from the indexed corpus.

### Ambiguous Cases

1. Tell me about empagliflozin.
2. What is the latest approval for metformin?
3. Which company owns this patent?

Expected behavior:

- The system should either answer narrowly based on retrieved context or state the ambiguity.
- It should avoid claiming unsupported ownership or interpretation beyond the retrieved data.

## Core Metrics to Record

The most important metrics for this stage are practical, evidence-oriented measures rather than only model-centric scores.

### Retrieval Metrics

- Hit Rate@k: whether at least one relevant source appears in the top-k retrieved results
- Precision@k: fraction of retrieved documents that are relevant
- Mean Reciprocal Rank: how early the first relevant document appears
- nDCG@k: ranking quality when multiple relevant documents exist

### Answer Quality Metrics

- Faithfulness: whether the answer is supported by the retrieved sources
- Completeness: whether the answer covers the main requested facts
- Correctness: whether the answer states the facts accurately
- Language Consistency: whether the answer language matches the query language appropriately

### Citation Metrics

- Citation Presence Rate: percentage of answers that include citations when factual claims are made
- Citation Accuracy: percentage of citations that actually support the cited claim
- Citation Specificity: whether citations point to the most relevant retrieved source rather than a broad or weakly related one

### Safety and Failure Metrics

- Hallucination Rate: percentage of answers containing unsupported claims
- Unsupported Specificity Rate: frequency of invented exact dates, patent numbers, manufacturers, or approvals
- Abstention Quality: whether the model properly says the answer is unavailable when context is insufficient

### Operational Metrics

- Query latency per request
- Index build time
- Retrieval-only latency versus full answer latency
- Failure rate under repeated bilingual queries

## Suggested Manual Rating Scale

For early-stage experiments, use a simple reviewer rubric.

### Retrieval Relevance

- Pass: top retrieved items clearly match the question intent
- Partial: at least one relevant item appears, but ranking is noisy
- Fail: retrieved items do not materially support the question

### Answer Grounding

- Pass: answer is fully supported by retrieved content
- Partial: answer is mostly supported but includes weak extrapolation or incomplete coverage
- Fail: answer includes unsupported or invented claims

### Citation Quality

- Pass: citations are present and support the claims they follow
- Partial: citations exist but are incomplete, overly broad, or not attached to each major claim
- Fail: citations are absent, misleading, or disconnected from the answer

## Recommended Thresholds for a Good Sanity Check

For an initial internal milestone, reasonable targets are:

- Hit Rate@5: at least 0.80
- Faithfulness: at least 0.90 on manually reviewed questions
- Citation Presence Rate: at least 0.90 for factual answers
- Citation Accuracy: at least 0.95 on manually checked cited claims
- Thai Query Handling: no critical language mismatch on the core Thai set
- Hallucination Rate: below 0.10 on the manual sanity set

These are internal targets, not publication-grade benchmarks. The thresholds should be tightened once a larger and more carefully labeled evaluation set exists.

## Evaluation Log Template

Use the following table structure when recording runs.

| Query ID | Language | Question | Top-k Sources | Answer Summary | Retrieval | Grounding | Citations | Notes |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| E01 | EN | What patents cover empagliflozin and when do they expire? | OB-... | Patent list returned | Pass | Partial | Pass | Retrieved combination products before pure ingredient products |

## Recommended Interpretation Rules

Use these interpretation rules when reviewing outputs.

1. If the answer is fluent but cites irrelevant documents, treat it as a retrieval problem first, not only an LLM problem.
2. If the retrieved documents are relevant but the answer adds unsupported facts, treat it as a grounding or prompting problem.
3. If Thai queries retrieve relevant English documents but the answer language or terminology is weak, treat it as a bilingual response-quality problem rather than a retrieval failure.
4. If the model refuses to answer when relevant documents were retrieved, treat it as an answer-generation calibration issue.
5. If the system answers confidently to out-of-scope questions, count that as a hallucination and not as successful coverage.

## Next-Step Recommendations

After the sanity-check phase, the next evaluation upgrades should be:

1. Build a 100-plus item bilingual evaluation set with expected evidence references.
2. Add side-by-side ThaiLLM versus Anthropic comparison on the same retrieval results.
3. Separate retrieval evaluation from generation evaluation so failure causes are easier to diagnose.
4. Add a small set of deliberately unanswerable questions to measure abstention quality.
5. Track latency and failure rate across repeated queries to assess operational stability.