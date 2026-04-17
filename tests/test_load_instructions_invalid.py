import pytest

from cfold.dialect.load_instructions import load_instructions


def test_load_instructions_invalid():
    """Test loading invalid dialect raises error."""
    with pytest.raises(ValueError):
        load_instructions("invalid")
