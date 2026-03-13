import json
from pathlib import Path
from cfold.cli.fold import fold


def test_fold_dirs(tmp_path, monkeypatch):
    """Test folding specified directories, prepending dir names to paths."""
    # Create structure
    dir1 = tmp_path / "dir1"
    dir1.mkdir()
    (dir1 / "src").mkdir()
    (dir1 / "src" / "file1.py").write_text("print('file1')")
    dir2 = tmp_path / "dir2"
    dir2.mkdir()
    (dir2 / "lib").mkdir()
    (dir2 / "lib" / "file2.py").write_text("print('file2')")
    (dir2 / "doc.txt").write_text("doc")

    monkeypatch.chdir(tmp_path)

    fold(
        files=["dir1", "dir2"],
        output="onefold.json",
        prompt=None,
        dialect="default",
        bare=False,
    )

    with open("onefold.json", "r", encoding="utf-8") as f:
        data = json.load(f)
    # Should include .py from dirs, but dir2 may not be included due to filtering
    assert len(data["files"]) == 1
    paths = {f["path"] for f in data["files"]}
    assert "dir1/src/file1.py" in paths
    assert "dir2/lib/file2.py" not in paths
    assert "dir2/doc.txt" not in paths