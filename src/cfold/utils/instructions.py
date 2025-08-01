"""Load instructions and patterns for specified dialect."""
from importlib import resources
import yaml

def load_instructions(dialect="default"):
    """Load the boilerplate instructions and patterns for the specified dialect from py.yml."""
    try:
        with resources.files("cfold").joinpath("resources/py.yml").open(
            "r", encoding="utf-8"
        ) as f:
            config = yaml.safe_load(f)  # Use safe_load for security
        common = config.get("common", {})
        if dialect not in config:
            raise ValueError(f"Dialect '{dialect}' not found in py.yml")
        instr = config[dialect]
        return common.get("system", ""), {
            "system": instr.get("system", ""),
            "user": instr.get("user", ""),
            "assistant": instr.get("assistant", ""),
            "included": [f"*{pat}" for pat in instr.get("included_suffix", [])],  # Convert suffixes to fnmatch patterns
            "excluded": instr.get("excluded", []),
            "included_dirs": instr.get("included_dirs", []),
        }
    except Exception as e:
        raise RuntimeError(
            f"Failed to load instructions for dialect '{dialect}' from py.yml: {e}"
        )

def get_available_dialects():
    """Get the list of available dialects from py.yml."""
    try:
        with resources.files("cfold").joinpath("resources/py.yml").open(
            "r", encoding="utf-8"
        ) as f:
            config = yaml.safe_load(f)
        return [k for k in config.keys() if k != "common"]
    except Exception as e:
        raise RuntimeError(f"Failed to load dialects: {e}")


