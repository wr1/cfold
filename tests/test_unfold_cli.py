from cfold.cli.fold import fold
from cfold.cli.unfold import unfold


def test_unfold_cli(tmp_path, monkeypatch):
    """Test the unfold CLI command."""
    project_dir = tmp_path / "project"
    project_dir.mkdir()
    (project_dir / "file.py").write_text("print('hello')")

    monkeypatch.chdir(project_dir)

    # Fold
    fold(files=["file.py"], output="folded.json", dialect="default", bare=True)

    # Unfold to a new dir
    output_dir = tmp_path / "output"
    unfold(foldfile="folded.json", original_dir=None, output_dir=str(output_dir))

    assert (output_dir / "file.py").exists()
    assert (output_dir / "file.py").read_text() == "print('hello')"
