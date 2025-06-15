"""Utilities for visualizing file trees using Rich Tree."""
import os
from rich.tree import Tree  # Import Rich Tree class

def get_folded_tree(files, cwd):
    """Generate a Rich Tree object for the folded files."""
    main_tree = Tree("Folded files tree")  # Create the main Tree
    for file_path in sorted(set(os.path.relpath(f, cwd) for f in files)):
        parts = file_path.split(os.sep)
        current_node = main_tree
        for part in parts[:-1]:  # Traverse directories
            subnodes = [node for node in current_node.children if node.label == part + os.sep]
            if subnodes:
                current_node = subnodes[0]
            else:
                new_node = current_node.add(part + os.sep)  # Add directory node
                current_node = new_node
        current_node.add(parts[-1])  # Add the file node
    return main_tree  # Return the Rich Tree object
