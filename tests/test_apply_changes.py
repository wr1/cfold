from cfold.models.codebase import codebase
from cfold.models.file_entry import file_entry
from cfold.unfold.apply_changes import apply_changes


def test_apply_changes(tmp_path):
    """Test apply_changes function."""
    # Create a codebase with one file
    data = codebase(
        instructions=[],
        files=[file_entry(path="test.py", content="print('test')")],
    )

    output_dir = tmp_path / "output"
    apply_changes(data, output_dir, original_dir=None)

    assert (output_dir / "test.py").exists()
    assert (output_dir / "test.py").read_text() == "print('test')"
