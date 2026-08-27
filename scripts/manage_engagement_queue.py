#!/usr/bin/env python3
"""Safely add, promote, skip, or inspect bounded engagement candidates."""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from datetime import datetime, timezone

from build_site import ROOT


QUEUE_PATH = ROOT / "engagement" / "queue.json"
STRATEGY_PATH = ROOT / "engagement" / "strategy.json"


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def load(path):
    return json.loads(path.read_text(encoding="utf-8"))


def slug(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", value.casefold()).strip("-")


def find(queue: dict, candidate_id: str) -> dict:
    matches = [item for item in queue["candidates"] if item.get("id") == candidate_id]
    if len(matches) != 1:
        raise SystemExit(f"queue must contain exactly one candidate for {candidate_id}")
    return matches[0]


def main() -> None:
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest="command", required=True)
    add = subparsers.add_parser("add")
    add.add_argument("--candidate-id")
    add.add_argument("--platform", choices=("medium", "linkedin"), required=True)
    add.add_argument("--action", choices=("response", "comment", "reply", "author_comment"), required=True)
    add.add_argument("--direction", choices=("inbound", "outbound"), required=True)
    add.add_argument("--target-url", required=True)
    add.add_argument("--title", required=True)
    add.add_argument("--author", required=True)
    add.add_argument("--reason", required=True)
    add.add_argument("--evidence", required=True)
    add.add_argument("--draft-response", required=True)
    add.add_argument("--priority-score", type=float, required=True)
    add.add_argument("--intended-mention", action="append", default=[])

    for command in ("ready", "skip"):
        child = subparsers.add_parser(command)
        child.add_argument("--candidate-id", required=True)
    subparsers.add_parser("list")
    args = parser.parse_args()
    queue = load(QUEUE_PATH)
    strategy = load(STRATEGY_PATH)
    if args.command == "list":
        print(json.dumps(queue["candidates"], indent=2, ensure_ascii=False))
        return

    original = QUEUE_PATH.read_text(encoding="utf-8")
    if args.command == "add":
        if args.platform == "medium" and args.action != "response":
            raise SystemExit("Medium candidates must use --action response")
        if args.platform == "linkedin" and args.action == "response":
            raise SystemExit("LinkedIn candidates must use comment, reply, or author_comment")
        candidate_id = args.candidate_id or f"{utc_now()[:10]}-{args.platform}-{args.action}-{slug(args.author)}-{slug(args.title)[:40]}"
        if any(item.get("id") == candidate_id for item in queue["candidates"]):
            raise SystemExit(f"candidate already exists: {candidate_id}")
        queue["candidates"].append({
            "id": candidate_id,
            "platform": args.platform,
            "action": args.action,
            "direction": args.direction,
            "targetUrl": args.target_url,
            "title": args.title,
            "author": args.author,
            "reason": args.reason,
            "evidence": args.evidence,
            "draftResponse": args.draft_response,
            "priorityScore": args.priority_score,
            "intendedMentions": args.intended_mention,
            "state": "proposed",
        })
    else:
        candidate = find(queue, args.candidate_id)
        if candidate.get("state") not in {"proposed", "ready_for_confirmation"}:
            raise SystemExit(f"candidate {args.candidate_id} cannot transition from {candidate.get('state')}")
        if args.command == "ready":
            threshold = strategy["candidateScoring"]["minimumPriorityScore"]
            if candidate.get("priorityScore", 0) < threshold:
                raise SystemExit(f"candidate score must be at least {threshold:.2f}")
            candidate["state"] = "ready_for_confirmation"
        else:
            candidate["state"] = "skipped"
    queue["updatedAt"] = utc_now()
    QUEUE_PATH.write_text(json.dumps(queue, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    try:
        subprocess.run([sys.executable, str(ROOT / "scripts" / "validate_engagement_automation.py")], cwd=ROOT, check=True)
    except BaseException:
        QUEUE_PATH.write_text(original, encoding="utf-8")
        raise
    print(f"engagement queue updated: {args.command}")


if __name__ == "__main__":
    main()
