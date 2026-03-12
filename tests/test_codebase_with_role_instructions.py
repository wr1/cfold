from cfold.models.codebase import codebase
from cfold.models.file_entry import file_entry


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
