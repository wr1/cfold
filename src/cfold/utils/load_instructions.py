"""Load the boilerplate instructions and patterns for the specified dialect from prompts.yaml as a list of Instruction."""

from importlib import resources
from pathlib import Path
import yaml
from typing import List, Optional, Dict
from .collect_instructions import collect_instructions
from .collect_patterns import collect_patterns


def load_instructions(
    dialect: str = "default", directory: Optional[Path] = None
) -> tuple[List, Dict]:
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
