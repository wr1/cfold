"""Extract docstring from a node if present."""

from ast import Expr, Constant


def get_docstring(node):
    """Extract docstring from a node if present."""
    if node.body and isinstance(node.body[0], Expr):
        expr = node.body[0]
        if isinstance(expr.value, Constant) and isinstance(expr.value.value, str):
            return expr.value.value
    return None
