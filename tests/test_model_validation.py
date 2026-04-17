import pytest
from pydantic import ValidationError

from cfold.models.codebase import codebase
from cfold.models.file_entry import file_entry
from cfold.models.instruction import instruction


def test_model_validation():
    """Test Pydantic model validation."""
    # Valid FileEntry
    file_entry(path="test.py", content="code")
    # Invalid: missing content without delete
    with pytest.raises(ValidationError):
        file_entry(path="test.py")
    # Valid delete
    file_entry(path="test.py", delete=True)
    # Valid Codebase
    codebase(instructions=[instruction(type="system", content="test")], files=[])
