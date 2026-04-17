from pathlib import Path

import pytest

from cfold.summarization.sum_codebases import sum_codebases


def test_sum_codebases_invalid_path():
    """Test error on invalid codebase path."""
    with pytest.raises(ValueError):
        sum_codebases([Path("nonexistent")])
