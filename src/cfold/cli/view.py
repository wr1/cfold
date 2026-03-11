"""Handle viewing command for cfold."""

import json
from rich.console import Console
from rich.tree import Tree
from ..models.codebase import Codebase


def view(foldfile: str):
    """View the prompts and files in a fold file."""
    console = Console()
    try:
        with open(foldfile, "r", encoding="utf-8") as f:
            raw = json.load(f)
        data = Codebase.model_validate(raw)
    except Exception as e:
        console.print(f"Error loading file: {e}")
        return
    instr_tree = Tree("Instructions", guide_style="dim")
    for instr in data.instructions:
        label = f"[bold]{instr.type}[/bold]"
        if instr.name:
            label += f" ({instr.name})"
        if instr.synopsis:
            label += f" - {instr.synopsis}"
        instr_tree.add(label)
    console.print(instr_tree)
    files_tree = Tree("Files", guide_style="dim")
    for file in data.files:
        files_tree.add(f"[green]{file.path}[/green]" if not file.delete else f"[red]{file.path} (delete)[/red]")
    console.print(files_tree)
