# --- File: cfold/cfold.py ---
#!/usr/bin/env python3
import os
import argparse
import shutil
import re
from pathlib import Path
import fnmatch
import ast
import difflib

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
    if root_dir:
        relpath = os.path.relpath(filepath, root_dir)
    else:
        relpath = str(path)
    if path.suffix not in INCLUDED_EXTENSIONS:
        return False
    if any(part in EXCLUDED_DIRS for part in path.parts):
        return False
    if path.suffix in EXCLUDED_FILES:
        return False
    if ignore_patterns:
        for pattern in ignore_patterns:
            if fnmatch.fnmatch(relpath, pattern):
                return False
    return True


def fold(files=None, output="codefold.txt"):
    """Wrap specified files or a directory into a single file with LLM instructions, using paths relative to CWD."""
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
        outfile.write(
            "# Instructions for LLM:\n"
            "# This file uses the cfold format to manage a Python project codebase.\n"
            "# - Folding: 'cfold fold <files> -o <output.txt>' captures specified files into this .txt.\n"
            "# - Unfolding: 'cfold unfold <modified.txt>' applies changes from this .txt to the directory.\n"
            "# Rules:\n"
            "# - To modify a file fully: Keep its '# --- File: path ---' header and update content below.\n"
            "# - To edit lines: Use unified diff format (---, +++, @@ ... @@) after '# --- File: path ---'.\n"
            "# - To delete a file: Replace its content with '# DELETE'.\n"
            "# - To add a file: Add a new '# --- File: path ---' section with content.\n"
            "# - To move/rename a file: Add '# MOVE: old_path -> new_path' (relative to CWD).\n"
            "# - Only include modified, new, deleted, or moved files in the modified .txt; unchanged files are preserved.\n"
            "# - For Markdown (e.g., .md files): Prefix every line with 'MD:' in full content mode.\n"
            "#   'unfold' strips 'MD:' only from .md files, not .py files; diff mode preserves literal content.\n"
            "# - Always preserve '# --- File: path ---' or '# MOVE: ...' format.\n"
            "# - Supports .foldignore file with gitignore-style patterns to exclude files during folding (directory mode).\n"
            "# - Paths are relative to the current working directory (CWD) by default.\n"
            "# Example:\n"
            "#   # --- File: my_project/docs/example.md ---\n"
            "#   MD:# Title\n"
            "#   MD:Text\n"
            "#   # --- File: my_project/src/test.py ---\n"
            "#   --- test.py\n"
            "#   +++ test.py\n"
            "#   @@ -1 +1 @@\n"
            "#   -print('Old')\n"
            "#   +print('New')\n"
            "#   # MOVE: my_project/src/test.py -> my_project/src/new_test.py\n\n"
        )
        for filepath in files:
            relpath = os.path.relpath(filepath, cwd)
            outfile.write(f"# --- File: {relpath} ---\n")
            with open(filepath, "r", encoding="utf-8") as infile:
                content = infile.read()
                if filepath.endswith(".md"):
                    content = "\n".join(f"MD:{line}" for line in content.splitlines())
                outfile.write(content + "\n\n")
    print(f"Codebase folded into {output}")


def apply_diff(original_lines, modified_lines):
    """Apply unified diff changes or full content replacement using difflib."""
    if not modified_lines or not any(line.startswith("---") for line in modified_lines):
        # Full content replacement
        return "".join(modified_lines)

    # Handle unified diff format
    diff_lines = [
        line for line in modified_lines if not line.startswith(("---", "+++"))
    ]
    if not diff_lines or not any(line.startswith("@@") for line in diff_lines):
        return "".join(modified_lines)  # No valid diff hunks, treat as full content

    # Construct a unified diff string and apply it
    diff_text = "\n".join(modified_lines) + "\n"
    original_text = "".join(original_lines)
    # Use a simple patch applicator for unified diff
    result = list(original_lines)
    current_pos = 0
    hunk = []
    for line in diff_lines:
        if line.startswith("@@"):
            if hunk:
                # Apply previous hunk
                for h_line in hunk:
                    if h_line.startswith("-") and current_pos < len(result):
                        result.pop(current_pos)
                    elif h_line.startswith("+"):
                        result.insert(current_pos, h_line[1:])
                        current_pos += 1
                    elif h_line.startswith(" "):
                        current_pos += 1
            hunk = [line]
        elif line.startswith(("+", "-", " ")):
            hunk.append(line)

    # Apply final hunk
    if hunk:
        for h_line in hunk:
            if h_line.startswith("-") and current_pos < len(result):
                result.pop(current_pos)
            elif h_line.startswith("+"):
                result.insert(current_pos, h_line[1:])
                current_pos += 1
            elif h_line.startswith(" "):
                current_pos += 1

    return "".join(result)


def update_references(modified_files, moves, cwd):
    """Update file references in Python files affected by moves."""
    for old_path, new_path in moves.items():
        old_relpath = Path(old_path)
        new_relpath = Path(new_path)
        old_module = ".".join(old_relpath.with_suffix("").parts)
        new_module = ".".join(new_relpath.with_suffix("").parts)

        for filepath, content in modified_files.items():
            if filepath.endswith(".py") and content != "# DELETE":
                lines = content.splitlines(keepends=True)
                if any(l.startswith("---") for l in lines):
                    # Apply diff if present
                    try:
                        with open(
                            os.path.join(cwd, filepath), "r", encoding="utf-8"
                        ) as f:
                            original_lines = f.read().splitlines(keepends=True)
                        content = apply_diff(original_lines, lines)
                    except FileNotFoundError:
                        # If no original file, assume diff is standalone
                        content = apply_diff([], lines)
                try:
                    tree = ast.parse(content)

                    class ImportVisitor(ast.NodeVisitor):
                        def __init__(self):
                            self.changes = []

                        def visit_Import(self, node):
                            for alias in node.names:
                                if alias.name == old_module:
                                    self.changes.append(
                                        (node.lineno, f"import {new_module}")
                                    )
                            self.generic_visit(node)

                        def visit_ImportFrom(self, node):
                            if node.module == old_module:
                                names = ", ".join(alias.name for alias in node.names)
                                self.changes.append(
                                    (node.lineno, f"from {new_module} import {names}")
                                )
                            self.generic_visit(node)

                    visitor = ImportVisitor()
                    visitor.visit(tree)
                    if visitor.changes:
                        lines = content.splitlines(keepends=True)
                        for lineno, new_line in sorted(visitor.changes, reverse=True):
                            lines[lineno - 1] = new_line + "\n"
                        modified_files[filepath] = "".join(lines)
                except SyntaxError:
                    print(f"Warning: Could not parse {filepath} for reference updates.")


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

    # Update references in Python files for moves
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
        # No original_dir: process modified_files and moves directly
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
        outfile.write(
            "# Instructions for LLM:\n"
            "# This file uses the cfold format to manage a Python project codebase.\n"
            "# - Folding: 'cfold fold <files> -o <output.txt>' captures specified files into this .txt.\n"
            "# - Unfolding: 'cfold unfold <modified.txt>' applies changes from this .txt to the directory.\n"
            "# Rules:\n"
            "# - To modify a file fully: Keep its '# --- File: path ---' header and update content below.\n"
            "# - To edit lines: Use unified diff format (---, +++, @@ ... @@) after '# --- File: path ---'.\n"
            "# - To delete a file: Replace its content with '# DELETE'.\n"
            "# - To add a file: Add a new '# --- File: path ---' section with content.\n"
            "# - To move/rename a file: Add '# MOVE: old_path -> new_path' (relative to CWD).\n"
            "# - Only include modified, new, deleted, or moved files in the modified .txt; unchanged files are preserved.\n"
            "# - For Markdown (e.g., .md files): Prefix every line with 'MD:' in full content mode.\n"
            "#   'unfold' strips 'MD:' only from .md files, not .py files; diff mode preserves literal content.\n"
            "# - Always preserve '# --- File: path ---' or '# MOVE: ...' format.\n"
            "# - Supports .foldignore file with gitignore-style patterns to exclude files during folding (directory mode).\n"
            "# - Paths are relative to the current working directory (CWD) by default.\n"
            "# Example:\n"
            "#   # --- File: my_project/docs/example.md ---\n"
            "#   MD:# Title\n"
            "#   MD:Text\n"
            "#   # --- File: my_project/src/test.py ---\n"
            "#   --- test.py\n"
            "#   +++ test.py\n"
            "#   @@ -1 +1 @@\n"
            "#   -print('Old')\n"
            "#   +print('New')\n"
            "#   # MOVE: my_project/src/test.py -> my_project/src/new_test.py\n\n"
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
        fold(args.files, args.output)
    elif args.command == "unfold":
        unfold(args.foldfile, args.original_dir, args.output_dir)
    elif args.command == "init":
        init(args.output, args.custom)


if __name__ == "__main__":
    main()
