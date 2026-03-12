from pathlib import Path
import json
from typing import List
from rich.console import Console
from ..models.codebase import Codebase
from ..models.file_entry import FileEntry
from ..models.instruction import Instruction
from loguru import logger


def build_codebase(
    files: List[Path],
    instructions: List[Instruction],
    prompt_content: str = "",
    cwd: Path = None,
) -> Codebase:
    """Build a complete Codebase from files and instructions."""
    if cwd is None:
        cwd = Path.cwd()
    if prompt_content:
        instructions = instructions + [Instruction(type="user", content=prompt_content, name="prompt")]
    file_entries = []
    for f in files:
        try:
            content = f.read_text(encoding="utf-8")
            file_entries.append(
                FileEntry(
                    path=str(f.resolve().relative_to(cwd.resolve())),
                    content=content,
                )
            )
        except UnicodeDecodeError:
            logger.warning(f"Skipping binary file: {f}")
            continue
    return Codebase(
        instructions=instructions,
        files=file_entries,
    )
