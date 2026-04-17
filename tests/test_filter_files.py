import tempfile
from pathlib import Path

from cfold.fold.filter_files import filter_files


def test_filter_files():
    """Test filtering files with include patterns."""
    with tempfile.TemporaryDirectory() as tmp:
        cwd = Path(tmp)
        (cwd / "src").mkdir()
        (cwd / "src" / "file.py").write_text("code")
        (cwd / "file.txt").write_text("text")
        result = filter_files(["src/**/*.py"], cwd)
        assert len(result) == 1
        assert result[0].name == "file.py"
