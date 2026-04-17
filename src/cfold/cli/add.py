"""Handle adding files to an existing cfold file."""

import json
from pathlib import Path
from typing import List

import pyperclip
from rich.console import Console

from ..models.codebase import codebase
from ..models.file_entry import file_entry
from ..tree.build_folded import build_folded_tree


def add(files: List[str], foldfile: str = "codefold.json"):
    """Add or update files in an existing cfold file."""
    console = Console()
    cwd = Path.cwd()
    path = Path(foldfile)
    if not path.exists():
        console.print(f"Error: {foldfile} does not exist.", style="red")
        return
    with open(path, "r", encoding="utf-8") as f:
        data = codebase.model_validate(json.load(f))
    existing = {f.path for f in data.files}
    new_added = False
    for f in files:
        abs_path = Path(f).absolute()
        if not abs_path.is_file():
            console.print(f"Warning: {f} is not a file, skipping.")
            continue
        rel = str(abs_path.relative_to(cwd))
        content = abs_path.read_text(encoding="utf-8")
        if rel in existing:
            for entry in data.files:
                if entry.path == rel:
                    entry.content = content
                    break
        else:
            data.files.append(file_entry(path=rel, content=content))
            new_added = True
    added_files = [Path(entry.path) for entry in data.files if entry.path not in existing]
    if added_files:
        tree = build_folded_tree(added_files, cwd)
        console.print(tree)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data.model_dump(), f, indent=2)
    pyperclip.copy(json.dumps(data.model_dump()))
    if new_added:
        console.print(f"Added files to [cyan]{foldfile}[/cyan] and copied to clipboard.")
    else:
        console.print("No new files added, but updated existing.")
