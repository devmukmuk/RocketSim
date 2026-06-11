#!/usr/bin/env python3
"""
MindIt Release Script
---------------------

Protected-main friendly release workflow.

Typical usage:

    # Build release artifacts, commit on release branch, push branch, create PR
    python -m tools.release --autobuild --publish --os win

    # Same, but skip tests/dashboard if needed
    python -m tools.release --autobuild --publish --os win --skip-tests --skip-dashboard

    # Build only current version binary; no version bump, no release folder, no git
    python -m tools.release --binary-only --os win

    # After release PR is merged, checkout/pull main, then create tag + GitHub release
    python -m tools.release --tag-only --version 0.2026.31 --os win

Workflow philosophy:

    main is protected.
    release.py prepares release branches.
    GitHub PR merges release into main.
    tags are created only after main contains the release commit.
"""

from __future__ import annotations

import argparse
import configparser
import importlib
import platform
import re
import shutil
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path

from googleapiclient.discovery import build
from rich import text


VERSION_PATTERN = r'__version__\s*=\s*["\'](\d+)\.(\d+)\.(\d+)["\']'


# -------------------------------------------------
# Data Models
# -------------------------------------------------
@dataclass(frozen=True)
class ReleaseArgs:
    """Parsed release command options."""

    major: int | None
    minor: int | None
    build: int | None
    version: str | None
    autobuild: bool
    target_os: str | None
    binary_only: bool
    publish: bool
    tag_only: bool
    skip_tests: bool
    skip_dashboard: bool
    no_pr: bool


@dataclass(frozen=True)
class TargetPlatform:
    """Resolved target platform flags."""

    is_windows: bool
    is_linux: bool

    @property
    def name(self) -> str:
        return "windows" if self.is_windows else "linux"


@dataclass(frozen=True)
class VersionInfo:
    """Resolved version and release folder."""

    version: str
    release_folder: Path
    major: int
    minor: int
    build: int


@dataclass(frozen=True)
class BinaryResult:
    """Built binary path and executable name."""

    exe_name: str
    dist_path: Path
    release_copy_path: Path | None = None


# -------------------------------------------------
# Argument Parsing
# -------------------------------------------------
def parse_args() -> ReleaseArgs:
    """Parse command line options."""
    parser = argparse.ArgumentParser(description="Build and publish MindIt releases.")

    parser.add_argument("--major", type=int)
    parser.add_argument("--minor", type=int)
    parser.add_argument("--build", type=int)
    parser.add_argument(
        "--version",
        help="Explicit version, mainly used with --tag-only. Example: 0.2026.31",
    )
    parser.add_argument("--autobuild", action="store_true")
    parser.add_argument("--os", dest="target_os", choices=["win", "linux"])
    parser.add_argument(
        "--binary-only",
        action="store_true",
        help="Build executable only from current version. No release folder or git actions.",
    )
    parser.add_argument(
        "--publish",
        action="store_true",
        help="Create release branch, commit release files, push branch, and create PR.",
    )
    parser.add_argument(
        "--tag-only",
        action="store_true",
        help="Create/push tag and GitHub release from current main after PR is merged.",
    )
    parser.add_argument(
        "--skip-tests",
        action="store_true",
        help="Skip the test suite during full release.",
    )
    parser.add_argument(
        "--skip-dashboard",
        action="store_true",
        help="Skip dashboard generation during full release.",
    )
    parser.add_argument(
        "--no-pr",
        action="store_true",
        help="With --publish, push release branch but do not create GitHub PR.",
    )

    parsed = parser.parse_args()

    if parsed.binary_only and parsed.publish:
        parser.error("--binary-only cannot be combined with --publish")

    if parsed.binary_only and parsed.tag_only:
        parser.error("--binary-only cannot be combined with --tag-only")

    if parsed.publish and parsed.tag_only:
        parser.error("--publish cannot be combined with --tag-only")

    return ReleaseArgs(
        major=parsed.major,
        minor=parsed.minor,
        build=parsed.build,
        version=parsed.version,
        autobuild=parsed.autobuild,
        target_os=parsed.target_os,
        binary_only=parsed.binary_only,
        publish=parsed.publish,
        tag_only=parsed.tag_only,
        skip_tests=parsed.skip_tests,
        skip_dashboard=parsed.skip_dashboard,
        no_pr=parsed.no_pr,
    )


# -------------------------------------------------
# Command Helpers
# -------------------------------------------------
def run_command(command: list[str], description: str, cwd: Path | None = None) -> None:
    """Run a command and stop on failure."""
    print(f"\n🔹 {description}")
    result = subprocess.run(command, cwd=cwd, check=False)
    if result.returncode != 0:
        print(f"❌ Failed: {description}")
        sys.exit(result.returncode)
    print(f"✅ Completed: {description}")


def run_git(command: list[str], description: str, project_root: Path) -> None:
    """Run a git command."""
    run_command(["git", *command], description, cwd=project_root)


def run_gh(command: list[str], description: str, project_root: Path) -> None:
    """Run a GitHub CLI command."""
    run_command(["gh", *command], description, cwd=project_root)


def capture_command(command: list[str], project_root: Path) -> str:
    """Run a command and return stdout."""
    result = subprocess.run(
        command,
        cwd=project_root,
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        stderr = result.stderr.strip()
        if stderr:
            print(stderr)
        sys.exit(result.returncode)
    return result.stdout.strip()


def capture_command_allow_failure(command: list[str], project_root: Path) -> tuple[int, str, str]:
    """Run a command and return returncode, stdout, stderr."""
    result = subprocess.run(
        command,
        cwd=project_root,
        capture_output=True,
        text=True,
        check=False,
    )
    return result.returncode, result.stdout.strip(), result.stderr.strip()


# -------------------------------------------------
# Git Helpers
# -------------------------------------------------
def get_current_branch(project_root: Path) -> str:
    """Return the current git branch."""
    return capture_command(["git", "rev-parse", "--abbrev-ref", "HEAD"], project_root)


def ensure_worktree_clean(project_root: Path) -> None:
    """Fail if working tree already has uncommitted changes."""
    status = capture_command(["git", "status", "--porcelain"], project_root)
    if status:
        print("❌ Working tree is not clean. Commit, stash, or discard changes first.")
        print(status)
        sys.exit(1)


def ensure_on_main(project_root: Path) -> None:
    """Ensure command is being run from main."""
    branch = get_current_branch(project_root)
    if branch != "main":
        print(f"❌ This command must run from main. Current branch: {branch}")
        sys.exit(1)


def ensure_tag_does_not_exist(project_root: Path, tag_name: str) -> None:
    """Fail if a tag already exists locally or remotely."""
    local_result = subprocess.run(
        ["git", "rev-parse", "--verify", tag_name],
        cwd=project_root,
        capture_output=True,
        text=True,
        check=False,
    )
    if local_result.returncode == 0:
        print(f"❌ Local tag already exists: {tag_name}")
        sys.exit(1)

    remote_result = subprocess.run(
        ["git", "ls-remote", "--tags", "origin", tag_name],
        cwd=project_root,
        capture_output=True,
        text=True,
        check=False,
    )
    if remote_result.returncode == 0 and remote_result.stdout.strip():
        print(f"❌ Remote tag already exists: {tag_name}")
        sys.exit(1)


def ensure_branch_does_not_exist(project_root: Path, branch_name: str) -> None:
    """Fail if release branch already exists locally or remotely."""
    local_code, _, _ = capture_command_allow_failure(
        ["git", "rev-parse", "--verify", branch_name],
        project_root,
    )
    if local_code == 0:
        print(f"❌ Local branch already exists: {branch_name}")
        sys.exit(1)

    remote_code, remote_out, _ = capture_command_allow_failure(
        ["git", "ls-remote", "--heads", "origin", branch_name],
        project_root,
    )
    if remote_code == 0 and remote_out:
        print(f"❌ Remote branch already exists: origin/{branch_name}")
        sys.exit(1)


def create_release_branch(project_root: Path, version: str) -> str:
    """Create a release branch from main."""
    branch_name = f"release/v{version}"
    ensure_branch_does_not_exist(project_root, branch_name)
    run_git(["checkout", "-b", branch_name], f"Creating release branch {branch_name}", project_root)
    return branch_name


def commit_release_changes(project_root: Path, version: str) -> None:
    """Stage and commit release changes if any exist."""
    tag_name = f"v{version}"

    run_git(["add", "-A"], "Staging release changes", project_root)

    status = capture_command(["git", "status", "--porcelain"], project_root)
    if not status:
        print("⚠️ No release changes to commit.")
        return

    run_git(["commit", "-m", f"release: {tag_name}"], "Committing release changes", project_root)


def push_release_branch(project_root: Path, branch_name: str) -> None:
    """Push release branch to origin."""
    run_git(
        ["push", "-u", "origin", branch_name],
        f"Pushing release branch {branch_name}",
        project_root,
    )


def create_release_pr(project_root: Path, version: str) -> None:
    """Create a GitHub pull request for the release branch."""
    tag_name = f"v{version}"

    run_gh(
        [
            "pr",
            "create",
            "--base",
            "main",
            "--title",
            f"Release {tag_name}",
            "--body",
            f"Automated release preparation for {tag_name}.",
        ],
        "Creating release pull request",
        project_root,
    )


# -------------------------------------------------
# Project / Config Detection
# -------------------------------------------------
def detect_project_module(project_root: Path) -> str:
    """Detect the package under src/ containing __version__."""
    src_dir = project_root / "src"
    if not src_dir.exists():
        print("❌ src/ directory not found")
        sys.exit(1)

    for init_file in src_dir.rglob("__init__.py"):
        content = init_file.read_text(encoding="utf-8")
        if re.search(VERSION_PATTERN, content):
            return ".".join(init_file.parent.relative_to(src_dir).parts)

    print("❌ Could not detect project module containing __version__.")
    sys.exit(1)


def get_version_file(project_root: Path, module_name: str) -> Path:
    """Return the __init__.py file for the detected module."""
    return project_root / "src" / Path(*module_name.split(".")) / "__init__.py"


def get_project_version(project_root: Path) -> str:
    """Import the project package and read __version__."""
    module_name = detect_project_module(project_root)
    src_path = project_root / "src"

    if str(src_path) not in sys.path:
        sys.path.insert(0, str(src_path))

    try:
        module = importlib.import_module(module_name)
    except ImportError as exc:
        print(f"❌ Could not import {module_name}: {exc}")
        sys.exit(1)

    return str(module.__version__)


def load_build_config(project_root: Path) -> configparser.SectionProxy:
    """Load tools/build.ini PyInstaller settings."""
    config_path = project_root / "tools" / "build.ini"
    if not config_path.exists():
        print("❌ tools/build.ini not found")
        sys.exit(1)

    config = configparser.ConfigParser()
    config.read(config_path)

    if "pyinstaller" not in config:
        print("❌ tools/build.ini is missing [pyinstaller]")
        sys.exit(1)

    return config["pyinstaller"]


# -------------------------------------------------
# Version Helpers
# -------------------------------------------------
def parse_version(version: str) -> tuple[int, int, int]:
    """Parse semantic-ish MindIt version X.Y.Z."""
    match = re.fullmatch(r"(\d+)\.(\d+)\.(\d+)", version)
    if not match:
        print(f"❌ Invalid version: {version}")
        print("Expected format: 0.2026.31")
        sys.exit(1)
    major, minor, build = map(int, match.groups())
    return major, minor, build


def read_current_version(init_file: Path) -> tuple[tuple[int, int, int], str]:
    """Read __version__ from package __init__.py."""
    text = init_file.read_text(encoding="utf-8")
    match = re.search(VERSION_PATTERN, text)
    if not match:
        print(f"❌ Could not locate __version__ in {init_file}")
        sys.exit(1)
    major, minor, build = map(int, match.groups())  
    return (major, minor, build), text


def update_version_file(init_file: Path, original_text: str, new_version: str) -> None:
    """Update __version__ in package __init__.py."""
    updated_text = re.sub(
        VERSION_PATTERN,
        f'__version__ = "{new_version}"',
        original_text,
    )
    init_file.write_text(updated_text, encoding="utf-8")
    print(f"\n🔢 Updated version to {new_version}")


def determine_version(project_root: Path, release_args: ReleaseArgs) -> VersionInfo:
    """Determine and write the release version."""
    module_name = detect_project_module(project_root)
    init_file = get_version_file(project_root, module_name)
    releases_root = project_root / "releases"

    (cur_major, cur_minor, cur_build), init_text = read_current_version(init_file)

    if release_args.version:
        major, minor, build = parse_version(release_args.version)
    elif release_args.autobuild:
        major = cur_major
        minor = cur_minor
        build = cur_build + 1
    else:
        major = release_args.major if release_args.major is not None else cur_major
        minor = release_args.minor if release_args.minor is not None else cur_minor
        build = release_args.build if release_args.build is not None else cur_build

    while True:
        version = f"{major}.{minor}.{build}"
        release_folder = releases_root / f"release-v{version}"

        if not release_folder.exists():
            break

        print(f"\n⚠️ Release folder exists: {release_folder.name}")
        if release_args.autobuild:
            build += 1
            continue

        choice = input("Overwrite (o), Increment build (i), Cancel (c)? ").lower()
        if choice == "o":
            break
        if choice == "i":
            build += 1
            continue

        print("Release cancelled.")
        sys.exit(0)

    update_version_file(init_file, init_text, version)
    return VersionInfo(
        version=version,
        release_folder=release_folder,
        major=major,
        minor=minor,
        build=build,
    )


# -------------------------------------------------
# Target OS
# -------------------------------------------------
def detect_target_platform(release_args: ReleaseArgs) -> TargetPlatform:
    """Resolve target OS from host or --os option."""
    current = platform.system().lower()
    is_windows = current == "windows"
    is_linux = current == "linux"

    if release_args.target_os == "win":
        is_windows = True
        is_linux = False
    elif release_args.target_os == "linux":
        is_windows = False
        is_linux = True

    if not is_windows and not is_linux:
        print(f"❌ Unsupported target platform: {current}")
        sys.exit(1)

    target = TargetPlatform(is_windows=is_windows, is_linux=is_linux)
    print(f"\n🖥️ Target OS: {target.name}")
    return target


# -------------------------------------------------
# Build Binary
# -------------------------------------------------
def _config_lines(config: configparser.SectionProxy, key: str) -> list[str]:
    """Return non-empty stripped lines from a build.ini key."""
    if key not in config:
        return []
    return [line.strip() for line in config[key].strip().splitlines() if line.strip()]


def build_binary(
    project_root: Path,
    version: str,
    target: TargetPlatform,
    release_folder: Path | None = None,
) -> BinaryResult:
    """Build PyInstaller binary and optionally copy it to release folder."""
    config = load_build_config(project_root)
    project_name = config.get("project", fallback="application")
    exe_name = f"{project_name}-v{version}.exe" if target.is_windows else f"{project_name}-v{version}"

    cmd = [
        "pyinstaller",
        "--onefile",
        "--clean",
        f"--name={exe_name}",
    ]

    for module in _config_lines(config, "exclude_modules"):
        cmd.append(f"--exclude-module={module}")

    for module in _config_lines(config, "collect_all"):
        cmd.extend(["--collect-all", module])

    for module in _config_lines(config, "hidden_imports"):
        cmd.append(f"--hidden-import={module}")

    hooks_dir = project_root / "tools" / "hooks"
    if hooks_dir.exists():
        cmd.append(f"--additional-hooks-dir={hooks_dir}")

    add_data_sep = ";" if target.is_windows else ":"
    for line in _config_lines(config, "add_data"):
        if "->" not in line:
            print(f"❌ Invalid add_data format: {line}")
            sys.exit(1)
        src, dest = [part.strip() for part in line.split("->", maxsplit=1)]
        cmd.append(f"--add-data={src}{add_data_sep}{dest}")

    icon_path = (
        project_root / "assets" / "icon.ico"
        if target.is_windows
        else project_root / "assets" / "icon.png"
    )

    if icon_path.exists():
        cmd.append(f"--icon={icon_path}")

    entry_point = config.get("entry_point", fallback="")
    if not entry_point:
        print("❌ Missing entry_point in tools/build.ini")
        sys.exit(1)

    cmd.append(entry_point)

    print(f"\n⚙️ Building {exe_name} ...")
    run_command(cmd, "Building executable", cwd=project_root)

    dist_path = project_root / "dist" / exe_name
    if not dist_path.exists():
        print(f"❌ Expected binary not found: {dist_path}")
        sys.exit(1)

    release_copy_path = None

    if release_folder is not None:
        release_folder.mkdir(parents=True, exist_ok=True)
        release_copy_path = release_folder / exe_name
        shutil.copy2(dist_path, release_copy_path)
        print(f"✅ Copied binary to {release_copy_path}")

    print(f"\n🎉 Binary complete: {exe_name}")
    return BinaryResult(
        exe_name=exe_name,
        dist_path=dist_path,
        release_copy_path=release_copy_path,
    )


# -------------------------------------------------
# Release Artifacts
# -------------------------------------------------
def run_tests(project_root: Path, release_args: ReleaseArgs) -> None:
    """Run release test suite unless skipped."""
    if release_args.skip_tests:
        print("\n⚠️ Skipping tests")
        return

    run_command([sys.executable, "-m", "tools.test"], "Running test suite", cwd=project_root)


def run_dashboards(project_root: Path, version_info: VersionInfo, release_args: ReleaseArgs) -> None:
    """Generate project and milestone dashboards unless skipped."""
    if release_args.skip_dashboard:
        print("\n⚠️ Skipping dashboards")
        return

    milestone = f"v{version_info.major}.{version_info.minor}.0"
    release_folder = version_info.release_folder

    run_command(
        [sys.executable, "-m", "tools.dashboard", "--save", f"--outdir={release_folder}"],
        "Running project dashboard",
        cwd=project_root,
    )
    run_command(
        [
            sys.executable,
            "-m",
            "tools.dashboard",
            "--save",
            f"--milestone={milestone}",
            f"--outdir={release_folder}",
        ],
        "Running milestone dashboard",
        cwd=project_root,
    )


def export_requirements(version_info: VersionInfo) -> None:
    """Export pip freeze into release folder."""
    requirements_file = version_info.release_folder / f"requirements_v{version_info.version}.txt"
    print(f"\n🔹 Exporting pip freeze to {requirements_file.name}")

    with requirements_file.open("w", encoding="utf-8") as file_handle:
        subprocess.run([sys.executable, "-m", "pip", "freeze"], stdout=file_handle, check=True)

    print("✅ Requirements exported")


# -------------------------------------------------
# Publish / Tag
# -------------------------------------------------
def prepare_release_pr(project_root: Path, version: str, release_args: ReleaseArgs) -> None:
    """Create release branch, commit release files, push branch, and optionally create PR."""
    ensure_on_main(project_root)

    branch_name = create_release_branch(project_root, version)
    commit_release_changes(project_root, version)
    push_release_branch(project_root, branch_name)

    if release_args.no_pr:
        print("\n⚠️ Skipping PR creation because --no-pr was used.")
    else:
        create_release_pr(project_root, version)

    print("\n✅ Release PR preparation complete.")
    print(f"   Branch: {branch_name}")
    print(f"   Version: v{version}")


def create_github_release(project_root: Path, version: str, binary_result: BinaryResult | None) -> None:
    """Create GitHub release and upload binary if available."""
    tag_name = f"v{version}"

    command = [
        "release",
        "create",
        tag_name,
        "--title",
        f"Release {tag_name}",
        "--notes",
        f"Automated release for {tag_name}",
    ]

    if binary_result is None:
        print("❌ No binary result available; refusing to create release without asset.")
        sys.exit(1)

    asset_path = binary_result.release_copy_path or binary_result.dist_path
    if not asset_path.exists():
        print(f"❌ Release asset not found: {asset_path}")
        sys.exit(1)

    command.append(str(asset_path))

    run_gh(command, "Creating GitHub release", project_root)


def create_tag_and_release(
    project_root: Path,
    version: str,
    target: TargetPlatform,
) -> None:
    """
    Create tag and GitHub release from main.

    This should be run after the release PR has been merged.
    """
    tag_name = f"v{version}"

    ensure_on_main(project_root)
    ensure_worktree_clean(project_root)
    ensure_tag_does_not_exist(project_root, tag_name)

    current_version = get_project_version(project_root)
    binary_result: BinaryResult | None = None
    
    if current_version != version:
        print(f"❌ Current project version is {current_version}, not {version}.")
        print("Make sure the release PR has been merged and main is pulled.")
        sys.exit(1)

    release_folder = project_root / "releases" / f"release-v{version}"
    release_folder.mkdir(parents=True, exist_ok=True)

    config = load_build_config(project_root)
    project_name = config.get("project", fallback="application")
    exe_name = f"{project_name}-v{version}.exe" if target.is_windows else f"{project_name}-v{version}"
    release_binary = release_folder / exe_name
    dist_binary = project_root / "dist" / exe_name

    if release_binary.exists():
        binary_result = BinaryResult(
            exe_name=exe_name,
            dist_path=dist_binary,
            release_copy_path=release_binary,
        )
    else:
        binary_result = build_binary(
            project_root=project_root,
            version=version,
            target=target,
            release_folder=release_folder,
        )

    run_git(["tag", "-a", tag_name, "-m", f"Release {tag_name}"], "Creating tag", project_root)
    run_git(["push", "origin", tag_name], "Pushing tag", project_root)
    create_github_release(project_root, version, binary_result)

    print("\n✅ Tag and GitHub release complete.")
    print(f"   Tag: {tag_name}")


# -------------------------------------------------
# Workflows
# -------------------------------------------------
def run_full_release(project_root: Path, release_args: ReleaseArgs, target: TargetPlatform) -> None:
    """Run full release workflow."""
    if release_args.publish:
        ensure_on_main(project_root)
        ensure_worktree_clean(project_root)

    version_info = determine_version(project_root, release_args)
    version_info.release_folder.mkdir(parents=True, exist_ok=True)

    run_tests(project_root, release_args)
    run_dashboards(project_root, version_info, release_args)
    export_requirements(version_info)

    build_binary(
        project_root=project_root,
        version=version_info.version,
        target=target,
        release_folder=version_info.release_folder,
    )

    if release_args.publish:
        prepare_release_pr(project_root, version_info.version, release_args)

    print("\n✅ Full release workflow complete.")
    print(f"   Version: v{version_info.version}")
    print(f"   Folder: {version_info.release_folder}")


def run_binary_only(project_root: Path, target: TargetPlatform) -> None:
    """Build only binary from current package version."""
    candidate_version = get_project_version(project_root)
    print(f"\n🔹 Binary-only mode: version {candidate_version}")
    build_binary(project_root, candidate_version, target)


def run_tag_only(project_root: Path, release_args: ReleaseArgs, target: TargetPlatform) -> None:
    """Create tag and GitHub release after release PR is merged."""
    version = release_args.version or get_project_version(project_root)
    create_tag_and_release(project_root, version, target)


# -------------------------------------------------
# Main
# -------------------------------------------------
def main() -> None:
    """Release script entry point."""
    release_args = parse_args()
    project_root = Path(__file__).resolve().parent.parent

    print(f"\n📦 Project: {project_root}")
    target = detect_target_platform(release_args)

    if release_args.binary_only:
        run_binary_only(project_root, target)
        return

    if release_args.tag_only:
        run_tag_only(project_root, release_args, target)
        return

    run_full_release(project_root, release_args, target)


if __name__ == "__main__":
    main()
