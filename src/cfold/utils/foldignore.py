from pathlib import Path
import fnmatch
import os


def load_foldignore(directory):
    """Load and parse .foldignore file if it exists."""
    print(f"Loading .foldignore from {directory}")
    ignore_file = Path(directory) / ".foldignore"
    ignore_patterns = []
    if ignore_file.exists():
        with open(ignore_file, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#"):
                    ignore_patterns.append(line)
    return ignore_patterns


def should_include_file(filepath, ignore_patterns=None, root_dir=None, suffixes=None):
    """Check if a file should be included based on extension, exclusion rules, and .foldignore patterns."""
    EXCLUDED_DIRS = {
        ".pytest_cache",
        "__pycache__",
        "build",
        "dist",
        ".egg-info",
        "venv",
        ".venv",
        "node_modules",  # Added to ignore common directories as per request
    }
    EXCLUDED_FILES = {".pyc"}

    path = Path(filepath)
    if root_dir:
        relpath = os.path.relpath(filepath, root_dir)
    else:
        relpath = str(path)
    if suffixes and path.suffix not in suffixes:
        return False
    if any(part in EXCLUDED_DIRS for part in path.parts):
        return False
    if path.suffix in EXCLUDED_FILES:
        return False
    if ignore_patterns:
        for pattern in ignore_patterns:
            if fnmatch.fnmatch(relpath, pattern):
                return False
    return True
