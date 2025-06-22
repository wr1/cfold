from importlib import resources
import yaml

def load_instructions(dialect="default"):
    """Load the boilerplate instructions and patterns for the specified dialect from py.yml."""
    try:
        with resources.files("cfold").joinpath("resources/py.yml").open(
            "r", encoding="utf-8"
        ) as f:
            config = yaml.safe_load(f)  # Use safe_load for security
        if dialect not in config:
            raise ValueError(f"Dialect '{dialect}' not found in py.yml")
        return {
            "prefix": config[dialect]["prefix"],
            "included": config[dialect].get("included", []),  # List of fnmatch patterns to include
            "excluded": config[dialect].get("excluded", []),  # List of fnmatch patterns to exclude
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
        return list(config.keys())
    except Exception as e:
        raise RuntimeError(f"Failed to load dialects: {e}")
