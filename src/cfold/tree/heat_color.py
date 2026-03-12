"""Get heat color based on percentage."""


def heat_color(percent: float) -> str:
    """Get heat color based on percentage."""
    if percent > 50:
        return "red"
    elif percent > 20:
        return "yellow"
    else:
        return "green"
