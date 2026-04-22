"""Unified ingestion pipeline for public-source scaffolds."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Callable

from pharma_intel.common import settings
from pharma_intel.ingestion import (
    clinicaltrials_api,
    egp_scraper,
    hdc_scraper,
    nhso_scraper,
    nlem_scraper,
    pubmed_api,
    ratchakitcha_scraper,
    tfda_scraper,
)


@dataclass(frozen=True)
class PipelineSource:
    """Configuration for one pipeline source."""

    source_id: str
    phase: str
    output_name: str
    description: str
    runner: Callable[[Path | None, Path | None], Path]


@dataclass(frozen=True)
class PipelineRunResult:
    """Outcome of one pipeline step."""

    source_id: str
    status: str
    output_path: Path


PIPELINE_SOURCES = (
    PipelineSource("hdc", "phase_2", hdc_scraper.SPEC.output_name, hdc_scraper.SPEC.description, hdc_scraper.run),
    PipelineSource("egp", "phase_2", egp_scraper.SPEC.output_name, egp_scraper.SPEC.description, egp_scraper.run),
    PipelineSource("nhso", "phase_2", nhso_scraper.SPEC.output_name, nhso_scraper.SPEC.description, nhso_scraper.run),
    PipelineSource(
        "clinicaltrials",
        "phase_2",
        clinicaltrials_api.SPEC.output_name,
        clinicaltrials_api.SPEC.description,
        clinicaltrials_api.run,
    ),
    PipelineSource("pubmed", "phase_2", pubmed_api.SPEC.output_name, pubmed_api.SPEC.description, pubmed_api.run),
    PipelineSource("tfda", "phase_3", tfda_scraper.SPEC.output_name, tfda_scraper.SPEC.description, tfda_scraper.run),
    PipelineSource(
        "ratchakitcha",
        "phase_3",
        ratchakitcha_scraper.SPEC.output_name,
        ratchakitcha_scraper.SPEC.description,
        ratchakitcha_scraper.run,
    ),
    PipelineSource("nlem", "phase_3", nlem_scraper.SPEC.output_name, nlem_scraper.SPEC.description, nlem_scraper.run),
)


def list_pipeline_sources() -> list[dict[str, str]]:
    """Return a serializable summary of known sources."""
    return [
        {
            "source_id": source.source_id,
            "phase": source.phase,
            "output_name": source.output_name,
            "description": source.description,
        }
        for source in PIPELINE_SOURCES
    ]


def run_ingestion_pipeline(
    source_ids: list[str] | None = None,
    output_dir: Path | None = None,
    force: bool = False,
) -> list[PipelineRunResult]:
    """Run the selected ingestion scaffold steps and persist parquet outputs."""
    settings.ensure_dirs()
    target_dir = output_dir or settings.processed_dir
    target_dir.mkdir(parents=True, exist_ok=True)

    known_sources = {source.source_id: source for source in PIPELINE_SOURCES}
    selected_ids = source_ids or [source.source_id for source in PIPELINE_SOURCES]
    unknown_ids = sorted(set(selected_ids) - set(known_sources))
    if unknown_ids:
        raise ValueError(f"Unknown source ids: {', '.join(unknown_ids)}")

    results: list[PipelineRunResult] = []
    for source_id in selected_ids:
        source = known_sources[source_id]
        output_path = target_dir / source.output_name
        if output_path.exists() and not force:
            results.append(PipelineRunResult(source_id=source_id, status="skipped", output_path=output_path))
            continue
        written_path = source.runner(output_path=output_path, input_path=None)
        results.append(PipelineRunResult(source_id=source_id, status="written", output_path=written_path))

    return results
