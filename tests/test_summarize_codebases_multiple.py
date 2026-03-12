from pathlib import Path
import tempfile
from cfold.summarization.summarize_codebases import summarize_codebases


def test_summarize_codebases_multiple():
    """Test summarizing multiple codebases."""
    with tempfile.TemporaryDirectory() as tmpdir:
        cb1 = Path(tmpdir) / "cb1"
        cb1.mkdir()
        (cb1 / "func.py").write_text("def func(): pass")
        cb2 = Path(tmpdir) / "cb2"
        cb2.mkdir()
        (cb2 / "class.py").write_text("class C: pass")
        summary = summarize_codebases([cb1, cb2])
        assert "Codebase: " in summary
        assert "function: func()" in summary
        assert "class: C" in summary
