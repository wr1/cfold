"""Handle init command for cfold."""

import json
import rich_click as click
from cfold.utils.instructions import load_instructions


@click.command()
@click.option("--output", "-o", default="start.txt", help="Output file")
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
    common = load_instructions("common")
    instructions = load_instructions(dialect)
    data = {
        "instructions": common["prefix"] + "\n\n" + instructions["prefix"],
        "files": [],
        "prompt": custom
    }
    with open(output, "w", encoding="utf-8") as outfile:
        json.dump(data, outfile, indent=2)
    click.echo(f"Initialized project template in {output}")

