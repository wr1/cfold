from pathlib import Path
import ast


def update_references(modified_files, moves, cwd):
    """Update file references in Python files affected by moves."""
    for old_path, new_path in moves.items():
        old_relpath = Path(old_path)
        new_relpath = Path(new_path)
        old_module = ".".join(old_relpath.with_suffix("").parts)
        new_module = ".".join(new_relpath.with_suffix("").parts)

        for filepath, content in modified_files.items():
            if filepath.endswith(".py") and content != "# DELETE":
                try:
                    tree = ast.parse(content)

                    class ImportVisitor(ast.NodeVisitor):
                        def __init__(self):
                            self.changes = []

                        def visit_Import(self, node):
                            for alias in node.names:
                                if alias.name == old_module:
                                    self.changes.append(
                                        (node.lineno, f"import {new_module}")
                                    )
                            self.generic_visit(node)

                        def visit_ImportFrom(self, node):
                            if node.module == old_module:
                                names = ", ".join(alias.name for alias in node.names)
                                self.changes.append(
                                    (node.lineno, f"from {new_module} import {names}")
                                )
                            self.generic_visit(node)

                    visitor = ImportVisitor()
                    visitor.visit(tree)
                    if visitor.changes:
                        lines = content.splitlines(keepends=True)
                        for lineno, new_line in sorted(visitor.changes, reverse=True):
                            lines[lineno - 1] = new_line + "\n"
                        modified_files[filepath] = "".join(lines)
                except SyntaxError:
                    print(f"Warning: Could not parse {filepath} for reference updates.")
