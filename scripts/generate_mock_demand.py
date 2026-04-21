"""Generate synthetic cardiometabolic demand panel.

Usage:
    python scripts/generate_mock_demand.py
    python scripts/generate_mock_demand.py --start 2018-01-01 --end 2025-12-31
    python scripts/generate_mock_demand.py --seed 42
"""

from __future__ import annotations

import polars as pl
import typer
from rich.console import Console
from rich.table import Table

from pharma_intel.common import logger, settings
from pharma_intel.forecasting import GeneratorConfig, generate_demand_panel

app = typer.Typer(add_completion=False)
console = Console()


@app.command()
def main(
    start: str = typer.Option("2018-01-01", "--start"),
    end: str = typer.Option("2025-12-31", "--end"),
    seed: int = typer.Option(42, "--seed"),
    output: str | None = typer.Option(None, "--output"),
):
    """Generate + save mock demand panel."""
    settings.ensure_dirs()
    cfg = GeneratorConfig(start_date=start, end_date=end, random_seed=seed)

    logger.info(f"Config: start={start}, end={end}, seed={seed}")
    df = generate_demand_panel(config=cfg)

    out_path = output or str(settings.processed_dir / "mock_demand_history.parquet")
    df.write_parquet(out_path)
    # Also save CSV for easy inspection
    csv_path = out_path.replace(".parquet", ".csv")
    df.write_csv(csv_path)

    console.print(f"\n[bold green]✓ Generated {len(df):,} rows[/bold green]")
    console.print(f"  Parquet: [cyan]{out_path}[/cyan]")
    console.print(f"  CSV:     [cyan]{csv_path}[/cyan]")

    # Summary by therapeutic area
    area_summary = (
        df.group_by("therapeutic_area")
        .agg(
            [
                pl.col("units_kddd").sum().alias("total_kddd"),
                pl.col("revenue_thb_million").sum().alias("total_revenue_mb"),
                pl.col("class_id").n_unique().alias("n_classes"),
            ]
        )
        .to_dicts()
    )

    table = Table(title="Summary by Therapeutic Area")
    table.add_column("Area", style="cyan")
    table.add_column("# Classes", justify="right")
    table.add_column("Total kDDD", justify="right")
    table.add_column("Total Revenue (THB M)", justify="right", style="green")

    for row in area_summary:
        table.add_row(
            row["therapeutic_area"],
            str(row["n_classes"]),
            f"{row['total_kddd']:,.0f}",
            f"{row['total_revenue_mb']:,.0f}",
        )
    console.print(table)

    # Show a sample of rows
    console.print("\n[bold]First 5 rows:[/bold]")
    console.print(df.head(5))


if __name__ == "__main__":
    app()
