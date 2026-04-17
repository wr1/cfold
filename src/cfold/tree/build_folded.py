import os
from pathlib import Path
from typing import List

from rich.tree import Tree

from .count_lines import count_lines
from .heat_color import heat_color


def build_folded_tree(files: List[Path], cwd: Path) -> Tree:
    """Generate a Rich Tree for folded files with percentages and heat colors."""
    line_counts = {os.path.relpath(str(f), str(cwd)): count_lines(f) for f in files}
    total_lines = sum(line_counts.values())
    dir_totals = {}
    for file_path_rel, lines in line_counts.items():
        parts = file_path_rel.split(os.sep)
        for i in range(1, len(parts)):
            dir_path = os.sep.join(parts[:i])
            dir_totals[dir_path] = dir_totals.get(dir_path, 0) + lines
    main_tree = Tree(f"Folded files tree (total lines: {total_lines})", guide_style="grey50")
    for file_path_rel in sorted(line_counts.keys()):
        parts = file_path_rel.split(os.sep)
        current_node = main_tree
        for i, part in enumerate(parts[:-1]):
            dir_path = os.sep.join(parts[: i + 1])
            subnodes = [
                node for node in current_node.children if node.label.startswith(f"[yellow]{part}/")
            ]
            if subnodes:
                current_node = subnodes[0]
            else:
                if dir_path in dir_totals:
                    dir_lines = dir_totals[dir_path]
                    percent = (dir_lines / total_lines) * 100 if total_lines > 0 else 0
                    color = heat_color(percent)
                    label = (
                        f"[yellow]{part}/[/yellow]"
                        f" ({dir_lines} lines, [{color}]{percent:.1f}%[/{color}])"
                    )
                    current_node = current_node.add(label)
                else:
                    current_node = current_node.add(f"[yellow]{part}/[/yellow]")
        file_name = parts[-1]
        if file_name.startswith("test_"):
            file_color = "blue"
        elif file_name.endswith(".md"):
            file_color = "red"
        elif file_name == "pyproject.toml":
            file_color = "orange"
        else:
            file_color = "green"
        current_node.add(f"[{file_color}]{file_name}[/{file_color}]")
    return main_tree
