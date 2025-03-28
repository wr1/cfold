#!/usr/bin/env python3
import os
import argparse
import shutil

def fold(directory, output="codefold.txt"):
    """Wrap a directory's codebase into a single file with LLM instructions."""
    with open(output, "w", encoding="utf-8") as outfile:
        # Write LLM instructions at the top
        outfile.write(
            "# Instructions for LLM:\n"
            "# - To modify a file, keep its '# --- File: path ---' header and update the content below.\n"
            "# - To delete a file, replace its content with '# DELETE'.\n"
            "# - To add a new file, include a new '# --- File: path ---' section with the desired content.\n"
            "# - Preserve the '# --- File: path ---' format for all files.\n\n"
        )
        # Fold the codebase
        for dirpath, _, filenames in os.walk(directory):
            for filename in filenames:
                if filename.endswith((".py", ".js", ".cpp", ".java", ".txt")):  # Add more extensions as needed
                    filepath = os.path.join(dirpath, filename)
                    relpath = os.path.relpath(filepath, directory)
                    outfile.write(f"# --- File: {relpath} ---\n")
                    with open(filepath, "r", encoding="utf-8") as infile:
                        outfile.write(infile.read() + "\n\n")
    print(f"Codebase folded into {output}")

def unfold(fold_file, output_dir="unfolded_codebase"):
    """Unfold a modified fold file back into a directory structure."""
    if os.path.exists(output_dir):
        shutil.rmtree(output_dir)  # Clear previous unfolded directory
    os.makedirs(output_dir, exist_ok=True)

    with open(fold_file, "r", encoding="utf-8") as infile:
        content = infile.read()
        # Skip instructions (everything before the first file marker)
        if "# Instructions for LLM:" in content:
            content = content.split("# Instructions for LLM:")[1].split("\n\n", 1)[1]
        # Split into file sections
        sections = content.split("# --- File: ")[1:]  # Skip empty first section

        for section in sections:
            lines = section.split("\n", 1)
            if len(lines) < 2:
                continue
            filepath = lines[0].strip()
            file_content = lines[1].strip()

            # Handle deletion
            if file_content == "# DELETE":
                print(f"Marked for deletion: {filepath} (skipped)")
                continue

            # Write the file (new or modified)
            full_path = os.path.join(output_dir, filepath)
            os.makedirs(os.path.dirname(full_path), exist_ok=True)
            with open(full_path, "w", encoding="utf-8") as outfile:
                outfile.write(file_content)
    print(f"Codebase unfolded into {output_dir}")

def main():
    parser = argparse.ArgumentParser(description="cfold: Fold and unfold codebases for LLM interaction.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # Fold command
    fold_parser = subparsers.add_parser("fold", help="Fold a directory into a single file.")
    fold_parser.add_argument("directory", help="Directory to fold.")
    fold_parser.add_argument("--output", "-o", default="codefold.txt", help="Output file (default: codefold.txt)")

    # Unfold command
    unfold_parser = subparsers.add_parser("unfold", help="Unfold a modified file into a directory.")
    unfold_parser.add_argument("foldfile", help="File to unfold.")
    unfold_parser.add_argument("--output-dir", "-d", default="unfolded_codebase", 
                              help="Output directory (default: unfolded_codebase)")

    args = parser.parse_args()

    if args.command == "fold":
        fold(args.directory, args.output)
    elif args.command == "unfold":
        unfold(args.foldfile, args.output_dir)

if __name__ == "__main__":
    main()