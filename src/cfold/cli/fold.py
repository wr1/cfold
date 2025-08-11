"""Handle folding command for cfold."""

import os
import json
from pathlib import Path
import rich_click as click  # Replaced for Rich-styled help
import pyperclip  # Added for clipboard functionality
from cfold.utils.instructions import load_instructions, get_available_dialects
import yaml  # Added for loading .foldrc
from cfold.utils.foldignore import load_foldignore, should_include_file
from rich.console import Console
from rich.tree import Tree
from cfold.utils.treeviz import get_folded_tree
from cfold.models import Codebase, FileEntry, Instruction  # Added for Pydantic model


@click.command()
@click.pass_context
@click.argument("files", nargs=-1)
@click.option("--output", "-o", default="codefold.json", help="Output file")
@click.option("--prompt", "-p", default=None, help="Prompt file to append")
@click.option(
    "--dialect",
    "-d",
    default="default",
    help="Instruction dialect (available: default, py, pytest, doc, typst)",
)
@click.option(
    "--bare", "-b", is_flag=True, help="Bare mode without boilerplate instructions"
)
def fold(ctx, files, output, prompt, dialect, bare):
    """Fold files or directory into a single text file and visualize the structure."""
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
        click.echo(
            f"Invalid dialect specified. Available dialects: {', '.join(available)}"
        )
        ctx.exit(1)
    except Exception as e:
        raise click.ClickException(f"Error loading instructions: {str(e)}")

    included_patterns = patterns.get("included", [])  # Adjust if needed
    excluded_patterns = patterns.get("excluded", [])
    included_dirs = patterns.get("included_dirs", [])

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
        instructions=instructions,
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

    console = Console()
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
        click.echo(f"Error writing to {output}: {e}")
        raise

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
