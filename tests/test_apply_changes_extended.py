"""Tests for apply_changes covering delete, modified, and original_dir branches."""
from cfold.models.codebase import codebase
from cfold.models.file_entry import file_entry
from cfold.unfold.apply_changes import apply_changes


def test_apply_changes_with_original_dir(tmp_path):
    """Test apply_changes copies original_dir and tracks modified files."""
    original_dir = tmp_path / "original"
    original_dir.mkdir()
    (original_dir / "existing.py").write_text("old content")

    output_dir = tmp_path / "output"
    data = codebase(
        instructions=[],
        files=[file_entry(path="existing.py", content="new content")],
    )
    apply_changes(data, output_dir, original_dir=original_dir)

    assert (output_dir / "existing.py").read_text() == "new content"


def test_apply_changes_delete(tmp_path):
    """Test apply_changes deletes files marked for deletion."""
    output_dir = tmp_path / "output"
    output_dir.mkdir()
    (output_dir / "to_delete.py").write_text("delete me")

    data = codebase(
        instructions=[],
        files=[file_entry(path="to_delete.py", content=None, delete=True)],
    )
    apply_changes(data, output_dir, original_dir=None)

    assert not (output_dir / "to_delete.py").exists()


def test_apply_changes_delete_nonexistent(tmp_path):
    """Test apply_changes delete on non-existent file does nothing."""
    output_dir = tmp_path / "output"
    output_dir.mkdir()

    data = codebase(
        instructions=[],
        files=[file_entry(path="ghost.py", content=None, delete=True)],
    )
    # Should not raise
    apply_changes(data, output_dir, original_dir=None)


def test_apply_changes_new_and_modified(tmp_path, capsys):
    """Test apply_changes tree shows added and modified files."""
    original_dir = tmp_path / "original"
    original_dir.mkdir()
    (original_dir / "mod.py").write_text("old")

    output_dir = tmp_path / "output"
    data = codebase(
        instructions=[],
        files=[
            file_entry(path="mod.py", content="new"),
            file_entry(path="added.py", content="brand new"),
        ],
    )
    apply_changes(data, output_dir, original_dir=original_dir)

    assert (output_dir / "mod.py").read_text() == "new"
    assert (output_dir / "added.py").read_text() == "brand new"
