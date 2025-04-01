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

### `cfold unfold`

```bash
cfold unfold folded.txt -o output_dir
```

## Refactoring

- Modify with full content.
- Delete with `# DELETE`.
- Add new files with `# --- File: path ---`.
