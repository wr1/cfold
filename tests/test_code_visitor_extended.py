"""Tests for code_visitor covering Import and ImportFrom branches."""

import ast

from cfold.summarization.code_visitor import code_visitor
from cfold.summarization.get_annotation_str import get_annotation_str


def test_visit_import():
    """Test visit_Import adds module names to imports."""
    source = "import os\nimport sys"
    tree = ast.parse(source)
    visitor = code_visitor()
    visitor.visit(tree)
    assert "os" in visitor.imports
    assert "sys" in visitor.imports


def test_visit_import_from():
    """Test visit_ImportFrom adds qualified names to imports."""
    source = "from pathlib import Path\nfrom typing import List"
    tree = ast.parse(source)
    visitor = code_visitor()
    visitor.visit(tree)
    assert "pathlib.Path" in visitor.imports
    assert "typing.List" in visitor.imports


def test_get_annotation_str_none():
    """Test get_annotation_str returns empty string for None."""
    assert get_annotation_str(None) == ""


def test_get_annotation_str_annotation():
    """Test get_annotation_str returns string for an annotation node."""
    source = "def f(x: int) -> str: pass"
    tree = ast.parse(source)
    func = tree.body[0]
    result = get_annotation_str(func.returns)
    assert result == "str"
