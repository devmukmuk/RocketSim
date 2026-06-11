#!/usr/bin/env python3
"""
Test Artifact Generator
--------------------------------
Creates release test artifacts and runs pytest.

Usage:
    python -m tools.test
"""

import shutil
import subprocess
import sys
from pathlib import Path
from datetime import datetime

# Import version info (single source of truth)
from src.mindit import __version__
version_parts = __version__.split(".")        # ["0","19","7"]
milestone = f"v{version_parts[0]}.{version_parts[1]}.0"
project_root = Path(__file__).resolve().parent.parent
release_folder = project_root / "releases" / f"release-v{__version__}"
test_folder = project_root / f"tests"
test_script = project_root / "tools" / "test.py"
requirements_file = release_folder / f"requirements_v{__version__}.txt"
project_dashboard_file = release_folder / f"dashboard_project.txt"
dashboard_file = release_folder / f"dashboard_v{__version__}.txt"
exe_name = f"PackIt-v{__version__}.exe"


# -------------------------------------------------------------------
# Helpers
# -------------------------------------------------------------------

def get_release_version() -> str:
    """
    Return release version formatted with leading 'v'.
    Ensures consistent folder naming like: v0.19.2
    """
    return __version__ if __version__.startswith("v") else f"v{__version__}"


def create_release_test_folder(release_version: str) -> Path:
    """Create release test folder structure."""
    release_root = release_folder
    test_folder = release_root / "tests"

    test_folder.mkdir(parents=True, exist_ok=True)

    return release_root


def copy_tests_to_release(release_root: Path):
    """Copy ./tests directory contents into release folder."""
    source_tests = test_folder
    dest_tests = release_root / "tests"

    if not source_tests.exists():
        print("ERROR: ./tests folder not found.")
        sys.exit(1)

    for item in source_tests.iterdir():
        dest = dest_tests / item.name
        if item.is_dir():
            shutil.copytree(item, dest, dirs_exist_ok=True)
        else:
            shutil.copy2(item, dest)


def run_pytest() -> subprocess.CompletedProcess:
    """Run pytest and capture output."""
    print("Running pytest...")
    return subprocess.run(
        ["pytest", "-v"],
        capture_output=True,
        text=True
    )


def write_test_summary(release_root: Path, release_version: str, result: subprocess.CompletedProcess):
    """Write pytest output and summary file."""
    summary_file = release_root / f"test_summary_{release_version}.txt"

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    with summary_file.open("w", encoding="utf-8") as f:
        f.write("Project Test Summary\n")
        f.write("=" * 60 + "\n")
        f.write(f"Release: {release_version}\n")
        f.write(f"Generated: {timestamp}\n")
        f.write(f"Return Code: {result.returncode}\n")
        f.write("=" * 60 + "\n\n")

        f.write("---- Pytest Output ----\n\n")
        f.write(result.stdout)

        if result.stderr:
            f.write("\n\n---- Errors ----\n\n")
            f.write(result.stderr)

    print(f"Test summary written to: {summary_file}")


# -------------------------------------------------------------------
# Main
# -------------------------------------------------------------------

def main():
    release_version = get_release_version()

    print(f"Preparing test artifacts for {release_version}")

    # Step 1
    release_root = create_release_test_folder(release_version)

    # Step 2
    copy_tests_to_release(release_root)

    # Step 3
    result = run_pytest()

    # Step 4
    write_test_summary(release_root, release_version, result)

    # Exit with pytest return code (important)
    sys.exit(result.returncode)


if __name__ == "__main__":
    main()
