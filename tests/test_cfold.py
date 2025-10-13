import pytest
import json
import sys
import yaml
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent / "src"))
sys.path.append(str(Path(__file__).parent.parent.parent / "treeparse" / "src"))

from cfold.cli.main import main  # Updated import


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


def test_fold(temp_project, tmp_path, monkeypatch, capsys):
    """Test fold command creates correct output."""
    files = [
        str(temp_project / "src" / "project" / "main.py"),
        str(temp_project / "docs" / "index.md"),
    ]
    output_file = tmp_path / "folded.json"
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(
        sys,
        "argv",
        ["cfold", "fold"] + files + ["-o", str(output_file), "-d", "default"],
    )
    main()
    captured = capsys.readouterr()
    assert "Codebase folded into" in captured.out
    assert output_file.exists()
    with open(output_file, "r", encoding="utf-8") as f:
        data = json.load(f)
    assert "instructions" in data
    assert len(data["files"]) == 2
    assert data["files"][0]["path"] == "src/project/main.py"
    assert data["files"][0]["content"] == 'print("Hello")\n'
    assert data["files"][1]["path"] == "docs/index.md"
    assert data["files"][1]["content"] == "# Docs\n"


def test_fold_directory_default(temp_project, tmp_path, monkeypatch, capsys):
    """Test folding directory when no files specified."""
    output_file = tmp_path / "folded.json"
    monkeypatch.chdir(temp_project)
    monkeypatch.setattr(
        sys, "argv", ["cfold", "fold", "-o", str(output_file), "-d", "default"]
    )
    main()
    captured = capsys.readouterr()
    assert "Codebase folded into" in captured.out
    assert output_file.exists()
    with open(output_file, "r", encoding="utf-8") as f:
        data = json.load(f)
    assert any(f["path"] == "src/project/main.py" for f in data["files"])
    assert any(f["path"] == "docs/index.md" for f in data["files"])
    assert any(f["path"] == "src/project/utils.py" for f in data["files"])


def test_fold_dialect_codeonly(temp_project, tmp_path, monkeypatch, capsys):
    """Test codeonly dialect excludes non-code files."""
    output_file = tmp_path / "folded.json"
    monkeypatch.chdir(temp_project)
    monkeypatch.setattr(
        sys, "argv", ["cfold", "fold", "-o", str(output_file), "-d", "py"]
    )
    main()
    captured = capsys.readouterr()
    assert "Codebase folded into" in captured.out
    assert output_file.exists()
    with open(output_file, "r", encoding="utf-8") as f:
        data = json.load(f)
    assert any(f["path"] == "src/project/main.py" for f in data["files"])
    assert any(f["path"] == "src/project/utils.py" for f in data["files"])
    assert any(f["path"] == "src/project/importer.py" for f in data["files"])
    assert not any(f["path"] == "docs/index.md" for f in data["files"])


def test_fold_dialect_doconly(temp_project, tmp_path, monkeypatch, capsys):
    """Test doconly dialect includes only doc files."""
    output_file = tmp_path / "folded.json"
    monkeypatch.chdir(temp_project)
    monkeypatch.setattr(
        sys, "argv", ["cfold", "fold", "-o", str(output_file), "-d", "doc"]
    )
    main()
    captured = capsys.readouterr()
    assert "Codebase folded into" in captured.out
    assert output_file.exists()
    with open(output_file, "r", encoding="utf-8") as f:
        data = json.load(f)
    assert any(f["path"] == "docs/index.md" for f in data["files"])
    assert not any(f["path"] == "src/project/utils.py" for f in data["files"])
    assert not any(f["path"] == "src/project/importer.py" for f in data["files"])


def test_unfold_new_files(temp_project, tmp_path, monkeypatch, capsys):
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
    output_dir = tmp_path / "unfolded"
    output_dir.mkdir()
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(
        sys, "argv", ["cfold", "unfold", str(fold_file), "-o", str(output_dir)]
    )
    main()
    captured = capsys.readouterr()
    assert "Codebase unfolded into" in captured.out
    assert (output_dir / "src" / "project" / "new.py").exists()
    assert (
        output_dir / "src" / "project" / "new.py"
    ).read_text() == "print('New file')\n"
    assert (output_dir / "docs" / "new.md").exists()
    assert (output_dir / "docs" / "new.md").read_text() == "# New Doc\n"


def test_unfold_modify_and_delete(temp_project, tmp_path, monkeypatch, capsys):
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
    output_dir = tmp_path / "unfolded"
    output_dir.mkdir()
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "cfold",
            "unfold",
            str(fold_file),
            "-i",
            str(temp_project),
            "-o",
            str(output_dir),
        ],
    )
    main()
    captured = capsys.readouterr()
    assert "Codebase unfolded into" in captured.out
    assert (output_dir / "src" / "project" / "main.py").exists()
    assert (
        output_dir / "src" / "project" / "main.py"
    ).read_text() == "print('Modified')\n"
    assert not (output_dir / "src" / "project" / "utils.py").exists()
    assert (output_dir / "docs" / "index.md").exists()


def test_unfold_relocate_and_update_references(
    temp_project, tmp_path, monkeypatch, capsys
):
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
    output_dir = tmp_path / "unfolded"
    output_dir.mkdir()
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "cfold",
            "unfold",
            str(fold_file),
            "-i",
            str(temp_project),
            "-o",
            str(output_dir),
        ],
    )
    main()
    captured = capsys.readouterr()
    assert "Codebase unfolded into" in captured.out
    assert (output_dir / "src" / "project" / "core" / "main.py").exists()
    assert (
        output_dir / "src" / "project" / "core" / "main.py"
    ).read_text() == 'print("Hello")\n'
    assert not (output_dir / "src" / "project" / "main.py").exists()
    assert (
        output_dir / "src" / "project" / "importer.py"
    ).read_text() == "from project.core.main import *\n"


def test_unfold_complex_full_content(temp_project, tmp_path, monkeypatch, capsys):
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
    output_dir = tmp_path / "unfolded"
    output_dir.mkdir()
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "cfold",
            "unfold",
            str(fold_file),
            "-i",
            str(temp_project),
            "-o",
            str(output_dir),
        ],
    )
    main()
    captured = capsys.readouterr()
    assert "Codebase unfolded into" in captured.out
    assert (
        output_dir / "src" / "project" / "main.py"
    ).read_text() == 'print("Modified Hello")\nprint("Extra line")\n'
    assert (
        output_dir / "src" / "project" / "core" / "utils.py"
    ).read_text() == "def new_util():\n    return 42\n"
    assert not (output_dir / "src" / "project" / "utils.py").exists()
    assert (
        output_dir / "src" / "project" / "importer.py"
    ).read_text() == "from project.main import *\nprint('Imported')\n"
    assert not (output_dir / "docs" / "index.md").exists()
    assert (
        output_dir / "src" / "project" / "new_file.py"
    ).read_text() == "print('Brand new file')\n"


def test_unfold_md_commands_not_interpreted(
    temp_project, tmp_path, monkeypatch, capsys
):
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
    output_dir = tmp_path / "unfolded"
    output_dir.mkdir()
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "cfold",
            "unfold",
            str(fold_file),
            "-i",
            str(temp_project),
            "-o",
            str(output_dir),
        ],
    )
    main()
    captured = capsys.readouterr()
    assert "Codebase unfolded into" in captured.out
    example_content = (output_dir / "docs" / "example.md").read_text()
    assert "# Example" in example_content
    assert "# DELETE" in example_content
    assert (
        output_dir / "src" / "project" / "utils.py"
    ).exists()  # Assuming it's copied


def test_fold_invalid_dialect(temp_project, tmp_path, monkeypatch, capsys):
    """Test fold with invalid dialect raises error."""
    output_file = tmp_path / "folded.json"
    monkeypatch.chdir(temp_project)
    monkeypatch.setattr(
        sys, "argv", ["cfold", "fold", "-o", str(output_file), "-d", "invalid"]
    )
    with pytest.raises(SystemExit) as exc:
        main()
    assert exc.value.code == 1
    captured = capsys.readouterr()
    assert "Invalid dialect specified" in captured.out


def test_fold_no_files(temp_project, tmp_path, monkeypatch, capsys):
    """Test fold with no valid files."""
    output_file = tmp_path / "folded.json"
    monkeypatch.chdir(
        temp_project / "docs"
    )  # Change to a dir with no includable files for py dialect
    monkeypatch.setattr(
        sys, "argv", ["cfold", "fold", "-o", str(output_file), "-d", "py"]
    )
    main()
    captured = capsys.readouterr()
    assert "No valid files to fold." in captured.out
    assert not output_file.exists()


def test_fold_with_prompt(temp_project, tmp_path, monkeypatch, capsys):
    """Test fold with prompt file."""
    output_file = tmp_path / "folded.json"
    prompt_file = tmp_path / "prompt.txt"
    prompt_file.write_text("Custom prompt content")
    monkeypatch.chdir(temp_project)
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "cfold",
            "fold",
            "-o",
            str(output_file),
            "-p",
            str(prompt_file),
            "-d",
            "default",
        ],
    )
    main()
    captured = capsys.readouterr()
    assert "Codebase folded into" in captured.out
    with open(output_file, "r", encoding="utf-8") as f:
        data = json.load(f)
    assert any(
        i["content"] == "Custom prompt content" and i["type"] == "user"
        for i in data["instructions"]
    )


def test_fold_with_invalid_prompt(temp_project, tmp_path, monkeypatch, capsys):
    """Test fold with non-existing prompt file."""
    output_file = tmp_path / "folded.json"
    monkeypatch.chdir(temp_project)
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "cfold",
            "fold",
            "-o",
            str(output_file),
            "-p",
            "nonexistent.txt",
            "-d",
            "default",
        ],
    )
    main()
    captured = capsys.readouterr()
    assert (
        "Warning: Prompt file 'nonexistent.txt' does not exist. Skipping."
        in captured.out
    )
    assert "Codebase folded into" in captured.out


def test_unfold_without_original_dir(temp_project, tmp_path, monkeypatch, capsys):
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
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(
        sys, "argv", ["cfold", "unfold", str(fold_file), "-o", str(output_dir)]
    )
    main()
    captured = capsys.readouterr()
    assert "Codebase unfolded into" in captured.out
    assert (output_dir / "new_file.py").exists()
    assert not (output_dir / "to_delete.py").exists()


def test_unfold_merge_existing_dir(temp_project, tmp_path, monkeypatch, capsys):
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
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(
        sys, "argv", ["cfold", "unfold", str(fold_file), "-o", str(output_dir)]
    )
    main()
    captured = capsys.readouterr()
    assert "Codebase unfolded into" in captured.out
    assert (output_dir / "existing.py").read_text() == "print('Modified')\n"
    assert (output_dir / "unchanged.py").read_text() == "unchanged"


def test_unfold_delete_outside_cwd(temp_project, tmp_path, monkeypatch, capsys):
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
    monkeypatch.chdir(output_dir)
    monkeypatch.setattr(sys, "argv", ["cfold", "unfold", str(fold_file), "-o", "."])
    main()
    captured = capsys.readouterr()
    assert "Codebase unfolded into" in captured.out
    assert outside_file.exists()  # Should not be deleted


def test_rc_command(temp_project, monkeypatch, capsys):
    """Test rc command creates .foldrc with local as default."""
    monkeypatch.chdir(temp_project)
    monkeypatch.setattr(sys, "argv", ["cfold", "rc"])
    main()
    captured = capsys.readouterr()
    assert ".foldrc created/updated" in captured.out
    foldrc_path = temp_project / ".foldrc"
    assert foldrc_path.exists()
    with open(foldrc_path, "r", encoding="utf-8") as f:
        config = yaml.safe_load(f)
    assert "default_dialect" in config and config["default_dialect"] == "local"
    assert "local" in config
    assert config["local"]["pre"] == ["py"]
    assert config["local"]["instructions"] == [
        {
            "type": "user",
            "synopsis": "local focus",
            "content": "Focus on brief and modular code.",
        }
    ]
    assert config["local"]["included_suffix"] == [".py", ".toml"]


def test_fold_uses_local_default(temp_project, tmp_path, monkeypatch, capsys):
    """Test fold uses local default dialect from .foldrc."""
    foldrc_path = temp_project / ".foldrc"
    config = {"default_dialect": "py"}
    with open(foldrc_path, "w", encoding="utf-8") as f:
        yaml.safe_dump(config, f)
    output_file = tmp_path / "folded.json"
    monkeypatch.chdir(temp_project)
    monkeypatch.setattr(sys, "argv", ["cfold", "fold", "-o", str(output_file)])
    main()
    captured = capsys.readouterr()
    assert "Codebase folded into" in captured.out
    with open(output_file, "r", encoding="utf-8") as f:
        data = json.load(f)
    # Check if it used 'py' dialect (excludes .md)
    assert any(f["path"] == "src/project/main.py" for f in data["files"])
    assert not any(f["path"] == "docs/index.md" for f in data["files"])


def test_fold_bare(temp_project, tmp_path, monkeypatch, capsys):
    """Test fold in bare mode has no instructions."""
    output_file = tmp_path / "folded.json"
    monkeypatch.chdir(temp_project)
    monkeypatch.setattr(
        sys, "argv", ["cfold", "fold", "-o", str(output_file), "-b", "True", "-d", "default"]
    )
    main()
    captured = capsys.readouterr()
    assert "Codebase folded into" in captured.out
    with open(output_file, "r", encoding="utf-8") as f:
        data = json.load(f)
    assert data["instructions"] == []
    assert any(f["path"] == "src/project/main.py" for f in data["files"])
    assert any(f["path"] == "docs/index.md" for f in data["files"])


def test_fold_bare_with_prompt(temp_project, tmp_path, monkeypatch, capsys):
    """Test fold in bare mode with prompt includes only the prompt."""
    output_file = tmp_path / "folded.json"
    prompt_file = tmp_path / "prompt.txt"
    prompt_file.write_text("Custom prompt")
    monkeypatch.chdir(temp_project)
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "cfold",
            "fold",
            "-o",
            str(output_file),
            "-b",
            "True",
            "-p",
            str(prompt_file),
            "-d",
            "default",
        ],
    )
    main()
    captured = capsys.readouterr()
    assert "Codebase folded into" in captured.out
    with open(output_file, "r", encoding="utf-8") as f:
        data = json.load(f)
    assert len(data["instructions"]) == 1
    assert data["instructions"][0]["content"] == "Custom prompt"
    assert data["instructions"][0]["type"] == "user"
    assert any(f["path"] == "src/project/main.py" for f in data["files"])
    assert any(f["path"] == "docs/index.md" for f in data["files"])


def test_fold_with_exclude(temp_project, tmp_path, monkeypatch, capsys):
    """Test fold excludes files specified in dialect's exclude list."""
    foldrc_path = temp_project / ".foldrc"
    config = {
        "default_dialect": "local",
        "local": {
            "pre": ["default"],
            "exclude": ["src/project/main.py"],
        },
    }
    with open(foldrc_path, "w", encoding="utf-8") as f:
        yaml.safe_dump(config, f)
    output_file = tmp_path / "folded.json"
    monkeypatch.chdir(temp_project)
    monkeypatch.setattr(sys, "argv", ["cfold", "fold", "-o", str(output_file)])
    main()
    captured = capsys.readouterr()
    assert "Codebase folded into" in captured.out
    with open(output_file, "r", encoding="utf-8") as f:
        data = json.load(f)
    assert not any(f["path"] == "src/project/main.py" for f in data["files"])
    assert any(f["path"] == "src/project/utils.py" for f in data["files"])
    assert any(f["path"] == "docs/index.md" for f in data["files"])


def test_view_command(tmp_path, monkeypatch, capsys):
    """Test view command displays instructions and files."""
    fold_file = tmp_path / "view_test.json"
    data = {
        "instructions": [
            {
                "type": "system",
                "content": "System prompt",
                "name": "sys",
                "synopsis": "Overview",
            },
            {"type": "user", "content": "User prompt"},
        ],
        "files": [
            {"path": "file1.py", "content": "code"},
            {"path": "file2.md", "delete": True},
        ],
    }
    with open(fold_file, "w", encoding="utf-8") as f:
        json.dump(data, f)

    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(sys, "argv", ["cfold", "view", str(fold_file)])
    main()
    captured = capsys.readouterr()
    assert "Instructions" in captured.out
    assert "system (sys) - Overview" in captured.out
    assert "user" in captured.out
    assert "Files" in captured.out
    assert "file1.py" in captured.out
    assert "file2.md (delete)" in captured.out


def test_view_invalid_file(tmp_path, monkeypatch, capsys):
    """Test view with invalid file shows error."""
    fold_file = tmp_path / "invalid.json"
    fold_file.write_text("invalid json")

    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(sys, "argv", ["cfold", "view", str(fold_file)])
    main()
    captured = capsys.readouterr()
    assert "Error loading" in captured.out


def test_add_files(temp_project, tmp_path, monkeypatch, capsys):
    """Test add command adds new files to existing cfold file."""
    fold_file = tmp_path / "codefold.json"
    initial_data = {
        "instructions": [],
        "files": [
            {"path": "existing.py", "content": "original"},
        ],
    }
    with open(fold_file, "w", encoding="utf-8") as f:
        json.dump(initial_data, f)
    new_file = temp_project / "src" / "project" / "new.py"
    new_file.write_text("new content")
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(
        sys, "argv", ["cfold", "add", str(new_file)]
    )
    main()
    captured = capsys.readouterr()
    assert "Added files to" in captured.out
    with open(fold_file, "r", encoding="utf-8") as f:
        data = json.load(f)
    assert len(data["files"]) == 2
    assert any(f["path"] == "existing.py" and f["content"] == "original" for f in data["files"])
    assert any(f["path"] == "src/project/new.py" and f["content"] == "new content" for f in data["files"])


def test_add_update_existing(temp_project, tmp_path, monkeypatch, capsys):
    """Test add command updates existing files."""
    fold_file = tmp_path / "codefold.json"
    initial_data = {
        "instructions": [],
        "files": [
            {"path": "src/project/main.py", "content": "old"},
        ],
    }
    with open(fold_file, "w", encoding="utf-8") as f:
        json.dump(initial_data, f)
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(
        sys, "argv", ["cfold", "add", str(temp_project / "src" / "project" / "main.py")]
    )
    main()
    captured = capsys.readouterr()
    assert "No new files added" in captured.out
    with open(fold_file, "r", encoding="utf-8") as f:
        data = json.load(f)
    assert len(data["files"]) == 1
    assert data["files"][0]["content"] == 'print("Hello")\n'


def test_add_nonexistent_foldfile(temp_project, tmp_path, monkeypatch, capsys):
    """Test add command with nonexistent foldfile."""
    fold_file = tmp_path / "nonexistent.json"
    new_file = temp_project / "src" / "project" / "new.py"
    new_file.write_text("content")
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(
        sys, "argv", ["cfold", "add", str(new_file), "-f", str(fold_file)]
    )
    main()
    captured = capsys.readouterr()
    assert "does not exist" in captured.out


def test_add_non_file(temp_project, tmp_path, monkeypatch, capsys):
    """Test add command with non-file input."""
    fold_file = tmp_path / "codefold.json"
    initial_data = {"instructions": [], "files": []}
    with open(fold_file, "w", encoding="utf-8") as f:
        json.dump(initial_data, f)
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(
        sys, "argv", ["cfold", "add", str(temp_project / "src")]  # directory
    )
    main()
    captured = capsys.readouterr()
    assert "Warning: " in captured.out and "is not a file" in captured.out
    with open(fold_file, "r", encoding="utf-8") as f:
        data = json.load(f)
    assert len(data["files"]) == 0
