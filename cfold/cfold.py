#!/usr/bin/env python3
import os
import argparse
import shutil
import re
from pathlib import Path
import difflib

# Define file patterns to include and exclude
INCLUDED_EXTENSIONS = {".py", ".toml", ".md", ".yml", ".yaml"}
EXCLUDED_DIRS = {".pytest_cache", "__pycache__", "build", "dist", ".egg-info"}
EXCLUDED_FILES = {".pyc"}


def should_include_file(filepath):
    """Check if a file should be included based on extension and exclusion rules."""
    path = Path(filepath)
    if path.suffix not in INCLUDED_EXTENSIONS:
        return False
    if any(part in EXCLUDED_DIRS for part in path.parts):
        return False
    if path.suffix in EXCLUDED_FILES:
        return False
    return True


def fold(directory=None, output="codefold.txt"):
    """Wrap a Poetry project's codebase into a single file with LLM instructions."""
    directory = directory or os.getcwd()
    directory = os.path.abspath(directory)

    with open(output, "w", encoding="utf-8") as outfile:
        outfile.write(
            "# Instructions for LLM:\n"
            "# - To modify a file, keep its '# --- File: path ---' header and update the content below.\n"
            "# - To delete a file, replace its content with '# DELETE'.\n"
            "# - To add a new file, include a new '# --- File: path ---' section with the desired content.\n"
            "# - Preserve the '# --- File: path ---' format for all files.\n\n"
        )
        for dirpath, _, filenames in os.walk(directory):
            for filename in filenames:
                filepath = os.path.join(dirpath, filename)
                if should_include_file(filepath):
                    relpath = os.path.relpath(filepath, directory)
                    outfile.write(f"# --- File: {relpath} ---\n")
                    with open(filepath, "r", encoding="utf-8") as infile:
                        outfile.write(infile.read() + "\n\n")
    print(f"Codebase folded into {output}")


def apply_diff(original_lines, modified_lines):
    """Apply changes from modified_lines to original_lines, preserving unchanged parts."""
    differ = difflib.Differ()
    diff = list(differ.compare(original_lines, modified_lines))

    result = []
    for line in diff:
        if line.startswith("  "):
            result.append(line[2:])
        elif line.startswith("+ "):
            result.append(line[2:])
    return "".join(result)


def unfold(fold_file, original_dir=None, output_dir=None):
    """Unfold a modified fold file, merging with original project if provided, into output_dir or cwd."""
    output_dir = output_dir or os.getcwd()
    output_dir = os.path.abspath(output_dir)

    with open(fold_file, "r", encoding="utf-8") as infile:
        content = infile.read()
        sections = re.split(r"# --- File: (.+?) ---\n", content)[1:]
        if len(sections) % 2 != 0:
            print("Warning: Malformed fold file - odd number of sections")
            return

        modified_files = {}
        for i in range(0, len(sections), 2):
            filepath = sections[i].strip()
            file_content = sections[i + 1].strip()
            # Strip MD: prefix for .md files
            if filepath.endswith(".md"):
                file_content = "\n".join(
                    line[3:] if line.startswith("MD:") else line
                    for line in file_content.splitlines()
                ).strip()
            modified_files[filepath] = file_content

    if os.path.exists(output_dir) and os.listdir(output_dir):
        print(f"Merging into existing directory: {output_dir}")
    else:
        os.makedirs(output_dir, exist_ok=True)

    if original_dir and os.path.isdir(original_dir):
        print(f"Merging with original codebase from {original_dir}")
        for dirpath, _, filenames in os.walk(original_dir):
            for filename in filenames:
                filepath = os.path.join(dirpath, filename)
                if should_include_file(filepath):
                    relpath = os.path.relpath(filepath, original_dir)
                    dst = os.path.join(output_dir, relpath)
                    os.makedirs(os.path.dirname(dst), exist_ok=True)

                    if relpath not in modified_files:
                        src = os.path.join(original_dir, relpath)
                        shutil.copy2(src, dst)
                        print(f"Copied unchanged file: {relpath}")
                    elif modified_files[relpath] == "# DELETE":
                        if os.path.exists(dst):
                            os.remove(dst)
                            print(f"Deleted file: {relpath}")
                    else:
                        original_path = os.path.join(original_dir, relpath)
                        if os.path.exists(original_path):
                            with open(
                                original_path, "r", encoding="utf-8"
                            ) as orig_file:
                                original_content = orig_file.read()
                            original_lines = original_content.splitlines(keepends=True)
                            modified_lines = modified_files[relpath].splitlines(
                                keepends=True
                            )
                            merged_content = apply_diff(original_lines, modified_lines)
                            with open(dst, "w", encoding="utf-8") as outfile:
                                outfile.write(merged_content)
                            print(f"Merged modified file: {relpath}")
                        else:
                            with open(dst, "w", encoding="utf-8") as outfile:
                                outfile.write(modified_files[relpath])
                            print(f"Wrote new file: {relpath}")
    else:
        for filepath, file_content in modified_files.items():
            if file_content == "# DELETE":
                full_path = os.path.join(output_dir, filepath)
                if os.path.exists(full_path):
                    os.remove(full_path)
                    print(f"Deleted file: {filepath}")
                continue
            full_path = os.path.join(output_dir, filepath)
            os.makedirs(os.path.dirname(full_path), exist_ok=True)
            with open(full_path, "w", encoding="utf-8") as outfile:
                outfile.write(file_content)
            print(f"Wrote file: {filepath}")

    print(f"Codebase unfolded into {output_dir}")


def init(output="start.txt", custom_instruction=""):
    """Create an initial .txt file with LLM instructions for project setup."""
    with open(output, "w", encoding="utf-8") as outfile:
        outfile.write(
            "# Instructions for LLM:\n"
            "# This file uses the cfold format to manage a Python project codebase.\n"
            "# - Folding: 'cfold fold <output.txt>' captures the current directory into a single .txt file.\n"
            "# - Unfolding: 'cfold unfold <modified.txt>' applies changes from the .txt back to the directory.\n"
            "# Rules:\n"
            "# - To modify a file, keep its '# --- File: path ---' header and update the content below.\n"
            "# - To delete a file, replace its content with '# DELETE'.\n"
            "# - To add a new file, include a new '# --- File: path ---' section with the content.\n"
            "# - For Markdown (.md) files, prefix each line with 'MD:' in the .txt; it will be stripped on unfold.\n"
            "# - Preserve the '# --- File: path ---' format for all files.\n\n"
            "# Project Setup Guidance:\n"
            "# Create a Poetry-managed Python project with:\n"
            "# - pyproject.toml: Define package metadata, dependencies, and scripts.\n"
            "# - CI: Add .github/workflows/ with .yml files for testing and publishing (e.g., test.yml, publish.yml).\n"
            "# - MkDocs: Add docs/ directory with .md files and mkdocs.yml for documentation.\n"
            "# Example structure:\n"
            "#   pyproject.toml\n"
            "#   README.md\n"
            "#   src/<package>/__init__.py\n"
            "#   .github/workflows/test.yml\n"
            "#   docs/index.md\n"
            "#   mkdocs.yml\n\n"
            f"# Custom Instruction:\n# {custom_instruction}\n"
        )
    print(f"Initialized project template in {output}")


def main():
    parser = argparse.ArgumentParser(
        description="cfold: Fold and unfold Poetry-managed Python projects with MkDocs and CI support."
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    # Fold command
    fold_parser = subparsers.add_parser(
        "fold", help="Fold a project directory into a single file."
    )
    fold_parser.add_argument(
        "output",
        nargs="?",
        default="codefold.txt",
        help="Output file (e.g., initial.txt)",
    )
    fold_parser.add_argument(
        "--directory", "-d", help="Directory to fold (defaults to current directory)"
    )

    # Unfold command
    unfold_parser = subparsers.add_parser(
        "unfold", help="Unfold a modified file into a project directory."
    )
    unfold_parser.add_argument("foldfile", help="File to unfold (e.g., llmmodifs.txt)")
    unfold_parser.add_argument(
        "--original-dir", "-i", help="Original project directory to merge with"
    )
    unfold_parser.add_argument(
        "--output-dir", "-o", help="Output directory (defaults to current directory)"
    )

    # Init command
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
        fold(args.directory, args.output)
    elif args.command == "unfold":
        unfold(args.foldfile, args.original_dir, args.output_dir)
    elif args.command == "init":
        init(args.output, args.custom)


if __name__ == "__main__":
    main()
