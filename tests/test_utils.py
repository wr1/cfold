import pytest
from cfold.utils import foldignore


def test_should_include_file():
    """Test file inclusion/exclusion rules."""
    assert (
        foldignore.should_include_file("src/main.py", suffixes=[".py", ".md", ".yml"])
        == True
    )
    assert (
        foldignore.should_include_file("docs/index.md", suffixes=[".py", ".md", ".yml"])
        == True
    )
    assert (
        foldignore.should_include_file("config.yml", suffixes=[".py", ".md", ".yml"])
        == True
    )
    assert (
        foldignore.should_include_file(
            "build/output.o", suffixes=[".py", ".md", ".yml"]
        )
        == False
    )
    assert (
        foldignore.should_include_file(
            "src/__pycache__/main.pyc", suffixes=[".py", ".md", ".yml"]
        )
        == False
    )
    assert (
        foldignore.should_include_file("test.txt", suffixes=[".py", ".md", ".yml"])
        == False
    )


def test_should_include_file_with_ignore():
    """Test file inclusion with .foldignore patterns."""
    ignore_patterns = ["*.log", "temp/*", "secret.conf"]
    assert foldignore.should_include_file("src/main.py", ignore_patterns) == True
    assert foldignore.should_include_file("logs/app.log", ignore_patterns) == False
    assert foldignore.should_include_file("temp/file.py", ignore_patterns) == False
    assert foldignore.should_include_file("secret.conf", ignore_patterns) == False
    assert foldignore.should_include_file("docs/index.md", ignore_patterns) == True


def test_load_foldignore(tmp_path):
    """Test loading and parsing .foldignore file."""
    ignore_file = tmp_path / ".foldignore"
    ignore_file.write_text("*.log\ntemp/*\n# comment\nsecret.conf\n")
    patterns = foldignore.load_foldignore(str(tmp_path))
    assert patterns == ["*.log", "temp/*", "secret.conf"]
