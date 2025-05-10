[![Tests](https://github.com/wr1/cfold/actions/workflows/python-app.yml/badge.svg)](https://github.com/wr1/cfold/actions/workflows/python-app.yml)

# cfold

`cfold` is a command-line tool that helps you prepare codebases for interaction with Large Language Models (LLMs). It can "fold" a directory of code into a single text file and "unfold" a modified version back into a directory structure.

## Installation

```bash
pip install cfold
```

Or locally with Poetry:

```bash
poetry install
python -m pip install .
```

## Usage

### Folding a codebase

```bash
cfold fold <directory> -o <output_file>
```

- `<directory>`: The directory to fold (defaults to current directory).
- `-o <output_file>`: Output file (default: `codefold.txt`).
- Supports `.foldignore` for exclusions.

### Unfolding a codebase

```bash
cfold unfold <fold_file> -d <output_directory>
```

- `<fold_file>`: The modified fold file.
- `-d <output_directory>`: Output directory (default: CWD).

## Fold File Format

- Starts with LLM instructions.
- Files are in `# --- File: <path> ---` sections.
- Modify with full content, delete with `# DELETE`, add with new sections.
