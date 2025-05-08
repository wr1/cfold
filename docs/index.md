# cfold Documentation

`cfold` is a command-line tool for folding Python codebases into a single text file and unfolding modified versions back into a directory, ideal for LLM interaction. All file paths are handled relative to the current working directory (CWD).

## Features

- **Fold**: Combine specific files or the current directory into a `.txt` file, with optional prompt inclusion.
- **Unfold**: Apply changes (modifications, deletions, or new files) back to a directory.
- **Init**: Generate a project template with custom instructions.
- Supports Poetry, GitHub CI, MkDocs, and `.foldignore` for file exclusions.

## Quick Start

Install:

```bash
pip install cfold
```

Fold a directory:

```bash
cfold fold -o folded.txt
```

Unfold changes:

```bash
cfold unfold folded.txt -o output_dir
```

Initialize a project:

```bash
cfold init start.txt --custom "Build a Python CLI tool."
```
