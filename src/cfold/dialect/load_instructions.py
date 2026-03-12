"""Load the boilerplate instructions and patterns for the specified dialect."""

from importlib import resources
from pathlib import Path
import yaml
from typing import List, Optional, Dict
from .collect_instructions import collect_instructions
from .collect_patterns import collect_patterns


def load_instructions(
    dialect: str = "default", directory: Optional[Path] = None
) -> tuple[List, List[str]]:
    """Load instructions and include patterns for the given dialect."""
    if directory is None:
        directory = Path.cwd()
    local_config = {}
    local_path = directory / ".foldrc"
    if local_path.exists():
        with local_path.open("r", encoding="utf-8") as f:
            local_config = yaml.safe_load(f) or {}
    try:
        with resources.files("cfold").joinpath("resources/prompts.yaml").open("r", encoding="utf-8") as f:
            default_config = yaml.safe_load(f)
    except Exception as e:
        raise RuntimeError(f"Failed to load default instructions: {e}")
    combined_config = {**default_config, **local_config}
    if dialect not in combined_config:
        raise ValueError(f"Dialect '{dialect}' not found")
    instructions_list = collect_instructions(combined_config, dialect)
    all_patterns = collect_patterns(combined_config, dialect)
    include_patterns = all_patterns.get("include", [])
    return instructions_list, include_patterns
