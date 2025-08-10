"""Handle rc command for cfold."""

import os
from pathlib import Path
import yaml
import rich_click as click
from rich.console import Console


@click.command()
def rc():
    """Create or update .foldrc with a 'local' profile and set it as the default dialect."""
    cwd = Path.cwd()
    foldrc_path = cwd / ".foldrc"
    config = {}

    if foldrc_path.exists():
        with foldrc_path.open("r", encoding="utf-8") as f:
            config = yaml.safe_load(f) or {}

    # Add or update 'local' profile, inheriting from 'py'
    if "local" not in config:
        config["local"] = {
            "pre": ["py"],
            "instructions": [
                {
                    "type": "user",
                    "synopsis": "local focus",
                    "content": "Focus on brief and modular code."
                }
            ],
            "included_suffix": [".py", ".toml"],
        }

    # Set default_dialect to 'local'
    config["default_dialect"] = "local"

    with foldrc_path.open("w", encoding="utf-8") as f:
        yaml.safe_dump(config, f, default_flow_style=False)

    console = Console()
    console.print(f"[green].foldrc created/updated with 'local' as default dialect.[/green]")





