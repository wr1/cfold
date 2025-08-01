"""Handle folding command for cfold."""

import os
import json
from pathlib import Path
import rich_click as click  # Replaced for Rich-styled help
import pyperclip  # Added for clipboard functionality
from cfold.utils.instructions import load_instructions, get_available_dialects
from cfold.utils.foldignore import load_foldignore, should_include_file
from rich.console import Console
from cfold.utils.treeviz import get_folded_tree


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
    common = load_instructions("common")
    try:
        instructions = load_instructions(dialect)
    except ValueError:
        available = get_available_dialects()
        click.echo(f"Available dialects: {', '.join(available)}")
        raise click.ClickException("Invalid dialect specified.")

    included_patterns = instructions.get("included", [])
    excluded_patterns = instructions.get("excluded", [])

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
                ):
                    files.append(filepath)
    else:
        files = [Path(f).absolute() for f in files if Path(f).is_file()]

    if not files:
        click.echo("No valid files to fold.")
        return

    data = {
        "instructions": common["prefix"] + "\n\n" + instructions["prefix"],
        "files": [],
        "prompt": "",
    }

    for filepath in files:
        relpath = filepath.relative_to(cwd)
        with open(filepath, "r", encoding="utf-8") as infile:
            content = infile.read()
        data["files"].append({"path": str(relpath), "content": content})

    if prompt and os.path.isfile(prompt):
        with open(prompt, "r", encoding="utf-8") as prompt_infile:
            data["prompt"] = prompt_infile.read()
    elif prompt:
        click.echo(f"Warning: Prompt file '{prompt}' does not exist. Skipping.")

    try:
        with open(output, "w", encoding="utf-8") as outfile:
            json.dump(data, outfile, indent=2)
        # Copy content to clipboard after writing the file
        pyperclip.copy(json.dumps(data))
        click.echo(f"Codebase folded into {output} and content copied to clipboard.")
    except IOError as e:
        click.echo(f"Error writing to {output}: {e}")
        raise

    console = Console()
    tree = get_folded_tree(files, cwd)
    if tree:
        console.print(tree)
