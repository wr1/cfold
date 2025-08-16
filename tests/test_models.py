from cfold.models import Codebase, FileEntry, Instruction
from pydantic import ValidationError
import pytest


def test_fileentry_validation():
    """Test FileEntry validation."""
    # Valid with content
    entry = FileEntry(path="file.py", content="content")
    assert entry.delete is False
    assert entry.content == "content"

    # Valid delete without content
    entry = FileEntry(path="file.py", delete=True)
    assert entry.delete is True
    assert entry.content is None

    # Invalid: no content and not delete
    with pytest.raises(ValidationError):
        FileEntry(path="file.py")

    # Invalid: delete with content (but allowed, as per model)
    entry = FileEntry(path="file.py", delete=True, content="ignored")
    assert entry.content == "ignored"


def test_instruction():
    """Test Instruction model."""
    instr = Instruction(type="system", content="content", name="test", synopsis="syn")
    assert instr.type == "system"
    assert instr.synopsis == "syn"  # Internal field


def test_codebase():
    """Test Codebase model."""
    codebase = Codebase(
        instructions=[Instruction(type="user", content="prompt")],
        files=[FileEntry(path="file.py", content="code")],
    )
    dumped = codebase.model_dump(exclude={"instructions": {"__all__": {"synopsis"}}})
    assert "synopsis" not in dumped["instructions"][0]

    # Test validator for instructions as dict (though not typically used)
    codebase = Codebase.model_validate({"instructions": [], "files": []})
    assert isinstance(codebase.instructions, list)
