"""Handle init command for cfold."""

import json
import rich_click as click
from cfold.utils.instructions import load_instructions
from cfold.models import Codebase


@click.command()
@click.option("--output", "-o", default="start.json", help="Output file")
@click.option(
    "--custom",
    "-c",
    default="Describe the purpose of your project here.",
    help="Custom instruction",
)
@click.option(
    "--dialect",
    "-d",
    default="default",
    help="Instruction dialect (available: default, codeonly, test, doconly, latex, typst)",
)
def init(output, custom, dialect):
    """Initialize a project template with LLM instructions."""
    common_system, instructions = load_instructions(dialect)
    data = Codebase(
        system=common_system + "\n\n" + instructions.get("system", ""),
        user=instructions.get("user", ""),
        assistant=instructions.get("assistant", ""),
        files=[],
    )
    if custom:
        if data.user:
            data.user += "\n\n" + custom
        else:
            data.user = custom
    with open(output, "w", encoding="utf-8") as outfile:
        json.dump(data.model_dump(), outfile, indent=2)
    click.echo(f"Initialized project template in {output}")



