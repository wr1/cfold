"""Handle init command for cfold."""

import rich_click as click
from cfold.utils.instructions import load_instructions


@click.command()
@click.argument("output", default="start.txt")
@click.option(
   "--custom",
   "-c",
   default="Describe the purpose of your project here.",
   help="Custom instruction",
)
@click.option("--dialect", "-d", default="default", help="Instruction dialect (available: default, codeonly, test, doconly, latex)")
def init(output, custom, dialect):
   """Initialize a project template with LLM instructions."""
   common = load_instructions("common")
   instructions = load_instructions(dialect)
   with open(output, "w", encoding="utf-8") as outfile:
       outfile.write(common["prefix"] + "\n\n")
       outfile.write(instructions["prefix"] + "\n\n")
       outfile.write(f"{custom}\n")
   click.echo(f"Initialized project template in {output}")
