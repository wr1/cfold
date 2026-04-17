"""Tests for build_codebase covering cwd=None, prompt_content, and binary files."""

from cfold.fold.fold import build_codebase


def test_build_codebase_no_cwd(tmp_path, monkeypatch):
    """Test build_codebase uses Path.cwd() when cwd=None."""
    monkeypatch.chdir(tmp_path)
    (tmp_path / "file.py").write_text("x = 1")
    result = build_codebase([tmp_path / "file.py"], instructions=[], cwd=None)
    assert len(result.files) == 1
    assert result.files[0].content == "x = 1"


def test_build_codebase_with_prompt(tmp_path):
    """Test build_codebase appends prompt instruction when prompt_content is set."""
    (tmp_path / "file.py").write_text("x = 1")
    result = build_codebase(
        [tmp_path / "file.py"], instructions=[], prompt_content="do something", cwd=tmp_path
    )
    assert any(i.type == "user" and i.name == "prompt" for i in result.instructions)


def test_build_codebase_skips_binary(tmp_path):
    """Test build_codebase skips binary files that cannot be decoded as UTF-8."""
    binary_file = tmp_path / "image.bin"
    binary_file.write_bytes(b"\xff\xfe\x00\x01\x80\x90\xa0\xb0")
    result = build_codebase([binary_file], instructions=[], cwd=tmp_path)
    assert len(result.files) == 0
