import tempfile
from pathlib import Path

from cfold.summarization.sum_codebases import sum_codebases


def test_sum_codebases_basic():
    """Test basic summing of a codebase with classes and functions."""
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
        summary, _ = sum_codebases([codebase_path])
        assert "Codebase:" in summary
        assert "- main.py" in summary
        assert "fn: greet(name: str) -> str - Greet someone." in summary
        assert "cls: Greeter - A greeter class." in summary
        assert "fn: __init__(self, name: str)" in summary
        assert "fn: say_hello(self) -> str - Say hello." in summary
