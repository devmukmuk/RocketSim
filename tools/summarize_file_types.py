from __future__ import annotations

from collections import Counter
from pathlib import Path
import argparse


def summarize_file_types(folder: Path, recursive: bool = True) -> Counter[str]:
    pattern = "**/*" if recursive else "*"
    counts: Counter[str] = Counter()

    for path in folder.glob(pattern):
        if not path.is_file():
            continue

        suffix = path.suffix.lower() or "[no extension]"
        counts[suffix] += 1

    return counts


def main() -> None:
    parser = argparse.ArgumentParser(description="Summarize file types by count.")
    parser.add_argument("folder", help="Folder to scan")
    parser.add_argument(
        "--no-recursive",
        action="store_true",
        help="Only scan the top-level folder",
    )

    args = parser.parse_args()

    folder = Path(args.folder).expanduser().resolve()

    if not folder.exists():
        raise FileNotFoundError(f"Folder not found: {folder}")

    if not folder.is_dir():
        raise NotADirectoryError(f"Not a folder: {folder}")

    counts = summarize_file_types(folder, recursive=not args.no_recursive)

    print(f"\nFile type summary for: {folder}\n")

    total = sum(counts.values())

    for ext, count in counts.most_common():
        print(f"{ext:20} {count:8}")

    print("-" * 30)
    print(f"{'TOTAL':20} {total:8}")


if __name__ == "__main__":
    main()
