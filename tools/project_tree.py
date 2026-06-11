#!/usr/bin/env python3

import os
import argparse

DEFAULT_EXCLUDED_DIRS = {'.venv', '.git', 'build', '.pytest_cache', 'data', 'dist', 'docs', 'releases', '__pycache__'}

def print_tree(start_path, max_depth=3, prefix="", exclude_files=False):
    for root, dirs, files in os.walk(start_path):
        # Calculate current depth
        depth = root[len(start_path):].count(os.sep)
        if depth >= max_depth:
            dirs[:] = []
            continue

        # Exclude .venv and .git folders
        dirs[:] = [d for d in dirs if d not in DEFAULT_EXCLUDED_DIRS]

        indent = "│   " * depth
        print(f"{indent}├── {os.path.basename(root)}/")

        if not exclude_files:
            sub_indent = "│   " * (depth + 1)
            for f in files:
                print(f"{sub_indent}└── {f}")

def main():
    parser = argparse.ArgumentParser(description="Show project folder tree.")
    parser.add_argument("-p", "--path", type=str, default=".", help="Root path (default: current)")
    parser.add_argument("-l", "--levels", type=int, default=3, help="Depth to show (default: 3)")
    parser.add_argument("--exclude-files", action="store_true", help="Only show folders")

    args = parser.parse_args()
    root_path = os.path.abspath(args.path)

    print(f"\n📁 Project Tree: {root_path} (levels: {args.levels})")
    print("--------------------------------------------------")
    print_tree(root_path, max_depth=args.levels, exclude_files=args.exclude_files)

if __name__ == "__main__":
    main()
