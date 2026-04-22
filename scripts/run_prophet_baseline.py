"""Fit the Prophet baseline on class-level monthly demand."""

from __future__ import annotations

import json
from pathlib import Path

import polars as pl
import typer
from rich.console import Console
from rich.table import Table

from pharma_intel.common import settings
from pharma_intel.forecasting import aggregate_to_class_monthly, evaluate_forecast, fit_prophet_baseline, prophet_available

app = typer.Typer(add_completion=False)
console = Console()

EXOG_FEATURES = [
    "diabetes_prevalence",
    "hypertension_prevalence",
    "dyslipidemia_prevalence",
    "obesity_prevalence",
    "healthcare_budget_index",
    "stockout_days",
]


@app.command()
def main(
    input_path: Path | None = typer.Option(None, "--input"),
    test_months: int = typer.Option(12, "--test-months", help="Held-out test set size"),
    with_exog: bool = typer.Option(False, "--with-exog", help="Include exogenous features"),
    output: Path | None = typer.Option(None, "--output", help="Save results JSON"),
):
    """Run Prophet across all class-month series."""
    if not prophet_available():
        console.print("[red]Prophet is not installed. Use the forecasting extra before running this script.[/red]")
        raise typer.Exit(1)

    settings.ensure_dirs()
    input_path = input_path or (settings.processed_dir / "mock_demand_history.parquet")
    if not input_path.exists():
        console.print(f"[red]Input not found:[/red] {input_path}")
        raise typer.Exit(1)

    class_df = aggregate_to_class_monthly(pl.read_parquet(input_path))
    exog_cols = EXOG_FEATURES if with_exog else None
    results: list[dict] = []

    for class_id in sorted(class_df["class_id"].unique().to_list()):
        series = class_df.filter(pl.col("class_id") == class_id).sort("month")
        train = series.head(len(series) - test_months)
        test = series.tail(test_months)
        forecast = fit_prophet_baseline(train, exog_cols=exog_cols, horizon_months=test_months)
        metrics = evaluate_forecast(test["units_kddd"].to_list(), forecast, y_train=train["units_kddd"].to_list())
        results.append({"class_id": class_id, **{key: round(value, 3) for key, value in metrics.items()}})

    table = Table(title="Prophet Forecast Evaluation")
    table.add_column("Class", style="cyan")
    table.add_column("MAPE %", justify="right")
    table.add_column("sMAPE %", justify="right")
    table.add_column("RMSE", justify="right")
    for result in sorted(results, key=lambda item: item["mape"]):
        table.add_row(result["class_id"], f"{result['mape']:.1f}", f"{result['smape']:.1f}", f"{result['rmse']:.0f}")
    console.print(table)

    if output:
        output.write_text(json.dumps(results, indent=2, ensure_ascii=False), encoding="utf-8")
        console.print(f"[green]Saved results to {output}[/green]")


if __name__ == "__main__":
    app()
