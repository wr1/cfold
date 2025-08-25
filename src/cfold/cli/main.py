"""Main CLI for cfold using treeparse."""

import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent.parent / "treeparse" / "src"))

from treeparse import cli, command, argument, option

from .fold import fold
from .unfold import unfold
from .rc import rc

app = cli(
    name="cfold",
    help="Fold code or docs tree into a single file with prompting for LLM interaction.",
    max_width=120,
    show_types=True,
    show_defaults=True,
    line_connect=True,
)

fold_cmd = command(
    name="fold",
    help="Fold files or directory into a single text file and visualize the structure.",
    callback=fold,
    arguments=[
        argument(name="files", arg_type=str, nargs="*", default=[], sort_key=0),
    ],
    options=[
        option(
            flags=["--output", "-o"],
            help="Output file",
            arg_type=str,
            default="codefold.json",
            sort_key=0,
        ),
        option(
            flags=["--prompt", "-p"],
            help="Prompt file to append",
            arg_type=str,
            default=None,
            sort_key=1,
        ),
        option(
            flags=["--dialect", "-d"],
            help="Instruction dialect (available: default, py, pytest, doc, typst)",
            arg_type=str,
            default="default",
            sort_key=2,
        ),
        option(
            flags=["--bare", "-b"],
            is_flag=True,
            help="Bare mode without boilerplate instructions",
            sort_key=3,
        ),
    ],
)
app.commands.append(fold_cmd)

unfold_cmd = command(
    name="unfold",
    help="Unfold a modified fold file into a directory.",
    callback=unfold,
    arguments=[
        argument(name="foldfile", arg_type=str, sort_key=0),
    ],
    options=[
        option(
            flags=["--original-dir", "-i"],
            help="Original project directory",
            arg_type=str,
            default=None,
            sort_key=0,
        ),
        option(
            flags=["--output-dir", "-o"],
            help="Output directory",
            arg_type=str,
            default=None,
            sort_key=1,
        ),
    ],
)
app.commands.append(unfold_cmd)

rc_cmd = command(
    name="rc",
    help="Create or update .foldrc with a 'local' profile and set it as the default dialect.",
    callback=rc,
)
app.commands.append(rc_cmd)


def main():
    app.run()


if __name__ == "__main__":
    main()
