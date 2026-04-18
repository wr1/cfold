"""Basic folding example demonstrating how to fold a simple project into a JSON file."""

import os
import json
from pathlib import Path
from cfold.cli.fold import fold


def main():
    """Demonstrate basic folding functionality."""
    # Create a temporary simple project
    project_dir = Path("temp_example_project")
    project_dir.mkdir(exist_ok=True)
    (project_dir / "main.py").write_text('print("Hello, World!")\n')
    (project_dir / "utils.py").write_text("def helper():\n    return 'help'\n")
    (project_dir / "README.md").write_text("# Example Project\n")

    # Change to project directory
    original_cwd = Path.cwd()
    try:
        os.chdir(project_dir)

        # Fold the project using default dialect
        print("Folding project...")
        fold(
            files=[],
            output="folded.json",
            prompt=None,
            dialect="default",
            bare=False,
        )

        # Check the folded file
        folded_file = project_dir / "folded.json"
        if folded_file.exists():
            with open(folded_file, "r", encoding="utf-8") as f:
                data = json.load(f)
            print(f"Folded {len(data['files'])} files.")
            for file_entry in data["files"]:
                print(f"  - {file_entry['path']}")
        else:
            print("Folded file not created.")

    finally:
        # Cleanup
        os.chdir(original_cwd)
        if project_dir.exists():
            import shutil

            shutil.rmtree(project_dir)


if __name__ == "__main__":
    main()
