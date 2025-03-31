#!/usr/bin/env python3
import os
import argparse
import shutil
import re
from pathlib import Path
import difflib
import fnmatch

# Define file patterns to include and exclude
INCLUDED_EXTENSIONS = {".py", ".toml", ".md", ".yml", ".yaml"}
EXCLUDED_DIRS = {".pytest_cache", "__pycache__", "build", "dist", ".egg-info", "venv"}
EXCLUDED_FILES = {".pyc"}

def load_foldignore(directory):
    """Load and parse .foldignore file if it exists."""
    ignore_file = Path(directory) / ".foldignore"
    ignore_patterns = []
    if ignore_file.exists():
        with open(ignore_file, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#"):
                    ignore_patterns.append(line)
    return ignore_patterns

def should_include_file(filepath, ignore_patterns=None, root_dir=None):
    """Check if a file should be included based on extension, exclusion rules, and .foldignore patterns."""
    path = Path(filepath)
    
    # Calculate relative path from root_dir if provided, otherwise use filepath as is
    if root_dir:
        relpath = os.path.relpath(filepath, root_dir)
    else:
        relpath = str(path)
    
    # Check basic inclusion rules
    if path.suffix not in INCLUDED_EXTENSIONS:
        return False
    if any(part in EXCLUDED_DIRS for part in path.parts):
        return False
    if path.suffix in EXCLUDED_FILES:
        return False
    
    # Check .foldignore patterns
    if ignore_patterns:
        for pattern in ignore_patterns:
            if fnmatch.fnmatch(relpath, pattern):
                return False
    
    return True

def fold(directory=None, output="codefold.txt"):
    """Wrap a project's codebase into a single file with LLM instructions, using paths relative to CWD."""
    cwd = os.getcwd()
    directory = os.path.abspath(directory or cwd)
    ignore_patterns = load_foldignore(directory)

    with open(output, "w", encoding="utf-8") as outfile:
        outfile.write(
            "# Instructions for LLM:\n"
            "# This file uses the cfold format to manage a Python project codebase.\n"
            "# - Folding: 'cfold fold <output.txt>' captures all included files from the directory into this .txt.\n"
            "# - Unfolding: 'cfold unfold <modified.txt>' applies changes from this .txt to the directory.\n"
            "# Rules:\n"
            "# - To modify a file: Keep its '# --- File: path ---' header and update content below.\n"
            "# - To delete a file: Replace its content with '# DELETE'.\n"
            "# - To add a file: Add a new '# --- File: path ---' section with content.\n"
            "# - Only include modified, new, or deleted files in the modified .txt; unchanged files are preserved by 'unfold'.\n"
            "# - For Markdown (e.g., .md files, docstrings, comments): Prefix every line with 'MD:' in the .txt.\n"
            "#   'unfold' strips 'MD:' only from .md files, not .py files.\n"
            "# - Always preserve '# --- File: path ---' format.\n"
            "# - Supports .foldignore file with gitignore-style patterns to exclude files during folding.\n"
            "# - Paths are relative to the current working directory (CWD) by default.\n"
            "# Example:\n"
            "#   # --- File: my_project/docs/example.md ---\n"
            "#   MD:# Title\n"
            "#   MD:Text\n"
            "#   # --- File: my_project/src/test.py ---\n"
            "#   MD:# Comment with MD: prefix\n"
            "#   print('Code')\n\n"
        )
        for dirpath, _, filenames in os.walk(directory):
            for filename in filenames:
                filepath = os.path.join(dirpath, filename)
                if should_include_file(filepath, ignore_patterns, directory):
                    relpath = os.path.relpath(filepath, cwd)
                    outfile.write(f"# --- File: {relpath} ---\n")
                    with open(filepath, "r", encoding="utf-8") as infile:
                        content = infile.read()
                        if filepath.endswith(".md"):
                            content = "\n".join(
                                f"MD:{line}" for line in content.splitlines()
                            )
                        outfile.write(content + "\n\n")
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
    """Unfold a modified fold file, using paths relative to CWD by default."""
    cwd = os.getcwd()
    output_dir = os.path.abspath(output_dir or cwd)

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
        original_dir = os.path.abspath(original_dir)
        ignore_patterns = load_foldignore(original_dir)
        for dirpath, _, filenames in os.walk(original_dir):
            for filename in filenames:
                filepath = os.path.join(dirpath, filename)
                if should_include_file(filepath, ignore_patterns, original_dir):
                    relpath = os.path.relpath(filepath, cwd)  # Relative to CWD
                    dst = os.path.join(output_dir, relpath)
                    os.makedirs(os.path.dirname(dst), exist_ok=True)

                    if relpath not in modified_files:
                        if os.path.abspath(filepath) != os.path.abspath(dst):  # Avoid copying file to itself
                            shutil.copy2(filepath, dst)
                            print(f"Copied unchanged file: {relpath}")
                    elif modified_files[relpath] == "# DELETE":
                        if os.path.exists(dst):
                            os.remove(dst)
                            print(f"Deleted file: {relpath}")
                    else:
                        original_path = os.path.join(cwd, relpath)
                        if os.path.exists(original_path):
                            with open(original_path, "r", encoding="utf-8") as orig_file:
                                original_content = orig_file.read()
                            original_lines = original_content.splitlines(keepends=True)
                            modified_lines = modified_files[relpath].splitlines(keepends=True)
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
            "# - Folding: 'cfold fold <output.txt>' captures all included files from the directory into this .txt.\n"
            "# - Unfolding: 'cfold unfold <modified.txt>' applies changes from this .txt to the directory.\n"
            "# Rules:\n"
            "# - To modify a file: Keep its '# --- File: path ---' header and update content below.\n"
            "# - To delete a file: Replace its content with '# DELETE'.\n"
            "# - To add a file: Add a new '# --- File: path ---' section with content.\n"
            "# - Only include modified, new, or deleted files in the modified .txt; unchanged files are preserved by 'unfold'.\n"
            "# - For Markdown (e.g., .md files, docstrings, comments): Prefix every line with 'MD:' in the .txt.\n"
            "#   'unfold' strips 'MD:' only from .md files, not .py files.\n"
            "# - Always preserve '# --- File: path ---' format.\n"
            "# - Supports .foldignore file with gitignore-style patterns to exclude files during folding.\n"
            "# - Paths are relative to the current working directory (CWD) by default.\n"
            "# Example:\n"
            "#   # --- File: my_project/docs/example.md ---\n"
            "#   MD:# Title\n"
            "#   MD:Text\n"
            "#   # --- File: my_project/src/test.py ---\n"
            "#   MD:# Comment with MD: prefix\n"
            "#   print('Code')\n\n"
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
        "fold", help="Fold a project directory into a single file."
    )
    fold_parser.add_argument(
        "output",
        nargs="?",
        default="codefold.txt",
        help="Output file (e.g., folded.txt)",
    )
    fold_parser.add_argument(
        "--directory", "-d", help="Directory to fold (defaults to current directory)"
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
        fold(args.directory, args.output)
    elif args.command == "unfold":
        unfold(args.foldfile, args.original_dir, args.output_dir)
    elif args.command == "init":
        init(args.output, args.custom)

if __name__ == "__main__":
    main()