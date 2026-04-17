"""Load the boilerplate instructions and patterns for the specified dialect."""

from pathlib import Path
from typing import List, Optional

import yaml

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
        foldrc_dir = Path(__file__).parent.parent.parent.parent / "foldrc"
        default_config = {}
        for yaml_file in foldrc_dir.glob("*.yaml"):
            with yaml_file.open("r", encoding="utf-8") as f:
                data = yaml.safe_load(f) or {}
                default_config.update(data)
    except Exception as e:
        raise RuntimeError(f"Failed to load default instructions: {e}")
    combined_config = {**default_config, **local_config}
    if dialect not in combined_config:
        raise ValueError(f"Dialect '{dialect}' not found")
    instructions_list = collect_instructions(combined_config, dialect)
    all_patterns = collect_patterns(combined_config, dialect)
    include_patterns = all_patterns.get("include", [])
    return instructions_list, include_patterns
