from pathlib import Path
import tempfile
from cfold.summarization.summarize_codebases import summarize_codebases


def test_summarize_codebases_exclude_venv():
    """Test excluding .venv directory."""
    with tempfile.TemporaryDirectory() as tmpdir:
        codebase_path = Path(tmpdir) / "test_codebase"
        codebase_path.mkdir()
        (codebase_path / "main.py").write_text("def main(): pass")
        venv_dir = codebase_path / ".venv"
        venv_dir.mkdir()
        (venv_dir / "script.py").write_text("def script(): pass")
        summary = summarize_codebases([codebase_path])
        assert "function: main()" in summary
        assert "function: script()" not in summary
