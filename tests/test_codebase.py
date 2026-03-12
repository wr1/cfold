from cfold.models.codebase import codebase
from cfold.models.file_entry import file_entry
from cfold.models.instruction import instruction


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
