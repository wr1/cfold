import json
from pathlib import Path
from cfold.cli.fold import fold


def test_fold_blank(tmp_path, monkeypatch):
    """Test folding the current directory with no arguments (blank)."""
    # Create a project structure
    (tmp_path / "main.py").write_text("print('main')")
    (tmp_path / "utils.py").write_text("def util(): pass")
    (tmp_path / "README.md").write_text("# Readme")
    (tmp_path / "ignore.txt").write_text("ignore this")

    monkeypatch.chdir(tmp_path)

    fold(
        files=[],
        output="folded.json",
        prompt=None,
        dialect="default",
        bare=False,
    )

    with open("folded.json", "r", encoding="utf-8") as f:
        data = json.load(f)
    # Default dialect includes .md, but not .py or .txt
    assert len(data["files"]) == 1
    paths = {f["path"] for f in data["files"]}
    assert "README.md" in paths
    assert "main.py" not in paths
    assert "utils.py" not in paths
    assert "ignore.txt" not in paths