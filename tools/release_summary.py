#!/usr/bin/env python3
"""
Script:     github_diff_summary.py
Version:    1.2.0
Author:     Mike & ChatGPT

Purpose:
    Summarize commits and changed files between two refs (tags/branches/SHAs).
    Modes:
      - github: use GitHub Compare API (both refs must exist on GitHub)
      - local : use local git repo (no need to push tags/commits)

Reads token/repo from `.env` or `config/github.config` for GitHub mode.
"""

import os
import argparse
import subprocess
import requests
from configparser import ConfigParser
from pathlib import Path
from dotenv import load_dotenv

BASE_URL = "https://api.github.com"

def get_headers(token):
    return {
        "Accept": "application/vnd.github+json",
        "Authorization": f"Bearer {token}",
    }


def load_token_and_repo():
    # Load .env from current working directory (project root)
    load_dotenv(override=True)

    token = os.getenv("GITHUB_TOKEN")
    owner = os.getenv("GITHUB_OWNER")
    repo = os.getenv("GITHUB_REPO")

    if token and owner and repo:
        return token, f"{owner}/{repo}"
    elif token and repo:
        return token, repo

    # Fallback to config file
    config_path = Path("config/github.config")
    if config_path.exists():
        config = ConfigParser()
        config.read(config_path)

        if "DEFAULT" in config:
            token = config["DEFAULT"].get("token")
            repo = config["DEFAULT"].get("repo")

            if token and repo:
                return token, repo

    return None, None

def get_compare_data(repo, headers, from_ref, to_ref):
    url = f"{BASE_URL}/repos/{repo}/compare/{from_ref}...{to_ref}"
    resp = requests.get(url, headers=headers)
    resp.raise_for_status()
    return resp.json()

# ---------- LOCAL MODE HELPERS ----------
def sh(*cmd):
    return subprocess.check_output(cmd, text=True, stderr=subprocess.STDOUT).strip()

def local_compare(from_ref, to_ref):
    """
    Returns a dict shaped similar to GitHub's compare for our needs.
    """
    # validate refs exist locally (raises if not)
    sh("git", "rev-parse", "--verify", from_ref)
    sh("git", "rev-parse", "--verify", to_ref)

    base_sha = sh("git", "rev-parse", from_ref)
    head_sha = sh("git", "rev-parse", to_ref)

    # oldest -> newest commit list (exclude merge body text)
    log = sh("git", "log", "--pretty=%H%x09%an%x09%s", f"{from_ref}..{to_ref}")
    commits = []
    if log:
        for line in log.splitlines():
            full_sha, author, subject = line.split("\t", 2)
            commits.append({
                "sha": full_sha,
                "commit": {"author": {"name": author}, "message": subject}
            })

    # name-status file list (A/M/D/R..)
    diff = sh("git", "diff", "--name-status", f"{from_ref}..{to_ref}")
    files = []
    if diff:
        for line in diff.splitlines():
            parts = line.split("\t")
            status = parts[0]
            # handle renames like "R100\told\tnew"
            filename = parts[-1]
            files.append({"status": status.lower(), "filename": filename})

    return {
        "base_commit": {"sha": base_sha},
        "head_commit": {"sha": head_sha},
        "total_commits": len(commits),
        "commits": commits,
        "files": files,
    }

# ---------- OUTPUT ----------
def print_summary(compare):
    base_sha = compare.get("base_commit", {}).get("sha", "")[:7]
    head_sha = compare.get("head_commit", {}).get("sha", "")[:7]
    print(f"\n🔍 Comparing: {base_sha} ➜ {head_sha}")
    print(f"📦 Commits: {compare.get('total_commits', '?')}, Files Changed: {len(compare.get('files', []))}")

    print("\n--- Commits ---")
    for commit in compare.get("commits", []):
        sha = commit["sha"][:7]
        msg = commit["commit"]["message"].split("\n")[0]
        author = commit["commit"]["author"]["name"]
        print(f"{sha}  {msg}  ({author})")

    print("\n--- Files Changed ---")
    for file in compare.get("files", []):
        status = file["status"].upper()
        filename = file["filename"]
        print(f"{status:8}  {filename}")

def format_markdown(compare, from_ref, to_ref):
    lines = []
    base_sha = compare.get("base_commit", {}).get("sha", "")[:7]
    head_sha = compare.get("head_commit", {}).get("sha", "")[:7]
    lines.append(f"# 🧾 Release Summary: `{from_ref}` → `{to_ref}`\n")
    lines.append(f"- **Base Commit:** `{base_sha}`")
    lines.append(f"- **Head Commit:** `{head_sha or '(n/a)'}`")
    lines.append(f"- **Total Commits:** {compare.get('total_commits', '?')}")
    lines.append(f"- **Files Changed:** {len(compare.get('files', []))}\n")

    commits = compare.get("commits", [])
    if not commits:
        lines.append("⚠️ No commits found between the specified refs.\n")
        return "\n".join(lines)

    lines.append("## 🚀 Commits")
    for c in commits:
        sha = c["sha"][:7]
        msg = c["commit"]["message"].split("\n")[0]
        author = c["commit"]["author"]["name"]
        lines.append(f"- `{sha}` {msg} _(by {author})_")
    lines.append("")

    lines.append("## 🗂️ Files Changed")
    for f in compare.get("files", []):
        status = f["status"].capitalize()
        lines.append(f"- **{status}:** `{f['filename']}`")
    return "\n".join(lines)

def save_to_file(content, output_folder, from_ref, to_ref):
    safe_to = to_ref.replace("/", "-")
    filename = Path(output_folder) / f"release-{safe_to}.md"
    filename.parent.mkdir(parents=True, exist_ok=True)
    filename.write_text(content, encoding="utf-8")
    print(f"📄 Markdown saved to: {filename}")

def main():
    p = argparse.ArgumentParser(description="Diff Summary (local or GitHub)")
    p.add_argument("--from", dest="from_ref", required=True, help="Start tag/branch/SHA")
    p.add_argument("--to", dest="to_ref", default="main", help="End tag/branch/SHA (default: main)")
    p.add_argument("--output", choices=["console", "markdown"], default="console")
    p.add_argument("--outdir", default="Docs/releases")
    p.add_argument("--mode", choices=["github", "local"], default="github", help="Compare mode")
    args = p.parse_args()

    if args.mode == "local":
        compare = local_compare(args.from_ref, args.to_ref)
    else:
        token, repo = load_token_and_repo()
        if not token or not repo:
            print("❌ Error: GitHub token and repo not configured.")
            return
        headers = get_headers(token)
        compare = get_compare_data(repo, headers, args.from_ref, args.to_ref)

    if args.output == "console":
        print_summary(compare)
    else:
        md = format_markdown(compare, args.from_ref, args.to_ref)
        print(md)
        save_to_file(md, args.outdir, args.from_ref, args.to_ref)

if __name__ == "__main__":
    main()
