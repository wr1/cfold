import pytest
from cfold import cfold

# Test suite for cfold utility functions


def test_should_include_file():
    """Test file inclusion/exclusion rules."""
    assert cfold.should_include_file("src/main.py") == True
    assert cfold.should_include_file("docs/index.md") == True
    assert cfold.should_include_file("config.yml") == True
    assert cfold.should_include_file("build/output.o") == False
    assert cfold.should_include_file("src/__pycache__/main.pyc") == False
    assert cfold.should_include_file("test.txt") == False


def test_apply_diff():
    """Test diff application for file modifications."""
    original = ["line1\n", "line2\n", "line3\n"]
    modified = ["line1\n", "new line2\n", "line3\n"]
    result = cfold.apply_diff(original, modified)
    assert result == "line1\nnew line2\nline3\n"
    # Test adding a line
    modified = ["line1\n", "line2\n", "line3\n", "line4\n"]
    result = cfold.apply_diff(original, modified)
    assert result == "line1\nline2\nline3\nline4\n"
