from pathlib import Path
import glob
from typing import List


def filter_files(include_patterns: List[str], cwd: Path, files: List[Path] | None = None) -> List[Path]:
    """Return files that match any include pattern."""
    if files is not None:
        filtered = [f for f in files if any(f.relative_to(cwd).match(p) for p in include_patterns)]
        return filtered
    matched = set()
    for pattern in include_patterns:
        for path_str in glob.glob(pattern, root_dir=str(cwd), recursive=True):
            path = cwd / path_str
            if path.is_file():
                matched.add(path)
    return list(matched)
