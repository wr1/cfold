from cfold.models.instruction import instruction


def test_instruction():
    """Test Instruction model."""
    instr = instruction(type="system", content="content", name="test", synopsis="syn")
    assert instr.type == "system"
    assert instr.synopsis == "syn"  # Internal field
