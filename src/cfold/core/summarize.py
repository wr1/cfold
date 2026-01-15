"""Summarize Python codebases using AST for LLM-readable structure."""

import ast
import os
from pathlib import Path
from typing import List, Optional
from loguru import logger


def get_annotation_str(annotation):
    """Convert AST annotation to string."""
    if annotation is None:
        return ""
    return ast.unparse(annotation) if hasattr(ast, "unparse") else str(annotation)


def get_docstring(node: ast.AST) -> Optional[str]:
    """Extract docstring from a node if present."""
    if node.body and isinstance(node.body[0], ast.Expr):
        expr = node.body[0]
        if isinstance(expr.value, ast.Constant) and isinstance(expr.value.value, str):
            return expr.value.value
        elif isinstance(expr.value, ast.Str):  # For older Python
            return expr.value.s
    return None


class CodeVisitor(ast.NodeVisitor):
    """Visitor to collect code structure."""

    def __init__(self):
        self.summary_lines = []
        self.current_class = None

    def visit_ClassDef(self, node: ast.ClassDef):
        self.summary_lines.append(f"    Class: {node.name}")
        doc = get_docstring(node)
        if doc:
            self.summary_lines.append(f"      Doc: {doc}")
        self.current_class = node
        self.generic_visit(node)
        self.current_class = None

    def visit_FunctionDef(self, node: ast.FunctionDef):
        args = []
        for arg in node.args.args:
            arg_str = arg.arg
            if arg.annotation:
                arg_str += f": {get_annotation_str(arg.annotation)}"
            args.append(arg_str)
        returns = f" -> {get_annotation_str(node.returns)}" if node.returns else ""
        indent = "      " if self.current_class else "    "
        self.summary_lines.append(
            f"{indent}Func: {node.name}({', '.join(args)}){returns}"
        )
        doc = get_docstring(node)
        if doc:
            self.summary_lines.append(f"{indent}  Doc: {doc}")
        self.generic_visit(node)


def summarize_codebases(codebase_paths: List[Path], include_tests: bool = False) -> str:
    """Walk through codebases, parse Python files with AST, and generate a summary of code structure."""
    summary_lines = []
    excluded_dirs = {".venv", "venv", "__pycache__", "node_modules", ".git"}
    if not include_tests:
        excluded_dirs.add("tests")
        excluded_dirs.add("test")
    for codebase_path in codebase_paths:
        if not codebase_path.is_dir():
            raise ValueError(f"{codebase_path} is not a directory")
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
                        summary_lines.append(f"  File: {rel_path}")
                        visitor = CodeVisitor()
                        visitor.visit(tree)
                        summary_lines.extend(visitor.summary_lines)
                    except SyntaxError:
                        logger.warning(f"Syntax error in {file_path}, skipped")
                        summary_lines.append(
                            f"  File: {rel_path} - Syntax error, skipped"
                        )
                    except Exception as e:
                        logger.error(f"Error processing {file_path}: {e}")
                        summary_lines.append(f"  File: {rel_path} - Error: {e}")
        summary_lines.append("")
    return "\n".join(summary_lines)
