#!/usr/bin/env python3
"""Generate the recurring Medium + LinkedIn operating packet."""

from __future__ import annotations

import argparse
import csv
import json
from collections import Counter
from datetime import datetime, timedelta, timezone
from pathlib import Path
from zoneinfo import ZoneInfo

from build_site import ROOT


QUEUE_PATH = ROOT / "engagement" / "queue.json"
STRATEGY_PATH = ROOT / "engagement" / "strategy.json"
IST = ZoneInfo("Asia/Kolkata")


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def parse_datetime(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def display_time(value: datetime) -> str:
    return value.astimezone(IST).strftime("%a, %d %b %Y · %I:%M %p IST")


def escape_cell(value: object) -> str:
    return str(value).replace("|", "\\|").replace("\n", " ")


def platform_label(value: str) -> str:
    return "LinkedIn" if value == "linkedin" else "Medium"


def schedule_rows(baseline: dict, windows: list[int]) -> tuple[list[dict], list[dict]]:
    schedule: list[dict] = []
    checkpoints: list[dict] = []
    for platform in ("medium", "linkedin"):
        for index, item in enumerate(baseline[platform]["verifiedSchedule"], start=1):
            label = item.get("story") or item.get("label")
            scheduled_at = parse_datetime(item["scheduledAt"])
            schedule_id = f"{platform}-{scheduled_at:%Y%m%d%H%M}-{index}"
            schedule.append({
                "id": schedule_id,
                "platform": platform,
                "label": label,
                "scheduledAt": scheduled_at,
            })
            for hours in windows:
                checkpoint_at = scheduled_at + timedelta(hours=hours)
                checkpoints.append({
                    "scheduleId": schedule_id,
                    "platform": platform,
                    "label": label,
                    "windowHours": hours,
                    "checkpointAt": checkpoint_at,
                })
    return sorted(schedule, key=lambda row: row["scheduledAt"]), sorted(checkpoints, key=lambda row: row["checkpointAt"])


def build_summary(queue: dict, strategy: dict, baseline: dict, now: datetime) -> str:
    windows = strategy["measurement"]["windowsHours"]
    schedule, checkpoints = schedule_rows(baseline, windows)
    candidates = sorted(
        queue["candidates"],
        key=lambda item: (item["state"] != "ready_for_confirmation", -item["priorityScore"], item["platform"], item["id"]),
    )
    active = [item for item in candidates if item["state"] in {"proposed", "ready_for_confirmation"}]
    ready = [item for item in candidates if item["state"] == "ready_for_confirmation"]
    states = Counter(item["state"] for item in candidates)
    horizon = now + timedelta(days=14)
    recent_floor = now - timedelta(days=3)
    due = [item for item in checkpoints if recent_floor <= item["checkpointAt"] <= horizon]
    upcoming = [item for item in schedule if now - timedelta(hours=24) <= item["scheduledAt"] <= horizon]

    lines = [
        "# Medium + LinkedIn engagement review",
        "",
        f"Generated: {display_time(now)}",
        "",
        "This issue is the operational control surface. Preparation, prioritization, calendar checks, and measurement windows are automated. Every public response or comment still requires its exact target and text to be confirmed immediately before signed-in execution.",
        "",
        "## Queue status",
        "",
        f"- Active candidates: {len(active)} (maximum {queue['maxBatchSizePerPlatform']} per platform)",
        f"- Ready for exact confirmation: {states['ready_for_confirmation']}",
        f"- Proposed: {states['proposed']}",
        f"- Posted with receipt: {states['posted']}",
        f"- Skipped: {states['skipped']}",
        "",
        "## Upcoming publishing calendar",
        "",
        "| Platform | Item | Scheduled time |",
        "|---|---|---|",
    ]
    if upcoming:
        lines.extend(f"| {platform_label(item['platform'])} | {escape_cell(item['label'])} | {display_time(item['scheduledAt'])} |" for item in upcoming)
    else:
        lines.append("| — | No scheduled item in the next 14 days | — |")

    lines.extend([
        "",
        "## Measurement checkpoints",
        "",
        "| Status | Platform | Item | Window | Checkpoint |",
        "|---|---|---|---:|---|",
    ])
    if due:
        for item in due:
            status = "DUE" if item["checkpointAt"] <= now else "upcoming"
            label = {48: "48 hours", 168: "7 days", 672: "28 days"}[item["windowHours"]]
            lines.append(f"| {status} | {platform_label(item['platform'])} | {escape_cell(item['label'])} | {label} | {display_time(item['checkpointAt'])} |")
    else:
        lines.append("| — | — | No checkpoint in the current review horizon | — | — |")

    lines.extend([
        "",
        "## Exact actions awaiting confirmation",
        "",
    ])
    if ready:
        for item in ready:
            mentions = ", ".join(item.get("intendedMentions", [])) or "none"
            lines.extend([
                f"### {platform_label(item['platform'])} · {item['action']} · {escape_cell(item['title'])}",
                "",
                f"- Candidate: `{item['id']}`",
                f"- Target: {item['targetUrl']}",
                f"- Author: {item['author']}",
                f"- Priority: {item['priorityScore']:.2f}",
                f"- Intended mention: {mentions}",
                f"- Evidence: {item['evidence']}",
                "",
                "> " + item["draftResponse"].replace("\n", "\n> "),
                "",
                "- [ ] Exact target, text, and mention shown to the user",
                "- [ ] Action-time confirmation obtained",
                "- [ ] Public result visibly verified",
                "- [ ] Execution receipt committed",
                "",
            ])
    else:
        lines.extend([
            "No candidate is authorized or awaiting action-time confirmation. A signed-in review may add source-specific candidates, then `manage_engagement_queue.py ready` can promote only those scoring at least 0.70.",
            "",
        ])

    lines.extend([
        "## Recurring signed-in review checklist",
        "",
        "- [ ] Review Medium notifications and story responses; answer substantive inbound questions first.",
        "- [ ] Review LinkedIn notifications and comments on recent posts; answer questions and credible counterarguments first.",
        "- [ ] Research at most five external candidates per platform and read each source before drafting.",
        "- [ ] Do not add links, generic praise, hashtag blocks, irrelevant mentions, or promotional calls to action to comments.",
        "- [ ] Capture only aggregate performance metrics due in the table above.",
        "- [ ] Record recurring reader questions as future article hypotheses.",
        "",
        "## Baseline and decision rule",
        "",
        f"- Medium baseline: {baseline['medium']['august2026']['presentations']} presentations, {baseline['medium']['august2026']['views']} views, {baseline['medium']['august2026']['reads']} reads.",
        f"- LinkedIn baseline: {baseline['linkedin']['sevenDay']['impressions']} impressions, {baseline['linkedin']['sevenDay']['socialEngagements']} social engagements, {baseline['linkedin']['sevenDay']['comments']} comments.",
        "- Continue a format only after comparing at least three posts or stories at the same measurement window; small samples are directional, not causal.",
        "",
        "## Integrity boundary",
        "",
        "GitHub Actions did not access either signed-in account and did not post, comment, respond, react, follow, repost, or generate traffic. It prepared this bounded, auditable control packet only.",
    ])
    return "\n".join(lines) + "\n"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", type=Path, default=ROOT / "engagement-review")
    parser.add_argument("--as-of", help="ISO-8601 timestamp used for deterministic review generation")
    args = parser.parse_args()
    queue = load_json(QUEUE_PATH)
    strategy = load_json(STRATEGY_PATH)
    baseline = load_json(ROOT / strategy["measurement"]["baselinePath"])
    now = parse_datetime(args.as_of) if args.as_of else datetime.now(timezone.utc)
    if now.tzinfo is None:
        now = now.replace(tzinfo=timezone.utc)
    schedule, checkpoints = schedule_rows(baseline, strategy["measurement"]["windowsHours"])
    args.output_dir.mkdir(parents=True, exist_ok=True)
    (args.output_dir / "summary.md").write_text(build_summary(queue, strategy, baseline, now), encoding="utf-8")

    with (args.output_dir / "schedule.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(["id", "platform", "label", "scheduled_at", "scheduled_at_ist"])
        for row in schedule:
            writer.writerow([row["id"], row["platform"], row["label"], row["scheduledAt"].isoformat(), display_time(row["scheduledAt"])])
    with (args.output_dir / "measurement-checkpoints.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(["schedule_id", "platform", "label", "window_hours", "checkpoint_at", "checkpoint_at_ist"])
        for row in checkpoints:
            writer.writerow([row["scheduleId"], row["platform"], row["label"], row["windowHours"], row["checkpointAt"].isoformat(), display_time(row["checkpointAt"])])
    print(f"generated cross-platform review with {len(queue['candidates'])} queue entries and {len(checkpoints)} checkpoints")


if __name__ == "__main__":
    main()
