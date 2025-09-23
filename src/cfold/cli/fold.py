"""Handle folding command for cfold."""

import os
import json
from pathlib import Path
import pyperclip  # Added for clipboard functionality
from cfold.utils.instructions import load_instructions, get_available_dialects
import yaml  # Added for loading .foldrc
from cfold.utils.foldignore import should_include_file
from rich.console import Console
from rich.tree import Tree
from cfold.utils.treeviz import get_folded_tree
from cfold.models import Codebase, FileEntry, Instruction  # Added for Pydantic model
import sys
from typing import List


def fold(
    files: List[str],
    output: str = "codefold.json",
    prompt: str = None,
    dialect: str = "default",
    bare: bool = False,
):
    """Fold files or directory into a single text file and visualize the structure."""
    bare = bool(bare)
    console = Console()
    cwd = Path.cwd()
    # Check for local default dialect if 'default' is specified
    if dialect == "default":
        local_path = cwd / ".foldrc"
        if local_path.exists():
            with local_path.open("r", encoding="utf-8") as f:
                local_config = yaml.safe_load(f) or {}
            if "default_dialect" in local_config:
                dialect = local_config["default_dialect"]

    try:
        instructions, patterns = load_instructions(dialect)
        if bare:
            instructions = []
    except ValueError:
        available = get_available_dialects()
        console.print(
            f"Invalid dialect specified. Available dialects: {', '.join(available)}",
            style="red",
        )
        sys.exit(1)
    except Exception as e:
        console.print(f"Error loading instructions: {str(e)}", style="red")
        sys.exit(1)

    included_patterns = patterns.get("included", [])  # Adjust if needed
    excluded_patterns = patterns.get("excluded", [])
    included_dirs = patterns.get("included_dirs", [])
    exclude_files = patterns.get("exclude_files", [])

    if not files:
        directory = cwd
        files = []
        for dirpath, _, filenames in os.walk(directory):
            for filename in filenames:
                filepath = Path(dirpath) / filename
                rel_path = os.path.relpath(str(filepath), str(directory))
                if (
                    should_include_file(
                        filepath,
                        directory,
                        included_patterns,
                        excluded_patterns,
                        included_dirs,
                    )
                    and rel_path not in exclude_files
                ):
                    files.append(filepath)
    else:
        files = [Path(f).absolute() for f in files if Path(f).is_file()]
        files = [
            f for f in files if os.path.relpath(str(f), str(cwd)) not in exclude_files
        ]

    if not files:
        console.print("No valid files to fold.")
        return

    data = Codebase(
        instructions=instructions,
        files=[
            FileEntry(
                path=os.path.relpath(str(filepath), str(cwd)),
                content=open(filepath, "r", encoding="utf-8").read(),
            )
            for filepath in files
        ],
    )

    prompt_content = ""
    if prompt and os.path.isfile(prompt):
        with open(prompt, "r", encoding="utf-8") as prompt_infile:
            prompt_content = prompt_infile.read()
    elif prompt:
        console.print(
            f"Warning: Prompt file '{prompt}' does not exist. Skipping.", style="yellow"
        )

    if prompt_content:
        data.instructions.append(
            Instruction(type="user", content=prompt_content, name="prompt")
        )

    try:
        with open(output, "w", encoding="utf-8") as outfile:
            json.dump(
                data.model_dump(),
                outfile,
                indent=2,
            )
        # Copy content to clipboard after writing the file
        pyperclip.copy(json.dumps(data.model_dump()))
    except IOError as e:
        console.print(f"Error writing to {output}: {e}", style="red")
        sys.exit(1)

    file_tree = get_folded_tree(files, cwd)
    if file_tree:
        console.print(file_tree)

    # Visualize instructions by type and name
    instr_tree = Tree("Instructions Added", guide_style="dim")
    for instr in data.instructions:
        label = f"[bold]{instr.type}[/bold]"
        if instr.name:
            label += f" ({instr.name})"
        if instr.synopsis:
            label += f" - {instr.synopsis}"
        instr_tree.add(label)
    console.print(instr_tree)

    console.print(
        f"Codebase folded into [cyan]{output}[/cyan] and content [green]copied to clipboard[/green]."
    )
