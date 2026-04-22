"""Run a live RAG query and print lightweight evaluation metrics."""

from __future__ import annotations

import typer
from rich.console import Console
from rich.table import Table

from pharma_intel.rag import RAGEngine, evaluate_rag_answer
from pharma_intel.rag.llm import get_llm

app = typer.Typer(add_completion=False)
console = Console()


@app.command()
def main(
    question: str = typer.Argument(..., help="Question to ask the RAG system"),
    k: int = typer.Option(5, "--k", help="Number of documents to retrieve"),
    provider: str | None = typer.Option(None, "--provider", help="Optional LLM provider override"),
):
    """Ask a question, then evaluate the answer heuristically."""
    engine = RAGEngine(llm=get_llm(override=provider) if provider else None, top_k=k)
    result = engine.answer(question=question, k=k)
    evaluation = evaluate_rag_answer(question=question, answer=result.answer, retrieved=result.retrieved)

    table = Table(title="RAG Evaluation Summary")
    table.add_column("Metric", style="cyan")
    table.add_column("Value")
    table.add_row("question_language", evaluation.question_language)
    table.add_row("answer_language", evaluation.answer_language)
    table.add_row("citation_count", str(evaluation.citation_count))
    table.add_row("has_citations", str(evaluation.has_citations))
    table.add_row("retrieved_count", str(evaluation.retrieved_count))
    table.add_row("avg_retrieval_score", f"{evaluation.avg_retrieval_score:.3f}")
    table.add_row("language_match", str(evaluation.language_match))
    table.add_row("abstained", str(evaluation.abstained))
    console.print(table)


if __name__ == "__main__":
    app()