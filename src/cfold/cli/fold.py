"""Handle folding command for cfold."""
import os
import click
from cfold.utils.instructions import load_instructions
from cfold.utils.foldignore import load_foldignore, should_include_file

@click.command()
@click.argument("files", nargs=-1)
@click.option("--output", "-o", default="codefold.txt", help="Output file")
@click.option("--prompt", "-p", default=None, help="Prompt file to append")
@click.option("--dialect", "-d", default="default", help="Instruction dialect")
def fold(files, output, prompt, dialect):
    """Fold files or directory into a single text file."""
    cwd = os.getcwd()
    common = load_instructions("common")
    instructions = load_instructions(dialect)
    included_suffixes = instructions["included_suffix"]

    if not files:
        directory = cwd
        ignore_patterns = load_foldignore(directory)
        files = []
        for dirpath, _, filenames in os.walk(directory):
            for filename in filenames:
                filepath = os.path.join(dirpath, filename)
                if should_include_file(
                    filepath, ignore_patterns, directory, included_suffixes
                ):
                    files.append(filepath)
    else:
        files = [os.path.abspath(f) for f in files if os.path.isfile(f)]

    if not files:
        click.echo("No valid files to fold.")
        return

    with open(output, "w", encoding="utf-8") as outfile:
        outfile.write(common["prefix"] + "\n\n")
        outfile.write(instructions["prefix"] + "\n\n")
        for filepath in files:
            relpath = os.path.relpath(filepath, cwd)
            outfile.write(f"# --- File: {relpath} ---\n")
            with open(filepath, "r", encoding="utf-8") as infile:
                content = infile.read()
                if filepath.endswith(".md"):
                    content = "\n".join(f"MD:{line}" for line in content.splitlines())
                outfile.write(content + "\n\n")
            if prompt and os.path.isfile(prompt):
                with open(prompt, "r", encoding="utf-8") as prompt_infile:
                    outfile.write("\n# Prompt:\n")
                    outfile.write(prompt_infile.read() + "\n")
            elif prompt:
                click.echo(f"Warning: Prompt file '{prompt}' does not exist. Skipping.")
    click.echo(f"Codebase folded into {output}")
