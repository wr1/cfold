from importlib import resources
import yaml

def load_instructions(dialect="default"):
    """Load the boilerplate instructions and suffixes for the specified dialect from py.yml."""
    try:
        with resources.files("cfold").joinpath("resources/py.yml").open("r", encoding="utf-8") as f:
            config = yaml.load(f, Loader=yaml.SafeLoader)
        if dialect not in config:
            raise ValueError(f"Dialect '{dialect}' not found in py.yml")
        return {
            "prefix": config[dialect]["prefix"],
            "included_suffix": config[dialect]["included_suffix"]
        }
    except Exception as e:
        raise RuntimeError(f"Failed to load instructions for dialect '{dialect}' from py.yml: {e}")
