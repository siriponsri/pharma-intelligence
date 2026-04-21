"""Download FDA Orange Book and run the ingestion pipeline.

Usage:
    python scripts/download_orange_book.py [--force]
"""

from __future__ import annotations

import typer
from rich.console import Console
from rich.table import Table

from pharma_intel.common import logger
from pharma_intel.ingestion.fda_orange_book import run_pipeline

app = typer.Typer(add_completion=False)
console = Console()


@app.command()
def main(force: bool = typer.Option(False, "--force", help="Re-download even if cached")):
    """Download Orange Book → parse → filter → save monographs."""
    logger.info("Starting Orange Book ingestion pipeline")
    monographs = run_pipeline(force_download=force)

    # Summary
    console.print("\n[bold green]✓ Ingestion complete[/bold green]")
    console.print(f"Total monographs: [cyan]{len(monographs)}[/cyan]")

    # Breakdown by therapeutic area
    area_counts: dict[str, int] = {}
    for m in monographs:
        area_counts[m.therapeutic_area] = area_counts.get(m.therapeutic_area, 0) + 1

    table = Table(title="Monographs by therapeutic area")
    table.add_column("Therapeutic Area", style="cyan")
    table.add_column("Count", justify="right", style="magenta")
    for area, count in sorted(area_counts.items(), key=lambda x: -x[1]):
        table.add_row(area, str(count))
    console.print(table)

    # Sample output
    if monographs:
        console.print("\n[bold]Sample monograph text:[/bold]")
        console.print(f"[dim]{monographs[0].text[:500]}...[/dim]")


if __name__ == "__main__":
    app()
