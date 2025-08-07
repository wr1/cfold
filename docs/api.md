# API Reference

This page documents the core models and utilities in the `cfold` module. Note: `cfold` is primarily a CLI tool; for CLI usage, see [Usage](/usage). The Python API focuses on data models for advanced usage.

## Models (`cfold.models`)

### `Instruction`

Represents an instruction for the LLM.

- `type`: str (e.g., `'system'`, `'user'`, `'assistant'`)
- `content`: str (the instruction text)
- `name`: Optional[str] (optional name for the instruction)
- `synopsis`: Optional[str] (internal synopsis, not serialized)

### `FileEntry`

Represents a file in the codebase.

- `path`: str (relative path to the file)
- `content`: Optional[str] (full file content; required unless deleting)
- `delete`: bool (set to `true` to delete the file; default: `false`)

Validation: If `delete` is `false`, `content` must be provided.

### `Codebase`

Represents the full codebase structure.

- `instructions`: List[Instruction] (list of instructions)
- `files`: List[FileEntry] (list of file entries)

Serialization: Use `model_dump()` to get a dict, excluding internal fields like `synopsis`.

## Utilities

- `cfold.utils.instructions.load_instructions(dialect: str)`: Load instructions and patterns for a dialect.
- `cfold.utils.foldignore.should_include_file(...)`: Check if a file should be included based on patterns.

For CLI commands, refer to the [Usage](/usage) page.



