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

Or install from source with UV:

```bash
uv pip install .
```

## Commands

### `cfold fold`

Fold specific files or the current directory into a single JSON file:

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
                        Output file (e.g., folded.json; default: codefold.json)
  --prompt PROMPT, -p PROMPT
                        Optional file containing a prompt to append to the output
  --dialect DIALECT, -d DIALECT
                        Dialect for instructions (e.g., default, py, pytest, doc, typst; default: default)
```

If `--dialect` is not specified and a `.foldrc` file exists with a `default_dialect` key, it will use that as the dialect.

After folding, copies content to clipboard, visualizes the file tree and instruction list (by type and name).

Example:

```bash
cfold fold src/main.py -o folded.json --prompt prompt.txt
```

Example (fold only code files):

```bash
cfold fold -o folded.json --dialect py
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
  foldfile              File to unfold (e.g., folded.json)

options:
  -h, --help            show this help message and exit
  --original-dir ORIGINAL_DIR, -i ORIGINAL_DIR
                        Original project directory to merge with
  --output-dir OUTPUT_DIR, -o OUTPUT_DIR
                        Output directory (defaults to current directory)
```

Example:

```bash
cfold unfold folded.json -i original_project -o output_dir
```

### `cfold rc`

Create or update a local `.foldrc` file with a 'local' profile and set it as the default dialect:

```bash
cfold rc
```

This adds a 'local' dialect (extending 'default') and sets `default_dialect: local` in `.foldrc`.

## Refactoring

- **Modify**: Update the `content` field in the `files` array with full content (set `delete: false` or omit).
- **Delete**: Add an object to `files` with `path` and set `delete: true` (content optional).
- **Add**: Add a new object to `files` with `path`, `content`, and `delete: false` (optional).
- **Move/Rename**: Add a delete object for the old path (`delete: true`) and a new object with the new `path`, full `content`, and `delete: false`.
- Paths are relative to the CWD.
- JSON is validated using Pydantic models.
- `instructions` is a list of objects; do not modify unless specified.






