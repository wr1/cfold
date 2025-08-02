"""Load instructions and patterns for specified dialect."""

from importlib import resources
import yaml
from typing import List, Dict
from cfold.models import Instruction


def collect_instructions(
    config: Dict, dialect: str, processed: set = None, path: set = None
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

    instructions = []
    for pre_d in instr.get("pre", []):
        instructions.extend(collect_instructions(config, pre_d, processed, path))

    path.remove(dialect)
    processed.add(dialect)

    for i in instr.get("instructions", []):
        instructions.append(Instruction(**i, name=dialect))

    return instructions


def load_instructions(dialect: str = "default") -> tuple[List[Instruction], Dict]:
    """Load the boilerplate instructions and patterns for the specified dialect from prompts.yaml as a list of Instruction."""
    try:
        with resources.files("cfold").joinpath("resources/prompts.yaml").open(
            "r", encoding="utf-8"
        ) as f:
            config = yaml.safe_load(f)  # Use safe_load for security
        if dialect not in config:
            raise ValueError(f"Dialect '{dialect}' not found in prompts.yaml")
        instructions_list = collect_instructions(config, dialect)
        instr = config[dialect]
        patterns = {
            "included": [
                f"*{pat}" for pat in instr.get("included_suffix", [])
            ],  # Convert suffixes to fnmatch patterns
            "excluded": instr.get("excluded", []),
            "included_dirs": instr.get("included_dirs", []),
        }
        return instructions_list, patterns
    except Exception as e:
        raise RuntimeError(
            f"Failed to load instructions for dialect '{dialect}' from prompts.yaml: {e}"
        )


def get_available_dialects() -> List[str]:
    """Get the list of available dialects from prompts.yaml."""
    try:
        with resources.files("cfold").joinpath("resources/prompts.yaml").open(
            "r", encoding="utf-8"
        ) as f:
            config = yaml.safe_load(f)
        return [k for k in config.keys() if k != "common"]
    except Exception as e:
        raise RuntimeError(f"Failed to load dialects: {e}")


