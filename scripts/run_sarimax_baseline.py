"""Fit SARIMAX baseline on mock demand and evaluate forecast quality.

Usage:
    python scripts/run_sarimax_baseline.py
    python scripts/run_sarimax_baseline.py --class-id sglt2i --horizon 24
    python scripts/run_sarimax_baseline.py --with-exog
"""

from __future__ import annotations

import json
from pathlib import Path

import polars as pl
import typer
from rich.console import Console
from rich.table import Table

from pharma_intel.common import logger, settings
from pharma_intel.forecasting import (
    CLASSES_BY_ID,
    aggregate_to_class_monthly,
    evaluate_forecast,
    fit_sarimax,
)

app = typer.Typer(add_completion=False)
console = Console()

# Feature sets
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
    class_id: str | None = typer.Option(None, "--class-id", help="Single class to forecast"),
    input_path: Path | None = typer.Option(None, "--input"),
    horizon: int = typer.Option(24, "--horizon", help="Forecast horizon in months"),
    test_months: int = typer.Option(12, "--test-months", help="Held-out test set size"),
    with_exog: bool = typer.Option(False, "--with-exog", help="Include exogenous features"),
    output: Path | None = typer.Option(None, "--output", help="Save results JSON"),
):
    """Fit SARIMAX, forecast, and evaluate on held-out data."""
    settings.ensure_dirs()
    input_path = input_path or (settings.processed_dir / "mock_demand_history.parquet")

    if not input_path.exists():
        console.print(f"[red]Error:[/red] {input_path} not found")
        console.print("Run [cyan]make generate-mock[/cyan] first")
        raise typer.Exit(1)

    logger.info(f"Loading demand panel from {input_path}")
    df = pl.read_parquet(input_path)

    # Aggregate to class × month
    class_df = aggregate_to_class_monthly(df)
    logger.info(f"Aggregated to {len(class_df):,} class-month rows")

    # Which classes to process
    if class_id:
        target_classes = [class_id]
    else:
        target_classes = sorted(class_df["class_id"].unique().to_list())

    exog_cols = EXOG_FEATURES if with_exog else None
    model_label = "SARIMAX+exog" if with_exog else "SARIMAX"

    results: list[dict] = []

    for cid in target_classes:
        if cid not in CLASSES_BY_ID:
            logger.warning(f"Unknown class '{cid}', skipping")
            continue

        class_data = class_df.filter(pl.col("class_id") == cid).sort("month")
        if len(class_data) < 36:
            logger.warning(f"{cid}: insufficient history ({len(class_data)} months)")
            continue

        # Train/test split
        train = class_data.head(len(class_data) - test_months)
        test = class_data.tail(test_months)

        try:
            forecast = fit_sarimax(
                train,
                target_col="units_kddd",
                exog_cols=exog_cols,
                horizon_months=test_months,
            )
        except Exception as e:
            logger.error(f"{cid}: fit failed — {e}")
            continue

        # Evaluate against held-out test
        metrics = evaluate_forecast(
            actual=test["units_kddd"].to_list(),
            forecast=forecast,
            y_train=train["units_kddd"].to_list(),
        )

        results.append(
            {
                "class_id": cid,
                "display_name": CLASSES_BY_ID[cid].display_name,
                "model": model_label,
                "n_train": len(train),
                "n_test": len(test),
                "horizon_months": test_months,
                **{k: round(v, 3) for k, v in metrics.items()},
                "aic": round(forecast.fitted_params["aic"], 1),
                "bic": round(forecast.fitted_params["bic"], 1),
            }
        )

    # Display table
    table = Table(title=f"{model_label} Forecast Evaluation ({test_months}-month held-out)")
    table.add_column("Class", style="cyan")
    table.add_column("MAPE %", justify="right", style="yellow")
    table.add_column("sMAPE %", justify="right")
    table.add_column("MASE", justify="right")
    table.add_column("RMSE", justify="right")
    table.add_column("AIC", justify="right", style="dim")

    for r in sorted(results, key=lambda x: x.get("mape", 999)):
        table.add_row(
            r["class_id"],
            f"{r['mape']:.1f}",
            f"{r['smape']:.1f}",
            f"{r.get('mase', float('nan')):.2f}",
            f"{r['rmse']:,.0f}",
            f"{r['aic']:.0f}",
        )
    console.print(table)

    # Aggregate
    if results:
        avg_mape = sum(r["mape"] for r in results) / len(results)
        console.print(f"\n[bold]Average MAPE across {len(results)} classes: {avg_mape:.2f}%[/bold]")

    # Save
    if output:
        output.write_text(json.dumps(results, indent=2, ensure_ascii=False), encoding="utf-8")
        console.print(f"\n[green]✓ Saved to {output}[/green]")


if __name__ == "__main__":
    app()
