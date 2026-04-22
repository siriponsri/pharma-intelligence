"""Prepare the TFT experiment scaffold and validate prerequisites."""

from __future__ import annotations

from pathlib import Path

import polars as pl
import typer
from rich.console import Console
from rich.table import Table

from pharma_intel.common import settings
from pharma_intel.forecasting import aggregate_to_class_monthly
from pharma_intel.forecasting.tft_model import build_tft_training_config, tft_dependencies_available

app = typer.Typer(add_completion=False)
console = Console()


@app.command()
def main(input_path: Path | None = typer.Option(None, "--input")):
    """Show the TFT training configuration and dependency status."""
    settings.ensure_dirs()
    input_path = input_path or (settings.processed_dir / "mock_demand_history.parquet")
    if not input_path.exists():
        console.print(f"[red]Input not found:[/red] {input_path}")
        raise typer.Exit(1)

    class_df = aggregate_to_class_monthly(pl.read_parquet(input_path))
    config = build_tft_training_config(class_df)

    table = Table(title="TFT Experiment Scaffold")
    table.add_column("Field", style="cyan")
    table.add_column("Value", justify="right")
    for key, value in config.items():
        table.add_row(str(key), str(value))
    table.add_row("dependencies_available", str(tft_dependencies_available()))
    console.print(table)

    if not tft_dependencies_available():
        console.print("[yellow]TFT dependencies are not installed yet. This script prepares the dataset contract only.[/yellow]")


if __name__ == "__main__":
    app()
