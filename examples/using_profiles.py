"""Example demonstrating the use of different dialects and custom profiles."""

import os
import json
from pathlib import Path
import yaml
from cfold.cli.fold import fold


def main():
    """Demonstrate using different profiles/dialects for folding."""
    # Create a temporary project
    project_dir = Path("temp_profile_example")
    project_dir.mkdir(exist_ok=True)
    (project_dir / "src").mkdir()
    (project_dir / "src" / "main.py").write_text('print("Main code")\n')
    (project_dir / "src" / "utils.py").write_text("def util(): pass\n")
    (project_dir / "tests").mkdir()
    (project_dir / "tests" / "test_main.py").write_text("def test_main(): pass\n")
    (project_dir / "docs").mkdir()
    (project_dir / "docs" / "index.md").write_text("# Docs\n")
    (project_dir / "pyproject.toml").write_text("[project]\nname = 'example'\n")

    # Create a custom .foldrc profile
    foldrc = {
        "default_dialect": "custom",
        "custom": {
            "pre": ["py"],
            "instructions": [
                {
                    "type": "user",
                    "synopsis": "custom focus",
                    "content": "Focus on custom project structure.",
                }
            ],
            "included_suffix": [".py", ".toml", ".md"],
            "included_dirs": [".", "src", "tests", "docs"],
        },
    }
    with open(project_dir / ".foldrc", "w", encoding="utf-8") as f:
        yaml.safe_dump(foldrc, f)

    original_cwd = Path.cwd()
    try:
        os.chdir(project_dir)

        # Fold using default (which is custom from .foldrc)
        print("Folding with custom profile...")
        fold(
            files=[],
            output="folded_custom.json",
            prompt=None,
            dialect="default",
            bare=False,
        )

        # Fold using py dialect explicitly
        print("\nFolding with py dialect...")
        fold(
            files=[],
            output="folded_py.json",
            prompt=None,
            dialect="py",
            bare=False,
        )

        # Compare the folded files
        for fname in ["folded_custom.json", "folded_py.json"]:
            fpath = project_dir / fname
            if fpath.exists():
                with open(fpath, "r", encoding="utf-8") as f:
                    data = json.load(f)
                print(f"\n{fname}: {len(data['files'])} files")
                for file_entry in data["files"]:
                    print(f"  - {file_entry['path']}")

    finally:
        # Cleanup
        os.chdir(original_cwd)
        if project_dir.exists():
            import shutil

            shutil.rmtree(project_dir)


if __name__ == "__main__":
    main()
