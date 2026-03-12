from pathlib import Path
from cfold.summarization.summarize_codebases import summarize_codebases
import pytest


def test_summarize_codebases_invalid_path():
    """Test error on invalid codebase path."""
    with pytest.raises(ValueError):
        summarize_codebases([Path("nonexistent")])
