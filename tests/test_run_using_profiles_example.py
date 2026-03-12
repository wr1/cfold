import subprocess


def test_run_using_profiles_example():
    """Test running the using_profiles example script."""
    result = subprocess.run(
        ["python", "examples/using_profiles.py"],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0
    assert "Codebase folded" in result.stdout
