"""Recursively collect instructions for the dialect."""

from typing import Dict, List, Set

from ..models.instruction import instruction


def collect_instructions(
    config: Dict, dialect: str, processed: Set = None, path: Set = None
) -> List[instruction]:
    """Recursively collect instructions, handling 'pre' dependencies without duplicates."""
    if processed is None:
        processed = set()
    if path is None:
        path = set()
    if dialect in processed:
        return []
    if dialect in path:
        raise ValueError(f"Cycle detected in 'pre' for dialect '{dialect}'")
    path.add(dialect)
    instr = config.get(dialect, {})
    instructions = []
    for pre_d in instr.get("pre", []):
        instructions.extend(collect_instructions(config, pre_d, processed, path))
    path.remove(dialect)
    processed.add(dialect)
    for i in instr.get("instructions", []):
        instructions.append(instruction(**i, name=dialect))
    return instructions
