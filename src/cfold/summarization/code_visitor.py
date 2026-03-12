"""Visitor to collect code structure."""

from ast import NodeVisitor
from .get_docstring import get_docstring
from .get_annotation_str import get_annotation_str


class CodeVisitor(NodeVisitor):
    """Visitor to collect code structure."""

    def __init__(self):
        self.summary_lines = []
        self.current_class = None

    def visit_ClassDef(self, node):
        self.summary_lines.append(f"    Class: {node.name}")
        doc = get_docstring(node)
        if doc:
            self.summary_lines.append(f"      Doc: {doc}")
        self.current_class = node
        self.generic_visit(node)
        self.current_class = None

    def visit_FunctionDef(self, node):
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
