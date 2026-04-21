"""Query the RAG system.

Usage:
    python scripts/query_rag.py "What patents cover empagliflozin?"
    python scripts/query_rag.py "สิทธิบัตรของ dapagliflozin หมดเมื่อไหร่"
    python scripts/query_rag.py "list all SGLT2 inhibitors" --k 10
    python scripts/query_rag.py "..." --provider anthropic   # benchmark
"""

from __future__ import annotations

import typer
from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
from rich.table import Table

from pharma_intel.common import logger
from pharma_intel.rag import RAGEngine
from pharma_intel.rag.llm import get_llm

app = typer.Typer(add_completion=False)
console = Console()


@app.command()
def main(
    question: str = typer.Argument(..., help="Question to ask the RAG system"),
    k: int = typer.Option(5, "--k", help="Number of documents to retrieve"),
    collection: str = typer.Option(
        "cardiometabolic_drugs", "--collection", help="Chroma collection name"
    ),
    therapeutic_area: str | None = typer.Option(
        None,
        "--area",
        help="Filter by therapeutic area: diabetes | hypertension | dyslipidemia | combination",
    ),
    provider: str | None = typer.Option(
        None,
        "--provider",
        help="Override LLM provider: 'thaillm' or 'anthropic'",
    ),
    show_sources: bool = typer.Option(
        True, "--sources/--no-sources", help="Show retrieved sources"
    ),
    temperature: float = typer.Option(0.3, "--temperature", help="Sampling temperature"),
):
    """Ask a question about cardiometabolic drugs."""
    llm = get_llm(override=provider) if provider else None
    engine = RAGEngine(collection_name=collection, top_k=k, llm=llm)

    where: dict | None = None
    if therapeutic_area:
        where = {"therapeutic_area": therapeutic_area}

    logger.info(f"Question: {question}")
    result = engine.answer(question=question, k=k, where=where, temperature=temperature)

    # Answer panel
    console.print()
    console.print(
        Panel(
            Markdown(result.answer),
            title=f"[bold green]Answer[/bold green] [dim]({result.provider}/{result.model})[/dim]",
            border_style="green",
        )
    )

    # Sources table
    if show_sources and result.retrieved:
        table = Table(title="Retrieved Sources", show_lines=True)
        table.add_column("Rank", style="dim", width=5)
        table.add_column("Score", width=7)
        table.add_column("Doc ID", style="cyan", width=22)
        table.add_column("Ingredient", style="magenta")
        table.add_column("Trade Name")
        table.add_column("Area", style="yellow")

        for i, chunk in enumerate(result.retrieved, 1):
            table.add_row(
                str(i),
                f"{chunk.score:.3f}",
                chunk.doc_id,
                chunk.metadata.get("ingredient", "")[:40],
                chunk.metadata.get("trade_name", "")[:25],
                chunk.metadata.get("therapeutic_area", ""),
            )
        console.print(table)

    # Token usage (if available)
    if result.input_tokens or result.output_tokens:
        console.print(
            f"\n[dim]Tokens: {result.input_tokens or '?'} in / "
            f"{result.output_tokens or '?'} out[/dim]"
        )


if __name__ == "__main__":
    app()
