# cfold Documentation

`cfold` is a command-line tool for folding Python codebases into a single JSON file and unfolding modified versions back into a directory, ideal for LLM interaction. All file paths are handled relative to the current working directory (CWD).

## Features

- **Fold**: Combine specific files or the current directory into a `.json` file, with optional prompt inclusion. Visualizes file tree and instruction categories.
- **Unfold**: Apply changes (modifications, deletions, or new files) back to a directory.
- **Init**: Generate a project template with custom instructions.
- Supports UV, GitHub CI, MkDocs, and `.foldignore` for file exclusions.
- Uses Pydantic for data validation of input/output JSON.

## Quick Start

Install:

```bash
pip install cfold
```

Fold a directory:

```bash
cfold fold -o folded.json
```

Unfold changes:

```bash
cfold unfold folded.json -o output_dir
```

Initialize a project:

```bash
cfold init start.json --custom "Build a Python CLI tool."
```

