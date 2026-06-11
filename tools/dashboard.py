#!/usr/bin/env python3
"""
Script:     tools\dashboard.py
Version:    2.2.2
Author:     Mike & ChatGPT

Purpose:
    Display GitHub issues grouped by milestone → epic → issues, or by epic when --milestone is not provided.
    Includes sorting and completion summaries.

Features:
    ✔ Reads GitHub token and repo from .env or config/github.config
    ✔ Handles pagination for issues and milestones
    ✔ Groups issues by milestone or epic
    ✔ Sorts milestones or epics by name or due date
    ✔ Shows issue and SP completion percentages
    
Usage:
    python -m tools.dashboard --save
"""

import os
import argparse
import requests
from pathlib import Path
from configparser import ConfigParser
from dotenv import load_dotenv
from datetime import datetime

BASE_URL = "https://api.github.com"

def get_headers(token):
    return {
        "Accept": "application/vnd.github+json",
        "Authorization": f"Bearer {token}",
    }

def extract_story_points(labels):
    for label in labels:
        if label.startswith("SP:"):
            return label
    return ""

def extract_epic(labels):
    for label in labels:
        if label.startswith("Epic:"):
            return label
    return "No Epic"

def fetch_all_issues(repo, headers):
    issues = []
    url = f"{BASE_URL}/repos/{repo}/issues"
    params = {"state": "all", "per_page": 100}
    while url:
        resp = requests.get(url, headers=headers, params=params)
        resp.raise_for_status()
        issues.extend([i for i in resp.json() if "pull_request" not in i])
        url = resp.links.get("next", {}).get("url")
        params = None
    return issues

def fetch_all_milestones(repo, headers):
    milestones = []
    url = f"{BASE_URL}/repos/{repo}/milestones"
    params = {"state": "all", "per_page": 100}
    while url:
        resp = requests.get(url, headers=headers, params=params)
        resp.raise_for_status()
        milestones.extend(resp.json())
        url = resp.links.get("next", {}).get("url")
        params = None
    return milestones

def group_issues(repo, headers, filters, status):
    issues = fetch_all_issues(repo, headers)
    grouped = {}

    for issue in issues:
        if status != "all" and issue["state"].lower() != status.lower():
            continue

        milestone = issue["milestone"]["title"] if issue.get("milestone") else "No Milestone"
        labels = [lbl["name"] for lbl in issue.get("labels", [])]
        points = extract_story_points(labels)
        epic = extract_epic(labels)
        assigned = issue["assignee"]["login"] if issue.get("assignee") else "Not Assigned"

        if filters.get("milestone") and filters["milestone"].lower() not in milestone.lower():
            continue
        if filters.get("assigned") and filters["assigned"].lower() not in assigned.lower():
            continue
        if filters.get("epic") and filters["epic"].lower() not in epic.lower():
            continue
        if filters.get("type") and filters["type"].lower() not in issue["title"].lower():
            continue
        if filters.get("label") and filters["label"].lower() not in [l.lower() for l in labels]:
            continue
        if filters.get("issue") and filters["issue"].lower() not in issue["title"].lower():
            continue

        entry = {
            "number": issue["number"],
            "title": issue["title"],
            "points": points,
            "state": issue["state"],
        }

        grouped \
            .setdefault(milestone, {}) \
            .setdefault(epic, {}) \
            .setdefault(assigned, []) \
            .append(entry)

    return grouped

def list_milestones(repo, headers, sort_by="due"):
    milestones = fetch_all_milestones(repo, headers)
    result = []
    for m in milestones:
        total = m["open_issues"] + m["closed_issues"]
        due = m.get("due_on", "")[:10] if m.get("due_on") else ""
        result.append((m["title"], m["state"], m["open_issues"], m["closed_issues"], total, due))

    if sort_by == "title":
        result.sort(key=lambda x: x[0])
    elif sort_by == "due":
        result.sort(key=lambda x: x[5] or "9999-99-99")

    return result

def load_token_and_repo():
    load_dotenv(override=True)

    token = os.getenv("GITHUB_TOKEN")
    owner = os.getenv("GITHUB_OWNER")
    repo = os.getenv("GITHUB_REPO")

    if token and owner and repo:
        return token, f"{owner}/{repo}"
    elif token and repo:
        return token, repo

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


def get_file_extension(output_type):
    return {
        "txt": ".txt",
        "md": ".md",
        "csv": ".csv",
    }.get(output_type, "")

def save_to_file(content, output_folder, milestone, output_type):
    date_stamp = datetime.now().strftime('%y%m%d')
    safe_milestone = milestone.replace('/', '-')
    ext = get_file_extension(output_type)
    filename = f"{output_folder}/dashboard-{safe_milestone}-{date_stamp}{ext}"
    Path(output_folder).mkdir(parents=True, exist_ok=True)
    with open(filename, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"📄 Saved to: {filename}")
    return filename

def main():
    parser = argparse.ArgumentParser(description="GitHub Dashboard CLI")
    parser.add_argument("--repo", help="Repository (user/repo)")
    parser.add_argument("--token", help="GitHub personal access token")
    parser.add_argument("--output", choices=["table", "txt", "csv"], default="txt")
    parser.add_argument("--sort", choices=["due", "title", "name"], default="due")
    parser.add_argument("--status", choices=["open", "closed", "all"], default="all")
    parser.add_argument("--save", action="store_true")
    parser.add_argument("--milestone", help="Filter by milestone substring")
    parser.add_argument("--assigned", help="Filter by assigned username")
    parser.add_argument("--epic", help="Filter by epic substring")
    parser.add_argument("--type", help="Filter by title substring")
    parser.add_argument("--label", help="Filter by label name")
    parser.add_argument("--issue", help="Filter by issue substring")
    parser.add_argument("--outdir", default="Docs/dashboards")

    args = parser.parse_args()

    filters = {
        "milestone": args.milestone,
        "assigned": args.assigned,
        "epic": args.epic,
        "type": args.type,
        "label": args.label,
        "issue": args.issue,
    }

    loaded_token, loaded_repo = load_token_and_repo()
    token = args.token or loaded_token
    repo = args.repo or loaded_repo

    if not token or not repo:
        print("❌ Error: GitHub token and repo must be provided.")
        return

    headers = get_headers(token)
    output = f"\n📘 Repository: {repo}\n\n"
    output += f"🔍 Status Filter: {args.status.capitalize()}\n\n"

    grouped_issues = group_issues(repo, headers, filters, args.status)

    if args.milestone:
        milestones = list_milestones(repo, headers, sort_by=args.sort)
        output += "🎯 Milestones\n"
        for title, state, open_, closed, total, due in milestones:
            if filters["milestone"] and filters["milestone"].lower() not in title.lower():
                continue
            pct = int(100 * closed / total) if total > 0 else 0
            output += f"{title} [{state}]  ({closed} / {total}  {pct}%) — Due: {due}\n"

            milestone_data = grouped_issues.get(title, {})
            milestone_total_sp = milestone_closed_sp = 0

            for epic, assigned_groups in milestone_data.items():
                epic_total_sp = epic_closed_sp = 0
                output += f"  {epic}\n"
                for assigned, issues in assigned_groups.items():
                    output += f"    Assigned: {assigned}\n"
                    for issue in sorted(issues, key=lambda x: x["number"]):
                        status_box = "[X]" if issue["state"] == "closed" else "[ ]"
                        output += f"      {status_box} #{issue['number']:3}  {issue['title']:<40} ({issue['points']})\n"

                        if issue["points"].startswith("SP:"):
                            try:
                                sp = int(issue["points"].split(":")[1])
                                epic_total_sp += sp
                                milestone_total_sp += sp
                                if issue["state"] == "closed":
                                    epic_closed_sp += sp
                                    milestone_closed_sp += sp
                            except ValueError:
                                pass

                if epic_total_sp > 0:
                    pct_epic_sp = int(100 * epic_closed_sp / epic_total_sp)
                    output += f"      SP: ({epic_closed_sp} / {epic_total_sp} {pct_epic_sp}%)\n"

            if milestone_total_sp > 0:
                pct_sp = int(100 * milestone_closed_sp / milestone_total_sp)
                output += f"    Total SP: ({milestone_closed_sp} / {milestone_total_sp} {pct_sp}%)\n\n"

    else:
        output += "📌 Epic Overview (All Issues)\n"
        epic_groups = {}
        total_issues = total_closed = 0
        total_sp = total_closed_sp = 0

        for milestone_data in grouped_issues.values():
            for epic, assigned_groups in milestone_data.items():
                for assigned, issues in assigned_groups.items():
                    epic_groups.setdefault(epic, []).extend(issues)

        sorted_epics = sorted(epic_groups.keys()) if args.sort == "name" else epic_groups.keys()

        for epic in sorted_epics:
            issues = epic_groups[epic]
            epic_total = epic_closed = 0
            epic_sp_total = epic_sp_closed = 0
            output += f"  {epic}\n"
            for issue in sorted(issues, key=lambda x: x["number"]):
                status_box = "[X]" if issue["state"] == "closed" else "[ ]"
                output += f"    {status_box} #{issue['number']:3}  {issue['title']:<40} ({issue['points']})\n"
                epic_total += 1
                total_issues += 1
                if issue["state"] == "closed":
                    epic_closed += 1
                    total_closed += 1
                if issue["points"].startswith("SP:"):
                    try:
                        sp = int(issue["points"].split(":")[1])
                        epic_sp_total += sp
                        total_sp += sp
                        if issue["state"] == "closed":
                            epic_sp_closed += sp
                            total_closed_sp += sp
                    except ValueError:
                        pass

            output += f"    ISSUES: ({epic_closed} / {epic_total}  {int(epic_closed / epic_total * 100)}%)\n"
            if epic_sp_total > 0:
                output += f"    SP:     ({epic_sp_closed} / {epic_sp_total}  {int(epic_sp_closed / epic_sp_total * 100)}%)\n"
            output += "\n"

        output += f"🔢 TOTAL ISSUES: ({total_closed} / {total_issues}  {int(total_closed / total_issues * 100)}%)\n"
        if total_sp > 0:
            output += f"📈 TOTAL SP:     ({total_closed_sp} / {total_sp}  {int(total_closed_sp / total_sp * 100)}%)\n"

    print(output)

    if args.save:
        name = args.milestone or "all"
        save_to_file(output, args.outdir, name, args.output)

if __name__ == "__main__":
    main()
