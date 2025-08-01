# API Reference

This page documents the Python API for the `cfold` module. All file paths are relative to the current working directory (CWD).

## `cfold.fold(files=None, output="codefold.json", prompt_file=None)`

Fold specific files or the current directory into a single JSON file.

- `files`: List of file paths to fold (default: `None`, folds the current directory).
- `output`: Output file path (default: `"codefold.json"`).
- `prompt_file`: Path to an optional prompt file to append (default: `None`).

When `files` is `None`, the function folds all valid files in the current directory, respecting `.foldignore` patterns. Outputs JSON validated by Pydantic and visualizes file tree + instruction categories.

## `cfold.unfold(fold_file, original_dir=None, output_dir=None)`

Unfold a modified fold file into a directory structure.

- `fold_file`: Path to the fold file to unfold.
- `original_dir`: Path to the original directory to merge with (default: `None`).
- `output_dir`: Output directory path (default: CWD).

Supports full content rewrites, deletions (`# DELETE`), and new file creation. Validates input JSON with Pydantic.

## `cfold.init(output="start.json", custom_instruction="")`

Initialize a project template with LLM instructions.

- `output`: Output file path (default: `"start.json"`).
- `custom_instruction`: Custom instruction for the LLM (default: `""`).

