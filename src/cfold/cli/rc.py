"""Handle rc command for cfold."""

from pathlib import Path
import yaml
from rich.console import Console


def rc():
    """Create or update .foldrc with a 'local' profile."""
    cwd = Path.cwd()
    foldrc_path = cwd / ".foldrc"
    config = {}
    if foldrc_path.exists():
        with foldrc_path.open("r", encoding="utf-8") as f:
            config = yaml.safe_load(f) or {}
    if "local" not in config:
        config["local"] = {"pre": ["py"], "instructions": [{"type": "user", "synopsis": "local focus", "content": "Focus on brief and modular code."}], "included_suffix": [".py", ".toml"]}
    config["default_dialect"] = "local"
    with foldrc_path.open("w", encoding="utf-8") as f:
        yaml.safe_dump(config, f, default_flow_style=False)
    Console().print("[green].foldrc created/updated with 'local' as default dialect.[/green]")
