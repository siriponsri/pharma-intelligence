"""Smoke tests — basic sanity checks that don't require network/API.

Run with: pytest -v
"""

from __future__ import annotations

from pharma_intel.common.constants import (
    CARDIOMETABOLIC_DRUGS,
    DIABETES_DRUGS,
    DYSLIPIDEMIA_DRUGS,
    HYPERTENSION_DRUGS,
    classify_therapeutic_area,
)


class TestConstants:
    def test_drug_sets_nonempty(self):
        assert len(DIABETES_DRUGS) > 20
        assert len(HYPERTENSION_DRUGS) > 20
        assert len(DYSLIPIDEMIA_DRUGS) > 5

    def test_combined_set_is_union(self):
        expected = DIABETES_DRUGS | HYPERTENSION_DRUGS | DYSLIPIDEMIA_DRUGS
        assert CARDIOMETABOLIC_DRUGS == expected

    def test_key_drugs_present(self):
        assert "METFORMIN HYDROCHLORIDE" in DIABETES_DRUGS
        assert "EMPAGLIFLOZIN" in DIABETES_DRUGS
        assert "LOSARTAN POTASSIUM" in HYPERTENSION_DRUGS
        assert "ATORVASTATIN CALCIUM" in DYSLIPIDEMIA_DRUGS


class TestTherapeuticAreaClassifier:
    def test_diabetes_drug(self):
        assert classify_therapeutic_area("METFORMIN HYDROCHLORIDE") == "diabetes"

    def test_hypertension_drug(self):
        assert classify_therapeutic_area("LOSARTAN POTASSIUM") == "hypertension"

    def test_dyslipidemia_drug(self):
        assert classify_therapeutic_area("ATORVASTATIN CALCIUM") == "dyslipidemia"

    def test_non_cardiometabolic_returns_none(self):
        assert classify_therapeutic_area("ASPIRIN") is None
        assert classify_therapeutic_area("ACETAMINOPHEN") is None

    def test_combination_product(self):
        # Losartan + HCTZ combo
        result = classify_therapeutic_area("LOSARTAN POTASSIUM; HYDROCHLOROTHIAZIDE")
        assert result == "hypertension"  # both are HTN drugs

    def test_multi_area_combination(self):
        # DM + HTN combo (hypothetical)
        result = classify_therapeutic_area("METFORMIN HYDROCHLORIDE; LOSARTAN POTASSIUM")
        assert result == "combination"

    def test_case_insensitive(self):
        assert classify_therapeutic_area("metformin hydrochloride") == "diabetes"

    def test_empty_string(self):
        assert classify_therapeutic_area("") is None


class TestImports:
    """Verify all modules import cleanly."""

    def test_common_imports(self):
        from pharma_intel.common import logger, settings  # noqa: F401

    def test_ingestion_imports(self):
        from pharma_intel.ingestion.fda_orange_book import (  # noqa: F401
            DrugMonograph,
            run_pipeline,
        )

    def test_rag_imports(self):
        from pharma_intel.rag import RAGEngine, VectorStore  # noqa: F401
