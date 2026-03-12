from cfold.models.codebase import codebase
from cfold.models.file_entry import file_entry
from cfold.models.instruction import instruction
from pydantic import ValidationError
import pytest


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


def test_instruction():
    """Test Instruction model."""
    instr = instruction(type="system", content="content", name="test", synopsis="syn")
    assert instr.type == "system"
    assert instr.synopsis == "syn"  # Internal field


def test_codebase():
    """Test Codebase model."""
    codebase_instance = codebase(
        instructions=[instruction(type="user", content="prompt")],
        files=[file_entry(path="file.py", content="code")],
    )
    dumped = codebase_instance.model_dump(
        exclude={"instructions": {"__all__": {"synopsis"}}}
    )
    assert "synopsis" not in dumped["instructions"][0]

    # Test validator for instructions as dict (though not typically used)
    codebase_instance = codebase.model_validate({"instructions": [], "files": []})
    assert isinstance(codebase_instance.instructions, list)


def test_codebase_with_role_instructions():
    """Test Codebase validation with instructions using 'type' field."""
    data = {
        "instructions": [
            {"type": "system", "content": "System prompt"},
            {"type": "user", "content": "User prompt", "synopsis": "User focus"},
        ],
        "files": [{"path": "test.py", "content": "code"}],
    }
    codebase_instance = codebase.model_validate(data)
    assert len(codebase_instance.instructions) == 2
    assert codebase_instance.instructions[0].type == "system"
    assert codebase_instance.instructions[1].synopsis == "User focus"
