"""Count lines in a file."""

from pathlib import Path


def count_lines(file_path: Path) -> int:
    """Count lines in a file."""
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return sum(1 for _ in f)
    except Exception:
        return 0
