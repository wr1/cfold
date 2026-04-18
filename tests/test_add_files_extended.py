"""Tests for add CLI covering missing foldfile, non-file, and update branches."""

import json

from cfold.cli.add import add
from cfold.cli.fold import fold


def test_add_missing_foldfile(tmp_path, monkeypatch, capsys):
    """Test add with a non-existent foldfile prints error."""
    monkeypatch.chdir(tmp_path)
    add(files=["any.py"], foldfile="missing.json")
    captured = capsys.readouterr()
    assert "Error" in captured.out


def test_add_non_file(tmp_path, monkeypatch, capsys):
    """Test add skips paths that are not files (e.g. directories)."""
    project_dir = tmp_path / "project"
    project_dir.mkdir()
    (project_dir / "file1.py").write_text("code1")
    monkeypatch.chdir(project_dir)

    fold(files=["file1.py"], output="fold.json", dialect="default", bare=True)
    capsys.readouterr()

    # Pass a directory, not a file
    add(files=[str(project_dir)], foldfile="fold.json")
    captured = capsys.readouterr()
    assert "Warning" in captured.out or "skipping" in captured.out


def test_add_updates_existing_file(tmp_path, monkeypatch, capsys):
    """Test add updates content of an existing file in the fold."""
    project_dir = tmp_path / "project"
    project_dir.mkdir()
    (project_dir / "file1.py").write_text("original")
    monkeypatch.chdir(project_dir)

    fold(files=["file1.py"], output="fold.json", dialect="default", bare=True)
    capsys.readouterr()

    # Update the file and re-add
    (project_dir / "file1.py").write_text("updated")
    add(files=["file1.py"], foldfile="fold.json")

    captured = capsys.readouterr()
    assert "updated existing" in captured.out

    with open("fold.json", "r", encoding="utf-8") as f:
        data = json.load(f)
    assert data["files"][0]["content"] == "updated"
