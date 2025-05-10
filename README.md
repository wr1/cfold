[![Tests](https://github.com/wr1/cfold/actions/workflows/python-app.yml/badge.svg)](https://github.com/wr1/cfold/actions/workflows/python-app.yml)

<<<<<<< HEAD
# cfold

`cfold` is a command-line tool that helps you prepare codebases for interaction with Large Language Models (LLMs). It can "fold" a directory of code into a single text file and "unfold" a modified version back into a directory structure.
=======
`cfold` is a command-line tool that helps you prepare codebases for interaction with Large Language Models (LLMs). It can "fold" a directory or specific files into a single text file and "unfold" a modified version back into a directory structure. All file paths are handled relative to the current working directory (CWD).
>>>>>>> 6115ec077a889059b095881bf1aa7f2e04373560

## Installation

```bash
pip install .
```

Or install locally with Poetry:

```bash
poetry install
python -m pip install .
```

## Usage

### Folding a codebase

Fold specific files or the current directory into a single text file:

```bash
cfold fold [files...] -o <output_file> [--prompt <prompt_file>]
```

- `[files...]`: Specific files to fold (optional; if omitted, folds the entire current directory).
- `-o <output_file>`: Output file (default: `codefold.txt`).
- `--prompt <prompt_file>`: Optional file to append as a prompt in the output.
- Supports `.foldignore` for excluding files when folding a directory.

Example:

```bash
cfold fold src/main.py docs/index.md -o folded.txt --prompt prompt.txt
```

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
cfold unfold folded.txt -o output_dir
```

### Initializing a project template

Create a template file with LLM instructions for project setup:

```bash
cfold init [<output_file>] [--custom <instruction>]
```

- `<output_file>`: Output file (default: `start.txt`).
- `--custom <instruction>`: Custom instruction for the LLM.

Example:

```bash
cfold init start.txt --custom "Build a Python CLI tool."
```

## Fold File Format

- Starts with LLM instructions.
- Files are in `# --- File: <path> ---` sections with paths relative to CWD.
- Modify files by providing full content.
- Delete files with `# DELETE`.
- Add new files with new `# --- File: <path> ---` sections.
- Markdown files have `MD:` prefix per line (stripped on unfold).
