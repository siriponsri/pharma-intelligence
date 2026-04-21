"""Benchmark: run the same questions through multiple LLM providers and save results.

Use this for the paper's comparative evaluation section.

Usage:
    python scripts/benchmark_providers.py --questions questions.json --out results.json

`questions.json` format:
    [
        {"id": "Q001", "question": "...", "reference": "..."},
        ...
    ]
"""

from __future__ import annotations

import json
import time
from pathlib import Path

import typer
from rich.console import Console
from rich.progress import Progress

from pharma_intel.common import logger
from pharma_intel.rag import RAGEngine
from pharma_intel.rag.llm import get_llm

app = typer.Typer(add_completion=False)
console = Console()


@app.command()
def main(
    questions: Path = typer.Option(
        ..., "--questions", help="Path to questions JSON"
    ),
    out: Path = typer.Option(..., "--out", help="Where to save benchmark results"),
    providers: str = typer.Option(
        "thaillm,anthropic",
        "--providers",
        help="Comma-separated list of providers to benchmark",
    ),
    k: int = typer.Option(5, "--k"),
    collection: str = typer.Option("cardiometabolic_drugs", "--collection"),
):
    """Run every question against every provider and record results."""
    with open(questions, encoding="utf-8") as f:
        question_list = json.load(f)

    provider_list = [p.strip() for p in providers.split(",")]
    logger.info(f"Benchmarking {len(provider_list)} providers on {len(question_list)} questions")

    results: list[dict] = []

    with Progress(console=console) as progress:
        total = len(question_list) * len(provider_list)
        task = progress.add_task("[cyan]Running benchmark...", total=total)

        for provider in provider_list:
            try:
                llm = get_llm(override=provider)
            except Exception as e:
                logger.error(f"Could not initialize {provider}: {e}")
                continue

            engine = RAGEngine(collection_name=collection, top_k=k, llm=llm)

            for q in question_list:
                start = time.time()
                try:
                    ans = engine.answer(question=q["question"], k=k)
                    results.append(
                        {
                            "question_id": q["id"],
                            "question": q["question"],
                            "reference": q.get("reference"),
                            "provider": provider,
                            "model": ans.model,
                            "answer": ans.answer,
                            "retrieved_ids": [c.doc_id for c in ans.retrieved],
                            "retrieval_scores": [c.score for c in ans.retrieved],
                            "input_tokens": ans.input_tokens,
                            "output_tokens": ans.output_tokens,
                            "latency_sec": round(time.time() - start, 2),
                            "error": None,
                        }
                    )
                except Exception as e:
                    logger.error(f"[{provider}] Q{q['id']} failed: {e}")
                    results.append(
                        {
                            "question_id": q["id"],
                            "question": q["question"],
                            "provider": provider,
                            "error": str(e),
                        }
                    )

                progress.update(task, advance=1)

    out.write_text(json.dumps(results, ensure_ascii=False, indent=2), encoding="utf-8")
    console.print(f"\n[bold green]✓ Saved {len(results)} results to {out}[/bold green]")


if __name__ == "__main__":
    app()
