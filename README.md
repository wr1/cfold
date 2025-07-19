![Tests](https://github.com/wr1/cfold/actions/workflows/tests.yml/badge.svg)![Version](https://img.shields.io/github/v/release/wr1/cfold)
# cfold

`cfold` is a command-line tool that helps you prepare codebases for interaction with Large Language Models (LLMs). It can "fold" a directory of code into a single text file and "unfold" a modified version back into a directory structure.

## Installation

```bash
pip install .
```

Or install locally with UV:

```bash
uv pip install .
```

## Usage

### Folding a codebase

Fold specific files or the current directory into a single text file:

```bash
cfold fold [files...] -o <output_file> [--prompt <prompt_file>] [--dialect <dialect>]
```

- `[files...]`: Specific files to fold (optional; if omitted, folds the entire current directory).
- `-o <output_file>`: Output file (default: `codefold.txt`).
- `--prompt <prompt_file>`: Optional file to append as a prompt in the output.
- `--dialect <dialect>`: Dialect for instructions (e.g., `default`, `codeonly`, `doconly`; default: `default`).
- Supports `.foldignore` for excluding files when folding a directory.

Example (fold only code files):

```bash
cfold fold -o folded.txt --dialect codeonly
```

Or simply
```bash
cfold fold
```
![alt text](docs/assets/image.png)

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
cfold init [<output_file>] [--custom <instruction>] [--dialect <dialect>]
```

- `<output_file>`: Output file (default: `start.txt`).
- `--custom <instruction>`: Custom instruction for the LLM.
- `--dialect <dialect>`: Dialect for instructions (e.g., `default`, `codeonly`, `doconly`; default: `default`).

Example:

```bash
cfold init start.txt --custom "Build a Python CLI tool." --dialect default
```

## Fold File Format

- Starts with LLM instructions.
- Files are in `# --- File: <path> ---` sections with paths relative to CWD.
- Modify files by providing full content.
- Delete files with `# DELETE`.
- Add new files with new `# --- File: <path> ---` sections.
- Markdown files have `MD:` prefix per line (stripped on unfold).
