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
    assert (output_dir / "project" / "new.py").read_text() == "print('New file')\n"
    assert (output_dir / "project" / "docs" / "new.md").exists()
    assert (output_dir / "project" / "docs" / "new.md").read_text() == "# New Doc\n"


def test_unfold_modify_and_delete(temp_project, tmp_path):
    """Test unfolding with modifications and deletions using paths relative to CWD."""
    fold_file = tmp_path / "folded.txt"
    fold_file.write_text(
        "# Instructions for LLM:\n\n"
        "# --- File: project/main.py ---\n"
        "--- main.py\n"
        "+++ main.py\n"
        "@@ -1 +1 @@\n"
        '-print("Hello")\n'
        '+print("Modified")\n'
        "# --- File: project/utils.py ---\n"
        "# DELETE\n\n"
    )
    os.chdir(tmp_path)
    output_dir = tmp_path
    cfold.unfold(str(fold_file), str(temp_project), str(output_dir))
    assert (output_dir / "project" / "main.py").exists()
    assert (output_dir / "project" / "main.py").read_text() == 'print("Modified")'
    assert not (output_dir / "project" / "utils.py").exists()
    assert (output_dir / "project" / "docs" / "index.md").exists()


def test_unfold_move_and_update_references(temp_project, tmp_path):
    """Test unfolding with file moves and reference updates."""
    fold_file = tmp_path / "folded.txt"
    fold_file.write_text(
        "# Instructions for LLM:\n\n"
        "# MOVE: project/main.py -> project/src/main.py\n"
        "# --- File: project/importer.py ---\n"
        "--- importer.py\n"
        "+++ importer.py\n"
        "@@ -1 +1 @@\n"
        "-import project.main\n"
        "+import project.src.main\n"
    )
    os.chdir(tmp_path)
    output_dir = tmp_path
    cfold.unfold(str(fold_file), str(temp_project), str(output_dir))
    assert (output_dir / "project" / "src" / "main.py").exists()
    assert (
        output_dir / "project" / "src" / "main.py"
    ).read_text() == 'print("Hello")\n'
    assert not (output_dir / "project" / "main.py").exists()
    assert (
        output_dir / "project" / "importer.py"
    ).read_text() == "import project.src.main"


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


def test_unfold_complex_diff(temp_project, tmp_path):
    """Test unfolding a complex diff file ensures no diff syntax remains in output."""
    fold_file = tmp_path / "complex_diff.txt"
    fold_file.write_text(
        "# Instructions for LLM:\n\n"
        "# --- File: project/main.py ---\n"  # Unified diff modification
        "--- main.py\n"
        "+++ main.py\n"
        "@@ -1 +1,2 @@\n"
        '-print("Hello")\n'
        '+print("Modified Hello")\n'
        '+print("Extra line")\n'
        "\n"
        "# --- File: project/utils.py ---\n"  # Full content replacement
        "def new_util():\n"
        "    return 42\n"
        "\n"
        "# --- File: project/importer.py ---\n"  # Unified diff with multiple hunks
        "--- importer.py\n"
        "+++ importer.py\n"
        "@@ -1 +1,2 @@\n"
        "-import project.main\n"
        "+from project.main import *\n"
        "+print('Imported')\n"
        "\n"
        "# --- File: project/docs/index.md ---\n"  # Delete
        "# DELETE\n"
        "\n"
        "# MOVE: project/utils.py -> project/src/utils.py\n"  # Move
        "# --- File: project/new_file.py ---\n"  # New file
        "print('Brand new file')\n"
        "\n"
    )
    # "# MOVE: project/utils.py -> project/src/utils.py\n"  # Move

    os.chdir(tmp_path)
    output_dir = tmp_path
    cfold.unfold(str(fold_file), str(temp_project), str(output_dir))

    # Check main.py (diff applied)
    main_content = (output_dir / "project" / "main.py").read_text()
    assert main_content == 'print("Modified Hello")\nprint("Extra line")'
    assert "---" not in main_content and "@@" not in main_content

    # Check utils.py (moved and replaced)
    utils_content = (output_dir / "project" / "src" / "utils.py").read_text()
    assert utils_content == "def new_util():\n    return 42"
    assert not (output_dir / "project" / "utils.py").exists()
    assert "---" not in utils_content and "@@" not in utils_content

    # Check importer.py (diff applied)
    importer_content = (output_dir / "project" / "importer.py").read_text()
    assert importer_content == "from project.main import *\nprint('Imported')"
    assert "---" not in importer_content and "@@" not in importer_content

    # Check index.md (deleted)
    assert not (output_dir / "project" / "docs" / "index.md").exists()

    # # Check new_file.py (new file added)
    assert (output_dir / "project" / "new_file.py").exists()
    new_file_content = (output_dir / "project" / "new_file.py").read_text()
    assert new_file_content == "print('Brand new file')"
    assert "---" not in new_file_content and "@@" not in new_file_content
