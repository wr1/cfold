from cfold.utils import foldignore


def test_should_include_file():
    """Test file inclusion/exclusion rules."""
    assert (
        foldignore.should_include_file("src/main.py", included_patterns=["*.py", "*.md", "*.yml"])
        is True
    )
    assert (
        foldignore.should_include_file("docs/index.md", included_patterns=["*.py", "*.md", "*.yml"])
        is True
    )
    assert (
        foldignore.should_include_file("config.yml", included_patterns=["*.py", "*.md", "*.yml"])
        is True
    )
    assert (
        foldignore.should_include_file(
            "build/output.o", included_patterns=["*.py", "*.md", "*.yml"]
        )
        is False
    )
    assert (
        foldignore.should_include_file(
            "src/__pycache__/main.pyc", included_patterns=["*.py", "*.md", "*.yml"]
        )
        is False
    )
    assert (
        foldignore.should_include_file("test.txt", included_patterns=["*.py", "*.md", "*.yml"])
        is False
    )


def test_should_include_file_with_ignore():
    """Test file inclusion with .foldignore patterns."""
    ignore_patterns = ["*.log", "temp/*", "secret.conf"]
    assert foldignore.should_include_file("src/main.py", ignore_patterns) is True
    assert foldignore.should_include_file("logs/app.log", ignore_patterns) is False
    assert foldignore.should_include_file("temp/file.py", ignore_patterns) is False
    assert foldignore.should_include_file("secret.conf", ignore_patterns) is False
    assert foldignore.should_include_file("docs/index.md", ignore_patterns) is True


def test_load_foldignore(tmp_path):
    """Test loading and parsing .foldignore file."""
    ignore_file = tmp_path / ".foldignore"
    ignore_file.write_text("*.log\ntemp/*\n# comment\nsecret.conf\n")
    patterns = foldignore.load_foldignore(str(tmp_path))
    assert patterns == ["*.log", "temp/*", "secret.conf"]


