"""Handle unfolding command for cfold."""

import os
import shutil
import json
import rich_click as click  # Replaced for Rich-styled help
from rich.console import Console
from rich.tree import Tree
from pathlib import Path
from cfold.utils.foldignore import should_include_file
from cfold.models import Codebase  # Added for Pydantic model


@click.command()
@click.argument("foldfile")
@click.option("--original-dir", "-i", help="Original project directory")
@click.option("--output-dir", "-o", help="Output directory")
def unfold(foldfile, original_dir, output_dir):
    """Unfold a modified fold file into a directory."""
    console = Console()
    cwd = os.getcwd()
    output_dir = os.path.abspath(output_dir or cwd)
    output_path = Path(output_dir).resolve()
    # Note: included_patterns etc. seem unused in unfold; if needed, adjust

    with open(foldfile, "r", encoding="utf-8") as infile:
        raw_data = json.load(infile)
        data = Codebase.model_validate(raw_data)

    modified_files = {f.path: f for f in data.files}

    if os.path.exists(output_dir) and os.listdir(output_dir):
        console.print(f"[dim]Merging into existing directory: {output_dir}[/dim]")
    else:
        os.makedirs(output_dir, exist_ok=True)

    added_files = []
    deleted_files = []
    modified_files_list = []

    if original_dir and os.path.isdir(original_dir):
        original_dir = os.path.abspath(original_dir)
        for dirpath, _, filenames in os.walk(original_dir):
            for filename in filenames:
                filepath = os.path.join(dirpath, filename)
                if should_include_file(
                    filepath,
                    original_dir,
                    [],  # included_patterns empty or adjust
                    [],  # excluded_patterns
                    [],  # included_dirs
                ):
                    relpath = os.path.relpath(
                        filepath, original_dir
                    )  # Changed to relpath from original_dir
                    dst = os.path.join(output_dir, relpath)
                    if relpath in modified_files:
                        entry = modified_files[relpath]
                        if entry.delete:
                            if os.path.exists(dst):
                                os.remove(dst)
                            deleted_files.append(relpath)
                        else:
                            os.makedirs(os.path.dirname(dst), exist_ok=True)
                            with open(dst, "w", encoding="utf-8") as outfile:
                                outfile.write(entry.content + "\n")
                            modified_files_list.append(relpath)
                    else:
                        os.makedirs(os.path.dirname(dst), exist_ok=True)
                        if os.path.abspath(filepath) != os.path.abspath(dst):
                            shutil.copy2(filepath, dst)
                            added_files.append(relpath)

        for path, entry in modified_files.items():
            original_path = os.path.join(original_dir, path)
            if os.path.exists(original_path):
                continue  # Already handled
            if entry.delete:
                continue  # Skip deleting non-existing
            full_path = os.path.join(output_dir, path)
            resolved_path = Path(full_path).resolve()
            if not resolved_path.is_relative_to(output_path):
                console.print(
                    f"[yellow]Skipping addition outside output dir: {path}[/yellow]"
                )
                continue
            os.makedirs(os.path.dirname(full_path), exist_ok=True)
            with open(full_path, "w", encoding="utf-8") as outfile:
                outfile.write(entry.content + "\n")
            added_files.append(path)
    else:
        for path, entry in modified_files.items():
            full_path = os.path.join(output_dir, path)
            resolved_path = Path(full_path).resolve()
            if not resolved_path.is_relative_to(output_path):
                console.print(
                    f"[yellow]Skipping operation outside output dir: {path}[/yellow]"
                )
                continue
            if entry.delete:
                if os.path.exists(full_path):
                    os.remove(full_path)
                    deleted_files.append(path)
                continue
            os.makedirs(os.path.dirname(full_path), exist_ok=True)
            with open(full_path, "w", encoding="utf-8") as outfile:
                outfile.write(entry.content + "\n")
            added_files.append(path)

    # Output summary tree
    tree = Tree(
        f"[bold dim]Operations in[/bold dim] [blue]{output_dir}[/blue]",
        guide_style="dim",
    )
    if added_files:
        added_node = tree.add("[green]Added files[/green]")
        for file in added_files:
            added_node.add("[dim]" + file + "[/dim]")
    if deleted_files:
        deleted_node = tree.add("[red]Deleted files[/red]")
        for file in deleted_files:
            deleted_node.add("[dim]" + file + "[/dim]")
    if modified_files_list:
        modified_node = tree.add("[yellow]Modified files[/yellow]")
        for file in modified_files_list:
            modified_node.add("[dim]" + file + "[/dim]")
    console.print(tree)
    console.print(f"[bold dim]Codebase unfolded into {output_dir}[/bold dim]")
