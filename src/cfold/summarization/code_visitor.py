"""Visitor to collect code structure."""

from ast import NodeVisitor
from .get_docstring import get_docstring
from .get_annotation_str import get_annotation_str


class code_visitor(NodeVisitor):
    """Visitor to collect code structure."""

    def __init__(self):
        self.summary_lines = []
        self.current_class = None
        self.imports = set()

    def visit_Import(self, node):
        for alias in node.names:
            self.imports.add(alias.name)
        self.generic_visit(node)

    def visit_ImportFrom(self, node):
        for alias in node.names:
            full = f"{node.module}.{alias.name}" if node.module else alias.name
            self.imports.add(full)
        self.generic_visit(node)

    def visit_ClassDef(self, node):
        doc = get_docstring(node)
        line = f"    cls: {node.name}"
        if doc:
            line += f" - {doc}"
        self.summary_lines.append(line)
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
        doc = get_docstring(node)
        line = f"{indent}fn: {node.name}({', '.join(args)}){returns}"
        if doc:
            line += f" - {doc}"
        self.summary_lines.append(line)
        self.generic_visit(node)
