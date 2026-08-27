#!/usr/bin/env python3
"""Record a verified signed-in Medium action without storing browser credentials."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from build_site import ROOT, load_stories


EXECUTIONS_DIR = ROOT / "medium" / "executions"
PUBLICATIONS_PATH = ROOT / "medium" / "publications.json"
QUEUE_PATH = ROOT / "engagement" / "queue.json"


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def bool_value(value: str) -> bool:
    lowered = value.casefold()
    if lowered == "true":
        return True
    if lowered == "false":
        return False
    raise argparse.ArgumentTypeError("expected true or false")


def operation_id(action: str, target: str, timestamp: str) -> str:
    compact_time = re.sub(r"[^0-9]", "", timestamp)[:14]
    compact_target = re.sub(r"[^a-z0-9]+", "-", target.casefold()).strip("-")
    return f"{compact_time}-{action.replace('_', '-')}-{compact_target}"[:120].rstrip("-")


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def common_receipt(args: argparse.Namespace, action: str, result: dict[str, Any], target: str) -> dict[str, Any]:
    recorded_at = args.recorded_at or utc_now()
    confirmed_at = args.confirmed_at or recorded_at
    verified_at = args.verified_at or recorded_at
    result["verifiedAt"] = verified_at
    result["verification"] = args.verification
    generated_id = operation_id(action, target, recorded_at)
    return {
        "$schema": "../execution.schema.json",
        "schemaVersion": 1,
        "operationId": args.operation_id or generated_id,
        "action": action,
        "recordedAt": recorded_at,
        "executionSurface": "user_initiated_signed_in_medium_ui",
        "initiatedBy": "user",
        "githubIssueNumber": args.issue_number,
        "userConfirmation": {
            "obtained": True,
            "confirmedAt": confirmed_at,
            "scope": args.confirmation_scope,
        },
        "result": result,
        "secretsStored": False,
        "githubActionsPerformedMediumAction": False,
    }


def update_publication(story_slug: str, medium_url: str) -> None:
    document = load_json(PUBLICATIONS_PATH)
    matches = [record for record in document["stories"] if record["storySlug"] == story_slug]
    if len(matches) != 1:
        raise SystemExit(f"publication registry must contain exactly one record for {story_slug}")
    matches[0]["status"] = "published"
    matches[0]["mediumUrl"] = medium_url
    document["verifiedAt"] = utc_now()[:10]
    document["verificationMethod"] = "signed_in_medium_published_stories"
    write_json(PUBLICATIONS_PATH, document)


def update_response_candidate(candidate_id: str, target_url: str, response_url: str, receipt_id: str, posted_at: str) -> None:
    queue = load_json(QUEUE_PATH)
    matches = [candidate for candidate in queue["candidates"] if candidate.get("id") == candidate_id]
    if len(matches) != 1:
        raise SystemExit(f"engagement queue must contain exactly one candidate for {candidate_id}")
    candidate = matches[0]
    if candidate.get("platform") != "medium" or candidate.get("action") != "response":
        raise SystemExit(f"engagement candidate {candidate_id} is not a Medium response")
    if candidate.get("state") != "ready_for_confirmation":
        raise SystemExit(f"engagement candidate {candidate_id} must be ready_for_confirmation before recording a response")
    if candidate.get("targetUrl") != target_url:
        raise SystemExit("response target URL does not match the reviewed engagement candidate")
    candidate["state"] = "posted"
    candidate["responseUrl"] = response_url
    candidate["receiptOperationId"] = receipt_id
    candidate["postedAt"] = posted_at
    queue["updatedAt"] = posted_at
    write_json(QUEUE_PATH, queue)


def add_common_arguments(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--issue-number", type=int, required=True)
    parser.add_argument("--confirmation-scope", required=True)
    parser.add_argument("--verification", required=True)
    parser.add_argument("--operation-id")
    parser.add_argument("--recorded-at")
    parser.add_argument("--confirmed-at")
    parser.add_argument("--verified-at")
    parser.add_argument("--dry-run", action="store_true")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Run only after the named Medium action has been completed and visibly verified."
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    draft_parser = subparsers.add_parser("draft-imported")
    add_common_arguments(draft_parser)
    draft_parser.add_argument("--story-slug", required=True)

    revision_parser = subparsers.add_parser("draft-revised")
    add_common_arguments(revision_parser)
    revision_parser.add_argument("--story-slug", required=True)
    revision_parser.add_argument("--canonical-url", required=True)
    revision_parser.add_argument("--topic", action="append", required=True)
    revision_parser.add_argument("--publication")
    revision_parser.add_argument("--subscriber-email", type=bool_value, required=True)
    revision_parser.add_argument("--paywall", type=bool_value, required=True)
    revision_parser.add_argument("--schedule-at", required=True)
    revision_parser.add_argument("--medium-word-count", type=int, required=True)
    revision_parser.add_argument("--medium-read-time", required=True)
    revision_parser.add_argument("--figure-count", type=int, required=True)
    revision_parser.add_argument("--caption-count", type=int, required=True)
    revision_parser.add_argument("--alt-text-count", type=int, required=True)
    revision_parser.add_argument(
        "--decision-format",
        choices=("medium_native_structured_list",),
        required=True,
    )
    revision_parser.add_argument("--featured-image", choices=("figure-01",), required=True)

    publish_parser = subparsers.add_parser("story-published")
    add_common_arguments(publish_parser)
    publish_parser.add_argument("--story-slug", required=True)
    publish_parser.add_argument("--medium-url", required=True)
    publish_parser.add_argument("--canonical-url", required=True)
    publish_parser.add_argument("--topic", action="append", required=True)
    publish_parser.add_argument("--publication")
    publish_parser.add_argument("--subscriber-email", type=bool_value, required=True)
    publish_parser.add_argument("--paywall", type=bool_value, required=True)
    publish_parser.add_argument("--schedule-at")

    schedule_parser = subparsers.add_parser("story-scheduled")
    add_common_arguments(schedule_parser)
    schedule_parser.add_argument("--story-slug", required=True)
    schedule_parser.add_argument("--medium-url", required=True)
    schedule_parser.add_argument("--canonical-url", required=True)
    schedule_parser.add_argument("--topic", action="append", required=True)
    schedule_parser.add_argument("--publication")
    schedule_parser.add_argument("--subscriber-email", type=bool_value, required=True)
    schedule_parser.add_argument("--paywall", type=bool_value, required=True)
    schedule_parser.add_argument("--schedule-at", required=True)

    stats_parser = subparsers.add_parser("stats-captured")
    add_common_arguments(stats_parser)
    stats_parser.add_argument("--snapshot-path", required=True)

    response_parser = subparsers.add_parser("response-posted")
    add_common_arguments(response_parser)
    response_parser.add_argument("--candidate-id", required=True)
    response_parser.add_argument("--target-url", required=True)
    response_parser.add_argument("--response-url", required=True)

    args = parser.parse_args()
    story_slugs = {story["slug"] for story in load_stories()}
    if getattr(args, "story_slug", None) and args.story_slug not in story_slugs:
        raise SystemExit(f"unknown story slug: {args.story_slug}")

    if args.command == "draft-imported":
        action = "draft_imported"
        target = args.story_slug
        result = {"status": "draft_saved", "storySlug": args.story_slug}
    elif args.command == "draft-revised":
        action = "draft_revised"
        target = args.story_slug
        source_path = ROOT / "stories" / f"{args.story_slug}.md"
        result = {
            "status": "draft_saved",
            "storySlug": args.story_slug,
            "settings": {
                "topics": args.topic,
                "publication": args.publication,
                "subscriberEmail": args.subscriber_email,
                "paywall": args.paywall,
                "scheduleAt": args.schedule_at,
                "canonicalUrl": args.canonical_url,
            },
            "content": {
                "mediumWordCount": args.medium_word_count,
                "mediumReadTime": args.medium_read_time,
                "figureCount": args.figure_count,
                "captionCount": args.caption_count,
                "altTextCount": args.alt_text_count,
                "decisionFormat": args.decision_format,
                "featuredImage": args.featured_image,
                "sourceSha256": hashlib.sha256(source_path.read_bytes()).hexdigest(),
            },
        }
    elif args.command == "story-scheduled":
        action = "story_scheduled"
        target = args.story_slug
        result = {
            "status": "scheduled",
            "storySlug": args.story_slug,
            "mediumUrl": args.medium_url,
            "settings": {
                "topics": args.topic,
                "publication": args.publication,
                "subscriberEmail": args.subscriber_email,
                "paywall": args.paywall,
                "scheduleAt": args.schedule_at,
                "canonicalUrl": args.canonical_url,
            },
        }
    elif args.command == "story-published":
        action = "story_published"
        target = args.story_slug
        result = {
            "status": "published",
            "storySlug": args.story_slug,
            "mediumUrl": args.medium_url,
            "settings": {
                "topics": args.topic,
                "publication": args.publication,
                "subscriberEmail": args.subscriber_email,
                "paywall": args.paywall,
                "scheduleAt": args.schedule_at,
                "canonicalUrl": args.canonical_url,
            },
        }
    elif args.command == "stats-captured":
        action = "stats_captured"
        target = Path(args.snapshot_path).stem
        result = {"status": "stats_captured", "snapshotPath": args.snapshot_path}
    else:
        action = "response_posted"
        target = args.candidate_id
        result = {
            "status": "response_posted",
            "candidateId": args.candidate_id,
            "targetUrl": args.target_url,
            "responseUrl": args.response_url,
        }

    receipt = common_receipt(args, action, result, target)
    if args.dry_run:
        print(json.dumps(receipt, indent=2, ensure_ascii=False))
        return
    receipt_path = EXECUTIONS_DIR / f"{receipt['operationId']}.json"
    if receipt_path.exists():
        raise SystemExit(f"receipt already exists: {receipt_path.relative_to(ROOT)}")

    original_publications = PUBLICATIONS_PATH.read_text(encoding="utf-8")
    original_queue = QUEUE_PATH.read_text(encoding="utf-8")
    try:
        if action == "story_published":
            update_publication(args.story_slug, args.medium_url)
        if action == "response_posted":
            update_response_candidate(
                args.candidate_id,
                args.target_url,
                args.response_url,
                receipt["operationId"],
                receipt["recordedAt"],
            )
        write_json(receipt_path, receipt)
        subprocess.run(
            [sys.executable, str(ROOT / "scripts" / "validate_medium_bridge.py")],
            cwd=ROOT,
            check=True,
        )
    except BaseException:
        PUBLICATIONS_PATH.write_text(original_publications, encoding="utf-8")
        QUEUE_PATH.write_text(original_queue, encoding="utf-8")
        receipt_path.unlink(missing_ok=True)
        raise
    print(f"recorded verified Medium execution: {receipt_path.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
