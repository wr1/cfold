"""Handle init command for cfold."""
import click
from cfold.utils.instructions import load_instructions  # Assuming this is needed

@click.command()
@click.argument("output", default="start.txt")
@click.option("--custom", "-c", default="Describe the purpose of your project here.", help="Custom instruction")
@click.option("--dialect", "-d", default="default", help="Instruction dialect")
def init(output, custom, dialect):
    """Initialize a project template with LLM instructions."""
    # Implementation would go here; original code not fully provided, so assuming it's copied over.
    common = load_instructions("common")
    instructions = load_instructions(dialect)
    with open(output, "w", encoding="utf-8") as outfile:
        outfile.write(instructions["prefix"] + "\n\n")
        outfile.write(
            f"{common['prefix']}\n\n\n{custom}\n"
        )
    click.echo(f"Initialized project template in {output}")
