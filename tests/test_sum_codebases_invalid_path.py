from pathlib import Path
from cfold.summarization.sum_codebases import sum_codebases
import pytest


def test_sum_codebases_invalid_path():
    """Test error on invalid codebase path."""
    with pytest.raises(ValueError):
        sum_codebases([Path("nonexistent")])
