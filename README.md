# cfold

[![Tests](https://github.com/wr1/cfold/actions/workflows/python-app.yml/badge.svg)](https://github.com/wr1/cfold/actions/workflows/python-app.yml) 
<!-- [![Coverage](https://codecov.io/gh/<your-username>/cfold/branch/master/graph/badge.svg)](https://codecov.io/gh/<your-username>/cfold) -->

cfold is a command-line tool that helps you prepare codebases for interaction with Large Language Models (LLMs). It can "fold" a directory of code into a single text file, and "unfold" a modified version of that file back into a directory structure. This is useful for providing LLMs with the context of an entire project in a manageable format, allowing them to make changes, add new files, or delete existing ones.

## Installation

```bash
pip install cfold
```

Alternatively, if you have the project locally:

```bash
poetry install # if using poetry
python -m pip install .
```

## Usage

### Folding a codebase

To fold a directory into a single file, use the `fold` command:

```bash
cfold fold <directory> -o <output_file>
```

*   `<directory>`: The directory containing the codebase you want to fold (defaults to current directory).
*   `-o <output_file>` or `--output <output_file>`: (Optional) The name of the output file. Defaults to `codefold.txt`.
*   Paths in the output file are relative to the current working directory (CWD).
*   Supports `.foldignore` file with gitignore-style patterns to exclude files during folding.

Example:

```bash
cfold fold my_project -o folded_code.txt
```

If run from `/home/user`, this will create `folded_code.txt` with paths like `my_project/main.py`. Create a `.foldignore` file in the directory to exclude specific patterns (e.g., `*.log` or `temp/`).

### Unfolding a codebase

To unfold a modified fold file back into a directory structure, use the `unfold` command:

```bash
cfold unfold <fold_file> -d <output_directory>
```

*   `<fold_file>`: The file containing the folded codebase (e.g., the one modified by an LLM).
*   `-d <output_directory>` or `--output-dir <output_directory>`: (Optional) The directory to unfold into. Defaults to the current working directory (CWD).

Example:

```bash
cfold unfold folded_code.txt -d my_project_modified
```

If run from `/home/user`, and without `-d`, it will unfold into `/home/user/my_project/...`. With `-d`, it will unfold into `/home/user/my_project_modified/...`.

## Fold File Format

The fold file format is designed to be easily understood by both humans and LLMs. It consists of the following structure:

1.  **Instructions:** The file begins with instructions for the LLM, explaining how to modify, delete, or add files.
2.  **File Sections:** The rest of the file is divided into sections, each representing a single file in the codebase. Each section starts with a line in the format `# --- File: <path> ---`, where `<path>` is the path relative to the CWD of the original `fold` command.

**Modifying Files:** To modify a file, keep its `# --- File: path ---` header and update the content below.

**Deleting Files:** To delete a file, replace its content with `# DELETE`.

**Adding New Files:** To add a new file, include a new `# --- File: path ---` section with the desired content.

**Ignoring Files:** Add patterns to a `.foldignore` file in the project root (e.g., `*.log` or `temp/`) to exclude files during folding.

**Important:** Preserve the `# --- File: path ---` format for all files.

## Example

Let's say you have a directory structure under `/home/user`:
```
/home/user/
├── my_project/
│   ├── main.py
│   ├── utils.py
│   └── .foldignore
```

With `.foldignore` containing:
```
my_project/utils.py
```

Running `cfold fold my_project -o folded.txt` from `/home/user` produces `folded.txt`:
```
