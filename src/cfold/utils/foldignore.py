from pathlib import Path
import fnmatch
import os


def should_include_file(
    filepath,
    root_dir=None,
    included_patterns=None,
    excluded_patterns=None,
    included_dirs=None,
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

    relpath_norm = relpath.replace(os.sep, "/")
    if included_dirs:
        is_in_included_dir = any(
            relpath_norm.startswith(d.replace(os.sep, "/") + "/") for d in included_dirs
        )
        is_root_file = "." in included_dirs and "/" not in relpath_norm
        if not (is_in_included_dir or is_root_file):
            return False

    EXCLUDED_PATTERNS = [
        "*.egg-info/*",
        ".*rc",
        "*.txt",
        "*.json",
        "build/*",
        "dist/*",
        ".venv/*",
        # "example*",
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
    return True
