"""Handle unfolding command for cfold."""
import os
import shutil
import re
import click
from rich.console import Console
from rich.tree import Tree
from rich.text import Text
from cfold.utils.instructions import load_instructions
from cfold.utils.foldignore import load_foldignore, should_include_file
from cfold.utils.references import update_references

@click.command()
@click.argument("foldfile")
@click.option("--original-dir", "-i", help="Original project directory")
@click.option("--output-dir", "-o", help="Output directory")
def unfold(foldfile, original_dir, output_dir):
    """Unfold a modified fold file into a directory."""
    console = Console()
    cwd = os.getcwd()
    output_dir = os.path.abspath(output_dir or cwd)
    instructions = load_instructions("default")
    included_suffixes = instructions["included_suffix"]

    with open(foldfile, "r", encoding="utf-8") as infile:
        content = infile.read().replace("CF"+"OLD: ", "").replace("CF"+"OLD:", "")
        sections = re.split(r"(# --- File: .+? ---)\n", content)[1:]
        if len(sections) % 2 != 0:
            console.print("[yellow]Warning: Malformed fold file - odd number of sections[/yellow]")
            return

        modified_files = {}
        for i in range(0, len(sections), 2):
            header = sections[i].strip()
            file_content = sections[i + 1].rstrip()
            filepath = header.replace("# --- File: ", "").replace(" ---", "").strip()
            if filepath.endswith(".md"):
                file_content = "\n".join(
                    line[3:] if line.startswith("MD:") else line
                    for line in file_content.splitlines()
                )
            modified_files[filepath] = file_content

    if os.path.exists(output_dir) and os.listdir(output_dir):
        console.print(f"[dim]Merging into existing directory: {output_dir}[/dim]")
    else:
        os.makedirs(output_dir, exist_ok=True)

    added_files = []
    deleted_files = []
    modified_files_list = []

    if original_dir and os.path.isdir(original_dir):
        original_dir = os.path.abspath(original_dir)
        ignore_patterns = load_foldignore(original_dir)
        for dirpath, _, filenames in os.walk(original_dir):
            for filename in filenames:
                filepath = os.path.join(dirpath, filename)
                if should_include_file(
                    filepath, ignore_patterns, original_dir, included_suffixes
                ):
                    relpath = os.path.relpath(filepath, cwd)
                    dst = os.path.join(output_dir, relpath)
                    if relpath not in modified_files:
                        os.makedirs(os.path.dirname(dst), exist_ok=True)
                        if os.path.abspath(filepath) != os.path.abspath(dst):
                            shutil.copy2(filepath, dst)
                            added_files.append(relpath)
                    elif modified_files[relpath] == "# DELETE":
                        if os.path.exists(dst):
                            os.remove(dst)
                            deleted_files.append(relpath)
                    else:
                        os.makedirs(os.path.dirname(dst), exist_ok=True)
                        with open(dst, "w", encoding="utf-8") as outfile:
                            outfile.write(modified_files[relpath] + "\n")
                        modified_files_list.append(relpath)

        for filepath, file_content in modified_files.items():
            if file_content == "# DELETE":
                continue  # Already handled
            full_path = os.path.join(output_dir, filepath)
            if not os.path.exists(os.path.join(original_dir, filepath)):
                os.makedirs(os.path.dirname(full_path), exist_ok=True)
                with open(full_path, "w", encoding="utf-8") as outfile:
                    outfile.write(file_content + "\n")
                added_files.append(filepath)
    else:
        for filepath, file_content in modified_files.items():
            full_path = os.path.join(output_dir, filepath)
            if file_content == "# DELETE":
                if os.path.exists(full_path):
                    os.remove(full_path)
                    deleted_files.append(filepath)
                continue
            os.makedirs(os.path.dirname(full_path), exist_ok=True)
            with open(full_path, "w", encoding="utf-8") as outfile:
                outfile.write(file_content + "\n")
            added_files.append(filepath)

    # Output summary tree
    tree = Tree(f"[bold dim]Operations in[/bold dim] [blue]{output_dir}[/blue]", guide_style="dim")
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
