from pathlib import Path
from typing import List
from ..models.codebase import codebase
from ..models.file_entry import file_entry
from ..models.instruction import instruction
from loguru import logger


def build_codebase(
    files: List[Path],
    instructions: List[instruction],
    prompt_content: str = "",
    cwd: Path = None,
) -> codebase:
    """Build a complete Codebase from files and instructions."""
    if cwd is None:
        cwd = Path.cwd()
    if prompt_content:
        instructions = instructions + [
            instruction(type="user", content=prompt_content, name="prompt")
        ]
    file_entries = []
    for f in files:
        try:
            content = f.read_text(encoding="utf-8")
            file_entries.append(
                file_entry(
                    path=str(f.resolve().relative_to(cwd.resolve())),
                    content=content,
                )
            )
        except UnicodeDecodeError:
            logger.warning(f"Skipping binary file: {f}")
            continue
    return codebase(
        instructions=instructions,
        files=file_entries,
    )
