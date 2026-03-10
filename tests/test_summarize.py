import pytest
from pathlib import Path
import tempfile
from cfold.core.summarize import summarize_codebases


def test_summarize_codebases_basic():
    """Test basic summarizing of a codebase with classes and functions."""
    with tempfile.TemporaryDirectory() as tmpdir:
        codebase_path = Path(tmpdir) / "test_codebase"
        codebase_path.mkdir()
        (codebase_path / "main.py").write_text(
            '''
"""Main module."""

def greet(name: str) -> str:
    """Greet someone."""
    return f"Hello {name}"

class Greeter:
    """A greeter class."""
    def __init__(self, name: str):
        self.name = name

    def say_hello(self) -> str:
        """Say hello."""
        return f"Hello {self.name}"
'''
        )
        summary = summarize_codebases([codebase_path])
        assert "Codebase:" in summary
        assert "File: main.py" in summary
        assert "Func: greet(name: str) -> str" in summary
        assert "Doc: Greet someone." in summary
        assert "Class: Greeter" in summary
        assert "Doc: A greeter class." in summary
        assert "Func: __init__(self, name: str)" in summary
        assert "Func: say_hello(self) -> str" in summary
        assert "Doc: Say hello." in summary


def test_summarize_codebases_multiple():
    """Test summarizing multiple codebases."""
    with tempfile.TemporaryDirectory() as tmpdir:
        cb1 = Path(tmpdir) / "cb1"
        cb1.mkdir()
        (cb1 / "func.py").write_text("def func(): pass")
        cb2 = Path(tmpdir) / "cb2"
        cb2.mkdir()
        (cb2 / "class.py").write_text("class C: pass")
        summary = summarize_codebases([cb1, cb2])
        assert "Codebase: " in summary
        assert "Func: func()" in summary
        assert "Class: C" in summary


def test_summarize_codebases_exclude_tests():
    """Test excluding test directories by default."""
    with tempfile.TemporaryDirectory() as tmpdir:
        codebase_path = Path(tmpdir) / "test_codebase"
        codebase_path.mkdir()
        (codebase_path / "main.py").write_text("def main(): pass")
        tests_dir = codebase_path / "tests"
        tests_dir.mkdir()
        (tests_dir / "test_main.py").write_text("def test_main(): pass")
        summary = summarize_codebases([codebase_path], include_tests=False)
        assert "Func: main()" in summary
        assert "Func: test_main()" not in summary


def test_summarize_codebases_include_tests():
    """Test including test directories when specified."""
    with tempfile.TemporaryDirectory() as tmpdir:
        codebase_path = Path(tmpdir) / "test_codebase"
        codebase_path.mkdir()
        (codebase_path / "main.py").write_text("def main(): pass")
        tests_dir = codebase_path / "tests"
        tests_dir.mkdir()
        (tests_dir / "test_main.py").write_text("def test_main(): pass")
        summary = summarize_codebases([codebase_path], include_tests=True)
        assert "Func: main()" in summary
        assert "Func: test_main()" in summary


def test_summarize_codebases_exclude_venv():
    """Test excluding .venv directory."""
    with tempfile.TemporaryDirectory() as tmpdir:
        codebase_path = Path(tmpdir) / "test_codebase"
        codebase_path.mkdir()
        (codebase_path / "main.py").write_text("def main(): pass")
        venv_dir = codebase_path / ".venv"
        venv_dir.mkdir()
        (venv_dir / "script.py").write_text("def script(): pass")
        summary = summarize_codebases([codebase_path])
        assert "Func: main()" in summary
        assert "Func: script()" not in summary


def test_summarize_codebases_invalid_path():
    """Test error on invalid codebase path."""
    with pytest.raises(ValueError):
        summarize_codebases([Path("nonexistent")])
