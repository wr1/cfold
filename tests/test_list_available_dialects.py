from cfold.dialect.load_instructions import list_available_dialects


def test_list_available_dialects():
    """Test getting available dialects."""
    dialects = list_available_dialects()
    assert "default" in dialects
    assert "py" in dialects
