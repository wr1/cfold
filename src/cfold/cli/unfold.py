"""Handle unfolding command for cfold."""

import json
from pathlib import Path

from rich.console import Console

from ..models.codebase import codebase
from ..unfold.apply_changes import apply_changes


def unfold(foldfile: str, original_dir: str = None, output_dir: str = None):
    """Unfold a modified fold file into a directory."""
    console = Console()
    cwd = Path.cwd()
    output_path = Path(output_dir or cwd)
    with open(foldfile, "r", encoding="utf-8") as f:
        raw = json.load(f)
    data = codebase.model_validate(raw)
    apply_changes(data, output_path, Path(original_dir) if original_dir else None)
    console.print(f"[bold dim]Codebase unfolded into {output_path}[/bold dim]")
