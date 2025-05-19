import pytest
import os
from pathlib import Path
from cfold import cfold


@pytest.fixture
def temp_project(tmp_path):
    """Create a temporary project directory with sample files."""
    proj_dir = tmp_path / "project"
    proj_dir.mkdir()
    (proj_dir / "main.py").write_text('print("Hello")\n')
    (proj_dir / "utils.py").write_text("def util():\n    pass\n")
    (proj_dir / "importer.py").write_text("import project.main\n")
    (proj_dir / "docs").mkdir()
    (proj_dir / "docs" / "index.md").write_text("# Docs\n")
    return proj_dir


def test_fold(temp_project, tmp_path):
    """Test the fold function creates the correct output with specific files."""
    output_file = tmp_path / "folded.txt"
    os.chdir(tmp_path)
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
    assert "utils.py" not in content


def test_fold_directory_default(temp_project, tmp_path):
    """Test folding the current directory when no files are specified."""
    output_file = tmp_path / "folded.txt"
    os.chdir(temp_project)
    cfold.fold(None, str(output_file))
    assert output_file.exists()
    with open(output_file, "r", encoding="utf-8") as f:
        content = f.read()
    assert "# --- File: main.py ---" in content
    assert "# --- File: docs/index.md ---" in content
    assert "# --- File: utils.py ---" in content


def test_fold_nodoc(temp_project, tmp_path):
    """Test folding with --nodoc excludes Markdown files."""
    output_file = tmp_path / "folded.txt"
    os.chdir(temp_project)
    cfold.fold(None, str(output_file), nodoc=True)
    assert output_file.exists()
    with open(output_file, "r", encoding="utf-8") as f:
        content = f.read()
    assert "# --- File: main.py ---" in content
    assert "# --- File: utils.py ---" in content
    assert "# --- File: importer.py ---" in content
    assert "# --- File: docs/index.md ---" not in content


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
    os.chdir(tmp_path)
    output_dir = tmp_path
    cfold.unfold(str(fold_file), None, str(output_dir))
    assert (output_dir / "project" / "new.py").exists()
    assert (
        output_dir / "project" / "new.py"
    ).read_text().strip() == "print('New file')"
    assert (output_dir / "project" / "docs" / "new.md").exists()
    assert (
        output_dir / "project" / "docs" / "new.md"
    ).read_text().strip() == "# New Doc"


def test_unfold_modify_and_delete(temp_project, tmp_path):
    """Test unfolding with modifications and deletions using full content."""
    fold_file = tmp_path / "folded.txt"
    fold_file.write_text(
        "# Instructions for LLM:\n\n"
        "# --- File: project/main.py ---\n"
        "print('Modified')\n"
        "# --- File: project/utils.py ---\n"
        "# DELETE\n\n"
    )
    os.chdir(tmp_path)
    output_dir = tmp_path
    cfold.unfold(str(fold_file), str(temp_project), str(output_dir))
    assert (output_dir / "project" / "main.py").exists()
    assert (
        output_dir / "project" / "main.py"
    ).read_text().strip() == "print('Modified')"
    assert not (output_dir / "project" / "utils.py").exists()
    assert (output_dir / "project" / "docs" / "index.md").exists()


def test_unfold_relocate_and_update_references(temp_project, tmp_path):
    """Test unfolding with file relocation and reference updates using delete and new file."""
    fold_file = tmp_path / "folded.txt"
    fold_file.write_text(
        "# Instructions for LLM:\n\n"
        "# --- File: project/main.py ---\n"
        "# DELETE\n"
        "# --- File: project/src/main.py ---\n"
        'print("Hello")\n'
        "# --- File: project/importer.py ---\n"
        "import project.src.main\n"
    )
    os.chdir(tmp_path)
    output_dir = tmp_path
    cfold.unfold(str(fold_file), str(temp_project), str(output_dir))
    assert (output_dir / "project" / "src" / "main.py").exists()
    assert (
        output_dir / "project" / "src" / "main.py"
    ).read_text().strip() == 'print("Hello")'
    assert not (output_dir / "project" / "main.py").exists()
    assert (
        output_dir / "project" / "importer.py"
    ).read_text().strip() == "import project.src.main"


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


def test_unfold_complex_full_content(temp_project, tmp_path):
    """Test unfolding a complex full-content file with delete and new file operations."""
    fold_file = tmp_path / "complex_full.txt"
    fold_file.write_text(
        "# Instructions for LLM:\n\n"
        "# --- File: project/main.py ---\n"
        'print("Modified Hello")\n'
        'print("Extra line")\n'
        "# --- File: project/utils.py ---\n"
        "# DELETE\n"
        "# --- File: project/src/utils.py ---\n"
        "def new_util():\n"
        "    return 42\n"
        "# --- File: project/importer.py ---\n"
        "from project.main import *\n"
        "print('Imported')\n"
        "# --- File: project/docs/index.md ---\n"
        "# DELETE\n"
        "# --- File: project/new_file.py ---\n"
        "print('Brand new file')\n"
    )
    os.chdir(tmp_path)
    output_dir = tmp_path
    cfold.unfold(str(fold_file), str(temp_project), str(output_dir))
    assert (
        output_dir / "project" / "main.py"
    ).read_text().strip() == 'print("Modified Hello")\nprint("Extra line")'
    assert (
        output_dir / "project" / "src" / "utils.py"
    ).read_text().strip() == "def new_util():\n    return 42"
    assert not (output_dir / "project" / "utils.py").exists()
    assert (
        output_dir / "project" / "importer.py"
    ).read_text().strip() == "from project.main import *\nprint('Imported')"
    assert not (output_dir / "project" / "docs" / "index.md").exists()
    assert (
        output_dir / "project" / "new_file.py"
    ).read_text().strip() == "print('Brand new file')"


def test_unfold_md_commands_not_interpreted(temp_project, tmp_path):
    """Test that MOVE and DELETE commands in .md files are not interpreted as instructions."""
    fold_file = tmp_path / "folded.txt"
    fold_file.write_text(
        "# Instructions for LLM:\n\n"
        "# --- File: project/docs/example.md ---\n"
        "MD:# Example\n"
        "MD:\n"
        "MD:Here's how to delete a file:\n"
        "MD:# DELETE\n"
        "# MOVE: project/main.py -> project/src/main.py\n"
    )
    os.chdir(tmp_path)
    output_dir = tmp_path
    cfold.unfold(str(fold_file), str(temp_project), str(output_dir))

    # Check example.md content (commands should be preserved as text)
    example_content = (output_dir / "project" / "docs" / "example.md").read_text()
    assert "# Example" in example_content

    # Check that no unintended deletions occurred
    assert (output_dir / "project" / "utils.py").exists()
