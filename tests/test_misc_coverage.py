"""Tests for misc coverage: rc existing file, codebase dict validator."""
from cfold.models.codebase import codebase
from cfold.models.instruction import instruction


def test_codebase_convert_dict_instructions():
    """Test codebase validator converts dict instructions to list."""
    # Pydantic field_validator with mode='before' handles dict -> list
    data = {
        "instructions": [{"type": "system", "content": "hello"}],
        "files": [],
    }
    cb = codebase.model_validate(data)
    assert len(cb.instructions) == 1
    assert cb.instructions[0].type == "system"


def test_rc_existing_foldrc(tmp_path, monkeypatch, capsys):
    """Test rc when .foldrc already exists updates it."""
    import yaml
    from cfold.cli.rc import rc

    foldrc = tmp_path / ".foldrc"
    foldrc.write_text(yaml.safe_dump({"existing_key": "value"}))
    monkeypatch.chdir(tmp_path)

    rc()
    captured = capsys.readouterr()
    assert "local" in captured.out or "created" in captured.out

    with foldrc.open() as f:
        config = yaml.safe_load(f)
    assert "local" in config
    assert config["default_dialect"] == "local"
    assert config["existing_key"] == "value"
