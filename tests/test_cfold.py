import pytest
import os
import json
from click.testing import CliRunner
from cfold.cli.main import cli  # Updated import to fix the error


@pytest.fixture
def temp_project(tmp_path):
    """Create a temporary project directory with sample files."""
    proj_dir = tmp_path
    src_dir = proj_dir / "src" / "project"
    src_dir.mkdir(parents=True)
    (src_dir / "main.py").write_text('print("Hello")\n')
    (src_dir / "utils.py").write_text("def util():\n    pass\n")
    (src_dir / "importer.py").write_text("from project.main import *\n")
    (proj_dir / "docs").mkdir(exist_ok=True)
    (proj_dir / "docs" / "index.md").write_text("# Docs\n")
    return proj_dir


@pytest.fixture
def runner():
    """Provide a CliRunner for testing CLI commands."""
    return CliRunner()


def test_fold(temp_project, tmp_path, runner):
    """Test fold command creates correct output."""
    output_file = tmp_path / "folded.json"
    os.chdir(tmp_path)
    files = [
        str(temp_project / "src" / "project" / "main.py"),
        str(temp_project / "docs" / "index.md"),
    ]
    result = runner.invoke(
        cli, ["fold", *files, "-o", str(output_file), "-d", "default"]
    )  # Updated to use cli
    assert result.exit_code == 0
    assert output_file.exists()
    with open(output_file, "r", encoding="utf-8") as f:
        data = json.load(f)
    assert "instructions" in data
    assert len(data["files"]) == 2
    assert data["files"][0]["path"] == "src/project/main.py"
    assert data["files"][0]["content"] == 'print("Hello")\n'
    assert data["files"][1]["path"] == "docs/index.md"
    assert data["files"][1]["content"] == "# Docs\n"


def test_fold_directory_default(temp_project, tmp_path, runner):
    """Test folding directory when no files specified."""
    output_file = tmp_path / "folded.json"
    os.chdir(temp_project)
    result = runner.invoke(
        cli, ["fold", "-o", str(output_file), "-d", "default"]
    )  # Updated to use cli
    assert result.exit_code == 0
    assert output_file.exists()
    with open(output_file, "r", encoding="utf-8") as f:
        data = json.load(f)
    assert any(f["path"] == "src/project/main.py" for f in data["files"])
    assert any(f["path"] == "docs/index.md" for f in data["files"])
    assert any(f["path"] == "src/project/utils.py" for f in data["files"])


def test_fold_dialect_codeonly(temp_project, tmp_path, runner):
    """Test codeonly dialect excludes non-code files."""
    output_file = tmp_path / "folded.json"
    os.chdir(temp_project)
    result = runner.invoke(
        cli, ["fold", "-o", str(output_file), "-d", "py"]
    )  # Updated to use cli
    assert result.exit_code == 0
    assert output_file.exists()
    with open(output_file, "r", encoding="utf-8") as f:
        data = json.load(f)
    assert any(f["path"] == "src/project/main.py" for f in data["files"])
    assert any(f["path"] == "src/project/utils.py" for f in data["files"])
    assert any(f["path"] == "src/project/importer.py" for f in data["files"])
    assert not any(f["path"] == "docs/index.md" for f in data["files"])


def test_fold_dialect_doconly(temp_project, tmp_path, runner):
    """Test doconly dialect includes only doc files."""
    output_file = tmp_path / "folded.json"
    os.chdir(temp_project)
    result = runner.invoke(
        cli, ["fold", "-o", str(output_file), "-d", "doc"]
    )  # Updated to use cli
    assert result.exit_code == 0
    assert output_file.exists()
    with open(output_file, "r", encoding="utf-8") as f:
        data = json.load(f)
    assert any(f["path"] == "docs/index.md" for f in data["files"])
    assert not any(f["path"] == "src/project/utils.py" for f in data["files"])
    assert not any(f["path"] == "src/project/importer.py" for f in data["files"])


def test_unfold_new_files(temp_project, tmp_path, runner):
    """Test unfolding creates new files."""
    fold_file = tmp_path / "folded.json"
    data = {
        "instructions": [],
        "files": [
            {"path": "src/project/new.py", "content": "print('New file')\n"},
            {"path": "docs/new.md", "content": "# New Doc\n"},
        ],
    }
    with open(fold_file, "w", encoding="utf-8") as f:
        json.dump(data, f)
    os.chdir(tmp_path)
    output_dir = tmp_path / "unfolded"
    output_dir.mkdir()
    result = runner.invoke(
        cli, ["unfold", str(fold_file), "-o", str(output_dir)]
    )  # Updated to use cli, removed -f
    assert result.exit_code == 0
    assert (output_dir / "src" / "project" / "new.py").exists()
    assert (
        output_dir / "src" / "project" / "new.py"
    ).read_text().strip() == "print('New file')"
    assert (output_dir / "docs" / "new.md").exists()
    assert (output_dir / "docs" / "new.md").read_text().strip() == "# New Doc"


def test_unfold_modify_and_delete(temp_project, tmp_path, runner):
    """Test unfolding with modifications and deletions."""
    fold_file = tmp_path / "folded.json"
    data = {
        "instructions": [],
        "files": [
            {"path": "src/project/main.py", "content": "print('Modified')\n"},
            {"path": "src/project/utils.py", "delete": True, "content": None},
        ],
    }
    with open(fold_file, "w", encoding="utf-8") as f:
        json.dump(data, f)
    os.chdir(tmp_path)
    output_dir = tmp_path / "unfolded"
    output_dir.mkdir()
    result = runner.invoke(
        cli, ["unfold", str(fold_file), "-i", str(temp_project), "-o", str(output_dir)]
    )  # Updated to use cli, removed -f
    assert result.exit_code == 0
    assert (output_dir / "src" / "project" / "main.py").exists()
    assert (
        output_dir / "src" / "project" / "main.py"
    ).read_text().strip() == "print('Modified')"
    assert not (output_dir / "src" / "project" / "utils.py").exists()
    assert (output_dir / "docs" / "index.md").exists()


def test_unfold_relocate_and_update_references(temp_project, tmp_path, runner):
    """Test unfolding with file relocation."""
    fold_file = tmp_path / "folded.json"
    data = {
        "instructions": [],
        "files": [
            {"path": "src/project/main.py", "delete": True, "content": None},
            {"path": "src/project/core/main.py", "content": 'print("Hello")\n'},
            {
                "path": "src/project/importer.py",
                "content": "from project.core.main import *\n",
            },
        ],
    }
    with open(fold_file, "w", encoding="utf-8") as f:
        json.dump(data, f)
    os.chdir(tmp_path)
    output_dir = tmp_path / "unfolded"
    output_dir.mkdir()
    result = runner.invoke(
        cli, ["unfold", str(fold_file), "-i", str(temp_project), "-o", str(output_dir)]
    )  # Updated to use cli, removed -f
    assert result.exit_code == 0
    assert (output_dir / "src" / "project" / "core" / "main.py").exists()
    assert (
        output_dir / "src" / "project" / "core" / "main.py"
    ).read_text().strip() == 'print("Hello")'
    assert not (output_dir / "src" / "project" / "main.py").exists()
    assert (
        output_dir / "src" / "project" / "importer.py"
    ).read_text().strip() == "from project.core.main import *"


def test_init(tmp_path, runner):
    """Test init creates template."""
    output_file = tmp_path / "start.json"
    custom = "Test custom instruction"
    result = runner.invoke(
        cli, ["init", "-o", str(output_file), "-c", custom, "-d", "default"]
    )  # Updated to use cli
    assert result.exit_code == 0
    assert output_file.exists()
    with open(output_file, "r", encoding="utf-8") as f:
        data = json.load(f)
    assert "instructions" in data
    assert any(
        i["type"] == "user" and i["content"] == custom for i in data["instructions"]
    )


def test_init_dialect(tmp_path, runner):
    """Test init with different dialects."""
    output_file = tmp_path / "start.json"
    custom = "Test custom instruction"
    result = runner.invoke(
        cli, ["init", "-o", str(output_file), "-c", custom, "-d", "doc"]
    )  # Updated to use cli
    assert result.exit_code == 0
    assert output_file.exists()
    with open(output_file, "r", encoding="utf-8") as f:
        data = json.load(f)
    assert "instructions" in data


def test_unfold_complex_full_content(temp_project, tmp_path, runner):
    """Test unfolding complex full-content file."""
    fold_file = tmp_path / "complex_full.json"
    data = {
        "instructions": [],
        "files": [
            {
                "path": "src/project/main.py",
                "content": 'print("Modified Hello")\nprint("Extra line")\n',
            },
            {"path": "src/project/utils.py", "delete": True, "content": None},
            {
                "path": "src/project/core/utils.py",
                "content": "def new_util():\n    return 42\n",
            },
            {
                "path": "src/project/importer.py",
                "content": "from project.main import *\nprint('Imported')\n",
            },
            {"path": "docs/index.md", "delete": True, "content": None},
            {"path": "src/project/new_file.py", "content": "print('Brand new file')\n"},
        ],
    }
    with open(fold_file, "w", encoding="utf-8") as f:
        json.dump(data, f)
    os.chdir(tmp_path)
    output_dir = tmp_path / "unfolded"
    output_dir.mkdir()
    result = runner.invoke(
        cli, ["unfold", str(fold_file), "-i", str(temp_project), "-o", str(output_dir)]
    )  # Updated to use cli, removed -f
    assert result.exit_code == 0
    assert (
        output_dir / "src" / "project" / "main.py"
    ).read_text().strip() == 'print("Modified Hello")\nprint("Extra line")'
    assert (
        output_dir / "src" / "project" / "core" / "utils.py"
    ).read_text().strip() == "def new_util():\n    return 42"
    assert not (output_dir / "src" / "project" / "utils.py").exists()
    assert (
        output_dir / "src" / "project" / "importer.py"
    ).read_text().strip() == "from project.main import *\nprint('Imported')"
    assert not (output_dir / "docs" / "index.md").exists()
    assert (
        output_dir / "src" / "project" / "new_file.py"
    ).read_text().strip() == "print('Brand new file')"


def test_unfold_md_commands_not_interpreted(temp_project, tmp_path, runner):
    """Test MOVE/DELETE in .md files not interpreted."""
    fold_file = tmp_path / "folded.json"
    data = {
        "instructions": [],
        "files": [
            {
                "path": "docs/example.md",
                "content": "# Example\n\nHere's how to delete a file:\n# DELETE\n# MOVE: src/project/main.py -> src/project/core/main.py\n",
            }
        ],
    }
    with open(fold_file, "w", encoding="utf-8") as f:
        json.dump(data, f)
    os.chdir(tmp_path)
    output_dir = tmp_path / "unfolded"
    output_dir.mkdir()
    result = runner.invoke(
        cli, ["unfold", str(fold_file), "-i", str(temp_project), "-o", str(output_dir)]
    )  # Updated to use cli, removed -f
    assert result.exit_code == 0
    example_content = (output_dir / "docs" / "example.md").read_text()
    assert "# Example" in example_content
    assert "# DELETE" in example_content
    assert (
        output_dir / "src" / "project" / "utils.py"
    ).exists()  # Assuming it's copied


