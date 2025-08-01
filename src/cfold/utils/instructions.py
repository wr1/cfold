"""Load instructions and patterns for specified dialect."""
from importlib import resources
import yaml
from typing import List
from cfold.models import Instruction

def load_instructions(dialect="default") -> List[Instruction]:
    """Load the boilerplate instructions and patterns for the specified dialect from py.yml as a list of Instruction."""
    try:
        with resources.files("cfold").joinpath("resources/py.yml").open(
            "r", encoding="utf-8"
        ) as f:
            config = yaml.safe_load(f)  # Use safe_load for security
        common = config.get("common", {})
        if dialect not in config:
            raise ValueError(f"Dialect '{dialect}' not found in py.yml")
        instr = config[dialect]
        instructions_list = []
        common_system = common.get("system", "")
        if common_system:
            instructions_list.append(Instruction(type="system", content=common_system, name="common"))
        dialect_system = instr.get("system", "")
        if dialect_system:
            instructions_list.append(Instruction(type="system", content=dialect_system, name=dialect))
        dialect_user = instr.get("user", "")
        if dialect_user:
            instructions_list.append(Instruction(type="user", content=dialect_user, name=dialect))
        dialect_assistant = instr.get("assistant", "")
        if dialect_assistant:
            instructions_list.append(Instruction(type="assistant", content=dialect_assistant, name=dialect))
        # Include patterns as part of the return? But for now, patterns are not in Instruction; adjust if needed
        # Actually, patterns are used separately, so perhaps return tuple: (instructions_list, patterns_dict)
        patterns = {
            "included": [f"*{pat}" for pat in instr.get("included_suffix", [])],  # Convert suffixes to fnmatch patterns
            "excluded": instr.get("excluded", []),
            "included_dirs": instr.get("included_dirs", []),
        }
        return instructions_list, patterns
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




