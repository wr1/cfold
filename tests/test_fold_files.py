import json

from cfold.cli.fold import fold


def test_fold_files(tmp_path, monkeypatch):
    """Test folding specified files directly, overriding dialect includes."""
    # Create files
    (tmp_path / "file1.py").write_text("print('file1')")
    (tmp_path / "file2.py").write_text("print('file2')")
    (tmp_path / "ignore.py").write_text("ignore this")
    (tmp_path / "doc.md").write_text("# Doc")

    monkeypatch.chdir(tmp_path)

    fold(
        files=["file1.py", "doc.md"],
        output="folded.json",
        prompt=None,
        dialect="default",
        bare=False,
    )

    with open("folded.json", "r", encoding="utf-8") as f:
        data = json.load(f)
    # Only the specified files, even if dialect would include more
    assert len(data["files"]) == 2
    paths = {f["path"] for f in data["files"]}
    assert "file1.py" in paths
    assert "doc.md" in paths
    assert "file2.py" not in paths
    assert "ignore.py" not in paths
