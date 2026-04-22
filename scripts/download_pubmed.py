"""Build the PubMed scaffold dataset from an optional local export."""

from __future__ import annotations

from pathlib import Path

import typer
from rich.console import Console

from pharma_intel.ingestion.pubmed_api import run

app = typer.Typer(add_completion=False)
console = Console()


@app.command()
def main(
    input_path: Path | None = typer.Option(None, "--input", help="Optional CSV export to normalize"),
    output: Path | None = typer.Option(None, "--output", help="Output parquet path"),
):
    """Write the PubMed parquet artifact."""
    written_path = run(output_path=output, input_path=input_path)
    console.print(f"[green]Saved PubMed dataset to {written_path}[/green]")


if __name__ == "__main__":
    app()
