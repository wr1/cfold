"""Load instructions and patterns for specified dialect."""

from importlib import resources
from pathlib import Path
import yaml
from typing import List, Dict, Optional
from cfold.core.models import Instruction


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


def collect_patterns(
    config: Dict, dialect: str, processed: set = None, path: set = None
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


def load_instructions(
    dialect: str = "default", directory: Optional[Path] = None
) -> tuple[List[Instruction], Dict]:
    """Load the boilerplate instructions and patterns for the specified dialect from prompts.yaml as a list of Instruction."""
    if directory is None:
        directory = Path.cwd()
    local_config = {}
    local_path = directory / ".foldrc"
    if local_path.exists():
        with local_path.open("r", encoding="utf-8") as f:
            local_config = yaml.safe_load(f) or {}

    try:
        with (
            resources.files("cfold")
            .joinpath("resources/prompts.yaml")
            .open("r", encoding="utf-8")
        ) as f:
            default_config = yaml.safe_load(f)  # Use safe_load for security
    except Exception as e:
        raise RuntimeError(f"Failed to load default instructions: {e}")

    combined_config = {**default_config, **local_config}

    if dialect not in combined_config:
        raise ValueError(f"Dialect '{dialect}' not found in combined configurations")
    instructions_list = collect_instructions(combined_config, dialect)
    all_patterns = collect_patterns(combined_config, dialect)

    # Override with defaults for specific dialects
    if dialect in ("py", "pytest"):
        all_patterns["included_suffix"] = [".py", ".toml"]
    elif dialect == "doc":
        all_patterns["included_suffix"] = [".md", ".rst"]
    elif dialect == "typst":
        all_patterns["included_suffix"] = [".typ"]

    patterns = {
        "included": [
            f"*{pat}" for pat in all_patterns.get("included_suffix", [])
        ],  # Convert suffixes to fnmatch patterns
        "excluded": all_patterns.get("excluded", []),
        "included_dirs": all_patterns.get("included_dirs", []),
        "exclude_files": all_patterns.get("exclude", []),
    }
    return instructions_list, patterns


def get_available_dialects(directory: Optional[Path] = None) -> List[str]:
    """Get the list of available dialects from prompts.yaml and .foldrc."""
    if directory is None:
        directory = Path.cwd()
    local_config = {}
    local_path = directory / ".foldrc"
    if local_path.exists():
        with local_path.open("r", encoding="utf-8") as f:
            local_config = yaml.safe_load(f) or {}

    try:
        with (
            resources.files("cfold")
            .joinpath("resources/prompts.yaml")
            .open("r", encoding="utf-8")
        ) as f:
            default_config = yaml.safe_load(f)
    except Exception as e:
        raise RuntimeError(f"Failed to load dialects: {e}")

    combined_config = {**default_config, **local_config}
    return [k for k in combined_config.keys() if k != "common"]
