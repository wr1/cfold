#!/usr/bin/env python3
import os
from pathlib import Path
import click
from cfold.utils.foldignore import load_foldignore, should_include_file
from cfold.utils.instructions import load_instructions
import re

EXCLUDED_DIRS = {".pytest_cache", "__pycache__", "build", "dist", ".egg-info", "venv"}
EXCLUDED_FILES = {".pyc"}


@click.group(
    context_settings={"help_option_names": ["-h", "--help"]},
    invoke_without_command=False,
)
def cli():
    """Fold code or docs tree into a single file with prompting for LLM interaction."""
    pass


@cli.command()
@click.argument("files", nargs=-1)
@click.option("--output", "-o", default="codefold.txt", help="Output file")
@click.option("--prompt", "-p", default=None, help="Prompt file to append")
@click.option("--dialect", "-d", default="default", help="Instruction dialect (available: default, codeonly, doconly, test, latex)")
def fold(files, output, prompt, dialect):
    """Fold files or directory into a single text file."""
    cwd = os.getcwd()
    common = load_instructions("common")
    instructions = load_instructions(dialect)
    included_suffixes = instructions["included_suffix"]

    print(cwd)

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
        # if files are provided, they don't need to have a specific suffix
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


@cli.command()
@click.argument("foldfile")
@click.option("--original-dir", "-i", help="Original project directory")
@click.option("--output-dir", "-o", help="Output directory")
def unfold(foldfile, original_dir, output_dir):
    """Unfold a modified fold file into a directory."""
    cwd = os.getcwd()
    output_dir = os.path.abspath(output_dir or cwd)
    instructions = load_instructions("default")
    included_suffixes = instructions["included_suffix"]

    with open(foldfile, "r", encoding="utf-8") as infile:
        content = infile.read().replace("CFOLD: ", "").replace("CFOLD:", "")
        sections = re.split(r"(# --- File: .+? ---)\n", content)[1:]
        if len(sections) % 2 != 0:
            click.echo("Warning: Malformed fold file - odd number of sections")
            return

        modified_files = {}
        for i in range(0, len(sections), 2):
            header = sections[i].strip()
            file_content = sections[i + 1].rstrip()
            filepath = header.replace("# --- File: ", "").replace(" ---", "").strip()
            if filepath.endswith(".md"):
                file_content = "\n".join(
                    line[3:] if line.startswith("MD:") else line
                    for line in file_content.splitlines()
                )
            modified_files[filepath] = file_content

    if os.path.exists(output_dir) and os.listdir(output_dir):
        click.echo(f"Merging into existing directory: {output_dir}")
    else:
        os.makedirs(output_dir, exist_ok=True)

    if original_dir and os.path.isdir(original_dir):
        click.echo(f"Merging with original codebase from {original_dir}")
        original_dir = os.path.abspath(original_dir)
        ignore_patterns = load_foldignore(original_dir)
        for dirpath, _, filenames in os.walk(original_dir):
            for filename in filenames:
                filepath = os.path.join(dirpath, filename)
                if should_include_file(
                    filepath, ignore_patterns, original_dir, included_suffixes
                ):
                    relpath = os.path.relpath(filepath, cwd)
                    dst = os.path.join(output_dir, relpath)
                    if relpath not in modified_files:
                        os.makedirs(os.path.dirname(dst), exist_ok=True)
                        if os.path.abspath(filepath) != os.path.abspath(dst):
                            shutil.copy2(filepath, dst)
                            click.echo(f"Copied unchanged file: {relpath}")
                    elif modified_files[relpath] == "# DELETE":
                        if os.path.exists(dst):
                            os.remove(dst)
                            click.echo(f"Deleted file: {relpath}")
                    else:
                        os.makedirs(os.path.dirname(dst), exist_ok=True)
                        with open(dst, "w", encoding="utf-8") as outfile:
                            outfile.write(modified_files[relpath] + "\n")
                        click.echo(f"Rewrote file: {relpath}")

        for filepath, file_content in modified_files.items():
            if file_content == "# DELETE":
                continue
            full_path = os.path.join(output_dir, filepath)
            if not os.path.exists(os.path.join(original_dir, filepath)):
                os.makedirs(os.path.dirname(full_path), exist_ok=True)
                with open(full_path, "w", encoding="utf-8") as outfile:
                    outfile.write(file_content + "\n")
                click.echo(f"Wrote new file: {filepath}")
    else:
        for filepath, file_content in modified_files.items():
            full_path = os.path.join(output_dir, filepath)
            if file_content == "# DELETE":
                if os.path.exists(full_path):
                    os.remove(full_path)
                    click.echo(f"Deleted file: {filepath}")
                continue
            os.makedirs(os.path.dirname(full_path), exist_ok=True)
            try:
                with open(full_path, "w", encoding="utf-8") as outfile:
                    outfile.write(file_content + "\n")
                click.echo(f"Wrote file: {filepath}")
            except Exception as e:
                click.echo(f"Error writing {filepath}: {e}")

    click.echo(f"Codebase unfolded into {output_dir}")


@cli.command()
@click.argument("output", default="start.txt")
@click.option(
    "--custom",
    "-c",
    default="Describe the purpose of your project here.",
    help="Custom instruction",
)
@click.option("--dialect", "-d", default="default", help="Instruction dialect")
def init(output, custom, dialect):
    """Initialize a project template with LLM instructions."""
    common = load_instructions("common")
    instructions = load_instructions(dialect)
    with open(output, "w", encoding="utf-8") as outfile:
        outfile.write(instructions["prefix"] + "\n\n")
        outfile.write(
            "# Project Setup Guidance:\n"
            "# Create a Poetry-managed Python project with:\n"
            "# - pyproject.toml: Define package metadata, dependencies, and scripts.\n"
            "# - CI: Add .github/workflows/ with .yml files for testing and publishing.\n"
            "# - MkDocs: Add docs/ directory with .md files and mkdocs.yml for documentation.\n"
            "# Example structure:\n"
            "#   my_project/pyproject.toml\n"
            "#   my_project/README.md\n"
            "#   my_project/src/<package>/__init__.py\n"
            "#   my_project/.github/workflows/test.yml\n"
            "#   my_project/docs/index.md\n"
            "#   my_project/mkdocs.yml\n\n"
            f"# Custom Instruction:\n{common['prefix']}\n\n\n{custom}\n"
        )
    click.echo(f"Initialized project template in {output}")


if __name__ == "__main__":
    cli()
