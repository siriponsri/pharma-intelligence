# Experiment Template

Use this template for every new experiment report under `docs/`. The structure is intentionally repetitive so later thesis writing, slide generation, and result comparison are easy.

```markdown
# Experiment XX: <Title>

**Date:** YYYY-MM-DD  
**Phase:** <1-6>  
**Engine:** <Forecasting | RAG | Shared Data | Integration>  
**Motivation:** <Why this experiment exists>

## Objective

<What question is being answered>

## Hypothesis

- <Hypothesis 1>
- <Hypothesis 2>

## Inputs

- Data source(s):
- Code path(s):
- Config / seed:
- Environment:

## Method

### Design

<Experimental design, train/test split, benchmark setup, retrieval setup, etc.>

### Procedure

1. <Step>
2. <Step>
3. <Step>

### Evaluation

- Primary metrics:
- Secondary metrics:
- Manual review method:

## Results

| Metric | Value |
| --- | ---: |
| <Metric> | <Value> |

## Interpretation

<Explain what the results mean and whether they support the hypothesis>

## Root Cause / Failure Analysis

<Explain why the result happened, especially for negative outcomes>

## Acceptance Check

- [ ] Criterion 1
- [ ] Criterion 2

## Artifacts

- Data:
- Result files:
- Notebook / script:
- Commit:

## Slide-Ready Summary

- Headline:
- Key number:
- Why it matters:
- Next decision:
```
