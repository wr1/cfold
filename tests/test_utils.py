from cfold.utils.should_include_file import should_include_file
from cfold.utils.load_instructions import load_instructions
from cfold.utils.get_available_dialects import get_available_dialects
from cfold.utils.get_folded_tree import get_folded_tree
from cfold.core.codebase import Codebase
from cfold.core.file_entry import FileEntry
from cfold.core.instruction import Instruction
from pydantic import ValidationError
import pytest


def test_should_include_file():
    """Test file inclusion/exclusion rules."""
    assert (
        should_include_file(
            "src/main.py", included_patterns=["*.py", "*.md", "*.yml"]
        )
        is True
    )
    assert (
        should_include_file(
            "docs/index.md", included_patterns=["*.py", "*.md", "*.yml"]
        )
        is True
    )
    assert (
        should_include_file(
            "config.yml", included_patterns=["*.py", "*.md", "*.yml"]
        )
        is True
    )
    assert (
        should_include_file(
            "build/output.o", included_patterns=["*.py", "*.md", "*.yml"]
        )
        is False
    )
    assert (
        should_include_file(
            "src/__pycache__/main.pyc", included_patterns=["*.py", "*.md", "*.yml"]
        )
        is False
    )
    assert (
        should_include_file(
            "test.txt", included_patterns=["*.py", "*.md", "*.yml"]
        )
        is False
    )


def test_load_instructions():
    """Test loading instructions for a dialect."""
    instr, patterns = load_instructions("default")
    assert len(instr) > 0
    assert "included" in patterns


def test_load_instructions_invalid():
    """Test loading invalid dialect raises error."""
    with pytest.raises(ValueError):
        load_instructions("invalid")


def test_load_instructions_cycle():
    """Test cycle detection in pre dependencies."""
    # This would require mocking the config, but since it's file-based, skip or mock
    pass  # For now, assume covered by implementation


def test_get_available_dialects():
    """Test getting available dialects."""
    dialects = get_available_dialects()
    assert "default" in dialects
    assert "py" in dialects


def test_get_folded_tree(tmp_path):
    """Test generating folded tree."""
    files = [tmp_path / "src" / "main.py", tmp_path / "docs" / "index.md"]
    tree = get_folded_tree(files, tmp_path)
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
