"""Handle summarize command for cfold."""

from pathlib import Path
from typing import List
from rich.console import Console
import pyperclip
from ..summarization.summarize_codebases import summarize_codebases


def summarize(
    codebases: List[str], output: str = "summary.txt", include_tests: bool = False, clip: bool = False
):
    """Summarize codebases using AST."""
    console = Console()
    paths = [Path(cb) for cb in codebases]
    summary = summarize_codebases(paths, include_tests)
    Path(output).write_text(summary, encoding="utf-8")
    if clip:
        pyperclip.copy(summary)
    console.print(f"Summary written to [cyan]{output}[/cyan]" + (" and copied to clipboard." if clip else "."))
