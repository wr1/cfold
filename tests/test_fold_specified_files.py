import json
from cfold.cli.fold import fold


def test_fold_specified_files(tmp_path, monkeypatch):
    """Test that specified files override dialect include patterns."""
    project_dir = tmp_path / "project"
    project_dir.mkdir()
    (project_dir / "root_file.py").write_text("print('root')")
    (project_dir / "src").mkdir()
    (project_dir / "src" / "src_file.py").write_text("print('src')")

    monkeypatch.chdir(project_dir)

    fold(
        files=["root_file.py"],
        output="folded.json",
        prompt=None,
        dialect="py",
        bare=False,
    )

    with open("folded.json", "r", encoding="utf-8") as f:
        data = json.load(f)
    assert len(data["files"]) == 1
    assert data["files"][0]["path"] == "root_file.py"
