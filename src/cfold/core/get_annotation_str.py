"""Convert AST annotation to string."""

from ast import AST, unparse


def get_annotation_str(annotation):
    """Convert AST annotation to string."""
    if annotation is None:
        return ""
    return unparse(annotation) if hasattr(AST, "unparse") else str(annotation)
