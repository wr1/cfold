#!/bin/bash

ruff format
ruff check --fix > out.txt
uv run pytest -v >> out.txt
git add tests/test_fold_blank.py
git commit tests/test_fold_blank.py -m 'Add test for folding blank (current directory)'
git add tests/test_fold_dirs.py
git commit tests/test_fold_dirs.py -m 'Add test for folding specified directories'
git add tests/test_fold_files.py
git commit tests/test_fold_files.py -m 'Add test for folding specified files'
git add admin.sh
git commit admin.sh -m 'Add admin.sh script for formatting, linting, testing, and committing'