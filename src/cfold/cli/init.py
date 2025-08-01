"""Handle init command for cfold."""

import json
import rich_click as click
from cfold.utils.instructions import load_instructions
from cfold.models import Codebase, Instruction


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
    instructions, _ = load_instructions(dialect)
    data = Codebase(
        instructions=instructions,
        files=[],
    )
    if custom:
        data.instructions.append(Instruction(type="user", content=custom, name="custom"))
    with open(output, "w", encoding="utf-8") as outfile:
        json.dump(data.model_dump(), outfile, indent=2)
    click.echo(f"Initialized project template in {output}")






