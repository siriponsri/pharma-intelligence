# Experiment 04: Real Public Data Integration

**Date:** 2026-04-22  
**Status:** Partial implementation  
**Phase:** 2  
**Engine:** Shared Data

## Objective

Wire the first real Phase 2 public-source ingestion path end to end, starting with HDC and NHSO, so the project can normalize real exported files into stable parquet artifacts and quality reports.

## What Was Implemented

- HDC ingestion now auto-discovers the newest raw export under `data/raw/hdc/` when `--input` is omitted.
- NHSO ingestion now auto-discovers the newest raw export under `data/raw/nhso/` when `--input` is omitted.
- Both sources accept real raw exports in `csv`, `tsv`, `parquet`, `json`, `jsonl`, `xlsx`, `xls`, and `zip` form.
- Both sources normalize common English and Thai column aliases into the project schema.
- Both sources emit a matching quality-report JSON into `data/interim/`.

## Constraint Observed During This Run

Direct scripted access to the HDC and NHSO websites could not be verified from the current environment. The public pages either failed extraction or reset the network connection during direct HTTP inspection. Because of that, this implementation uses a manual-export ingestion contract rather than claiming a stable unattended downloader that has not been proven.

That is the correct boundary for now: the pipeline is real and reproducible on real exported data, but the portal download step still needs site-specific access validation later.

## Source Contracts

### HDC

- Raw location: `data/raw/hdc/`
- Canonical output: `data/processed/hdc_ncd_prevalence.parquet`
- Quality report: `data/interim/hdc_ncd_prevalence_quality.json`
- Core normalized fields: `year`, `province`, `age_group`, `disease_code`, `gender`, `prevalence_per_1000`

Supported alias examples:

- `ปี`, `ปีงบประมาณ` -> `year`
- `จังหวัด` -> `province`
- `กลุ่มอายุ` -> `age_group`
- `รหัสโรค`, `icd10` -> `disease_code`
- `เพศ` -> `gender`
- `อัตราป่วยต่อพันประชากร` -> `prevalence_per_1000`

### NHSO

- Raw location: `data/raw/nhso/`
- Canonical output: `data/processed/nhso_utilization.parquet`
- Quality report: `data/interim/nhso_utilization_quality.json`
- Core normalized fields: `service_month`, `scheme`, `drug_class`, `claims_count`, `units_dispensed`, `reimbursement_thb`

Supported alias examples:

- `เดือนบริการ`, `ปีเดือน` -> `service_month`
- `สิทธิการรักษา`, `กองทุน` -> `scheme`
- `กลุ่มยา`, `หมวดยา` -> `drug_class`
- `จำนวนรายการ`, `จำนวนเคลม` -> `claims_count`
- `จำนวนหน่วย` -> `units_dispensed`
- `ยอดชดเชย`, `มูลค่าชดเชย(บาท)` -> `reimbursement_thb`

## Evaluation

This slice was validated with focused regression tests covering:

- Thai-column alias normalization for HDC
- Thai-column alias normalization for NHSO
- Auto-discovery of the newest raw export under `data/raw/<source>/`
- Generation of the matching quality-report JSON

## Remaining Work

- Verify whether HDC and NHSO expose stable machine-download endpoints or require authentication/session handling.
- Add field-level sanity checks against external summary tables once real production exports are available.
- Extend the same contract to e-GP and other Phase 2 sources.
