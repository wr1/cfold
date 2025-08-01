import pytest
import os
import json
from click.testing import CliRunner
from cfold.cli.main import cli  # Updated import to fix the error


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


@pytest.fixture
def runner():
    """Provide a CliRunner for testing CLI commands."""
    return CliRunner()


def test_fold(temp_project, tmp_path, runner):
    """Test fold command creates correct output."""
    output_file = tmp_path / "folded.txt"
    os.chdir(tmp_path)
    files = [str(temp_project / "main.py"), str(temp_project / "docs" / "index.md")]
    result = runner.invoke(
        cli, ["fold", *files, "-o", str(output_file), "-d", "default"]
    )  # Updated to use cli
    assert result.exit_code == 0
    assert output_file.exists()
    with open(output_file, "r", encoding="utf-8") as f:
        data = json.load(f)
    assert "instructions" in data
    assert len(data["files"]) == 2
    assert data["files"][0]["path"] == "project/main.py"
    assert data["files"][0]["content"] == 'print("Hello")\n'
    assert data["files"][1]["path"] == "project/docs/index.md"
    assert data["files"][1]["content"] == "# Docs\n"


def test_fold_directory_default(temp_project, tmp_path, runner):
    """Test folding directory when no files specified."""
    output_file = tmp_path / "folded.txt"
    os.chdir(temp_project)
    result = runner.invoke(
        cli, ["fold", "-o", str(output_file), "-d", "default"]
    )  # Updated to use cli
    assert result.exit_code == 0
    assert output_file.exists()
    with open(output_file, "r", encoding="utf-8") as f:
        data = json.load(f)
    assert any(f["path"] == "main.py" for f in data["files"])
    assert any(f["path"] == "docs/index.md" for f in data["files"])
    assert any(f["path"] == "utils.py" for f in data["files"])


def test_fold_dialect_codeonly(temp_project, tmp_path, runner):
    """Test codeonly dialect excludes non-code files."""
    output_file = tmp_path / "folded.txt"
    os.chdir(temp_project)
    result = runner.invoke(
        cli, ["fold", "-o", str(output_file), "-d", "codeonly"]
    )  # Updated to use cli
    assert result.exit_code == 0
    assert output_file.exists()
    with open(output_file, "r", encoding="utf-8") as f:
        data = json.load(f)
    assert any(f["path"] == "main.py" for f in data["files"])
    assert any(f["path"] == "utils.py" for f in data["files"])
    assert any(f["path"] == "importer.py" for f in data["files"])
    assert not any(f["path"] == "docs/index.md" for f in data["files"])


def test_fold_dialect_doconly(temp_project, tmp_path, runner):
    """Test doconly dialect includes only doc files."""
    output_file = tmp_path / "folded.txt"
    os.chdir(temp_project)
    result = runner.invoke(
        cli, ["fold", "-o", str(output_file), "-d", "doconly"]
    )  # Updated to use cli
    assert result.exit_code == 0
    assert output_file.exists()
    with open(output_file, "r", encoding="utf-8") as f:
        data = json.load(f)
    assert any(f["path"] == "docs/index.md" for f in data["files"])
    assert not any(f["path"] == "utils.py" for f in data["files"])
    assert not any(f["path"] == "importer.py" for f in data["files"])


def test_unfold_new_files(temp_project, tmp_path, runner):
    """Test unfolding creates new files."""
    fold_file = tmp_path / "folded.txt"
    data = {
        "instructions": "# Instructions for LLM:\n\n",
        "files": [
            {"path": "project/new.py", "content": "print('New file')\n"},
            {"path": "project/docs/new.md", "content": "# New Doc\n"}
        ]
    }
    with open(fold_file, "w", encoding="utf-8") as f:
        json.dump(data, f)
    os.chdir(tmp_path)
    output_dir = tmp_path
    result = runner.invoke(
        cli, ["unfold", "-f", str(fold_file), "-o", str(output_dir)]
    )  # Updated to use cli
    assert result.exit_code == 0
    assert (output_dir / "project" / "new.py").exists()
    assert (
        output_dir / "project" / "new.py"
    ).read_text().strip() == "print('New file')"
    assert (output_dir / "project" / "docs" / "new.md").exists()
    assert (
        output_dir / "project" / "docs" / "new.md"
    ).read_text().strip() == "# New Doc"


def test_unfold_modify_and_delete(temp_project, tmp_path, runner):
    """Test unfolding with modifications and deletions."""
    fold_file = tmp_path / "folded.txt"
    data = {
        "instructions": "# Instructions for LLM:\n\n",
        "files": [
            {"path": "project/main.py", "content": "print('Modified')\n"},
            {"path": "project/utils.py", "content": "# DELETE\n"}
        ]
    }
    with open(fold_file, "w", encoding="utf-8") as f:
        json.dump(data, f)
    os.chdir(tmp_path)
    output_dir = tmp_path
    result = runner.invoke(
        cli, ["unfold", "-f", str(fold_file), "-i", str(temp_project), "-o", str(output_dir)]
    )  # Updated to use cli
    assert result.exit_code == 0
    assert (output_dir / "project" / "main.py").exists()
    assert (
        output_dir / "project" / "main.py"
    ).read_text().strip() == "print('Modified')"
    assert not (output_dir / "project" / "utils.py").exists()
    assert (output_dir / "project" / "docs" / "index.md").exists()


def test_unfold_relocate_and_update_references(temp_project, tmp_path, runner):
    """Test unfolding with file relocation."""
    fold_file = tmp_path / "folded.txt"
    data = {
        "instructions": "# Instructions for LLM:\n\n",
        "files": [
            {"path": "project/main.py", "content": "# DELETE"},
            {"path": "project/src/main.py", "content": 'print("Hello")\n'},
            {"path": "project/importer.py", "content": "import project.src.main\n"}
        ]
    }
    with open(fold_file, "w", encoding="utf-8") as f:
        json.dump(data, f)
    os.chdir(tmp_path)
    output_dir = tmp_path
    result = runner.invoke(
        cli, ["unfold", "-f", str(fold_file), "-i", str(temp_project), "-o", str(output_dir)]
    )  # Updated to use cli
    assert result.exit_code == 0
    assert (output_dir / "project" / "src" / "main.py").exists()
    assert (
        output_dir / "project" / "src" / "main.py"
    ).read_text().strip() == 'print("Hello")'
    assert not (output_dir / "project" / "main.py").exists()
    assert (
        output_dir / "project" / "importer.py"
    ).read_text().strip() == "import project.src.main"


def test_init(tmp_path, runner):
    """Test init creates template."""
    output_file = tmp_path / "start.txt"
    custom = "Test custom instruction"
    result = runner.invoke(
        cli, ["init", "-o", str(output_file), "-c", custom, "-d", "default"]
    )  # Updated to use cli
    assert result.exit_code == 0
    assert output_file.exists()
    with open(output_file, "r", encoding="utf-8") as f:
        data = json.load(f)
    assert "instructions" in data
    assert data["prompt"] == custom


def test_init_dialect(tmp_path, runner):
    """Test init with different dialects."""
    output_file = tmp_path / "start.txt"
    custom = "Test custom instruction"
    result = runner.invoke(
        cli, ["init", "-o", str(output_file), "-c", custom, "-d", "doconly"]
    )  # Updated to use cli
    assert result.exit_code == 0
    assert output_file.exists()
    with open(output_file, "r", encoding="utf-8") as f:
        data = json.load(f)
    assert "instructions" in data


def test_unfold_complex_full_content(temp_project, tmp_path, runner):
    """Test unfolding complex full-content file."""
    fold_file = tmp_path / "complex_full.txt"
    data = {
        "instructions": "# Instructions for LLM:\n\n",
        "files": [
            {"path": "project/main.py", "content": 'print("Modified Hello")\nprint("Extra line")\n'},
            {"path": "project/utils.py", "content": "# DELETE"},
            {"path": "project/src/utils.py", "content": "def new_util():\n    return 42\n"},
            {"path": "project/importer.py", "content": "from project.main import *\nprint('Imported')\n"},
            {"path": "project/docs/index.md", "content": "# DELETE"},
            {"path": "project/new_file.py", "content": "print('Brand new file')\n"}
        ]
    }
    with open(fold_file, "w", encoding="utf-8") as f:
        json.dump(data, f)
    os.chdir(tmp_path)
    output_dir = tmp_path
    result = runner.invoke(
        cli, ["unfold", "-f", str(fold_file), "-i", str(temp_project), "-o", str(output_dir)]
    )  # Updated to use cli
    assert result.exit_code == 0
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


def test_unfold_md_commands_not_interpreted(temp_project, tmp_path, runner):
    """Test MOVE/DELETE in .md files not interpreted."""
    fold_file = tmp_path / "folded.txt"
    data = {
        "instructions": "# Instructions for LLM:\n\n",
        "files": [
            {"path": "project/docs/example.md", "content": "# Example\n\nHere's how to delete a file:\n# DELETE\n# MOVE: project/main.py -> project/src/main.py\n"}
        ]
    }
    with open(fold_file, "w", encoding="utf-8") as f:
        json.dump(data, f)
    os.chdir(tmp_path)
    output_dir = tmp_path
    result = runner.invoke(
        cli, ["unfold", "-f", str(fold_file), "-i", str(temp_project), "-o", str(output_dir)]
    )  # Updated to use cli
    assert result.exit_code == 0
    example_content = (output_dir / "project" / "docs" / "example.md").read_text()
    assert "# Example" in example_content
    assert "# DELETE" in example_content
    assert (output_dir / "project" / "utils.py").exists()  # Assuming it's copied

