import sys
from pathlib import Path
from cfold.cli.entrypoint import main


def test_entrypoint_fold(tmp_path, monkeypatch):
    """Test entrypoint fold command."""
    monkeypatch.chdir(tmp_path)
    (tmp_path / "file.py").write_text("print('hello')")
    monkeypatch.setattr(sys, "argv", ["cfold", "fold", "file.py", "-o", "folded.json"])
    main()
    assert Path("folded.json").exists()


def test_entrypoint_sum(tmp_path, monkeypatch):
    """Test entrypoint sum command."""
    codebase_dir = tmp_path / "codebase"
    codebase_dir.mkdir()
    (codebase_dir / "main.py").write_text("def main(): pass")
    monkeypatch.setattr(
        sys, "argv", ["cfold", "sum", str(codebase_dir), "-o", "summary.txt"]
    )
    main()
    assert Path("summary.txt").exists()
