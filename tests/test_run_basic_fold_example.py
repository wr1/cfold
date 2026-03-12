import subprocess


def test_run_basic_fold_example():
    """Test running the basic_fold example script."""
    result = subprocess.run(
        ["python", "examples/basic_fold.py"],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0
    assert "Folded" in result.stdout
