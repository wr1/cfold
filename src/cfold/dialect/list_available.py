"""Get the list of available dialects."""

from importlib import resources
from pathlib import Path
import yaml
from typing import List, Optional
from loguru import logger


def list_available_dialects(directory: Optional[Path] = None) -> List[str]:
    """Get the list of available dialects from foldrc/*.yaml and .foldrc."""
    if directory is None:
        directory = Path.cwd()
    local_config = {}
    local_path = directory / ".foldrc"
    if local_path.exists():
        logger.info(f"Loading local dialects from {local_path}")
        with local_path.open("r", encoding="utf-8") as f:
            local_config = yaml.safe_load(f) or {}
    try:
        foldrc_dir = Path(__file__).parent.parent.parent / "foldrc"
        logger.info(f"Loading default dialects from {foldrc_dir}")
        default_config = {}
        for yaml_file in foldrc_dir.glob("*.yaml"):
            logger.info(f"Loading {yaml_file}")
            with yaml_file.open("r", encoding="utf-8") as f:
                data = yaml.safe_load(f) or {}
                default_config.update(data)
    except Exception as e:
        raise RuntimeError(f"Failed to load dialects: {e}")
    combined_config = {**default_config, **local_config}
    return [k for k in combined_config.keys() if k != "common"]
