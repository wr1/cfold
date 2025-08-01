"""Main CLI group for cfold. Available dialects: default, codeonly, test, doconly, latex."""

import rich_click as click  # Replaced for Rich-styled help
from .fold import fold as fold_command
from .unfold import unfold as unfold_command
from .init import init as init_command


@click.group(
   context_settings={"help_option_names": ["-h", "--help"]},
   invoke_without_command=False,
)
def cli():
   """Fold code or docs tree into a single file with prompting for LLM interaction."""
   pass


cli.add_command(fold_command, name="fold")
cli.add_command(unfold_command, name="unfold")
cli.add_command(init_command, name="init")

if __name__ == "__main__":
   cli()

