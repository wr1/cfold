#!/usr/bin/env python3
import os
import argparse
import shutil
import re
from pathlib import Path
from importlib import resources
from cfold.utils.foldignore import load_foldignore, should_include_file
from cfold.utils.instructions import load_instructions
from cfold.utils.diff import apply_diff
from cfold.utils.references import update_references

# Define file patterns to include and exclude
INCLUDED_EXTENSIONS = {".py", ".toml", ".md", ".yml", ".yaml"}
EXCLUDED_DIRS = {".pytest_cache", "__pycache__", "build", "dist", ".egg-info", "venv"}
EXCLUDED_FILES = {".pyc"}


def fold(files=None, output="codefold.txt", prompt_file=None):
    """Wrap specified files or a directory into a single file with LLM instructions and optional prompt, using paths relative to CWD."""
    cwd = os.getcwd()
    if not files:
        directory = cwd
        ignore_patterns = load_foldignore(directory)
        files = []
        for dirpath, _, filenames in os.walk(directory):
            for filename in filenames:
                filepath = os.path.join(dirpath, filename)
                if should_include_file(filepath, ignore_patterns, directory):
                    files.append(filepath)
    else:
        files = [
            os.path.abspath(f)
            for f in files
            if os.path.isfile(f) and should_include_file(f)
        ]

    if not files:
        print("No valid files to fold.")
        return

    with open(output, "w", encoding="utf-8") as outfile:
        # Write the external instructions from resources
        outfile.write(load_instructions())

        # Write the folded files
        for filepath in files:
            relpath = os.path.relpath(filepath, cwd)
            outfile.write(f"# --- File: {relpath} ---\n")
            with open(filepath, "r", encoding="utf-8") as infile:
                content = infile.read()
                if filepath.endswith(".md"):
                    content = "\n".join(f"MD:{line}" for line in content.splitlines())
                outfile.write(content + "\n\n")

        # Append the prompt file content if provided
        if prompt_file:
            if not os.path.isfile(prompt_file):
                print(f"Warning: Prompt file '{prompt_file}' does not exist. Skipping.")
            else:
                with open(prompt_file, "r", encoding="utf-8") as prompt_infile:
                    outfile.write("\n# Prompt:\n")
                    outfile.write(prompt_infile.read())
                    outfile.write("\n")

    print(f"Codebase folded into {output}")


def unfold(fold_file, original_dir=None, output_dir=None):
    """Unfold a modified fold file with support for moves and diff edits, using paths relative to CWD."""
    cwd = os.getcwd()
    output_dir = os.path.abspath(output_dir or cwd)

    with open(fold_file, "r", encoding="utf-8") as infile:
        content = infile.read()
        sections = re.split(r"(# --- File: .+? ---|# MOVE: .+? -> .+?)\n", content)[1:]
        if len(sections) % 2 != 0:
            print("Warning: Malformed fold file - odd number of sections")
            return

        modified_files = {}
        moves = {}
        for i in range(0, len(sections), 2):
            header = sections[i].strip()
            file_content = sections[i + 1].rstrip()
            if header.startswith("# --- File:"):
                filepath = (
                    header.replace("# --- File: ", "").replace(" ---", "").strip()
                )
                if filepath.endswith(".md") and not file_content.startswith("---"):
                    file_content = "\n".join(
                        line[3:] if line.startswith("MD:") else line
                        for line in file_content.splitlines()
                    )
                modified_files[filepath] = file_content
            elif header.startswith("# MOVE:"):
                old_path, new_path = header.replace("# MOVE: ", "").split(" -> ")
                moves[old_path.strip()] = new_path.strip()

    update_references(modified_files, moves, cwd)

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
                if should_include_file(filepath, ignore_patterns, original_dir):
                    relpath = os.path.relpath(filepath, cwd)
                    dst = os.path.join(output_dir, relpath)
                    new_path = moves.get(relpath)

                    if new_path:  # File is moved
                        new_dst = os.path.join(output_dir, new_path)
                        os.makedirs(os.path.dirname(new_dst), exist_ok=True)
                        shutil.copy2(filepath, new_dst)
                        if os.path.exists(dst):
                            os.remove(dst)
                        print(f"Moved file: {relpath} -> {new_path}")
                    elif relpath not in modified_files:  # Unchanged file
                        os.makedirs(os.path.dirname(dst), exist_ok=True)
                        if os.path.abspath(filepath) != os.path.abspath(dst):
                            shutil.copy2(filepath, dst)
                            print(f"Copied unchanged file: {relpath}")
                    elif modified_files[relpath] == "# DELETE":  # Deleted file
                        if os.path.exists(dst):
                            os.remove(dst)
                            print(f"Deleted file: {relpath}")
                    else:  # Modified file
                        with open(filepath, "r", encoding="utf-8") as orig_file:
                            original_content = orig_file.read()
                        original_lines = original_content.splitlines(keepends=True)
                        modified_lines = modified_files[relpath].splitlines(
                            keepends=True
                        )
                        merged_content = apply_diff(original_lines, modified_lines)
                        os.makedirs(os.path.dirname(dst), exist_ok=True)
                        with open(dst, "w", encoding="utf-8") as outfile:
                            outfile.write(merged_content)
                        print(f"Applied changes to file: {relpath}")
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

        for old_path, new_path in moves.items():
            old_full_path = os.path.join(output_dir, old_path)
            new_full_path = os.path.join(output_dir, new_path)
            if os.path.exists(old_full_path):
                os.makedirs(os.path.dirname(new_full_path), exist_ok=True)
                shutil.move(old_full_path, new_full_path)
                print(f"Moved file: {old_path} -> {new_path}")

    print(f"Codebase unfolded into {output_dir}")


def init(output="start.txt", custom_instruction=""):
    """Create an initial .txt file with LLM instructions for project setup."""
    with open(output, "w", encoding="utf-8") as outfile:
        outfile.write(load_instructions())
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
            f"# Custom Instruction:\n# {custom_instruction}\n"
        )
    print(f"Initialized project template in {output}")


def main():
    parser = argparse.ArgumentParser(
        description="cfold: Fold and unfold Python projects with paths relative to CWD."
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

    args = parser.parse_args()

    if args.command == "fold":
        fold(args.files, args.output, args.prompt)
    elif args.command == "unfold":
        unfold(args.foldfile, args.original_dir, args.output_dir)
    elif args.command == "init":
        init(args.output, args.custom)


if __name__ == "__main__":
    main()
