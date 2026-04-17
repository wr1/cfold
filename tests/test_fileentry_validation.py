import pytest
from pydantic import ValidationError

from cfold.models.file_entry import file_entry


def test_fileentry_validation():
    """Test FileEntry validation."""
    # Valid with content
    entry = file_entry(path="file.py", content="content")
    assert entry.delete is False
    assert entry.content == "content"

    # Valid delete without content
    entry = file_entry(path="file.py", delete=True)
    assert entry.delete is True
    assert entry.content is None

    # Invalid: no content and not delete
    with pytest.raises(ValidationError):
        file_entry(path="file.py")

    # Invalid: delete with content (but allowed, as per model)
    entry = file_entry(path="file.py", delete=True, content="ignored")
    assert entry.content == "ignored"
