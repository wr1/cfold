"""Handle init command for cfold."""

import json
import rich_click as click
from rich.console import Console  # Added for colored output
from cfold.utils.instructions import load_instructions, get_available_dialects
from cfold.models import Codebase, Instruction


@click.command()
@click.pass_context
@click.option("--output", "-o", default="start.json", help="Output file")
@click.option(
    "--custom",
    "-c",
    default=None,
    help="Custom instruction",
)
@click.option(
    "--dialect",
    "-d",
    default="default",
    help="Instruction dialect (available: default, py, pytest, doc, typst)",
)
def init(ctx, output, custom, dialect):
    """Initialize a project template with LLM instructions."""
    try:
        instructions, _ = load_instructions(dialect)
    except ValueError:
        available = get_available_dialects()
        click.echo(f"Invalid dialect specified. Available dialects: {', '.join(available)}")
        ctx.exit(1)
    except Exception as e:
        raise click.ClickException(f"Error loading instructions: {str(e)}")
    data = Codebase(
        instructions=instructions,
        files=[],
    )
    if custom:
        data.instructions.append(Instruction(type="user", content=custom, name="custom"))
    with open(output, "w", encoding="utf-8") as outfile:
        json.dump(
            data.model_dump(exclude={"instructions": {"__all__": {"synopsis"}}}),
            outfile,
            indent=2,
        )
    console = Console()
    console.print(f"Initialized project template in [blue]{output}[/blue]")












