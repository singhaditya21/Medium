#!/usr/bin/env python3
"""Record one verified, individually approved LinkedIn private message."""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlparse

from build_site import ROOT


EXECUTIONS_DIR = ROOT / "linkedin" / "message-executions"


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def linkedin_profile_url(value: str) -> bool:
    parsed = urlparse(value)
    return parsed.scheme == "https" and parsed.netloc.casefold() in {"linkedin.com", "www.linkedin.com"} and parsed.path.startswith("/in/")


def operation_id(profile_url: str, timestamp: str) -> str:
    compact_time = re.sub(r"[^0-9]", "", timestamp)[:14]
    profile_slug = re.sub(r"[^a-z0-9]+", "-", urlparse(profile_url).path.casefold()).strip("-")
    return f"{compact_time}-message-posted-{profile_slug}"[:120].rstrip("-")


def main() -> None:
    parser = argparse.ArgumentParser(description="Run only after the LinkedIn message is sent and visibly verified.")
    parser.add_argument("--recipient-profile-url", required=True)
    parser.add_argument("--message-sha256", required=True)
    parser.add_argument("--issue-number", type=int, required=True)
    parser.add_argument("--confirmation-scope", required=True)
    parser.add_argument("--verification", required=True)
    parser.add_argument("--operation-id")
    parser.add_argument("--recorded-at")
    parser.add_argument("--confirmed-at")
    parser.add_argument("--verified-at")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    if not linkedin_profile_url(args.recipient_profile_url):
        raise SystemExit("recipient profile URL must be an HTTPS linkedin.com /in/ URL")
    if not re.fullmatch(r"[0-9a-f]{64}", args.message_sha256):
        raise SystemExit("message SHA-256 must be 64 lowercase hexadecimal characters")

    recorded_at = args.recorded_at or utc_now()
    confirmed_at = args.confirmed_at or recorded_at
    verified_at = args.verified_at or recorded_at
    receipt_id = args.operation_id or operation_id(args.recipient_profile_url, recorded_at)
    receipt = {
        "$schema": "../message-execution.schema.json",
        "schemaVersion": 1,
        "operationId": receipt_id,
        "action": "message_posted",
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
            "status": "message_posted",
            "recipientProfileUrl": args.recipient_profile_url,
            "messageTextSha256": args.message_sha256,
            "verifiedAt": verified_at,
            "verification": args.verification,
        },
        "secretsStored": False,
        "githubActionsPerformedLinkedInAction": False,
    }
    if args.dry_run:
        print(json.dumps(receipt, indent=2, ensure_ascii=False))
        return

    EXECUTIONS_DIR.mkdir(parents=True, exist_ok=True)
    receipt_path = EXECUTIONS_DIR / f"{receipt_id}.json"
    if receipt_path.exists():
        raise SystemExit(f"receipt already exists: {receipt_path.relative_to(ROOT)}")
    try:
        receipt_path.write_text(json.dumps(receipt, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        subprocess.run([sys.executable, str(ROOT / "scripts" / "validate_engagement_automation.py")], cwd=ROOT, check=True)
    except BaseException:
        receipt_path.unlink(missing_ok=True)
        raise
    print(f"recorded verified LinkedIn message execution: {receipt_path.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
