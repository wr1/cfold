"""Handle viewing command for cfold."""

import json
from rich.console import Console
from rich.tree import Tree
from cfold.models import Codebase


def view(foldfile: str):
    """View the prompts and files in a fold file."""
    console = Console()

    try:
        with open(foldfile, "r", encoding="utf-8") as infile:
            raw_data = json.load(infile)
            data = Codebase.model_validate(raw_data)
    except Exception as e:
        console.print(f"Error loading {foldfile}: {e}", style="red")
        return

    # Visualize instructions
    instr_tree = Tree("Instructions", guide_style="dim")
    for instr in data.instructions:
        label = f"[bold]{instr.type}[/bold]"
        if instr.name:
            label += f" ({instr.name})"
        if instr.synopsis:
            label += f" - {instr.synopsis}"
        instr_tree.add(label)
    console.print(instr_tree)

    # Visualize files
    files_tree = Tree("Files", guide_style="dim")
    for file in data.files:
        if file.delete:
            files_tree.add(f"[red]{file.path} (delete)[/red]")
        else:
            files_tree.add(f"[green]{file.path}[/green]")
    console.print(files_tree)
