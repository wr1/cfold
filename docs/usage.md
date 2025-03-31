# Usage

`cfold` provides three main commands to manage your codebase.

## Installation

```bash
pip install cfold
```

Or, with Poetry locally:

```bash
poetry install
```

## Commands

### `cfold init`

Create a starting template with LLM instructions:

```bash
cfold init start.txt --custom "Build a tool to process data."
```

- `-c/--custom`: Specify the project’s purpose (default: "Describe the purpose of your project here.").
- Output: `start.txt` (customizable).

### `cfold fold`

Fold a directory into a single file:

```bash
cfold fold my_project -o folded.txt
```

- `-d/--directory`: Directory to fold (default: current dir).
- `-o/--output`: Output file (default: `codefold.txt`).
- Paths are relative to the current working directory (CWD).
- Supports `.foldignore` file with gitignore-style patterns to exclude files (e.g., `*.log`, `temp/`).

### `cfold unfold`

Unfold a modified file back into a directory:

```bash
cfold unfold folded.txt -o my_project_modified -i my_project
```

- `-i/--original-dir`: Original directory to merge with (optional).
- `-o/--output-dir`: Output directory (default: current working directory).