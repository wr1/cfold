"""Apply all changes from a folded file to the target directory."""

from pathlib import Path
import shutil
from rich.console import Console
from rich.tree import Tree
from ..models.codebase import codebase


def apply_changes(
    data: codebase, output_dir: Path, original_dir: Path | None = None
) -> None:
    """Apply adds, modifies, and deletes."""
    console = Console()
    if original_dir:
        shutil.copytree(original_dir, output_dir, dirs_exist_ok=True)
    added = []
    deleted = []
    modified = []
    for entry in data.files:
        full_path = output_dir / entry.path
        full_path.parent.mkdir(parents=True, exist_ok=True)
        if entry.delete:
            if full_path.exists() and full_path.resolve().is_relative_to(
                output_dir.resolve()
            ):
                full_path.unlink()
                deleted.append(entry.path)
        else:
            full_path.write_text(entry.content or "", encoding="utf-8")
            if original_dir and (original_dir / entry.path).exists():
                modified.append(entry.path)
            else:
                added.append(entry.path)
    operations_tree = Tree(f"Operations in {output_dir}")
    if added:
        added_branch = operations_tree.add("Added files")
        for f in added:
            added_branch.add(f"[green]{f}[/green]")
    if modified:
        modified_branch = operations_tree.add("Modified files")
        for f in modified:
            modified_branch.add(f"[yellow]{f}[/yellow]")
    if deleted:
        deleted_branch = operations_tree.add("Deleted files")
        for f in deleted:
            deleted_branch.add(f"[red]{f}[/red]")
    console.print(operations_tree)
