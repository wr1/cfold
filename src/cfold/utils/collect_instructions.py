"""Recursively collect instructions for the dialect, handling 'pre' dependencies without duplicates."""

from typing import List, Dict, Set
from cfold.core.instruction import Instruction


def collect_instructions(
    config: Dict, dialect: str, processed: Set = None, path: Set = None
) -> List[Instruction]:
    """Recursively collect instructions for the dialect, handling 'pre' dependencies without duplicates."""
    if processed is None:
        processed = set()
    if path is None:
        path = set()

    if dialect in processed:
        return []
    if dialect in path:
        raise ValueError(f"Cycle detected in 'pre' for dialect '{dialect}'")

    path.add(dialect)
    instr = config.get(dialect)
    if instr is None:
        path.remove(dialect)
        return []
    if not isinstance(instr, dict):
        raise ValueError(
            f"Dialect '{dialect}' config must be a dictionary, got {type(instr).__name__}"
        )

    instructions = []
    for pre_d in instr.get("pre", []):
        instructions.extend(collect_instructions(config, pre_d, processed, path))

    path.remove(dialect)
    processed.add(dialect)

    for i in instr.get("instructions", []):
        instructions.append(Instruction(**i, name=dialect))

    return instructions
