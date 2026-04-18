from cfold.dialect.load_instructions import collect_patterns


def test_collect_patterns_with_pre():
    """Test collecting include patterns with pre dependencies."""
    config = {
        "base": {"include": ["**/*.py"]},
        "test": {"pre": ["base"], "include": ["src/**/*.py"]},
    }
    result = collect_patterns(config, "test")
    assert result == {"include": ["src/**/*.py"]}
