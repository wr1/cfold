from importlib import resources

def load_instructions():
    """Load the boilerplate instructions from the resources file."""
    try:
        with resources.files("cfold").joinpath("resources/instructions.txt").open("r", encoding="utf-8") as f:
            instructions = f.read()
        return instructions
    except Exception as e:
        raise RuntimeError(f"Failed to load instructions from resources: {e}")
