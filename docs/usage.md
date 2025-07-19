# Usage

This guide explains how to use the `cfold` command-line tool to fold and unfold Python codebases for LLM interaction. All file paths are relative to the current working directory (CWD).

## Installation

Install `cfold` using pip:

```bash
pip install cfold
```

If you encounter pip errors (e.g., `html5lib` issues), reinstall pip:

```bash
python -m ensurepip --upgrade
python -m pip install --force-reinstall pip
pip install cfold
```

Or install locally with UV:

```bash
uv pip install .
```

## Commands

### `cfold init`

Initialize a project template with LLM instructions:

```bash
cfold init [<output_file>] [--custom <instruction>] [--dialect <dialect>]
```

- `<output_file>`: Output file (default: `start.txt`).
- `--custom <instruction>`: Custom instruction for the LLM (e.g., project purpose).
- `--dialect <dialect>`: Dialect for instructions (e.g., `default`, `codeonly`, `test`, `doconly`, `latex`; default: `default`).

Example:

```bash
cfold init start.txt --custom "Build a tool for code folding."
```

### `cfold fold`

Fold specific files or the current directory into a single text file:

```bash
cfold fold [files...] [--output <output_file>] [--prompt <prompt_file>] [--dialect <dialect>]
```

Options:

```bash
usage: cfold fold [-h] [--output OUTPUT] [--prompt PROMPT] [--dialect DIALECT] [files ...]

positional arguments:
  files                 Files to fold (optional; if omitted, folds the current directory)

options:
  -h, --help            show this help message and exit
  --output OUTPUT, -o OUTPUT
                        Output file (e.g., folded.txt; default: codefold.txt)
  --prompt PROMPT, -p PROMPT
                        Optional file containing a prompt to append to the output
  --dialect DIALECT, -d DIALECT
                        Dialect for instructions (e.g., default, codeonly, test, doconly, latex; default: default)
```

Example:

```bash
cfold fold src/main.py -o folded.txt --prompt prompt.txt
```

Example (fold only code files):

```bash
cfold fold -o folded.txt --dialect codeonly
```

### `cfold unfold`

Unfold a modified fold file into a directory structure:

```bash
cfold unfold <fold_file> [--original-dir <original_dir>] [--output-dir <output_dir>]
```

Options:

```bash
usage: cfold unfold [-h] [--original-dir ORIGINAL_DIR] [--output-dir OUTPUT_DIR] foldfile

positional arguments:
  foldfile              File to unfold (e.g., folded.txt)

options:
  -h, --help            show this help message and exit
  --original-dir ORIGINAL_DIR, -i ORIGINAL_DIR
                        Original project directory to merge with
  --output-dir OUTPUT_DIR, -o OUTPUT_DIR
                        Output directory (defaults to current directory)
```

Example:

```bash
cfold unfold folded.txt -i original_project -o output_dir
```

## Refactoring

- **Modify**: Provide the full content under `# --- File: <path> ---`.
- **Delete**: Use `# DELETE` under the file's header.
- **Add**: Create a new `# --- File: <path> ---` section with full content.
- **Move/Rename**: Delete the old file with `# DELETE` and add a new file section with the updated path and content.
- Paths are relative to the CWD.
