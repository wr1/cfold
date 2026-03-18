from pathlib import Path
import tempfile
from cfold.summarization.sum_codebases import sum_codebases


def test_sum_codebases_exclude_venv():
    """Test excluding .venv directory."""
    with tempfile.TemporaryDirectory() as tmpdir:
        codebase_path = Path(tmpdir) / "test_codebase"
        codebase_path.mkdir()
        (codebase_path / "main.py").write_text("def main(): pass")
        venv_dir = codebase_path / ".venv"
        venv_dir.mkdir()
        (venv_dir / "script.py").write_text("def script(): pass")
        summary, _ = sum_codebases([codebase_path])
        assert "fn: main()" in summary
        assert "fn: script()" not in summary
