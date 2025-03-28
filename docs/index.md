# cfold Documentation

`cfold` is a command-line tool that helps you prepare Python codebases for interaction with Large Language Models (LLMs). It "folds" a directory into a single text file and "unfolds" a modified version back into a directory structure, making it easy to manage project context for LLMs.

## Features

- **Fold**: Combine a codebase into a single `.txt` file with LLM instructions.
- **Unfold**: Apply changes from a modified `.txt` back to a directory, merging with the original if provided.
- **Init**: Generate a starting `.txt` template with setup guidance and custom instructions.
- Supports Poetry projects, GitHub CI workflows, and MkDocs documentation.

See [Usage](usage.md) for commands and [API](api.md) for technical details.