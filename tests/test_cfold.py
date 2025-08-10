import pytest
import os
import json
from click.testing import CliRunner
from cfold.cli.main import cli  # Updated import to fix the error
import yaml


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
    """Test unfolding new files."""
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


def test_fold_invalid_dialect(temp_project, tmp_path, runner):
    """Test fold with invalid dialect raises error."""
    output_file = tmp_path / "folded.json"
    os.chdir(temp_project)
    result = runner.invoke(
        cli, ["fold", "-o", str(output_file), "-d", "invalid"]
    )
    assert result.exit_code == 1
    assert "Invalid dialect specified" in result.output


def test_fold_no_files(temp_project, tmp_path, runner):
    """Test fold with no valid files."""
    output_file = tmp_path / "folded.json"
    os.chdir(temp_project / "docs")  # Change to a dir with no includable files for py dialect
    result = runner.invoke(
        cli, ["fold", "-o", str(output_file), "-d", "py"]
    )
    assert result.exit_code == 0
    assert "No valid files to fold." in result.output
    assert not output_file.exists()


def test_fold_with_prompt(temp_project, tmp_path, runner):
    """Test fold with prompt file."""
    output_file = tmp_path / "folded.json"
    prompt_file = tmp_path / "prompt.txt"
    prompt_file.write_text("Custom prompt content")
    os.chdir(temp_project)
    result = runner.invoke(
        cli, ["fold", "-o", str(output_file), "-p", str(prompt_file), "-d", "default"]
    )
    assert result.exit_code == 0
    with open(output_file, "r", encoding="utf-8") as f:
        data = json.load(f)
    assert any(i["content"] == "Custom prompt content" and i["type"] == "user" for i in data["instructions"])


def test_fold_with_invalid_prompt(temp_project, tmp_path, runner):
    """Test fold with non-existing prompt file."""
    output_file = tmp_path / "folded.json"
    os.chdir(temp_project)
    result = runner.invoke(
        cli, ["fold", "-o", str(output_file), "-p", "nonexistent.txt", "-d", "default"]
    )
    assert result.exit_code == 0
    assert "Warning: Prompt file 'nonexistent.txt' does not exist. Skipping." in result.output


def test_unfold_without_original_dir(temp_project, tmp_path, runner):
    """Test unfold without original directory."""
    fold_file = tmp_path / "folded.json"
    data = {
        "instructions": [],
        "files": [
            {"path": "new_file.py", "content": "print('New')\n"},
            {"path": "to_delete.py", "delete": True},
        ],
    }
    with open(fold_file, "w", encoding="utf-8") as f:
        json.dump(data, f)
    output_dir = tmp_path / "unfolded"
    output_dir.mkdir()
    (output_dir / "to_delete.py").write_text("delete me")
    os.chdir(tmp_path)
    result = runner.invoke(
        cli, ["unfold", str(fold_file), "-o", str(output_dir)]
    )
    assert result.exit_code == 0
    assert (output_dir / "new_file.py").exists()
    assert not (output_dir / "to_delete.py").exists()


def test_unfold_merge_existing_dir(temp_project, tmp_path, runner):
    """Test unfold merging into existing directory."""
    fold_file = tmp_path / "folded.json"
    data = {
        "instructions": [],
        "files": [
            {"path": "existing.py", "content": "print('Modified')\n"},
        ],
    }
    with open(fold_file, "w", encoding="utf-8") as f:
        json.dump(data, f)
    output_dir = tmp_path / "unfolded"
    output_dir.mkdir()
    (output_dir / "existing.py").write_text("original")
    (output_dir / "unchanged.py").write_text("unchanged")
    os.chdir(tmp_path)
    result = runner.invoke(
        cli, ["unfold", str(fold_file), "-o", str(output_dir)]
    )
    assert result.exit_code == 0
    assert (output_dir / "existing.py").read_text().strip() == "print('Modified')"
    assert (output_dir / "unchanged.py").read_text().strip() == "unchanged"


def test_unfold_delete_outside_cwd(temp_project, tmp_path, runner):
    """Test unfold does not delete files outside CWD."""
    fold_file = tmp_path / "folded.json"
    data = {
        "instructions": [],
        "files": [
            {"path": "../outside.py", "delete": True},
        ],
    }
    with open(fold_file, "w", encoding="utf-8") as f:
        json.dump(data, f)
    output_dir = tmp_path / "unfolded"
    output_dir.mkdir()
    outside_file = tmp_path / "outside.py"
    outside_file.write_text("should not delete")
    os.chdir(output_dir)
    result = runner.invoke(
        cli, ["unfold", str(fold_file), "-o", "."]
    )
    assert result.exit_code == 0
    assert outside_file.exists()  # Should not be deleted


def test_fold_with_foldignore(temp_project, tmp_path, runner):
    """Test fold respects .foldignore."""
    ignore_file = temp_project / ".foldignore"
    ignore_file.write_text("*.md\n")
    output_file = tmp_path / "folded.json"
    os.chdir(temp_project)
    result = runner.invoke(
        cli, ["fold", "-o", str(output_file), "-d", "default"]
    )
    assert result.exit_code == 0
    with open(output_file, "r", encoding="utf-8") as f:
        data = json.load(f)
    assert any(f["path"] == "src/project/main.py" for f in data["files"])
    assert not any(f["path"] == "docs/index.md" for f in data["files"])

def test_rc_command(temp_project, runner):
    """Test rc command creates .foldrc with local as default."""
    os.chdir(temp_project)
    result = runner.invoke(cli, ["rc"])
    assert result.exit_code == 0
    foldrc_path = temp_project / ".foldrc"
    assert foldrc_path.exists()
    with open(foldrc_path, "r", encoding="utf-8") as f:
        config = yaml.safe_load(f)
    assert "default_dialect" in config and config["default_dialect"] == "local"
    assert "local" in config
    assert config["local"]["pre"] == ["py"]
    assert config["local"]["instructions"] == [{"type": "user", "synopsis": "local focus", "content": "Focus on brief and modular code."}]
    assert config["local"]["included_suffix"] == [".py", ".toml"]

def test_fold_uses_local_default(temp_project, tmp_path, runner):
    """Test fold uses local default dialect from .foldrc."""
    os.chdir(temp_project)
    # Create .foldrc with default_dialect: py
    foldrc_path = temp_project / ".foldrc"
    config = {"default_dialect": "py"}
    with open(foldrc_path, "w", encoding="utf-8") as f:
        yaml.safe_dump(config, f)
    output_file = tmp_path / "folded.json"
    result = runner.invoke(cli, ["fold", "-o", str(output_file)])
    assert result.exit_code == 0
    with open(output_file, "r", encoding="utf-8") as f:
        data = json.load(f)
    # Check if it used 'py' dialect (excludes .md)
    assert any(f["path"] == "src/project/main.py" for f in data["files"])
    assert not any(f["path"] == "docs/index.md" for f in data["files"])



