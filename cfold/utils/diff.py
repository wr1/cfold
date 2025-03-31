def apply_diff(original_lines, modified_lines):
    """Apply unified diff changes or full content replacement."""
    if not modified_lines or not any(line.startswith("---") for line in modified_lines):
        # Full content replacement
        return "".join(modified_lines)

    # Handle unified diff format
    diff_lines = [
        line for line in modified_lines if not line.startswith(("---", "+++"))
    ]
    if not diff_lines or not any(line.startswith("@@") for line in diff_lines):
        return "".join(modified_lines)  # No valid diff hunks, treat as full content

    result = list(original_lines)
    current_pos = 0
    hunk = []
    for line in diff_lines:
        if line.startswith("@@"):
            if hunk:
                # Apply previous hunk
                for h_line in hunk:
                    if h_line.startswith("-") and current_pos < len(result):
                        result.pop(current_pos)
                    elif h_line.startswith("+"):
                        result.insert(current_pos, h_line[1:])
                        current_pos += 1
                    elif h_line.startswith(" "):
                        current_pos += 1
            hunk = [line]
        elif line.startswith(("+", "-", " ")):
            hunk.append(line)

    # Apply final hunk
    if hunk:
        for h_line in hunk:
            if h_line.startswith("-") and current_pos < len(result):
                result.pop(current_pos)
            elif h_line.startswith("+"):
                result.insert(current_pos, h_line[1:])
                current_pos += 1
            elif h_line.startswith(" "):
                current_pos += 1

    return "".join(result)
