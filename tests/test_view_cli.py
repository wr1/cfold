from cfold.cli.fold import fold
from cfold.cli.view import view


def test_view_cli(tmp_path, monkeypatch, capsys):
    """Test the view CLI command."""
    project_dir = tmp_path / "project"
    project_dir.mkdir()
    (project_dir / "file.py").write_text("print('hello')")

    monkeypatch.chdir(project_dir)

    # Fold
    fold(files=["file.py"], output="folded.json", dialect="default", bare=True)

    # View
    view(foldfile="folded.json")

    captured = capsys.readouterr()
    assert "Instructions" in captured.out
    assert "Files" in captured.out
    assert "file.py" in captured.out
