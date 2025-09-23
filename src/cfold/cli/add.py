"""Handle adding files to an existing cfold file."""

import json
import os
from pathlib import Path
from rich.console import Console
from cfold.models import Codebase, FileEntry
from typing import List


def add(files: List[str], foldfile: str = "codefold.json"):
    """Add files to an existing cfold file."""
    console = Console()
    cwd = Path.cwd()

    if not Path(foldfile).exists():
        console.print(f"Error: {foldfile} does not exist.", style="red")
        return

    try:
        with open(foldfile, "r", encoding="utf-8") as infile:
            raw_data = json.load(infile)
            data = Codebase.model_validate(raw_data)
    except Exception as e:
        console.print(f"Error loading {foldfile}: {e}", style="red")
        return

    existing_paths = {f.path for f in data.files}

    added_files = []
    for file_path in files:
        abs_path = Path(file_path).absolute()
        if not abs_path.is_file():
            console.print(
                f"Warning: {file_path} is not a file, skipping.", style="yellow"
            )
            continue
        rel_path = os.path.relpath(str(abs_path), str(cwd))
        if rel_path in existing_paths:
            # Update existing
            for f in data.files:
                if f.path == rel_path:
                    f.content = open(abs_path, "r", encoding="utf-8").read()
                    break
        else:
            # Add new
            data.files.append(
                FileEntry(
                    path=rel_path,
                    content=open(abs_path, "r", encoding="utf-8").read(),
                )
            )
            added_files.append(rel_path)

    try:
        with open(foldfile, "w", encoding="utf-8") as outfile:
            json.dump(data.model_dump(), outfile, indent=2)
    except IOError as e:
        console.print(f"Error writing to {foldfile}: {e}", style="red")
        return

    if added_files:
        console.print(
            f"Added files to [cyan]{foldfile}[/cyan]: {', '.join(added_files)}"
        )
    else:
        console.print(f"No new files added to [cyan]{foldfile}[/cyan].")
