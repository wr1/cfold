#!/usr/bin/env python3
import os
import argparse
import shutil
import re
from pathlib import Path
from importlib import resources
from cfold.utils.foldignore import load_foldignore, should_include_file
from cfold.utils.instructions import load_instructions

# Define file patterns to exclude
EXCLUDED_DIRS = {".pytest_cache", "__pycache__", "build", "dist", ".egg-info", "venv"}
EXCLUDED_FILES = {".pyc"}


def fold(files=None, output="codefold.txt", prompt_file=None, dialect="default"):
    """Wrap specified files or a directory into a single file with LLM instructions and optional prompt, using paths relative to CWD."""
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
        files = [
            os.path.abspath(f)
            for f in files
            if os.path.isfile(f) and Path(f).suffix in included_suffixes
        ]

    if not files:
        print("No valid files to fold.")
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
        if prompt_file and os.path.isfile(prompt_file):
            with open(prompt_file, "r", encoding="utf-8") as prompt_infile:
                outfile.write("\n# Prompt:\n")
                outfile.write(prompt_infile.read())
                outfile.write("\n")
        elif prompt_file:
            print(f"Warning: Prompt file '{prompt_file}' does not exist. Skipping.")
    print(f"Codebase folded into {output}")


def unfold(fold_file, original_dir=None, output_dir=None):
    """Unfold a modified fold file with support for deletes and full rewrites, using paths relative to CWD."""
    cwd = os.getcwd()
    output_dir = os.path.abspath(output_dir or cwd)
    instructions = load_instructions(
        "default"
    )  # Use default dialect for suffix filtering
    included_suffixes = instructions["included_suffix"]

    with open(fold_file, "r", encoding="utf-8") as infile:
        # hack to deal with grok sometimes not rendering as code block
        content = infile.read().replace("CFOLD: ", "").replace("CFOLD:", "")
        sections = re.split(r"(# --- File: .+? ---)\n", content)[1:]
        if len(sections) % 2 != 0:
            print("Warning: Malformed fold file - odd number of sections")
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
        print(f"Merging into existing directory: {output_dir}")
    else:
        os.makedirs(output_dir, exist_ok=True)

    if original_dir and os.path.isdir(original_dir):
        print(f"Merging with original codebase from {original_dir}")
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
                            print(f"Copied unchanged file: {relpath}")
                    elif modified_files[relpath] == "# DELETE":
                        if os.path.exists(dst):
                            os.remove(dst)
                            print(f"Deleted file: {relpath}")
                    else:
                        os.makedirs(os.path.dirname(dst), exist_ok=True)
                        with open(dst, "w", encoding="utf-8") as outfile:
                            outfile.write(modified_files[relpath] + "\n")
                        print(f"Rewrote file: {relpath}")

        for filepath, file_content in modified_files.items():
            if file_content == "# DELETE":
                continue
            full_path = os.path.join(output_dir, filepath)
            if not os.path.exists(os.path.join(original_dir, filepath)):
                os.makedirs(os.path.dirname(full_path), exist_ok=True)
                with open(full_path, "w", encoding="utf-8") as outfile:
                    outfile.write(file_content + "\n")
                print(f"Wrote new file: {filepath}")
    else:
        for filepath, file_content in modified_files.items():
            full_path = os.path.join(output_dir, filepath)
            if file_content == "# DELETE":
                if os.path.exists(full_path):
                    os.remove(full_path)
                    print(f"Deleted file: {filepath}")
                continue
            os.makedirs(os.path.dirname(full_path), exist_ok=True)
            try:
                with open(full_path, "w", encoding="utf-8") as outfile:
                    outfile.write(file_content + "\n")
                print(f"Wrote file: {filepath}")
            except Exception as e:
                print(f"Error writing {filepath}: {e}")

    print(f"Codebase unfolded into {output_dir}")


def init(output="start.txt", custom_instruction="", dialect="default"):
    """Create an initial .txt file with LLM instructions for project setup."""
    common = load_instructions("common")
    instructions = load_instructions(dialect)
    with open(output, "w", encoding="utf-8") as outfile:
        outfile.write(instructions["prefix"] + "\n\n")
        outfile.write(
            "# Project Setup Guidance:\n"
            "# Create a Poetry-managed Python project with:\n"
            "# - pyproject.toml: Define package metadata, dependencies, and scripts.\n"
            "# - CI: Add .github/workflows/ with .yml files for testing and publishing (e.g., test.yml, publish.yml).\n"
            "# - MkDocs: Add docs/ directory with .md files and mkdocs.yml for documentation.\n"
            "# Example structure:\n"
            "#   my_project/pyproject.toml\n"
            "#   my_project/README.md\n"
            "#   my_project/src/<package>/__init__.py\n"
            "#   my_project/.github/workflows/test.yml\n"
            "#   my_project/docs/index.md\n"
            "#   my_project/mkdocs.yml\n\n"
            f"# Custom Instruction:\n{common['prefix']}\n\n\n{custom_instruction}\n"
        )
    print(f"Initialized project template in {output}")


def main():
    parser = argparse.ArgumentParser(
        description="Fold and unfold Python projects with paths relative to CWD."
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    fold_parser = subparsers.add_parser(
        "fold", help="Fold specified files or a directory into a single file."
    )
    fold_parser.add_argument(
        "files",
        nargs="*",
        default=None,
        help="Files to fold (optional; if omitted, folds the current directory)",
    )
    fold_parser.add_argument(
        "--output",
        "-o",
        default="codefold.txt",
        help="Output file (e.g., folded.txt; default: codefold.txt)",
    )
    fold_parser.add_argument(
        "--prompt",
        "-p",
        default=None,
        help="Optional file containing a prompt to append to the output",
    )
    fold_parser.add_argument(
        "--dialect",
        "-d",
        default="default",
        help="Dialect for instructions (e.g., default, codeonly, doconly, latex; default: default)",
    )

    unfold_parser = subparsers.add_parser(
        "unfold", help="Unfold a modified file into a project directory."
    )
    unfold_parser.add_argument("foldfile", help="File to unfold (e.g., folded.txt)")
    unfold_parser.add_argument(
        "--original-dir", "-i", help="Original project directory to merge with"
    )
    unfold_parser.add_argument(
        "--output-dir", "-o", help="Output directory (defaults to current directory)"
    )

    init_parser = subparsers.add_parser(
        "init", help="Initialize a project template with LLM instructions."
    )
    init_parser.add_argument(
        "output", nargs="?", default="start.txt", help="Output file (e.g., start.txt)"
    )
    init_parser.add_argument(
        "--custom",
        "-c",
        default="Describe the purpose of your project here.",
        help="Custom instruction for the LLM",
    )
    init_parser.add_argument(
        "--dialect",
        "-d",
        default="default",
        help="Dialect for instructions (e.g., default, codeonly, doconly, latex; default: default)",
    )

    args = parser.parse_args()

    if args.command == "fold":
        fold(args.files, args.output, args.prompt, args.dialect)
    elif args.command == "unfold":
        unfold(args.foldfile, args.original_dir, args.output_dir)
    elif args.command == "init":
        init(args.output, args.custom, args.dialect)


if __name__ == "__main__":
    main()
