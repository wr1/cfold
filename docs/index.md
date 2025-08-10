# cfold Documentation

`cfold` is a command-line tool for folding Python codebases into a single JSON file and unfolding modified versions back into a directory, ideal for LLM interaction. All file paths are handled relative to the current working directory (CWD).

## Features

- **Fold**: Combine specific files or the current directory into a `.json` file, with optional prompt inclusion. Copies output to clipboard, visualizes file tree and instruction list (by type and name).
- **Unfold**: Apply changes (modifications, deletions, or new files) back to a directory.
- Supports UV, GitHub CI, MkDocs, and `.foldignore` for file exclusions.
- Uses Pydantic for data validation of input/output JSON.
- `instructions` is a list of objects with `type`, `content`, and optional `name`.
- Dialects: `default`, `py`, `pytest`, `doc`, `typst`.

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






