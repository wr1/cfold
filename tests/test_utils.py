import pytest
from pydantic import ValidationError

from cfold.dialect.list_available import list_available_dialects
from cfold.dialect.load_instructions import load_instructions
from cfold.models.codebase import codebase
from cfold.models.file_entry import file_entry
from cfold.models.instruction import instruction
from cfold.tree.build_folded import build_folded_tree


def test_load_instructions():
    """Test loading instructions for a dialect."""
    instr, patterns = load_instructions("default")
    assert len(instr) > 0
    assert len(patterns) > 0


def test_load_instructions_invalid():
    """Test loading invalid dialect raises error."""
    with pytest.raises(ValueError):
        load_instructions("invalid")


def test_list_available_dialects():
    """Test getting available dialects."""
    dialects = list_available_dialects()
    assert "default" in dialects
    assert "py" in dialects


def test_build_folded_tree(tmp_path):
    """Test generating folded tree."""
    files = [tmp_path / "src" / "main.py", tmp_path / "docs" / "index.md"]
    tree = build_folded_tree(files, tmp_path)
    assert tree.label == "Folded files tree (total lines: 0)"


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
