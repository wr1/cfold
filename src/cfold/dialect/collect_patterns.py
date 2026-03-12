from typing import Dict, List, Set


def collect_patterns(config: Dict, dialect: str, processed: Set = None, path: Set = None) -> Dict[str, List[str]]:
    """Collect include patterns for the dialect, ignoring pre for patterns."""
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
    own = instr.get("include", [])
    if own:
        patterns["include"] = own
    path.remove(dialect)
    processed.add(dialect)
    return patterns
