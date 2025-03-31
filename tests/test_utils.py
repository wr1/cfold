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

def test_should_include_file_with_ignore():
    """Test file inclusion with .foldignore patterns."""
    ignore_patterns = ["*.log", "temp/*", "secret.conf"]
    assert cfold.should_include_file("src/main.py", ignore_patterns) == True
    assert cfold.should_include_file("logs/app.log", ignore_patterns) == False
    assert cfold.should_include_file("temp/file.py", ignore_patterns) == False
    assert cfold.should_include_file("secret.conf", ignore_patterns) == False
    assert cfold.should_include_file("docs/index.md", ignore_patterns) == True

def test_load_foldignore(tmp_path):
    """Test loading and parsing .foldignore file."""
    ignore_file = tmp_path / ".foldignore"
    ignore_file.write_text("*.log\ntemp/*\n# comment\nsecret.conf\n")
    patterns = cfold.load_foldignore(str(tmp_path))
    assert patterns == ["*.log", "temp/*", "secret.conf"]

def test_apply_diff():
    """Test diff application for file modifications."""
    original = ["line1\n", "line2\n", "line3\n"]
    modified = ["line1\n", "new line2\n", "line3\n"]
    result = cfold.apply_diff(original, modified)
    assert result == "line1\nnew line2\nline3\n"
    modified = ["line1\n", "line2\n", "line3\n", "line4\n"]
    result = cfold.apply_diff(original, modified)
    assert result == "line1\nline2\nline3\nline4\n"