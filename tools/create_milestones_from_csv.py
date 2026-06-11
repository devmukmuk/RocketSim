#!/usr/bin/env python3
"""
Script:     create_milestones_from_csv.py
Version:    2.3.0
Author:     Mike & ChatGPT

Purpose:
    Create GitHub milestones from a CSV file with columns:
    Date,Year,ISOWeek,Milestone,Major,Minor,Patch
    
✅ Features:
    --csv <path>: load milestones from a CSV file
    --weeks N: create milestones due in the next N weeks (default: 4)
    --all: create all milestones in CSV
    --reset: delete all existing milestones before creating new ones
    --dry-run: simulate actions without calling the GitHub API
    ✅ Skips existing milestones (pre-checked from GitHub)

Usage:
    python -m tools.create_milestones_from_csv --csv ./tools/milestones.csv --weeks 4
"""

import os
import csv
import argparse
import requests
from datetime import datetime, timedelta
from dotenv import load_dotenv
from pathlib import Path

# 🔧 Load environment from project root
load_dotenv(override=True)

# 🔐 GitHub config
token = os.getenv("GITHUB_TOKEN")
owner = os.getenv("GITHUB_OWNER")
repo = os.getenv("GITHUB_REPO")

headers = {
    "Accept": "application/vnd.github+json",
    "Authorization": f"token {token}"
}

def parse_date(date_str):
    for fmt in ("%m/%d/%Y", "%Y-%m-%d"):
        try:
            return datetime.strptime(date_str, fmt).date()
        except ValueError:
            continue
    raise ValueError(f"Unrecognized date format: {date_str}")

def create_milestone(title, due_date, dry_run=False):
    url = f"https://api.github.com/repos/{owner}/{repo}/milestones"
    payload = {
        "title": title,
        "state": "open",
        "due_on": due_date.strftime("%Y-%m-%dT23:59:59Z"),
        "description": f"Sprint ending {due_date.strftime('%Y-%m-%d')}"
    }
    if dry_run:
        print(f"🔍 Would create: {title} (due {due_date})")
        return

    response = requests.post(url, headers=headers, json=payload)
    if response.status_code == 201:
        print(f"✅ Created milestone: {title}")
    elif response.status_code == 422 and 'already_exists' in response.text:
        print(f"⚠️  Milestone already exists: {title}")
    else:
        print(f"❌ Failed to create milestone {title}: {response.status_code} - {response.text}")

def delete_all_milestones(dry_run=False):
    url = f"https://api.github.com/repos/{owner}/{repo}/milestones?state=open"
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        print(f"❌ Failed to fetch milestones: {response.status_code}")
        return

    milestones = response.json()
    for ms in milestones:
        del_url = f"https://api.github.com/repos/{owner}/{repo}/milestones/{ms['number']}"
        if dry_run:
            print(f"🗑️  Would delete: {ms['title']}")
        else:
            del_response = requests.delete(del_url, headers=headers)
            if del_response.status_code == 204:
                print(f"🗑️  Deleted: {ms['title']}")
            else:
                print(f"❌ Failed to delete {ms['title']}: {del_response.status_code}")

def get_existing_milestone_titles():
    url = f"https://api.github.com/repos/{owner}/{repo}/milestones?state=all&per_page=100"
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        print(f"❌ Failed to fetch existing milestones: {response.status_code}")
        return set()
    return {m["title"] for m in response.json()}

def main():
    parser = argparse.ArgumentParser(description="Create milestones from CSV")
    parser.add_argument("--csv", type=str, help="Path to milestones.csv (required unless using --reset only)")
    parser.add_argument("--weeks", type=int, default=4, help="Create milestones due in the next N weeks (default: 4)")
    parser.add_argument("--all", action="store_true", help="Create all milestones in the CSV file")
    parser.add_argument("--reset", action="store_true", help="Delete all existing milestones before creating new ones")
    parser.add_argument("--dry-run", action="store_true", help="Preview actions without modifying GitHub")
    args = parser.parse_args()

    if not args.reset and not args.csv:
        parser.error("argument --csv is required unless --reset is specified alone")

    if not token or not owner or not repo:
        print("❌ GITHUB_TOKEN, GITHUB_OWNER, and GITHUB_REPO must be set in .env")
        return

    today = datetime.today().date()
    cutoff = today + timedelta(weeks=args.weeks)

    print(f"📁 Reading: {args.csv}")
    print(f"🔐 Target repo: {owner}/{repo}")
    if args.all:
        print(f"📦 Mode: --all (create all milestones)")
    else:
        print(f"📅 Mode: --weeks {args.weeks} (cutoff: {cutoff})")

    if args.reset:
        print("♻️  --reset enabled: deleting all milestones...")
        delete_all_milestones(dry_run=args.dry_run)
        if not args.csv:
            return  # Exit early if no CSV provided


    existing_titles = get_existing_milestone_titles()

    with open(args.csv, newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            try:
                title = row["Milestone"].strip()
                due_date = parse_date(row["Date"].strip())

                if title in existing_titles:
                    print(f"⏭️  Skipping (already exists): {title}")
                    continue

                if args.all or (today <= due_date <= cutoff):
                    create_milestone(title, due_date, dry_run=args.dry_run)
            except Exception as e:
                print(f"❌ Error processing row: {row} — {e}")

if __name__ == "__main__":
    main()
