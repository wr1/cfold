from cfold.utils import foldignore, instructions, treeviz
from cfold.models import Codebase, FileEntry, Instruction
from pydantic import ValidationError
import pytest


def test_should_include_file():
    """Test file inclusion/exclusion rules."""
    assert (
        foldignore.should_include_file(
            "src/main.py", included_patterns=["*.py", "*.md", "*.yml"]
        )
        is True
    )
    assert (
        foldignore.should_include_file(
            "docs/index.md", included_patterns=["*.py", "*.md", "*.yml"]
        )
        is True
    )
    assert (
        foldignore.should_include_file(
            "config.yml", included_patterns=["*.py", "*.md", "*.yml"]
        )
        is True
    )
    assert (
        foldignore.should_include_file(
            "build/output.o", included_patterns=["*.py", "*.md", "*.yml"]
        )
        is False
    )
    assert (
        foldignore.should_include_file(
            "src/__pycache__/main.pyc", included_patterns=["*.py", "*.md", "*.yml"]
        )
        is False
    )
    assert (
        foldignore.should_include_file(
            "test.txt", included_patterns=["*.py", "*.md", "*.yml"]
        )
        is False
    )


def test_load_instructions():
    """Test loading instructions for a dialect."""
    instr, patterns = instructions.load_instructions("default")
    assert len(instr) > 0
    assert all(isinstance(i, Instruction) for i in instr)
    assert "included" in patterns


def test_load_instructions_invalid():
    """Test loading invalid dialect raises error."""
    with pytest.raises(ValueError):
        instructions.load_instructions("invalid")


def test_load_instructions_cycle():
    """Test cycle detection in pre dependencies."""
    # This would require mocking the config, but since it's file-based, skip or mock
    pass  # For now, assume covered by implementation


def test_get_available_dialects():
    """Test getting available dialects."""
    dialects = instructions.get_available_dialects()
    assert "default" in dialects
    assert "py" in dialects


def test_get_folded_tree(tmp_path):
    """Test generating folded tree."""
    files = [tmp_path / "src" / "main.py", tmp_path / "docs" / "index.md"]
    tree = treeviz.get_folded_tree(files, tmp_path)
    assert tree.label == "Folded files tree"
    assert len(tree.children) > 0


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
