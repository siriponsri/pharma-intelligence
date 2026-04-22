"""Tests for the unified ingestion scaffold."""

from __future__ import annotations

import polars as pl

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