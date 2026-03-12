from pathlib import Path
import tempfile
from cfold.summarization.summarize_codebases import summarize_codebases


def test_summarize_codebases_include_tests():
    """Test including test directories when specified."""
    with tempfile.TemporaryDirectory() as tmpdir:
        codebase_path = Path(tmpdir) / "test_codebase"
        codebase_path.mkdir()
        (codebase_path / "main.py").write_text("def main(): pass")
        tests_dir = codebase_path / "tests"
        tests_dir.mkdir()
        (tests_dir / "test_main.py").write_text("def test_main(): pass")
        summary = summarize_codebases([codebase_path], include_tests=True)
        assert "function: main()" in summary
        assert "function: test_main()" in summary
