"""Tests for sum_codebases covering non-stdlib imports, syntax errors, and errors."""

from cfold.summarization.sum_codebases import sum_codebases


def test_sum_codebases_non_stdlib_imports(tmp_path):
    """Test sum_codebases includes non-stdlib imports in output."""
    (tmp_path / "app.py").write_text("import requests\nimport pydantic\n\ndef run(): pass\n")
    result, _ = sum_codebases([tmp_path])
    assert "requests" in result or "pydantic" in result


def test_sum_codebases_syntax_error(tmp_path):
    """Test sum_codebases reports syntax errors without crashing."""
    (tmp_path / "bad.py").write_text("def broken(\n")
    result, _ = sum_codebases([tmp_path])
    assert "Syntax error" in result or "skipped" in result


def test_sum_codebases_filter_with_files(tmp_path):
    """Test filter_files with files parameter filters by pattern."""
    from cfold.fold.fold import filter_files

    (tmp_path / "a.py").write_text("a")
    (tmp_path / "b.txt").write_text("b")
    files = [tmp_path / "a.py", tmp_path / "b.txt"]
    result = filter_files(["*.py"], tmp_path, files=files)
    assert tmp_path / "a.py" in result
    assert tmp_path / "b.txt" not in result
