from pathlib import Path
import tempfile
from cfold.summarization.sum_codebases import sum_codebases


def test_sum_codebases_multiple():
    """Test summing multiple codebases."""
    with tempfile.TemporaryDirectory() as tmpdir:
        cb1 = Path(tmpdir) / "cb1"
        cb1.mkdir()
        (cb1 / "func.py").write_text("def func(): pass")
        cb2 = Path(tmpdir) / "cb2"
        cb2.mkdir()
        (cb2 / "class.py").write_text("class C: pass")
        summary = sum_codebases([cb1, cb2])
        assert "Codebase: " in summary
        assert "fn: func()" in summary
        assert "cls: C" in summary
