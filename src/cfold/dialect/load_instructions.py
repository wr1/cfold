from pathlib import Path
from typing import Dict, List, Optional, Set

import yaml
from loguru import logger

from ..models.instruction import instruction


def _load_config(directory: Path) -> Dict:
    local_config = {}
    local_path = directory / ".foldrc"
    if local_path.exists():
        logger.info(f"Loading local dialects from {local_path}")
        with local_path.open("r", encoding="utf-8") as f:
            local_config = yaml.safe_load(f) or {}
    try:
        foldrc_dir = Path(__file__).parent.parent.parent.parent / "foldrc"
        logger.info(f"Loading default dialects from {foldrc_dir}")
        default_config = {}
        for yaml_file in foldrc_dir.glob("*.yaml"):
            logger.info(f"Loading {yaml_file}")
            with yaml_file.open("r", encoding="utf-8") as f:
                data = yaml.safe_load(f) or {}
                default_config.update(data)
    except Exception as e:
        raise RuntimeError(f"Failed to load dialects: {e}")
    return {**default_config, **local_config}


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


def collect_patterns(
    config: Dict, dialect: str, processed: Set = None, path: Set = None
) -> Dict[str, List[str]]:
    """Collect include patterns for the dialect.

    Falls back to building patterns from included_suffix/included_dirs if include not present.
    """
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


def list_available_dialects(directory: Optional[Path] = None) -> List[str]:
    """Get the list of available dialects from foldrc/*.yaml and .foldrc."""
    if directory is None:
        directory = Path.cwd()
    config = _load_config(directory)
    return [k for k in config.keys() if k != "common"]


def load_instructions(
    dialect: str = "default", directory: Optional[Path] = None
) -> tuple[List, List[str]]:
    """Load instructions and include patterns for the given dialect."""
    if directory is None:
        directory = Path.cwd()
    combined_config = _load_config(directory)
    if dialect not in combined_config:
        raise ValueError(f"Dialect '{dialect}' not found")
    instructions_list = collect_instructions(combined_config, dialect)
    all_patterns = collect_patterns(combined_config, dialect)
    include_patterns = all_patterns.get("include", [])
    return instructions_list, include_patterns
