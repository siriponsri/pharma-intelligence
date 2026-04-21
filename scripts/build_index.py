"""Build the vector index from processed monographs.

Usage:
    python scripts/build_index.py [--reset]
"""

from __future__ import annotations

import polars as pl
import typer
from rich.console import Console

from pharma_intel.common import logger, settings
from pharma_intel.ingestion.fda_orange_book import DrugMonograph, run_pipeline
from pharma_intel.rag.indexer import index_monographs
from pharma_intel.rag.vectorstore import VectorStore

app = typer.Typer(add_completion=False)
console = Console()


def _load_from_parquet() -> list[DrugMonograph]:
    """Load monographs from cached Parquet if available."""
    path = settings.processed_dir / "orange_book_cardiometabolic.parquet"
    if not path.exists():
        return []

    df = pl.read_parquet(path)
    logger.info(f"Loaded {len(df)} monographs from cache: {path}")

    monographs = []
    for row in df.iter_rows(named=True):
        monographs.append(
            DrugMonograph(
                appl_no=row["appl_no"],
                product_no=row["product_no"],
                ingredient=row["ingredient"],
                trade_name=row["trade_name"],
                applicant=row["applicant"],
                strength=row["strength"],
                dosage_form_route=row["dosage_form_route"],
                approval_date=row["approval_date"],
                therapeutic_area=row["therapeutic_area"],
                patents=[],  # not needed for indexing (text already contains)
                exclusivities=[],
                text=row["text"],
            )
        )
    return monographs


@app.command()
def main(
    reset: bool = typer.Option(False, "--reset", help="Drop existing collection first"),
    collection: str = typer.Option(
        "cardiometabolic_drugs", "--collection", help="Chroma collection name"
    ),
):
    """Embed + index all cardiometabolic drug monographs."""
    settings.ensure_dirs()

    # Try loading from cache, otherwise run full pipeline
    monographs = _load_from_parquet()
    if not monographs:
        logger.info("No cached monographs found — running full ingestion pipeline")
        monographs = run_pipeline()

    if reset:
        store = VectorStore(collection_name=collection)
        store.reset()

    store = index_monographs(monographs, collection_name=collection)

    console.print(f"\n[bold green]✓ Indexing complete[/bold green]")
    console.print(f"Collection: [cyan]{collection}[/cyan]")
    console.print(f"Total documents: [cyan]{store.collection.count()}[/cyan]")
    console.print(f"Persisted at: [dim]{settings.chroma_persist_dir}[/dim]")


if __name__ == "__main__":
    app()
