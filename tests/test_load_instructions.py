from cfold.dialect.load_instructions import load_instructions


def test_load_instructions():
    """Test loading instructions for a dialect."""
    instr, patterns = load_instructions("default")
    assert len(instr) > 0
    assert len(patterns) > 0
