from pathlib import Path
import tempfile
from cfold.summarization.summarize_codebases import summarize_codebases


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
        assert "- main.py" in summary
        assert "function: greet(name: str) -> str - Greet someone." in summary
        assert "class: Greeter - A greeter class." in summary
        assert "function: __init__(self, name: str)" in summary
        assert "function: say_hello(self) -> str - Say hello." in summary
