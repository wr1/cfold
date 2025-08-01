"""Utilities for visualizing file trees using Rich Tree."""

import os
from rich.tree import Tree  # Import Rich Tree class


def get_folded_tree(files, cwd):
    """Generate a Rich Tree object for the folded files with dim styling."""
    main_tree = Tree("Folded files tree", guide_style="dim")  # Create the main Tree
    for file_path in sorted(set(os.path.relpath(f, cwd) for f in files)):
        parts = file_path.split(os.sep)
        current_node = main_tree
        for part in parts[:-1]:  # Traverse directories
            subnodes = [
                node for node in current_node.children if node.label == part + os.sep
            ]
            if subnodes:
                current_node = subnodes[0]
            else:
                new_node = current_node.add(
                    f"{part + os.sep}"
                )  # Add directory node with dim
                current_node = new_node
        if parts[-1].endswith(".py"):
            current_node.add(f"[green]{parts[-1]}[/green]")
        elif parts[-1].endswith(".tex") or parts[-1].endswith(".md"):
            current_node.add(f"[cyan]{parts[-1]}[/cyan]")
        elif parts[-1].endswith(".yml") or parts[-1].endswith(".toml"):
            current_node.add(f"[yellow]{parts[-1]}[/yellow]")
        else:
            current_node.add(f"{parts[-1]}")  # Add the file node with dim
    return main_tree  # Return the Rich Tree object



