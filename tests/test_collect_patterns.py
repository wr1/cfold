import pytest
from cfold.dialect.collect_patterns import collect_patterns


def test_collect_patterns_simple():
    """Test collecting include patterns without pre."""
    config = {"test": {"include": ["src/**/*.py"]}}
    result = collect_patterns(config, "test")
    assert result == {"include": ["src/**/*.py"]}


def test_collect_patterns_with_pre():
    """Test collecting include patterns with pre dependencies."""
    config = {
        "base": {"include": ["**/*.py"]},
        "test": {"pre": ["base"], "include": ["src/**/*.py"]},
    }
    result = collect_patterns(config, "test")
    assert result == {"include": ["src/**/*.py"]}
