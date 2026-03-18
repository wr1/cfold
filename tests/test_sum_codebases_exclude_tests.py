from pathlib import Path
import tempfile
from cfold.summarization.sum_codebases import sum_codebases


def test_sum_codebases_exclude_tests():
    """Test excluding test directories by default."""
    with tempfile.TemporaryDirectory() as tmpdir:
        codebase_path = Path(tmpdir) / "test_codebase"
        codebase_path.mkdir()
        (codebase_path / "main.py").write_text("def main(): pass")
        tests_dir = codebase_path / "tests"
        tests_dir.mkdir()
        (tests_dir / "test_main.py").write_text("def test_main(): pass")
        summary, _ = sum_codebases([codebase_path], include_tests=False)
        assert "fn: main()" in summary
        assert "fn: test_main()" not in summary
