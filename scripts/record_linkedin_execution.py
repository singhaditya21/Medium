#!/usr/bin/env python3
"""Record one verified, individually approved LinkedIn interaction."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

from build_site import ROOT


QUEUE_PATH = ROOT / "engagement" / "queue.json"
EXECUTIONS_DIR = ROOT / "linkedin" / "executions"
COMMAND_TO_ACTION = {
    "comment-posted": ("comment_posted", "comment"),
    "reply-posted": ("reply_posted", "reply"),
    "author-comment-posted": ("author_comment_posted", "author_comment"),
}


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def operation_id(action: str, candidate_id: str, timestamp: str) -> str:
    compact_time = re.sub(r"[^0-9]", "", timestamp)[:14]
    compact_candidate = re.sub(r"[^a-z0-9]+", "-", candidate_id.casefold()).strip("-")
    return f"{compact_time}-{action.replace('_', '-')}-{compact_candidate}"[:120].rstrip("-")


def main() -> None:
    parser = argparse.ArgumentParser(description="Run only after the LinkedIn action is completed and visibly verified.")
    subparsers = parser.add_subparsers(dest="command", required=True)
    for command in COMMAND_TO_ACTION:
        child = subparsers.add_parser(command)
        child.add_argument("--candidate-id", required=True)
        child.add_argument("--target-url", required=True)
        child.add_argument("--public-url", required=True)
        child.add_argument("--issue-number", type=int, required=True)
        child.add_argument("--confirmation-scope", required=True)
        child.add_argument("--verification", required=True)
        child.add_argument("--operation-id")
        child.add_argument("--recorded-at")
        child.add_argument("--confirmed-at")
        child.add_argument("--verified-at")
        child.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    action, candidate_action = COMMAND_TO_ACTION[args.command]
    queue = json.loads(QUEUE_PATH.read_text(encoding="utf-8"))
    matches = [candidate for candidate in queue["candidates"] if candidate.get("id") == args.candidate_id]
    if len(matches) != 1:
        raise SystemExit(f"engagement queue must contain exactly one candidate for {args.candidate_id}")
    candidate = matches[0]
    if candidate.get("platform") != "linkedin" or candidate.get("action") != candidate_action:
        raise SystemExit(f"candidate {args.candidate_id} does not match {candidate_action}")
    if candidate.get("state") != "ready_for_confirmation":
        raise SystemExit(f"candidate {args.candidate_id} must be ready_for_confirmation")
    if candidate.get("targetUrl") != args.target_url:
        raise SystemExit("target URL does not match the reviewed candidate")

    recorded_at = args.recorded_at or utc_now()
    confirmed_at = args.confirmed_at or recorded_at
    verified_at = args.verified_at or recorded_at
    receipt_id = args.operation_id or operation_id(action, args.candidate_id, recorded_at)
    receipt = {
        "$schema": "../execution.schema.json",
        "schemaVersion": 1,
        "operationId": receipt_id,
        "action": action,
        "recordedAt": recorded_at,
        "executionSurface": "user_initiated_signed_in_linkedin_ui",
        "initiatedBy": "user",
        "githubIssueNumber": args.issue_number,
        "userConfirmation": {
            "obtained": True,
            "confirmedAt": confirmed_at,
            "scope": args.confirmation_scope,
        },
        "result": {
            "status": action,
            "candidateId": args.candidate_id,
            "targetUrl": args.target_url,
            "publicUrl": args.public_url,
            "publishedTextSha256": hashlib.sha256(candidate["draftResponse"].encode("utf-8")).hexdigest(),
            "verifiedAt": verified_at,
            "verification": args.verification,
        },
        "secretsStored": False,
        "githubActionsPerformedLinkedInAction": False,
    }
    if args.dry_run:
        print(json.dumps(receipt, indent=2, ensure_ascii=False))
        return

    receipt_path = EXECUTIONS_DIR / f"{receipt_id}.json"
    if receipt_path.exists():
        raise SystemExit(f"receipt already exists: {receipt_path.relative_to(ROOT)}")
    original_queue = QUEUE_PATH.read_text(encoding="utf-8")
    candidate["state"] = "posted"
    candidate["responseUrl"] = args.public_url
    candidate["receiptOperationId"] = receipt_id
    candidate["postedAt"] = recorded_at
    queue["updatedAt"] = recorded_at
    try:
        QUEUE_PATH.write_text(json.dumps(queue, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        receipt_path.write_text(json.dumps(receipt, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        subprocess.run([sys.executable, str(ROOT / "scripts" / "validate_medium_bridge.py")], cwd=ROOT, check=True)
        subprocess.run([sys.executable, str(ROOT / "scripts" / "validate_engagement_automation.py")], cwd=ROOT, check=True)
    except BaseException:
        QUEUE_PATH.write_text(original_queue, encoding="utf-8")
        receipt_path.unlink(missing_ok=True)
        raise
    print(f"recorded verified LinkedIn execution: {receipt_path.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
