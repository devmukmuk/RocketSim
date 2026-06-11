#!/usr/bin/env python3
"""
Script:     create_issues_from_csv.py
Version:    1.3.0
Author:     Mike & ChatGPT

Purpose:
    Read issues from a CSV file and create them on GitHub.
    Skips duplicate titles. Supports dry-run preview.
    Expects 'Labels' column to be a GitHub-style JSON array (e.g., ["cli", "SP:3"])

Usage:
    python -m tools.create_issues_from_csv --file ./tools/issues_v002.csv
"""

import os
import csv
import json
import argparse
import requests
from dotenv import load_dotenv
from pathlib import Path

# 🔧 Load environment from project root
load_dotenv(override=True)
token = os.getenv("GITHUB_TOKEN")
owner = os.getenv("GITHUB_OWNER")
repo = os.getenv("GITHUB_REPO")

headers = {
    "Accept": "application/vnd.github+json",
    "Authorization": f"token {token}"
}

def safe_parse_labels(label_str):
    try:
        return json.loads(label_str)
    except json.JSONDecodeError:
        try:
            fixed = label_str.replace("'", '"')
            return json.loads(fixed)
        except Exception as e:
            raise ValueError(f"Unable to parse label string: {label_str}") from e

def get_existing_issue_titles(repo_full):
    url = f"https://api.github.com/repos/{repo_full}/issues"
    params = {"state": "all", "per_page": 100}
    response = requests.get(url, headers=headers, params=params)
    if not response.ok:
        print(f"[!] Failed to retrieve existing issues: {response.status_code}")
        return set()
    return set(issue["title"] for issue in response.json() if "pull_request" not in issue)

def get_milestone_id(repo_full, title):
    url = f"https://api.github.com/repos/{repo_full}/milestones"
    response = requests.get(url, headers=headers)
    if response.ok:
        for ms in response.json():
            if ms["title"] == title:
                return ms["number"]
    print(f"[!] Milestone not found: {title}")
    return None

def create_issue(repo_full, title, body, label_list, milestone_title):
    milestone_id = get_milestone_id(repo_full, milestone_title) if milestone_title else None
    data = {
        "title": title,
        "body": body,
        "labels": label_list,
        "milestone": milestone_id
    }
    url = f"https://api.github.com/repos/{repo_full}/issues"
    response = requests.post(url, headers=headers, json=data)
    if response.ok:
        print(f"[+] Created: {title}")
    else:
        print(f"[!] Failed to create: {title} — {response.status_code}, {response.text}")

def main():
    parser = argparse.ArgumentParser(description="Create GitHub issues from CSV")
    parser.add_argument("--file", default="tools/issues.csv", help="CSV file with issues")
    parser.add_argument("--dry-run", action="store_true", help="Simulate issue creation without writing to GitHub")
    args = parser.parse_args()

    repo_full = f"{owner}/{repo}"
    existing_titles = get_existing_issue_titles(repo_full)

    with open(args.file, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            title = row["Title"]
            body = row.get("Body", "")
            raw_labels = row.get("Labels", "[]")
            milestone = row.get("Milestone", "")

            try:
                label_list = safe_parse_labels(raw_labels)
                if not isinstance(label_list, list):
                    raise ValueError("Labels must be a list")
            except Exception as e:
                print(f"[!] Invalid label format for '{title}': {e}")
                continue

            if title in existing_titles:
                print(f"[=] Skipped (already exists): {title}")
                continue

            if args.dry_run:
                print(f"[~] Would create: {title} [Labels: {label_list}] → {milestone}")
            else:
                create_issue(repo_full, title, body, label_list, milestone)

if __name__ == "__main__":
    main()
