#!/usr/bin/env python3
"""Validate the engagement snapshot and generate a compact review report."""

from __future__ import annotations

import argparse
import csv
import json
from datetime import datetime, timezone
from pathlib import Path

from build_site import ROOT


BASELINE = ROOT / "analytics" / "engagement-baseline.json"
ARTIFACT = ROOT / "analytics" / "engagement-dashboard.artifact.json"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", type=Path, default=ROOT / "metrics-report")
    args = parser.parse_args()
    baseline = json.loads(BASELINE.read_text(encoding="utf-8"))
    artifact = json.loads(ARTIFACT.read_text(encoding="utf-8"))
    snapshot = artifact["snapshot"]["datasets"]
    current = baseline["scopes"]["currentMonth"]
    audience = baseline["scopes"]["audienceLifetime"]
    account = snapshot["account_summary"][0]
    expected_account = {
        "presentations": current["presentations"],
        "views": current["views"],
        "reads": current["reads"],
        "followers": audience["followers"],
        "email_subscribers": audience["emailSubscribers"],
    }
    for key, value in expected_account.items():
        if account[key] != value:
            raise SystemExit(f"dashboard mismatch for {key}: {account[key]} != {value}")

    baseline_stories = {row["slug"]: row for row in baseline["scopes"]["storyLifetime"]}
    artifact_stories = {row["slug"]: row for row in snapshot["story_lifetime"]}
    if set(baseline_stories) != set(artifact_stories):
        raise SystemExit("dashboard story set does not match engagement baseline")
    for slug, row in baseline_stories.items():
        dashboard_row = artifact_stories[slug]
        expected = (row["presentations"], row["views"], row["reads"], row["readRatio"])
        observed = (dashboard_row["presentations"], dashboard_row["views"], dashboard_row["reads"], dashboard_row["read_ratio"])
        if expected != observed:
            raise SystemExit(f"dashboard mismatch for {slug}: {observed} != {expected}")

    captured = datetime.fromisoformat(baseline["capturedAt"].replace("Z", "+00:00"))
    age_days = (datetime.now(timezone.utc) - captured).days
    rows = sorted(artifact_stories.values(), key=lambda item: (item["read_ratio"], item["views"]), reverse=True)
    report = [
        "# Medium engagement review",
        "",
        f"Snapshot captured: {baseline['capturedAt']} ({age_days} days old)",
        "",
        "## Account summary",
        "",
        f"- {current['presentations']} presentations, {current['views']} views, and {current['reads']} reads in {baseline['scopes']['currentMonth']['label']}.",
        f"- {audience['followers']} lifetime followers and {audience['emailSubscribers']} lifetime email subscribers.",
        "",
        "## Story retention",
        "",
        "| Story | Presentations | Views | Reads | Read ratio |",
        "|---|---:|---:|---:|---:|",
    ]
    report.extend(
        f"| {row['story']} | {row['presentations']} | {row['views']} | {row['reads']} | {row['read_ratio']:.0%} |"
        for row in rows
    )
    report.extend([
        "",
        "## Review notes",
        "",
        "- Current-month account totals and lifetime story totals have different scopes.",
        "- Samples are too small for causal claims; use the ranking to prioritize tests.",
        "- Update the baseline through a signed-in, read-only Medium stats review before using this report for a new period.",
        "- GitHub Actions does not sign in to Medium, scrape private stats, or store account cookies.",
    ])
    args.output_dir.mkdir(parents=True, exist_ok=True)
    (args.output_dir / "engagement-summary.md").write_text("\n".join(report) + "\n", encoding="utf-8")
    with (args.output_dir / "story-metrics.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=["story", "slug", "presentations", "views", "reads", "read_ratio"])
        writer.writeheader()
        writer.writerows(rows)
    print(f"validated dashboard snapshot and wrote metrics report ({age_days} days old)")


if __name__ == "__main__":
    main()
