import glob
import json
from pathlib import Path
from typing import List

import pyperclip
from loguru import logger
from rich.console import Console

from ..models.codebase import codebase
from ..models.file_entry import file_entry
from ..models.instruction import instruction


def filter_files(
    include_patterns: List[str], cwd: Path, files: List[Path] | None = None
) -> List[Path]:
    """Return files that match any include pattern."""
    if files is not None:
        filtered = [f for f in files if any(f.relative_to(cwd).match(p) for p in include_patterns)]
        return filtered
    matched = set()
    for pattern in include_patterns:
        for path_str in glob.glob(pattern, root_dir=str(cwd), recursive=True):
            path = cwd / path_str
            if path.is_file():
                matched.add(path)
    return list(matched)


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
                    path=str(f.resolve().relative_to(cwd.resolve()))
                    if f.resolve().is_relative_to(cwd.resolve())
                    else str(f.resolve()),
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


def write_json(cb: codebase, output: Path, clip: bool = False) -> None:
    """Write folded codebase to JSON."""
    console = Console()
    with open(output, "w", encoding="utf-8") as f:
        json.dump(cb.model_dump(), f, indent=2)
    if clip:
        pyperclip.copy(json.dumps(cb.model_dump()))
    console.print(
        f"Codebase folded into [cyan]{output}[/cyan]"
        + (" and copied to clipboard" if clip else ".")
    )
