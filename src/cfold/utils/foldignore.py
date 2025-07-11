from pathlib import Path
import fnmatch
import os


def load_foldignore(directory):
    """Load and parse .foldignore file if it exists."""
    ignore_file = Path(directory) / ".foldignore"
    ignore_patterns = []
    if ignore_file.exists():
        with open(ignore_file, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#"):
                    ignore_patterns.append(line)
    return ignore_patterns


def should_include_file(
    filepath,
    ignore_patterns=None,
    root_dir=None,
    included_patterns=None,
    excluded_patterns=None,
):
    """Check if a file should be included based on patterns."""
    EXCLUDED_DIRS = {
        ".pytest_cache",
        "__pycache__",
        "build",
        "dist",
        ".egg-info",
        "venv",
        ".venv",
        ".ruff_cache",
        ".git",
        "node_modules",  # Added to ignore common directories
    }
    EXCLUDED_FILES = {".pyc", ".egg-info"}

    path = Path(filepath)
    if root_dir:
        relpath = os.path.relpath(filepath, root_dir)
    else:
        relpath = str(path)

    EXCLUDED_PATTERNS = [
        "*.egg-info/*",
        ".*rc",
        "*.txt",
        "*.json",
        "build/*",
        "dist/*",
        ".venv/*",
        "example*",
        "htmlcov/*",
        "*png",
        "*vtu",
        "*xdmf",
        "*data/*",
        "*log",
        ".*",
        "*sh",
    ]

    if excluded_patterns is None:
        excluded_patterns = []
    for i in EXCLUDED_PATTERNS:
        if i not in excluded_patterns:
            excluded_patterns.append(i)

    if any(part in EXCLUDED_DIRS for part in path.parts):
        return False
    if path.suffix in EXCLUDED_FILES:
        return False

    if included_patterns and not any(
        fnmatch.fnmatch(relpath, pattern) for pattern in included_patterns
    ):
        return False
    if excluded_patterns and any(
        fnmatch.fnmatch(relpath, pattern) for pattern in excluded_patterns
    ):
        return False
    if ignore_patterns and any(
        fnmatch.fnmatch(relpath, pattern) for pattern in ignore_patterns
    ):
        return False
    return True
