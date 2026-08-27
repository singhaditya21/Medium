#!/usr/bin/env python3
"""Render a safe GitHub issue comment for one Medium execution receipt."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


ACTION_LABELS = {
    "draft_imported": "Private Medium draft saved",
    "draft_revised": "Scheduled Medium draft revised",
    "story_scheduled": "Medium story scheduled",
    "story_published": "Medium story published",
    "stats_captured": "Medium aggregate stats captured",
    "response_posted": "Medium response posted",
}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--receipt", type=Path, required=True)
    args = parser.parse_args()
    receipt = json.loads(args.receipt.read_text(encoding="utf-8"))
    result = receipt["result"]
    lines = [
        f"<!-- medium-execution:{receipt['operationId']} -->",
        "## Signed-in Medium execution verified",
        "",
        f"- Action: {ACTION_LABELS[receipt['action']]}",
        f"- Operation: `{receipt['operationId']}`",
        f"- Result: `{result['status']}`",
        f"- Verified: {result['verifiedAt']}",
        f"- Verification: {result['verification']}",
        "- Medium action performed by GitHub Actions: **no**",
    ]
    if result.get("mediumUrl"):
        story_label = "Scheduled story" if receipt["action"] == "story_scheduled" else "Published story"
        lines.append(f"- {story_label}: {result['mediumUrl']}")
    if result.get("settings", {}).get("scheduleAt"):
        lines.append(f"- Scheduled for: {result['settings']['scheduleAt']}")
    if result.get("responseUrl"):
        lines.append(f"- Published response: {result['responseUrl']}")
    if result.get("snapshotPath"):
        lines.append(f"- Snapshot: `{result['snapshotPath']}`")
    lines.extend([
        "",
        "GitHub Actions has resumed repository validation and reporting from this credential-free receipt.",
    ])
    print("\n".join(lines))


if __name__ == "__main__":
    main()
