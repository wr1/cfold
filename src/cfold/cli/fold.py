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
from cfold.models import Codebase  # Added for Pydantic model


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
    common_system, instructions = load_instructions(dialect)  # Updated to get common_system
    try:
        pass  # No need for separate common load
    except ValueError:
        available = get_available_dialects()
        click.echo(f"Available dialects: {', '.join(available)}")
        raise click.ClickException("Invalid dialect specified.")

    included_patterns = instructions.get("included", [])
    excluded_patterns = instructions.get("excluded", [])
    included_dirs = instructions.get("included_dirs", [])

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
        system=common_system + "\n\n" + instructions.get("system", ""),
        user=instructions.get("user", ""),
        assistant=instructions.get("assistant", ""),
        files=[{"path": str(filepath.relative_to(cwd)), "content": open(filepath, "r", encoding="utf-8").read()} for filepath in files]
    )

    prompt_content = ""
    if prompt and os.path.isfile(prompt):
        with open(prompt, "r", encoding="utf-8") as prompt_infile:
            prompt_content = prompt_infile.read()
    elif prompt:
        click.echo(f"Warning: Prompt file '{prompt}' does not exist. Skipping.")

    if prompt_content:
        if data.user:
            data.user += "\n\n" + prompt_content
        else:
            data.user = prompt_content

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

    # Visualize instructions by category
    instr_tree = Tree("Instructions Added (Categories)", guide_style="dim")
    if common_system:
        instr_tree.add("[bold]Common System[/bold]")
    if instructions.get("system"):
        instr_tree.add("[bold]Dialect System[/bold]")
    if data.user:
        instr_tree.add("[bold]User[/bold]")
    if data.assistant:
        instr_tree.add("[bold]Assistant[/bold]")
    console.print(instr_tree)


