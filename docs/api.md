# API Reference

## `cfold.fold(directory=None, output="codefold.txt")`

Wrap a project into a single file with LLM instructions.

- **Args**:
  - `directory` (str): Directory to fold (default: current dir).
  - `output` (str): Output file path (default: "codefold.txt").

## `cfold.unfold(fold_file, original_dir=None, output_dir=None)`

Unfold a modified fold file into a directory, merging with the original if provided.

- **Args**:
  - `fold_file` (str): Path to the folded `.txt` file.
  - `original_dir` (str): Original project directory (optional).
  - `output_dir` (str): Output directory (default: current dir).

## `cfold.init(output="start.txt", custom_instruction="")`

Create an initial `.txt` template with LLM instructions.

- **Args**:
  - `output` (str): Output file path (default: "start.txt").
  - `custom_instruction` (str): Custom project purpose (default: "Describe the purpose of your project here.").