"""Convert AST annotation to string."""

import ast
from ast import AST


def get_annotation_str(annotation):
    """Convert AST annotation to string."""
    if annotation is None:
        return ""
    return ast.unparse(annotation) if hasattr(ast, "unparse") else str(annotation)
