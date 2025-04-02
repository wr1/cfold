# API Reference

## `cfold.fold(files=None, output="codefold.txt", prompt_file=None)`

- `files`: Files or directory to fold (default: CWD).
- `output`: Output file (default: `codefold.txt`).
- `prompt_file`: Optional prompt file.

## `cfold.unfold(fold_file, original_dir=None, output_dir=None)`

- `fold_file`: The fold file to unfold.
- `original_dir`: Original directory to merge (optional).
- `output_dir`: Output directory (default: CWD).

## `cfold.init(output="start.txt", custom_instruction="")`

- `output`: Output file (default: `start.txt`).
- `custom_instruction`: Custom project purpose.
