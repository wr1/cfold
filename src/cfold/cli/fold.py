import glob
from pathlib import Path
from typing import List

import yaml
from rich.console import Console
from rich.tree import Tree

from ..dialect.load_instructions import list_available_dialects, load_instructions
from ..fold.fold import build_codebase, filter_files, write_json
from ..tree.build_folded import build_folded_tree


def fold(
    files: List[str],
    output: str = "codefold.json",
    prompt: str = None,
    dialect: str = "default",
    bare: bool = False,
    clip: bool = False,
):
    """Fold files or directory into a single file."""
    console = Console()
    cwd = Path.cwd()
    output_path = Path(output)
    if dialect == "default":
        local_path = cwd / ".foldrc"
        if local_path.exists():
            with local_path.open("r", encoding="utf-8") as f:
                local = yaml.safe_load(f) or {}
                if "default_dialect" in local:
                    dialect = local["default_dialect"]
    try:
        instructions, include_patterns = (
            load_instructions(dialect, cwd)
            if not bare
            else ([], load_instructions("default", cwd)[1])
        )
    except ValueError:
        if dialect == "default":
            console.print("Default dialect not found, falling back to bare mode.")
            instructions, include_patterns = [], load_instructions("default", cwd)[1]
            bare = True
        else:
            available = list_available_dialects()
            console.print(f"Invalid dialect. Available: {', '.join(available)}", style="red")
            raise SystemExit(1)
    if bare:
        console.print("[orange]Using bare mode[/orange]")
    else:
        console.print(f"[orange]Using dialect: {dialect}[/orange]")
        instr_tree = Tree("Instructions")
        for instr in instructions:
            label = f"{instr.type}"
            if instr.name:
                label += f" ({instr.name})"
            if instr.synopsis:
                label += f" - {instr.synopsis}"
            instr_tree.add(label)
        console.print(instr_tree)
    dirs = [f for f in files if Path(f).is_dir()]
    non_dirs = [f for f in files if f not in dirs]
    actual_files = [f for f in non_dirs if (cwd / f).is_file() or Path(f).is_file()]
    glob_patterns = [f for f in non_dirs if f not in actual_files]

    if files:
        filtered = []
        for d in dirs:
            dir_path = cwd / d
            filtered.extend(filter_files(include_patterns, dir_path))
        for f in actual_files:
            path = Path(f) if Path(f).is_absolute() else cwd / f
            if path.is_file():
                filtered.append(path)
        for f in glob_patterns:
            pattern = f
            if "**" in f and "/" not in f and f.startswith("**"):
                suffix = f[2:]
                pattern = f"**/*{suffix}"
            for path_str in glob.glob(pattern, root_dir=str(cwd), recursive=True):
                path = cwd / path_str
                if path.is_file():
                    filtered.append(path)
        filtered = [f for f in filtered if f.name != output]
    else:
        filtered = filter_files(include_patterns, cwd)
        filtered = [f for f in filtered if f.name != output]
    if not filtered:
        console.print("No valid files to fold.")
        return
    prompt_content = (
        Path(prompt).read_text(encoding="utf-8") if prompt and Path(prompt).exists() else ""
    )
    if prompt and not Path(prompt).exists():
        console.print(f"Warning: Prompt file '{prompt}' does not exist. Skipping.")
    codebase = build_codebase(filtered, instructions, prompt_content, cwd)
    tree = build_folded_tree(filtered, cwd)
    console.print(tree)
    write_json(codebase, output_path, clip)
