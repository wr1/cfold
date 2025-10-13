#set page(paper: "a4", margin: 2cm)
#set heading(numbering: "1.")

= Project Design Brief: cfold

#outline()

== Overview

Create a command-line tool called `cfold` that folds a codebase (files and directories) into a single JSON file with embedded instructions for Large Language Model (LLM) interaction. It should also unfold modified JSON files back into a directory structure, applying changes like additions, modifications, deletions, and renames. The tool is designed for Python projects but should be extensible. Emphasize modularity, maintainability, and best practices.

== Key Features

- **Fold Command**: Combine specified files or the current directory into a JSON file. Include optional prompts and dialect-based instructions. Copy output to clipboard and visualize file tree and instructions.
- **Unfold Command**: Apply changes from a modified JSON to a directory, merging with an optional original directory if provided.
- **Dialects**: Support predefined instruction sets (e.g., `default`, `py`, `pytest`, `doc`, `typst`) loaded from YAML, with custom extensions via `.foldrc`.
- **JSON Format**: `{ "instructions": [ { "type": "system|user|assistant", "content": string, "name": optional string } ], "files": [ { "path": string, "content": optional string, "delete": bool } ] }`.
- **Visualization**: Use Rich for console output of trees and summaries.

== Technical Requirements

- **Language**: Python 3.10+.
- **Dependencies**: Click (with rich-click for styled help), Pydantic for models/validation, PyYAML, Rich, Pyperclip.
- **Structure**: Modular codebase in `src/cfold/` with subdirs like `cli/`, `utils/`, `models.py`. Use pyproject.toml for packaging and CLI entrypoint.
- **Testing**: Pytest with coverage for CLI commands, utils, and models.
- **Documentation**: MkDocs with Material theme; include usage, API reference.
- **Best Practices**: PEP 8 style, single-responsibility files (50-200 lines), high-level docstrings, modular design.
- **Additional**: Support UV for installation; GitHub CI for tests; admin.sh for formatting, linting, committing.

== Usage Examples

- Fold: `cfold fold -o folded.json --dialect py`
- Unfold: `cfold unfold folded.json -o output_dir`

== Guidelines for Implementation

Follow refactoring rules: Organize into functional subdirs, split into small files, ensure modularity. Use vectorization if applicable (e.g., NumPy for any data ops). Validate with Pydantic. Do not include LLM instructions in code output.

This brief can be used as a starting point: Fold this file with `cfold fold brief.typ -o start.json --prompt "Implement this project."` and send to an LLM.
