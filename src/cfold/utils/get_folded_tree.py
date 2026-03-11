"""Generate a Rich Tree object for the folded files with dim styling and percentages for all directories."""

import os
from rich.tree import Tree
from pathlib import Path
from typing import List
from .count_lines import count_lines
from .get_heat_color import get_heat_color


def get_folded_tree(files: List[Path], cwd: Path) -> Tree:
    """Generate a Rich Tree object for the folded files with dim styling and percentages for all directories."""
    # Compute line counts for all files
    line_counts = {os.path.relpath(str(f), str(cwd)): count_lines(f) for f in files}
    total_lines = sum(line_counts.values())

    main_tree = Tree(
        f"Folded files tree (total lines: {total_lines})", guide_style="dim"
    )  # Create the main Tree

    # Build tree
    for file_path_rel in sorted(line_counts.keys()):
        parts = file_path_rel.split(os.sep)
        current_node = main_tree
        for part in parts[:-1]:
            subnodes = [
                node for node in current_node.children if node.label == part + "/"
            ]
            if subnodes:
                current_node = subnodes[0]
            else:
                current_node = current_node.add(part + "/")
        # Add file
        if parts[-1].endswith(".py"):
            current_node.add(f"[green]{parts[-1]}[/green]")
        elif parts[-1].endswith(".tex") or parts[-1].endswith(".md"):
            current_node.add(f"[cyan]{parts[-1]}[/cyan]")
        elif parts[-1].endswith(".yml") or parts[-1].endswith(".toml"):
            current_node.add(f"[yellow]{parts[-1]}[/yellow]")
        else:
            current_node.add(f"{parts[-1]}")

    # Calculate directory lines
    dir_lines = {}

    def calc_dir_lines(node, rel_path):
        if not node.children:
            return 0
        lines = 0
        for child in node.children:
            if child.children:  # dir
                dir_name = child.label.rstrip("/")
                child_rel = rel_path + dir_name + "/"
                child_lines = calc_dir_lines(child, child_rel)
                dir_lines[child_rel.rstrip("/")] = child_lines
                lines += child_lines
            else:  # file
                file_label = child.label
                file_name = file_label
                if file_name.startswith("[green]"):
                    file_name = file_name[7:-8]
                elif file_name.startswith("[cyan]"):
                    file_name = file_name[7:-8]
                elif file_name.startswith("[yellow]"):
                    file_name = file_name[7:-8]
                full_path = rel_path + file_name
                lines += line_counts.get(full_path, 0)
        return lines

    calc_dir_lines(main_tree, "")

    # Update directory labels with percentages
    def update_dir_labels(node, rel_path):
        if node.children and node.label.endswith("/"):
            dir_rel = rel_path.rstrip("/")
            lines = dir_lines.get(dir_rel, 0)
            percent = (lines / total_lines * 100) if total_lines > 0 else 0
            color = get_heat_color(percent)
            percent_str = f"([{color}]{percent:.1f}%[/{color}])"
            node.label = node.label + percent_str
        for child in node.children:
            if child.children:
                child_dir_name = child.label.rstrip("/")
                child_rel_path = rel_path + child_dir_name + "/"
                update_dir_labels(child, child_rel_path)

    update_dir_labels(main_tree, "")

    return main_tree  # Return the Rich Tree object
