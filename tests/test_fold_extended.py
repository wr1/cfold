"""Tests for fold CLI covering invalid dialect, glob patterns, no files, and missing prompt."""
import json
import pytest
from cfold.cli.fold import fold


def test_fold_invalid_dialect(tmp_path, monkeypatch):
    """Test fold with invalid dialect raises SystemExit."""
    monkeypatch.chdir(tmp_path)
    (tmp_path / "file.py").write_text("x = 1")
    with pytest.raises(SystemExit):
        fold(files=["file.py"], output="out.json", dialect="nonexistent_dialect_xyz")


def test_fold_no_valid_files(tmp_path, monkeypatch, capsys):
    """Test fold with no matching files prints message and returns."""
    monkeypatch.chdir(tmp_path)
    # No files created, empty dir
    fold(files=[], output="out.json", dialect="default", bare=True)
    captured = capsys.readouterr()
    assert "No valid files to fold" in captured.out


def test_fold_missing_prompt_file(tmp_path, monkeypatch, capsys):
    """Test fold with a missing prompt file prints warning."""
    (tmp_path / "file.py").write_text("x = 1")
    monkeypatch.chdir(tmp_path)
    fold(
        files=["file.py"],
        output="out.json",
        prompt="nonexistent_prompt.txt",
        dialect="default",
        bare=True,
    )
    captured = capsys.readouterr()
    assert "Warning" in captured.out or "does not exist" in captured.out


def test_fold_glob_pattern(tmp_path, monkeypatch):
    """Test fold with glob pattern expands and includes matching files."""
    (tmp_path / "a.py").write_text("a = 1")
    (tmp_path / "b.py").write_text("b = 2")
    monkeypatch.chdir(tmp_path)
    fold(files=["**.py"], output="out.json", dialect="default", bare=True)

    with open("out.json", "r", encoding="utf-8") as f:
        data = json.load(f)
    paths = {entry["path"] for entry in data["files"]}
    assert "a.py" in paths
    assert "b.py" in paths
