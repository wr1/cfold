"""Main CLI for cfold using treeparse."""

import treeparse
from typing import List, Optional

from .fold import fold
from .unfold import unfold
from .rc import rc
from .view import view
from .add import add

app = treeparse.cli(
    name="cfold",
    help="Fold code or docs tree into a single file with prompting for LLM interaction.",
    max_width=120,
    show_types=True,
    show_defaults=True,
    line_connect=True,
)

fold_cmd = treeparse.command(
    name="fold",
    help="Fold files or directory into a single file and visualize the structure.",
    callback=fold,
    arguments=[
        treeparse.argument(
            name="files", arg_type=str, nargs="*", default=[], sort_key=0
        ),
    ],
    options=[
        treeparse.option(
            flags=["--output", "-o"],
            help="Output file",
            arg_type=str,
            default="codefold.json",
            sort_key=0,
        ),
        treeparse.option(
            flags=["--prompt", "-p"],
            help="Prompt file to append",
            arg_type=str,
            default=None,
            sort_key=1,
        ),
        treeparse.option(
            flags=["--dialect", "-d"],
            help="Instruction dialect (available: default, py, pytest, doc, typst)",
            arg_type=str,
            default="default",
            sort_key=2,
        ),
        treeparse.option(
            flags=["--bare", "-b"],
            help="Bare mode without boilerplate instructions",
            default=False,
            arg_type=bool,
            sort_key=3,
        ),
    ],
)
app.commands.append(fold_cmd)

unfold_cmd = treeparse.command(
    name="unfold",
    help="Unfold a modified fold file into a directory.",
    callback=unfold,
    arguments=[
        treeparse.argument(name="foldfile", arg_type=str, sort_key=0),
    ],
    options=[
        treeparse.option(
            flags=["--original-dir", "-i"],
            help="Original project directory",
            arg_type=str,
            default=None,
            sort_key=0,
        ),
        treeparse.option(
            flags=["--output-dir", "-o"],
            help="Output directory",
            arg_type=str,
            default=None,
            sort_key=1,
        ),
    ],
)
app.commands.append(unfold_cmd)

rc_cmd = treeparse.command(
    name="rc",
    help="Create or update .foldrc with a 'local' profile and set it as the default dialect.",
    callback=rc,
)
app.commands.append(rc_cmd)

view_cmd = treeparse.command(
    name="view",
    help="View the prompts and files in a fold file.",
    callback=view,
    arguments=[
        treeparse.argument(name="foldfile", arg_type=str, default="codefold.json", sort_key=0),
    ],
)
app.commands.append(view_cmd)

add_cmd = treeparse.command(
    name="add",
    help="Add files to an existing cfold file.",
    callback=add,
    arguments=[
        treeparse.argument(
            name="files", arg_type=str, nargs="*", default=[], sort_key=0
        ),
    ],
    options=[
        treeparse.option(
            flags=["--foldfile", "-f"],
            help="Cfold file to add to",
            arg_type=str,
            default="codefold.json",
            sort_key=0,
        ),
    ],
)
app.commands.append(add_cmd)


def main():
    app.run()


if __name__ == "__main__":
    main()
