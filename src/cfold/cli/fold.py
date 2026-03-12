from pathlib import Path
from typing import List
import yaml
import glob
from rich.console import Console
from rich.tree import Tree
from ..fold.build_codebase import build_codebase
from ..fold.filter_files import filter_files
from ..fold.write_json import write_json
from ..tree.build_folded import build_folded_tree
from ..dialect.list_available import list_available_dialects
from ..dialect.load_instructions import load_instructions


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
        instructions, include_patterns = load_instructions(dialect, cwd) if not bare else ([], [])
    except ValueError:
        if dialect == "default":
            console.print("Default dialect not found, falling back to bare mode.")
            instructions, include_patterns = [], []
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
    if not files:
        filtered = filter_files(include_patterns, cwd)
        filtered = [f for f in filtered if f.name != output]
    else:
        file_paths = []
        for f in files:
            if '*' in f or '?' in f:
                file_paths.extend(cwd / p for p in glob.glob(f, root_dir=str(cwd), recursive=True) if (cwd / p).is_file())
            else:
                path = cwd / f
                if path.is_file():
                    file_paths.append(path)
        filtered = filter_files(include_patterns, cwd, file_paths)
    if not filtered:
        console.print("No valid files to fold.")
        return
    prompt_content = Path(prompt).read_text(encoding="utf-8") if prompt and Path(prompt).exists() else ""
    if prompt and not Path(prompt).exists():
        console.print(f"Warning: Prompt file '{prompt}' does not exist. Skipping.")
    codebase = build_codebase(filtered, instructions, prompt_content, cwd)
    tree = build_folded_tree(filtered, cwd)
    console.print(tree)
    write_json(codebase, output_path, clip)
