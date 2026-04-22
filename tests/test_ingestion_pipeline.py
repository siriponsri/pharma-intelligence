"""Tests for the unified ingestion scaffold."""

from __future__ import annotations

import json

import polars as pl

from pharma_intel.common import settings
from pharma_intel.ingestion.hdc_scraper import build_dataset as build_hdc_dataset, run as run_hdc
from pharma_intel.ingestion.nhso_scraper import build_dataset as build_nhso_dataset, run as run_nhso
from pharma_intel.ingestion.pipeline import list_pipeline_sources, run_ingestion_pipeline


class TestIngestionPipeline:
    def test_pipeline_lists_expected_sources(self):
        source_ids = {item["source_id"] for item in list_pipeline_sources()}
        assert {"hdc", "egp", "nhso", "clinicaltrials", "pubmed", "tfda", "ratchakitcha", "nlem"} <= source_ids

    def test_pipeline_writes_selected_scaffold_outputs(self, tmp_path):
        results = run_ingestion_pipeline(source_ids=["hdc", "tfda"], output_dir=tmp_path, force=True)

        assert [result.source_id for result in results] == ["hdc", "tfda"]
        assert all(result.output_path.exists() for result in results)

        hdc_frame = pl.read_parquet(tmp_path / "hdc_ncd_prevalence.parquet")
        tfda_frame = pl.read_parquet(tmp_path / "tfda_registrations.parquet")

        assert hdc_frame.columns == [
            "year",
            "province",
            "age_group",
            "disease_code",
            "gender",
            "prevalence_per_1000",
        ]
        assert tfda_frame.columns == [
            "registration_number",
            "product_name",
            "active_ingredient",
            "dosage_form",
            "license_holder",
            "approval_date",
            "status",
        ]

    def test_hdc_build_dataset_normalizes_real_export_aliases(self, tmp_path):
        raw_path = tmp_path / "hdc_export.csv"
        raw_path.write_text(
            "ปี,จังหวัด,กลุ่มอายุ,รหัสโรค,เพศ,อัตราป่วยต่อพันประชากร\n"
            "2024,Chiang Mai,45-59,E119,หญิง,12.5\n",
            encoding="utf-8",
        )

        frame = build_hdc_dataset(raw_path)

        assert frame.to_dicts() == [
            {
                "year": 2024,
                "province": "Chiang Mai",
                "age_group": "45-59",
                "disease_code": "E119",
                "gender": "female",
                "prevalence_per_1000": 12.5,
            }
        ]

    def test_nhso_build_dataset_normalizes_real_export_aliases(self, tmp_path):
        raw_path = tmp_path / "nhso_export.csv"
        raw_path.write_text(
            "เดือนบริการ,สิทธิการรักษา,กลุ่มยา,จำนวนรายการ,จำนวนหน่วย,ยอดชดเชย\n"
            "202401,UCS,SGLT2,125,4500,985432.75\n",
            encoding="utf-8",
        )

        frame = build_nhso_dataset(raw_path)

        assert frame.to_dicts() == [
            {
                "service_month": "2024-01",
                "scheme": "UCS",
                "drug_class": "SGLT2",
                "claims_count": 125,
                "units_dispensed": 4500.0,
                "reimbursement_thb": 985432.75,
            }
        ]

    def test_source_run_auto_discovers_latest_raw_export_and_writes_quality_report(self, tmp_path):
        original_data_dir = settings.data_dir
        settings.data_dir = tmp_path
        try:
            hdc_dir = settings.raw_dir / "hdc"
            hdc_dir.mkdir(parents=True, exist_ok=True)
            raw_path = hdc_dir / "hdc_2024.csv"
            raw_path.write_text(
                "year,province,age_group,disease_code,gender,prevalence_per_1000\n"
                "2024,Bangkok,60+,I10,male,33.2\n",
                encoding="utf-8",
            )

            output_path = tmp_path / "processed" / "hdc_ncd_prevalence.parquet"
            written_path = run_hdc(output_path=output_path, input_path=None)

            assert written_path.exists()
            report_path = settings.interim_dir / "hdc_ncd_prevalence_quality.json"
            assert report_path.exists()
            report = json.loads(report_path.read_text(encoding="utf-8"))
            assert report["row_count"] == 1
            assert report["input_path"].endswith("hdc_2024.csv")

            nhso_dir = settings.raw_dir / "nhso"
            nhso_dir.mkdir(parents=True, exist_ok=True)
            nhso_raw_path = nhso_dir / "nhso_2024.csv"
            nhso_raw_path.write_text(
                "service_month,scheme,drug_class,claims_count,units_dispensed,reimbursement_thb\n"
                "2024-02,SSS,STATIN,98,2200,443210.0\n",
                encoding="utf-8",
            )
            nhso_output = tmp_path / "processed" / "nhso_utilization.parquet"
            nhso_written_path = run_nhso(output_path=nhso_output, input_path=None)
            assert nhso_written_path.exists()
            nhso_report_path = settings.interim_dir / "nhso_utilization_quality.json"
            assert nhso_report_path.exists()
        finally:
            settings.data_dir = original_data_dir