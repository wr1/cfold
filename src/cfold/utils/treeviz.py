"""Utilities for visualizing file trees."""
import os
from collections import defaultdict

def get_folded_tree_lines(files, cwd):
    """Generate lines for a tree visualization of the folded files."""
    tree = defaultdict(list)
    for file_path in files:
        relpath = os.path.relpath(file_path, cwd)
        dirpath, filename = os.path.split(relpath)
        tree[dirpath].append(filename)
    
    lines = []
    def add_tree_lines(current_dir, prefix=''):
        subdirs = sorted([d for d in tree.keys() if d.startswith(current_dir + os.sep) or d == current_dir])
        files_in_dir = sorted(tree[current_dir])
        items = subdirs + files_in_dir  # Process subdirs first, then files
        
        for i, item in enumerate(items):
            is_last = i == len(items) - 1
            if item in subdirs:  # It's a subdirectory
                lines.append(prefix + '+-- ' + item + os.sep)
                next_prefix = prefix + ('    ' if is_last else '|   ')
                add_tree_lines(os.path.join(current_dir, item), next_prefix)
            else:  # It's a file
                lines.append(prefix + '+-- ' + item)
    add_tree_lines('')
    return lines
