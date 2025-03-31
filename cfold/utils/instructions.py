import pkg_resources


def load_instructions():
    """Load the boilerplate instructions from the resources file."""
    try:
        instructions = pkg_resources.resource_string(
            "cfold", "resources/instructions.txt"
        ).decode("utf-8")
        return instructions
    except Exception as e:
        raise RuntimeError(f"Failed to load instructions from resources: {e}")
