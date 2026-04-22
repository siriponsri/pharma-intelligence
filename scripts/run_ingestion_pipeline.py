"""Run the unified public-source ingestion pipeline."""

from __future__ import annotations

from pathlib import Path

import typer
from rich.console import Console
from rich.table import Table

from pharma_intel.ingestion import list_pipeline_sources, run_ingestion_pipeline

app = typer.Typer(add_completion=False)
console = Console()


@app.command()
def main(
    source: list[str] | None = typer.Option(None, "--source", help="Run only specific source ids"),
    output_dir: Path | None = typer.Option(None, "--output-dir", help="Override output directory"),
    force: bool = typer.Option(False, "--force", help="Rewrite outputs even if they already exist"),
    list_only: bool = typer.Option(False, "--list", help="List known sources without running"),
):
    """Run scaffolded ingestion steps and write parquet artifacts."""
    if list_only:
        table = Table(title="Pipeline Sources")
        table.add_column("Source ID", style="cyan")
        table.add_column("Phase")
        table.add_column("Output")
        table.add_column("Description")
        for item in list_pipeline_sources():
            table.add_row(item["source_id"], item["phase"], item["output_name"], item["description"])
        console.print(table)
        raise typer.Exit()

    results = run_ingestion_pipeline(source_ids=source, output_dir=output_dir, force=force)

    table = Table(title="Ingestion Pipeline Results")
    table.add_column("Source ID", style="cyan")
    table.add_column("Status")
    table.add_column("Output Path", overflow="fold")
    for result in results:
        table.add_row(result.source_id, result.status, str(result.output_path))
    console.print(table)


if __name__ == "__main__":
    app()
