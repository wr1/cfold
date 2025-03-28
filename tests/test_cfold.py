import pytest
import os
from pathlib import Path
from cfold import cfold

# Test suite for cfold main functionality


@pytest.fixture
def temp_project(tmp_path):
    """Create a temporary project directory with sample files."""
    proj_dir = tmp_path / "project"
    proj_dir.mkdir()
    (proj_dir / "main.py").write_text('print("Hello")')
    (proj_dir / "utils.py").write_text("def util():\n    pass")
    (proj_dir / "docs").mkdir()
    (proj_dir / "docs" / "index.md").write_text("# Docs")
    return proj_dir


@pytest.fixture
def folded_content():
    """Expected folded content for a basic project."""
    return (
        "# Instructions for LLM:\n"
        "# - To modify a file, keep its '# --- File: path ---' header and update the content below.\n"
        "# - To delete a file, replace its content with '# DELETE'.\n"
        "# - To add a new file, include a new '# --- File: path ---' section with the desired content.\n"
        "# - Preserve the '# --- File: path ---' format for all files.\n\n"
        "# --- File: main.py ---\n"
        'print("Hello")\n\n'
        "# --- File: utils.py ---\n"
        "def util():\n    pass\n\n"
        "# --- File: docs/index.md ---\n"
        "# Docs\n\n"
    )


def test_fold(temp_project, tmp_path):
    """Test the fold function creates the correct output."""
    output_file = tmp_path / "folded.txt"
    cfold.fold(str(temp_project), str(output_file))
    assert output_file.exists()
    with open(output_file, "r", encoding="utf-8") as f:
        content = f.read()
    assert content.startswith("# Instructions for LLM:")
    assert "# --- File: main.py ---" in content
    assert 'print("Hello")' in content
    assert "# --- File: docs/index.md ---" in content


def test_unfold_new_files(temp_project, tmp_path):
    """Test unfolding creates new files correctly."""
    fold_file = tmp_path / "folded.txt"
    fold_file.write_text(
        "# Instructions for LLM:\n\n"
        "# --- File: new.py ---\n"
        "print('New file')\n\n"
        "# --- File: docs/new.md ---\n"
        "# New Doc\n\n"
    )
    output_dir = tmp_path / "output"
    cfold.unfold(str(fold_file), None, str(output_dir))
    assert (output_dir / "new.py").exists()
    assert (output_dir / "new.py").read_text() == "print('New file')"
    assert (output_dir / "docs" / "new.md").exists()
    assert (output_dir / "docs" / "new.md").read_text() == "# New Doc"


def test_unfold_modify_and_delete(temp_project, tmp_path):
    """Test unfolding with modifications and deletions."""
    fold_file = tmp_path / "folded.txt"
    fold_file.write_text(
        "# Instructions for LLM:\n\n"
        "# --- File: main.py ---\n"
        "print('Modified')\n\n"
        "# --- File: utils.py ---\n"
        "# DELETE\n\n"
    )
    output_dir = tmp_path / "output"
    cfold.unfold(str(fold_file), str(temp_project), str(output_dir))
    assert (output_dir / "main.py").exists()
    assert (output_dir / "main.py").read_text() == "print('Modified')"
    assert not (output_dir / "utils.py").exists()
    assert (output_dir / "docs" / "index.md").exists()  # Copied from original


def test_init(tmp_path):
    """Test init creates a template with custom instruction."""
    output_file = tmp_path / "start.txt"
    custom = "Test custom instruction"
    cfold.init(str(output_file), custom)
    assert output_file.exists()
    content = output_file.read_text()
    assert "Instructions for LLM:" in content
    assert "Create a Poetry-managed Python project" in content
    assert custom in content
