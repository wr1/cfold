import yaml

from cfold.cli.rc import rc


def test_rc(tmp_path, monkeypatch):
    """Test rc command creates .foldrc with local as default."""
    monkeypatch.chdir(tmp_path)
    rc()
    foldrc = tmp_path / ".foldrc"
    assert foldrc.exists()
    with open(foldrc, "r", encoding="utf-8") as f:
        config = yaml.safe_load(f)
    assert config["default_dialect"] == "local"
    assert "local" in config
