import json

from cfold.cli.fold import fold


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
    assert "Codebase folded" in captured.out
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
