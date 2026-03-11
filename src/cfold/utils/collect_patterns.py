"""Recursively collect patterns for the dialect, handling 'pre' dependencies."""

from typing import Dict, List, Set


def collect_patterns(
    config: Dict, dialect: str, processed: Set = None, path: Set = None
) -> Dict[str, List[str]]:
    """Recursively collect patterns for the dialect, handling 'pre' dependencies."""
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

    patterns = {
        "included_suffix": [],
        "excluded": [],
        "included_dirs": [],
        "exclude": [],
    }

    for pre_d in instr.get("pre", []):
        pre_patterns = collect_patterns(config, pre_d, processed, path)
        for key in patterns:
            patterns[key].extend(pre_patterns.get(key, []))

    for key in patterns:
        patterns[key].extend(instr.get(key, []))

    path.remove(dialect)
    processed.add(dialect)
    return patterns
