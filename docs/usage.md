# Usage

## Installation

```bash
pip install cfold
```

Or with Poetry:

```bash
poetry install
```

## Commands

### `cfold init`

```bash
cfold init start.txt --custom "Build a tool."
```

### `cfold fold`

```bash
cfold fold -o folded.txt
```

```bash 

usage: cfold fold [-h] [--output OUTPUT] [--prompt PROMPT] [files ...]

positional arguments:
  files                 Files to fold (optional; if omitted, folds the current directory)

options:
  -h, --help            show this help message and exit
  --output OUTPUT, -o OUTPUT
                        Output file (e.g., folded.txt; default: codefold.txt)
  --prompt PROMPT, -p PROMPT
                        Optional file containing a prompt to append to the output
```



### `cfold unfold`

```bash
cfold unfold folded.txt -o output_dir
```

## Refactoring

- Modify with full content.
- Delete with `# DELETE`.
- Add new files with `# --- File: path ---`.
