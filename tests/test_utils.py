from cfold.dialect.load_instructions import load_instructions
from cfold.dialect.list_available import list_available_dialects
from cfold.tree.build_folded import build_folded_tree
from cfold.models.codebase import Codebase
from cfold.models.file_entry import FileEntry
from cfold.models.instruction import Instruction
from pydantic import ValidationError
import pytest


def test_load_instructions():
    """Test loading instructions for a dialect."""
    instr, patterns = load_instructions("default")
    assert len(instr) > 0
    assert "included" in patterns


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
    FileEntry(path="test.py", content="code")
    # Invalid: missing content without delete
    with pytest.raises(ValidationError):
        FileEntry(path="test.py")
    # Valid delete
    FileEntry(path="test.py", delete=True)
    # Valid Codebase
    Codebase(instructions=[Instruction(type="system", content="test")], files=[])
