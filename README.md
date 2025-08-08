![Tests](https://github.com/wr1/cfold/actions/workflows/tests.yml/badge.svg)![Version](https://img.shields.io/github/v/release/wr1/cfold)
# cfold

`cfold` is a command-line tool that helps you prepare codebases for interaction with Large Language Models (LLMs). It can "fold" a directory of code into a single JSON file and "unfold" a modified version back into a directory structure.

## Installation

```bash
pip install cfold
```

Or install from source with UV:

```bash
uv pip install .
```

## Usage

![use gif](docs/assets/use.gif)

### Folding a codebase

Fold specific files or the current directory into a single JSON file:

```bash
cfold fold [files...] -o <output_file> [--prompt <prompt_file>] [--dialect <dialect>]
```

- `[files...]`: Specific files to fold (optional; if omitted, folds the entire current directory).
- `-o <output_file>`: Output file (default: `codefold.json`).
- `--prompt <prompt_file>`: Optional file to append as a prompt in the output.
- `--dialect <dialect>`: Dialect for instructions (e.g., `default`, `py`, `pytest`, `doc`, `typst`; default: `default`).
- Supports `.foldignore` for excluding files when folding a directory.

Example (fold only code files):

```bash
cfold fold -o folded.json --dialect py
```

Or simply
```bash
cfold fold
```

The output file can then be sent to an LLM either through the GUI or through a tool like [grk](https://github.com/wr1/grk). 

After folding, copies content to clipboard, visualizes the file tree and added instructions (by type and name).

### Unfolding a codebase

Unfold a modified fold file back into a directory structure:

```bash
cfold unfold <fold_file> [-i <original_dir>] [-o <output_dir>]
```

- `<fold_file>`: The modified fold file to unfold.
- `-i <original_dir>`: Original directory to merge with (optional).
- `-o <output_dir>`: Output directory (default: CWD).

Example:

```bash
cfold unfold folded.json -o output_dir
```

### Initializing a project template

Create a template file with LLM instructions for project setup:

```bash
cfold init [<output_file>] [--custom <instruction>] [--dialect <dialect>]
```

- `<output_file>`: Output file (default: `start.json`).
- `--custom <instruction>`: Custom instruction for the LLM.
- `--dialect <dialect>`: Dialect for instructions (e.g., `default`, `py`, `pytest`, `doc`, `typst`; default: `default`).

Example:

```bash
cfold init start.json --custom "Build a Python CLI tool." --dialect default
```

## Fold File Format

- JSON structure with keys: `instructions` (list of objects), `files`.
- Each instruction object: `{type: 'system'|'user'|'assistant', content: string, name: string (optional)}`.
- `files`: Array of objects with `path` (relative to CWD), `content` (full file content, optional if deleting), and `delete` (bool, default false).
- Modify files by updating `content` (with `delete: false`).
- Delete files with `delete: true` (content optional).
- Add new files by adding new objects with `path` and `content`.
- Move/rename: Delete old (`delete: true`) and add new with updated path and content.





