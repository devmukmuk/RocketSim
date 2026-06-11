#!/usr/bin/env python3
"""
Script:     create_labels_from_csv.py
Version:    1.0.0
Author:     Mike & ChatGPT

Purpose:
    Create GitHub issue labels from a points.csv file using the GitHub API.
    Each row in the CSV should contain: Label,Points,Description

Usage:
    python -m tools.create_labels_from_csv [--csv ./tools/points.csv] [--dry-run]
"""

import os
import csv
import argparse
import requests
from pathlib import Path
from dotenv import load_dotenv

# 🔧 Load environment from project root
load_dotenv(override=True)
token = os.getenv("GITHUB_TOKEN")
owner = os.getenv("GITHUB_OWNER")
repo = os.getenv("GITHUB_REPO")

headers = {
    "Accept": "application/vnd.github+json",
    "Authorization": f"token {token}"
}

def create_label(label, description, color, dry_run=False):
    url = f"https://api.github.com/repos/{owner}/{repo}/labels"
    payload = {
        "name": label,
        "description": description,
        "color": color.lstrip("#")
    }

    if dry_run:
        print(f"🔍 Would create: {label} — {description} (color #{color})")
        return

    response = requests.post(url, headers=headers, json=payload)
    if response.status_code == 201:
        print(f"✅ Created label: {label}")
    elif response.status_code == 422 and "already_exists" in response.text:
        print(f"⚠️  Label already exists: {label}")
    else:
        print(f"❌ Failed to create {label}: {response.status_code} - {response.text}")

def load_labels_from_csv(csv_path, dry_run=False):
    if not Path(csv_path).exists():
        print(f"❌ CSV file not found: {csv_path}")
        return

    color_map = {
        "1": "c2e0c6", "2": "a2eeef", "3": "d4c5f9",
        "5": "fef2c0", "8": "f9d0c4", "13": "f7c6c7",
        "21": "e99695", "∞": "ededed"
    }

    with open(csv_path, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            label = row["Label"]
            points = row["Points"]
            description = row["Description"]
            color = color_map.get(points, "cccccc")
            create_label(label, description, color, dry_run)

def main():
    parser = argparse.ArgumentParser(description="Create GitHub labels from a CSV file")
    parser.add_argument("--csv", default="scripts/points.csv", help="Path to CSV file")
    parser.add_argument("--dry-run", action="store_true", help="Only show what would be created")
    args = parser.parse_args()

    if not token or not owner or not repo:
        print("❌ Error: GITHUB_TOKEN, GITHUB_OWNER, and GITHUB_REPO must be set in .env")
        return

    print(f"🔐 Using GitHub repo: {owner}/{repo}")
    load_labels_from_csv(args.csv, args.dry_run)

if __name__ == "__main__":
    main()
