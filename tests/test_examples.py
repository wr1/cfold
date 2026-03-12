import json
import yaml
import subprocess
from cfold.cli.fold import fold
from cfold.cli.add import add
from cfold.cli.rc import rc


def test_basic_fold(tmp_path, monkeypatch, capsys):
    """Test the basic_fold example runs successfully."""
    # Create a temporary simple project
    project_dir = tmp_path / "temp_example_project"
    project_dir.mkdir()
    (project_dir / "src").mkdir()
    (project_dir / "src" / "main.py").write_text('print("Hello, World!")\n')
    (project_dir / "src" / "utils.py").write_text("def helper():\n    return 'help'\n")
    (project_dir / "README.md").write_text("# Example Project\n")

    # Change to project directory
    monkeypatch.chdir(project_dir)

    # Fold the project using default dialect
    fold(
        files=[],
        output="folded.json",
        prompt=None,
        dialect="default",
        bare=False,
    )

    captured = capsys.readouterr()
    assert "Folded" in captured.out
    assert "files" in captured.out

    # Check the folded file
    folded_file = project_dir / "folded.json"
    assert folded_file.exists()
    with open(folded_file, "r", encoding="utf-8") as f:
        data = json.load(f)
    assert len(data["files"]) == 3
    assert any(f["path"] == "src/main.py" for f in data["files"])
    assert any(f["path"] == "src/utils.py" for f in data["files"])
    assert any(f["path"] == "README.md" for f in data["files"])


def test_using_profiles(tmp_path, monkeypatch, capsys):
    """Test the using_profiles example runs successfully."""
    # Create a temporary project
    project_dir = tmp_path / "temp_profile_example"
    project_dir.mkdir()
    (project_dir / "src").mkdir()
    (project_dir / "src" / "main.py").write_text('print("Main code")\n')
    (project_dir / "src" / "utils.py").write_text("def util(): pass\n")
    (project_dir / "tests").mkdir()
    (project_dir / "tests" / "test_main.py").write_text("def test_main(): pass\n")
    (project_dir / "docs").mkdir()
    (project_dir / "docs" / "index.md").write_text("# Docs\n")
    (project_dir / "pyproject.toml").write_text("[project]\nname = 'example'\n")

    # Create a custom .foldrc profile
    foldrc = {
        "default_dialect": "custom",
        "custom": {
            "pre": ["py"],
            "instructions": [
                {
                    "type": "user",
                    "synopsis": "custom focus",
                    "content": "Focus on custom project structure.",
                }
            ],
            "included_suffix": [".py", ".toml", ".md"],
            "included_dirs": [".", "src", "tests", "docs"],
        },
    }
    with open(project_dir / ".foldrc", "w", encoding="utf-8") as f:
        yaml.safe_dump(foldrc, f)

    monkeypatch.chdir(project_dir)

    # Fold using default (which is custom from .foldrc)
    fold(
        files=[],
        output="folded_custom.json",
        prompt=None,
        dialect="default",
        bare=False,
    )

    # Fold using py dialect explicitly
    fold(
        files=[],
        output="folded_py.json",
        prompt=None,
        dialect="py",
        bare=False,
    )

    captured = capsys.readouterr()
    assert "Codebase folded into folded_custom.json." in captured.out
    assert "Codebase folded into folded_py.json." in captured.out
    assert "files" in captured.out

    # Compare the folded files
    for fname in ["folded_custom.json", "folded_py.json"]:
        fpath = project_dir / fname
        assert fpath.exists()
        with open(fpath, "r", encoding="utf-8") as f:
            data = json.load(f)
        assert len(data["files"]) > 0
        assert any(f["path"] == "src/main.py" for f in data["files"])
        if fname == "folded_custom.json":
            assert len(data["files"]) == 5
            assert any(f["path"] == "docs/index.md" for f in data["files"])
        else:
            assert len(data["files"]) == 4
            assert not any(f["path"] == "docs/index.md" for f in data["files"])


def test_fold_specified_files(tmp_path, monkeypatch):
    """Test that specified files override dialect include patterns."""
    project_dir = tmp_path / "project"
    project_dir.mkdir()
    (project_dir / "root_file.py").write_text("print('root')")
    (project_dir / "src").mkdir()
    (project_dir / "src" / "src_file.py").write_text("print('src')")

    monkeypatch.chdir(project_dir)

    fold(
        files=["root_file.py"],
        output="folded.json",
        prompt=None,
        dialect="py",
        bare=False,
    )

    with open("folded.json", "r", encoding="utf-8") as f:
        data = json.load(f)
    assert len(data["files"]) == 1
    assert data["files"][0]["path"] == "root_file.py"


def test_add_files(tmp_path, monkeypatch, capsys):
    """Test adding files to an existing fold file and check tree output."""
    project_dir = tmp_path / "project"
    project_dir.mkdir()
    (project_dir / "file1.py").write_text("code1")
    (project_dir / "file2.py").write_text("code2")

    monkeypatch.chdir(project_dir)

    # First fold file1
    fold(
        files=["file1.py"],
        output="fold.json",
        prompt=None,
        dialect="default",
        bare=True,
    )

    # Then add file2
    add(files=["file2.py"], foldfile="fold.json")

    captured = capsys.readouterr()
    assert "Added files to fold.json and copied to clipboard." in captured.out
    assert "file2.py" in captured.out

    # Check the file has both
    with open("fold.json", "r", encoding="utf-8") as f:
        data = json.load(f)
    assert len(data["files"]) == 2
    paths = {f["path"] for f in data["files"]}
    assert "file1.py" in paths
    assert "file2.py" in paths


def test_rc(tmp_path, monkeypatch):
    """Test rc command creates .foldrc with local as default."""
    monkeypatch.chdir(tmp_path)
    rc()
    foldrc = tmp_path / ".foldrc"
    assert foldrc.exists()
    with open(foldrc, "r", encoding="utf-8") as f:
        config = yaml.safe_load(f)
    assert config["default_dialect"] == "local"
    assert "local" in config


def test_run_basic_fold_example():
    """Test running the basic_fold example script."""
    result = subprocess.run(
        ["python", "examples/basic_fold.py"],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0
    assert "Folded" in result.stdout


def test_run_using_profiles_example():
    """Test running the using_profiles example script."""
    result = subprocess.run(
        ["python", "examples/using_profiles.py"],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0
    assert "Codebase folded" in result.stdout
