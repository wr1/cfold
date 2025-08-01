"""Handle folding command for cfold."""

import os
import json
from pathlib import Path
import rich_click as click  # Replaced for Rich-styled help
import pyperclip  # Added for clipboard functionality
from cfold.utils.instructions import load_instructions, get_available_dialects
from cfold.utils.foldignore import load_foldignore, should_include_file
from rich.console import Console
from rich.tree import Tree
from cfold.utils.treeviz import get_folded_tree
from cfold.models import Codebase, FileEntry, Instruction  # Added for Pydantic model


@click.command()
@click.argument("files", nargs=-1)
@click.option("--output", "-o", default="codefold.json", help="Output file")
@click.option("--prompt", "-p", default=None, help="Prompt file to append")
@click.option(
    "--dialect",
    "-d",
    default="default",
    help="Instruction dialect (available: default, codeonly, test, doconly, latex)",
)
def fold(files, output, prompt, dialect):
    """Fold files or directory into a single text file and visualize the structure."""
    cwd = Path.cwd()
    try:
        instructions_list = load_instructions(dialect)
    except ValueError:
        available = get_available_dialects()
        click.echo(f"Available dialects: {', '.join(available)}")
        raise click.ClickException("Invalid dialect specified.")

    included_patterns = instructions_list[1].get("included", [])  # Adjust if needed
    excluded_patterns = instructions_list[1].get("excluded", [])
    included_dirs = instructions_list[1].get("included_dirs", [])

    if not files:
        directory = cwd
        ignore_patterns = load_foldignore(directory)
        files = []
        for dirpath, _, filenames in os.walk(directory):
            for filename in filenames:
                filepath = Path(dirpath) / filename
                if should_include_file(
                    filepath,
                    ignore_patterns,
                    directory,
                    included_patterns,
                    excluded_patterns,
                    included_dirs,
                ):
                    files.append(filepath)
    else:
        files = [Path(f).absolute() for f in files if Path(f).is_file()]

    if not files:
        click.echo("No valid files to fold.")
        return

    data = Codebase(
        instructions=instructions_list[0],
        files=[
            FileEntry(
                path=str(filepath.relative_to(cwd)),
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
        click.echo(f"Warning: Prompt file '{prompt}' does not exist. Skipping.")

    if prompt_content:
        data.instructions.append(
            Instruction(type="user", content=prompt_content, name="prompt")
        )

    try:
        with open(output, "w", encoding="utf-8") as outfile:
            json.dump(data.model_dump(), outfile, indent=2)
        # Copy content to clipboard after writing the file
        pyperclip.copy(json.dumps(data.model_dump()))
        click.echo(f"Codebase folded into {output} and content copied to clipboard.")
    except IOError as e:
        click.echo(f"Error writing to {output}: {e}")
        raise

    console = Console()
    file_tree = get_folded_tree(files, cwd)
    if file_tree:
        console.print(file_tree)

    # Visualize instructions by type and name
    instr_tree = Tree("Instructions Added", guide_style="dim")
    for instr in data.instructions:
        label = f"[bold]{instr.type}[/bold]"
        if instr.name:
            label += f" ({instr.name})"
        instr_tree.add(label)
    console.print(instr_tree)
