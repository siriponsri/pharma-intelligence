"""Fit the global XGBoost baseline on engineered class-month features."""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import polars as pl
import typer
from rich.console import Console
from rich.table import Table

from pharma_intel.common import settings
from pharma_intel.forecasting import aggregate_to_class_monthly
from pharma_intel.forecasting.xgboost_model import (
    fit_xgboost_global_model,
    infer_feature_columns,
    prepare_training_frame,
    xgboost_available,
)

app = typer.Typer(add_completion=False)
console = Console()


@app.command()
def main(
    input_path: Path | None = typer.Option(None, "--input"),
    output: Path | None = typer.Option(None, "--output", help="Save summary JSON"),
):
    """Fit a global XGBoost regressor and evaluate on the last 12 months."""
    if not xgboost_available():
        console.print("[red]XGBoost is not installed. Use the forecasting extra before running this script.[/red]")
        raise typer.Exit(1)

    settings.ensure_dirs()
    input_path = input_path or (settings.processed_dir / "mock_demand_history.parquet")
    if not input_path.exists():
        console.print(f"[red]Input not found:[/red] {input_path}")
        raise typer.Exit(1)

    class_df = aggregate_to_class_monthly(pl.read_parquet(input_path))
    train_frame = prepare_training_frame(class_df)
    latest_months = sorted(train_frame["month"].unique().to_list())[-12:]
    train = train_frame.filter(~pl.col("month").is_in(latest_months))
    test = train_frame.filter(pl.col("month").is_in(latest_months))

    artifact = fit_xgboost_global_model(train)
    feature_cols = artifact["feature_columns"]
    model = artifact["model"]
    test_features = test.select(
        [pl.col(column_name).cast(pl.Float64, strict=False).fill_null(0.0).alias(column_name) for column_name in feature_cols]
    )
    predictions = model.predict(test_features.to_numpy())
    actual = test["units_kddd"].to_numpy()
    rmse = float(np.sqrt(np.mean((actual - predictions) ** 2)))
    mae = float(np.mean(np.abs(actual - predictions)))

    table = Table(title="XGBoost Global Baseline")
    table.add_column("Metric", style="cyan")
    table.add_column("Value", justify="right")
    table.add_row("Training rows", f"{artifact['n_rows']}")
    table.add_row("Feature count", f"{len(feature_cols)}")
    table.add_row("Held-out rows", f"{len(test)}")
    table.add_row("MAE", f"{mae:,.2f}")
    table.add_row("RMSE", f"{rmse:,.2f}")
    console.print(table)

    if output:
        summary = {
            "n_rows": artifact["n_rows"],
            "feature_columns": infer_feature_columns(train),
            "held_out_rows": len(test),
            "mae": round(mae, 3),
            "rmse": round(rmse, 3),
        }
        output.write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")
        console.print(f"[green]Saved results to {output}[/green]")


if __name__ == "__main__":
    app()
