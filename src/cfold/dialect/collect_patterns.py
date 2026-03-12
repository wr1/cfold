from typing import Dict, List, Set


def collect_patterns(
    config: Dict, dialect: str, processed: Set = None, path: Set = None
) -> Dict[str, List[str]]:
    """Collect include patterns for the dialect, handling included_suffix and included_dirs if include not present."""
    if processed is None:
        processed = set()
    if path is None:
        path = set()
    if dialect in processed:
        return {}
    if dialect in path:
        raise ValueError(f"Cycle detected in 'pre' for patterns in '{dialect}'")
    path.add(dialect)
    instr = config.get(dialect, {})
    patterns = {"include": []}
    if "include" in instr:
        patterns["include"] = instr["include"]
    else:
        include_list = []
        suffixes = instr.get("included_suffix", [])
        dirs = instr.get("included_dirs", [])
        for d in dirs:
            for s in suffixes:
                if d == ".":
                    include_list.append(f"**/*{s}")
                else:
                    include_list.append(f"{d}/**/*{s}")
        patterns["include"] = include_list
    path.remove(dialect)
    processed.add(dialect)
    return patterns
