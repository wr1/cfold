import pytest
from pathlib import Path
import os
import sys

# Add the project root to sys.path to import examples
sys.path.insert(0, str(Path(__file__).parent.parent))

from examples.basic_fold import main as basic_main
from examples.using_profiles import main as using_profiles_main


def test_basic_fold(tmp_path, monkeypatch, capsys):
    """Test the basic_fold example runs successfully."""
    monkeypatch.chdir(tmp_path)
    basic_main()
    captured = capsys.readouterr()
    assert "Folded" in captured.out
    assert "files" in captured.out


def test_using_profiles(tmp_path, monkeypatch, capsys):
    """Test the using_profiles example runs successfully."""
    monkeypatch.chdir(tmp_path)
    using_profiles_main()
    captured = capsys.readouterr()
    assert "Folding with custom profile" in captured.out
    assert "Folding with py dialect" in captured.out
    assert "files" in captured.out
