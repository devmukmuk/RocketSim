#!/usr/bin/env python3
"""
Script:     create_epic_labels_from_csv.py
Version:    1.0.0
Author:     Mike & ChatGPT

Purpose:
    Read epics from a CSV file and create GitHub labels for each Epic.
    Useful for tagging issues with their corresponding Epic.

Usage:
    python -m tools.create_epic_labels_from_csv --file ./tools/epics.csv
"""

import os
import csv
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

# Color generator for labels (unique but consistent)
def generate_color(index):
    # Generate a hex color code based on index
    colors = [
        "0366d6", "28a745", "d73a4a", "f9d0c4", "f66a0a",
        "fbca04", "d4c5f9", "006b75", "cfd3d7", "e4e669"
    ]
    return colors[index % len(colors)]

def get_existing_labels(repo_full):
    url = f"https://api.github.com/repos/{repo_full}/labels"
    response = requests.get(url, headers=headers)
    if response.ok:
        return {label["name"] for label in response.json()}
    else:
        print(f"[!] Failed to retrieve labels: {response.status_code}")
        return set()

def create_label(repo_full, name, description, color):
    url = f"https://api.github.com/repos/{repo_full}/labels"
    data = {
        "name": name,
        "color": color,
        "description": description[:100]  # GitHub description limit
    }
    response = requests.post(url, headers=headers, json=data)
    if response.ok:
        print(f"[+] Created label: {name}")
    else:
        print(f"[!] Failed to create label {name}: {response.status_code} {response.text}")

def main():
    parser = argparse.ArgumentParser(description="Create GitHub labels for Epics from CSV")
    parser.add_argument("--file", default="tools/epics.csv", help="CSV file with Epics")
    parser.add_argument("--dry-run", action="store_true", help="Preview label creation without GitHub changes")
    args = parser.parse_args()

    repo_full = f"{owner}/{repo}"
    existing_labels = get_existing_labels(repo_full)

    with open(args.file, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for idx, row in enumerate(reader):
            epic_name = row["Epic"].strip()
            description = row.get("Description", "").strip()
            label_name = f"Epic: {epic_name}"
            color = generate_color(idx)

            if label_name in existing_labels:
                print(f"[=] Skipped (exists): {label_name}")
                continue

            if args.dry_run:
                print(f"[~] Would create label: {label_name} (Color: {color}) Desc: {description}")
            else:
                create_label(repo_full, label_name, description, color)

if __name__ == "__main__":
    main()
