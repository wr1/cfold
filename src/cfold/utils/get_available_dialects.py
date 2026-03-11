"""Get the list of available dialects from prompts.yaml and .foldrc."""

from importlib import resources
from pathlib import Path
import yaml
from typing import List, Optional


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
