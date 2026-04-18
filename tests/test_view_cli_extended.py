"""Tests for view CLI covering error and instructions-with-metadata branches."""

from cfold.cli.view import view


def test_view_invalid_file(tmp_path, monkeypatch, capsys):
    """Test view with a non-existent file prints error."""
    monkeypatch.chdir(tmp_path)
    view(foldfile="nonexistent.json")
    captured = capsys.readouterr()
    assert "Error" in captured.out


def test_view_instructions_with_name_and_synopsis(tmp_path, monkeypatch, capsys):
    """Test view with instructions that have name and synopsis."""
    import json

    fold_data = {
        "instructions": [
            {"type": "system", "name": "my_instr", "synopsis": "does stuff", "content": "hello"}
        ],
        "files": [{"path": "a.py", "content": "x = 1"}],
    }
    fold_file = tmp_path / "test.json"
    fold_file.write_text(json.dumps(fold_data))
    monkeypatch.chdir(tmp_path)

    view(foldfile="test.json")
    captured = capsys.readouterr()
    assert "my_instr" in captured.out
    assert "does stuff" in captured.out
    assert "a.py" in captured.out


def test_view_with_delete_file(tmp_path, monkeypatch, capsys):
    """Test view shows delete files in red."""
    import json

    fold_data = {
        "instructions": [],
        "files": [{"path": "old.py", "content": None, "delete": True}],
    }
    fold_file = tmp_path / "test.json"
    fold_file.write_text(json.dumps(fold_data))
    monkeypatch.chdir(tmp_path)

    view(foldfile="test.json")
    captured = capsys.readouterr()
    assert "old.py" in captured.out
