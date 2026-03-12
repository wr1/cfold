import json
from cfold.cli.fold import fold
from cfold.cli.add import add


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
