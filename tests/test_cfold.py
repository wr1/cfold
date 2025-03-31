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

def test_fold(temp_project, tmp_path):
    """Test the fold function creates the correct output with specific files."""
    output_file = tmp_path / "folded.txt"
    os.chdir(tmp_path)  # Simulate running from tmp_path as CWD
    files = [str(temp_project / "main.py"), str(temp_project / "docs" / "index.md")]
    cfold.fold(files, str(output_file))
    assert output_file.exists()
    with open(output_file, "r", encoding="utf-8") as f:
        content = f.read()
    assert content.startswith("# Instructions for LLM:")
    assert "# --- File: project/main.py ---" in content
    assert 'print("Hello")' in content
    assert "# --- File: project/docs/index.md ---" in content
    assert "MD:# Docs" in content
    assert "utils.py" not in content  # Not included in files list

def test_fold_directory_default(temp_project, tmp_path):
    """Test folding the current directory when no files are specified."""
    output_file = tmp_path / "folded.txt"
    os.chdir(temp_project)  # Set CWD to project dir
    cfold.fold(None, str(output_file))
    assert output_file.exists()
    with open(output_file, "r", encoding="utf-8") as f:
        content = f.read()
    assert "# --- File: main.py ---" in content
    assert "# --- File: docs/index.md ---" in content
    assert "# --- File: utils.py ---" in content

def test_unfold_new_files(temp_project, tmp_path):
    """Test unfolding creates new files correctly using paths relative to CWD."""
    fold_file = tmp_path / "folded.txt"
    fold_file.write_text(
        "# Instructions for LLM:\n\n"
        "# --- File: project/new.py ---\n"
        "print('New file')\n\n"
        "# --- File: project/docs/new.md ---\n"
        "# New Doc\n\n"
    )
    os.chdir(tmp_path)  # Simulate running from tmp_path as CWD
    output_dir = tmp_path
    cfold.unfold(str(fold_file), None, str(output_dir))
    assert (output_dir / "project" / "new.py").exists()
    assert (output_dir / "project" / "new.py").read_text() == "print('New file')"
    assert (output_dir / "project" / "docs" / "new.md").exists()
    assert (output_dir / "project" / "docs" / "new.md").read_text() == "# New Doc"

def test_unfold_modify_and_delete(temp_project, tmp_path):
    """Test unfolding with modifications and deletions using paths relative to CWD."""
    fold_file = tmp_path / "folded.txt"
    fold_file.write_text(
        "# Instructions for LLM:\n\n"
        "# --- File: project/main.py ---\n"
        "print('Modified')\n\n"
        "# --- File: project/utils.py ---\n"
        "# DELETE\n\n"
    )
    os.chdir(tmp_path)  # Simulate running from tmp_path as CWD
    output_dir = tmp_path
    cfold.unfold(str(fold_file), str(temp_project), str(output_dir))
    assert (output_dir / "project" / "main.py").exists()
    assert (output_dir / "project" / "main.py").read_text() == "print('Modified')"
    assert not (output_dir / "project" / "utils.py").exists()
    assert (output_dir / "project" / "docs" / "index.md").exists()  # Copied from original

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