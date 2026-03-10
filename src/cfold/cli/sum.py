"""Handle sum command for cfold."""

from pathlib import Path
from typing import List
from rich.console import Console
from cfold.core.summarize import summarize_codebases


def sum_codebases(
    codebases: List[str], output: str = "summary.txt", include_tests: bool = False
):
    """Summarize codebases using AST to generate LLM-readable structure."""
    console = Console()
    codebase_paths = [Path(cb) for cb in codebases]
    output_path = Path(output)

    try:
        summary = summarize_codebases(codebase_paths, include_tests=include_tests)
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(summary)
        console.print(f"Summary written to [cyan]{output_path}[/cyan].")
    except Exception as e:
        console.print(f"Error summarizing codebases: {e}", style="red")
