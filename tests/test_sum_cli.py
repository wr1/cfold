from cfold.cli.sum import sum


def test_sum_cli(tmp_path):
    """Test the sum CLI command."""
    # Create a test codebase
    codebase_dir = tmp_path / "codebase"
    codebase_dir.mkdir()
    (codebase_dir / "main.py").write_text("def main(): pass")

    output_file = tmp_path / "summary.txt"
    sum(
        codebases=[str(codebase_dir)],
        output=str(output_file),
        include_tests=False,
        clip=False,
    )

    assert output_file.exists()
    content = output_file.read_text(encoding="utf-8")
    assert "Codebase:" in content
    assert "fn: main()" in content
