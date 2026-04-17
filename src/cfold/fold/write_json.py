"""Write Codebase to JSON and optionally copy to clipboard."""

import json
from pathlib import Path

import pyperclip
from rich.console import Console

from ..models.codebase import codebase


def write_json(codebase: codebase, output: Path, clip: bool = False) -> None:
    """Write folded codebase to JSON."""
    console = Console()
    with open(output, "w", encoding="utf-8") as f:
        json.dump(codebase.model_dump(), f, indent=2)
    if clip:
        pyperclip.copy(json.dumps(codebase.model_dump()))
    console.print(
        f"Codebase folded into [cyan]{output}[/cyan]"
        + (" and copied to clipboard" if clip else ".")
    )
