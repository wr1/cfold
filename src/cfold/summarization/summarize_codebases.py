"""Summarize Python codebases using AST for LLM-readable structure."""

import ast
import os
import sys
from pathlib import Path
from typing import List
from loguru import logger
from .code_visitor import code_visitor


def summarize_codebases(codebase_paths: List[Path], include_tests: bool = False) -> str:
    """Walk through codebases, parse Python files with AST, and generate a summary of code structure."""
    summary_lines = []
    excluded_dirs = {
        "venv",
        "build",
        "dist",
        "__pycache__",
        ".venv",
        ".git",
        "node_modules",
    }
    if not include_tests:
        excluded_dirs.add("tests")
        excluded_dirs.add("test")
    stdlib = set(sys.stdlib_module_names)
    valid_paths = [p for p in codebase_paths if p.is_dir()]
    if not valid_paths:
        raise ValueError("No valid directories provided")
    for codebase_path in valid_paths:
        logger.info(f"Navigating codebase: {codebase_path}")
        summary_lines.append(f"Codebase: {codebase_path}")
        for root, dirs, files in os.walk(codebase_path):
            # Prune excluded directories
            dirs[:] = [d for d in dirs if d not in excluded_dirs]
            for file in files:
                if file.endswith(".py"):
                    file_path = Path(root) / file
                    logger.info(f"Processing file: {file_path}")
                    try:
                        with open(file_path, "r", encoding="utf-8") as f:
                            source = f.read()
                        tree = ast.parse(source, filename=str(file_path))
                        rel_path = file_path.relative_to(codebase_path)
                        summary_lines.append(f"  - {rel_path}")
                        visitor = code_visitor()
                        visitor.visit(tree)
                        non_stdlib_imports = sorted(visitor.imports - stdlib)
                        if non_stdlib_imports:
                            summary_lines.append(f"    imports: {', '.join(non_stdlib_imports)}")
                        summary_lines.extend(visitor.summary_lines)
                    except SyntaxError:
                        logger.warning(f"Syntax error in {file_path}, skipped")
                        rel_path = file_path.relative_to(codebase_path)
                        summary_lines.append(
                            f"  - {rel_path} - Syntax error, skipped"
                        )
                    except Exception as e:
                        logger.error(f"Error processing {file_path}: {e}")
                        rel_path = file_path.relative_to(codebase_path)
                        summary_lines.append(f"  - {rel_path} - Error: {e}")
        summary_lines.append("")
    return "\n".join(summary_lines)
