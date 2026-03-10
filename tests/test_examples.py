import json
import yaml
from cfold.cli.fold import fold


def test_basic_fold(tmp_path, monkeypatch, capsys):
    """Test the basic_fold example runs successfully."""
    # Create a temporary simple project
    project_dir = tmp_path / "temp_example_project"
    project_dir.mkdir()
    (project_dir / "main.py").write_text('print("Hello, World!")\n')
    (project_dir / "utils.py").write_text("def helper():\n    return 'help'\n")
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
    assert any(f["path"] == "main.py" for f in data["files"])
    assert any(f["path"] == "utils.py" for f in data["files"])
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
