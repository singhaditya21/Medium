#!/usr/bin/env python3
"""Validate credential-free Medium handoff state and build a continuation report."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
from collections import Counter
from datetime import datetime
from pathlib import Path
from typing import Any
from urllib.parse import urlsplit

from build_site import ROOT, load_stories


EXECUTIONS_DIR = ROOT / "medium" / "executions"
PUBLICATIONS_PATH = ROOT / "medium" / "publications.json"
SNAPSHOTS_DIR = ROOT / "analytics" / "snapshots"
BASELINE_PATH = ROOT / "analytics" / "engagement-baseline.json"
QUEUE_PATH = ROOT / "engagement" / "queue.json"
SENSITIVE_KEY_PARTS = {
    "authentication",
    "credential",
    "password",
    "cookie",
    "token",
    "session",
    "authorization",
    "secret",
    "storage",
}
ACTION_STATUS = {
    "draft_imported": "draft_saved",
    "draft_revised": "draft_saved",
    "story_scheduled": "scheduled",
    "story_published": "published",
    "stats_captured": "stats_captured",
    "response_posted": "response_posted",
}


def load_json(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        raise ValueError(f"missing file: {path.relative_to(ROOT)}") from None
    except json.JSONDecodeError as exc:
        raise ValueError(f"invalid JSON in {path.relative_to(ROOT)}: {exc}") from exc


def require_datetime(value: Any, label: str, errors: list[str]) -> None:
    if not isinstance(value, str):
        errors.append(f"{label} must be an ISO-8601 string")
        return
    try:
        datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        errors.append(f"{label} must be an ISO-8601 timestamp")


def medium_url(value: Any) -> bool:
    return isinstance(value, str) and urlsplit(value).scheme == "https" and urlsplit(value).netloc.casefold().endswith("medium.com")


def linkedin_url(value: Any) -> bool:
    return isinstance(value, str) and urlsplit(value).scheme == "https" and urlsplit(value).netloc.casefold().endswith("linkedin.com")


def platform_url(platform: str, value: Any) -> bool:
    if platform == "medium":
        return medium_url(value)
    if platform == "linkedin":
        return linkedin_url(value)
    return False


def nonnegative_int(value: Any) -> bool:
    return isinstance(value, int) and not isinstance(value, bool) and value >= 0


def sensitive_key_paths(value: Any, prefix: str = "") -> list[str]:
    matches: list[str] = []
    if isinstance(value, dict):
        for key, child in value.items():
            path = f"{prefix}.{key}" if prefix else key
            normalized = "".join(character for character in key.casefold() if character.isalnum())
            # Receipts intentionally carry this negative assertion. Treat only
            # the schema-required false value as safe; any other value remains
            # both a validation error and a sensitive-field finding.
            safe_secret_assertion = normalized == "secretsstored" and child is False
            if not safe_secret_assertion and any(part in normalized for part in SENSITIVE_KEY_PARTS):
                matches.append(path)
            matches.extend(sensitive_key_paths(child, path))
    elif isinstance(value, list):
        for index, child in enumerate(value):
            matches.extend(sensitive_key_paths(child, f"{prefix}[{index}]"))
    return matches


def validate_snapshot(path: Path, story_slugs: set[str]) -> tuple[dict[str, Any], list[str]]:
    snapshot = load_json(path)
    errors: list[str] = []
    label = str(path.relative_to(ROOT))
    if snapshot.get("schemaVersion") != 1:
        errors.append(f"{label}: schemaVersion must be 1")
    if snapshot.get("captureMethod") != "user_initiated_signed_in_medium_ui_read_only":
        errors.append(f"{label}: captureMethod must identify the user-initiated read-only UI")
    require_datetime(snapshot.get("capturedAt"), f"{label}.capturedAt", errors)
    if isinstance(snapshot.get("capturedAt"), str) and path.stem != snapshot["capturedAt"][:10]:
        errors.append(f"{label}: filename must match the capturedAt date")
    scopes = snapshot.get("scopes")
    if not isinstance(scopes, dict):
        errors.append(f"{label}: scopes must be an object")
        return snapshot, errors
    current = scopes.get("currentMonth", {})
    audience = scopes.get("audienceLifetime", {})
    for key in ("presentations", "views", "reads"):
        if not nonnegative_int(current.get(key)):
            errors.append(f"{label}: currentMonth.{key} must be a non-negative integer")
    for key in ("followers", "emailSubscribers"):
        if not nonnegative_int(audience.get(key)):
            errors.append(f"{label}: audienceLifetime.{key} must be a non-negative integer")
    rows = scopes.get("storyLifetime")
    if not isinstance(rows, list):
        errors.append(f"{label}: storyLifetime must be an array")
        return snapshot, errors
    seen: set[str] = set()
    for row in rows:
        if not isinstance(row, dict):
            errors.append(f"{label}: each storyLifetime item must be an object")
            continue
        slug = row.get("slug")
        if slug not in story_slugs:
            errors.append(f"{label}: unknown story slug {slug}")
        if slug in seen:
            errors.append(f"{label}: duplicate story slug {slug}")
        if isinstance(slug, str):
            seen.add(slug)
        for key in ("presentations", "views", "reads"):
            if not nonnegative_int(row.get(key)):
                errors.append(f"{label}: {slug}.{key} must be a non-negative integer")
        ratio = row.get("readRatio")
        if not isinstance(ratio, (int, float)) or isinstance(ratio, bool) or not 0 <= ratio <= 1:
            errors.append(f"{label}: {slug}.readRatio must be between zero and one")
    return snapshot, errors


def validate_queue() -> tuple[dict[str, Any], list[str]]:
    queue = load_json(QUEUE_PATH)
    errors: list[str] = []
    if queue.get("schemaVersion") != 2:
        errors.append("engagement queue schemaVersion must be 2")
    exposed_keys = sensitive_key_paths(queue)
    if exposed_keys:
        errors.append(f"engagement queue contains prohibited credential/session fields: {', '.join(exposed_keys)}")
    require_datetime(queue.get("updatedAt"), "engagement queue updatedAt", errors)
    if queue.get("maxBatchSizePerPlatform") not in range(1, 6):
        errors.append("engagement queue maxBatchSizePerPlatform must be between one and five")
    policy = queue.get("policy", {})
    expected_policy = {
        "requiresExactActionTimeConfirmation": True,
        "allowUnattendedPosting": False,
        "allowBulkEngagement": False,
        "allowAutomatedAccountAccess": False,
        "allowAutomatedLikesOrFollows": False,
    }
    if policy != expected_policy:
        errors.append("engagement queue policy must preserve exact confirmation and prohibit unattended/bulk posting")
    candidates = queue.get("candidates")
    if not isinstance(candidates, list) or len(candidates) > 100:
        errors.append("engagement queue candidates must be an array of at most 100 audited items")
        return queue, errors
    seen: set[str] = set()
    active_by_platform: Counter[str] = Counter()
    for candidate in candidates:
        if not isinstance(candidate, dict):
            errors.append("each engagement candidate must be an object")
            continue
        candidate_id = candidate.get("id")
        if not isinstance(candidate_id, str) or not candidate_id:
            errors.append("each engagement candidate needs a non-empty id")
            continue
        if candidate_id in seen:
            errors.append(f"duplicate engagement candidate id: {candidate_id}")
        seen.add(candidate_id)
        allowed_fields = {
            "id",
            "platform",
            "action",
            "direction",
            "targetUrl",
            "title",
            "author",
            "reason",
            "evidence",
            "draftResponse",
            "priorityScore",
            "intendedMentions",
            "state",
            "responseUrl",
            "receiptOperationId",
            "postedAt",
        }
        unexpected_fields = set(candidate) - allowed_fields
        if unexpected_fields:
            errors.append(f"{candidate_id}: unexpected fields: {', '.join(sorted(unexpected_fields))}")
        platform = candidate.get("platform")
        action = candidate.get("action")
        if platform not in {"medium", "linkedin"}:
            errors.append(f"{candidate_id}: platform must be medium or linkedin")
        if platform == "medium" and action != "response":
            errors.append(f"{candidate_id}: Medium candidates must use the response action")
        if platform == "linkedin" and action not in {"comment", "reply", "author_comment"}:
            errors.append(f"{candidate_id}: LinkedIn candidates must use comment, reply, or author_comment")
        if candidate.get("direction") not in {"inbound", "outbound"}:
            errors.append(f"{candidate_id}: direction must be inbound or outbound")
        if isinstance(platform, str) and not platform_url(platform, candidate.get("targetUrl")):
            errors.append(f"{candidate_id}: targetUrl must be an HTTPS {platform}.com URL")
        for field in ("title", "author", "reason", "evidence", "draftResponse"):
            if not isinstance(candidate.get(field), str) or not candidate[field].strip():
                errors.append(f"{candidate_id}: {field} must be non-empty")
        state = candidate.get("state")
        if state not in {"proposed", "ready_for_confirmation", "posted", "skipped"}:
            errors.append(f"{candidate_id}: invalid state")
        if state in {"proposed", "ready_for_confirmation"} and isinstance(platform, str):
            active_by_platform[platform] += 1
        score = candidate.get("priorityScore")
        if not isinstance(score, (int, float)) or isinstance(score, bool) or not 0 <= score <= 1:
            errors.append(f"{candidate_id}: priorityScore must be between zero and one")
        mentions = candidate.get("intendedMentions", [])
        if not isinstance(mentions, list) or len(mentions) > 1 or not all(isinstance(item, str) and item.strip() for item in mentions):
            errors.append(f"{candidate_id}: intendedMentions must contain at most one non-empty value")
        if state == "posted":
            if isinstance(platform, str) and not platform_url(platform, candidate.get("responseUrl")):
                errors.append(f"{candidate_id}: posted interactions require a public {platform} responseUrl")
            if not isinstance(candidate.get("receiptOperationId"), str):
                errors.append(f"{candidate_id}: posted responses require receiptOperationId")
    maximum = queue.get("maxBatchSizePerPlatform")
    if isinstance(maximum, int):
        for platform, count in active_by_platform.items():
            if count > maximum:
                errors.append(f"engagement queue has {count} active {platform} candidates; maximum is {maximum}")
    return queue, errors


def publication_map() -> dict[str, dict[str, Any]]:
    document = load_json(PUBLICATIONS_PATH)
    return {record["storySlug"]: record for record in document.get("stories", [])}


def validate_receipt(
    path: Path,
    story_slugs: set[str],
    publications: dict[str, dict[str, Any]],
    queue: dict[str, Any],
) -> tuple[dict[str, Any], list[str]]:
    receipt = load_json(path)
    errors: list[str] = []
    label = str(path.relative_to(ROOT))
    if receipt.get("schemaVersion") != 1:
        errors.append(f"{label}: schemaVersion must be 1")
    allowed_receipt_fields = {
        "$schema",
        "schemaVersion",
        "operationId",
        "action",
        "recordedAt",
        "executionSurface",
        "initiatedBy",
        "githubIssueNumber",
        "userConfirmation",
        "result",
        "secretsStored",
        "githubActionsPerformedMediumAction",
    }
    unexpected_receipt_fields = set(receipt) - allowed_receipt_fields
    if unexpected_receipt_fields:
        errors.append(f"{label}: unexpected receipt fields: {', '.join(sorted(unexpected_receipt_fields))}")
    operation_id = receipt.get("operationId")
    if operation_id != path.stem:
        errors.append(f"{label}: operationId must match the filename")
    action = receipt.get("action")
    if action not in ACTION_STATUS:
        errors.append(f"{label}: unsupported action")
    require_datetime(receipt.get("recordedAt"), f"{label}.recordedAt", errors)
    if receipt.get("executionSurface") != "user_initiated_signed_in_medium_ui":
        errors.append(f"{label}: invalid executionSurface")
    if receipt.get("initiatedBy") != "user":
        errors.append(f"{label}: initiatedBy must be user")
    if not isinstance(receipt.get("githubIssueNumber"), int) or receipt["githubIssueNumber"] < 1:
        errors.append(f"{label}: githubIssueNumber must be positive")
    confirmation = receipt.get("userConfirmation", {})
    if not isinstance(confirmation, dict):
        errors.append(f"{label}: userConfirmation must be an object")
        confirmation = {}
    elif set(confirmation) - {"obtained", "confirmedAt", "scope"}:
        errors.append(f"{label}: userConfirmation contains unexpected fields")
    if confirmation.get("obtained") is not True or not isinstance(confirmation.get("scope"), str) or not confirmation.get("scope", "").strip():
        errors.append(f"{label}: exact user confirmation must be recorded")
    require_datetime(confirmation.get("confirmedAt"), f"{label}.userConfirmation.confirmedAt", errors)
    if receipt.get("secretsStored") is not False:
        errors.append(f"{label}: secretsStored must be false")
    if receipt.get("githubActionsPerformedMediumAction") is not False:
        errors.append(f"{label}: GitHub Actions must not perform the Medium action")
    exposed_keys = sensitive_key_paths(receipt)
    if exposed_keys:
        errors.append(f"{label}: prohibited credential/session fields: {', '.join(exposed_keys)}")

    result = receipt.get("result", {})
    if not isinstance(result, dict):
        errors.append(f"{label}: result must be an object")
        result = {}
    result_fields = {
        "draft_imported": {"status", "storySlug", "verifiedAt", "verification"},
        "draft_revised": {"status", "storySlug", "settings", "content", "verifiedAt", "verification"},
        "story_scheduled": {"status", "storySlug", "mediumUrl", "settings", "verifiedAt", "verification"},
        "story_published": {"status", "storySlug", "mediumUrl", "settings", "verifiedAt", "verification"},
        "stats_captured": {"status", "snapshotPath", "verifiedAt", "verification"},
        "response_posted": {"status", "candidateId", "targetUrl", "responseUrl", "verifiedAt", "verification"},
    }
    if action in result_fields and set(result) - result_fields[action]:
        errors.append(f"{label}: result contains unexpected fields for {action}")
    if action in ACTION_STATUS and result.get("status") != ACTION_STATUS[action]:
        errors.append(f"{label}: result status does not match action")
    require_datetime(result.get("verifiedAt"), f"{label}.result.verifiedAt", errors)
    if not isinstance(result.get("verification"), str) or not result.get("verification", "").strip():
        errors.append(f"{label}: result verification must be non-empty")

    story_slug = result.get("storySlug")
    if action in {"draft_imported", "draft_revised", "story_scheduled", "story_published"} and story_slug not in story_slugs:
        errors.append(f"{label}: unknown storySlug")
    if action in {"draft_imported", "draft_revised"} and any(key in result for key in ("mediumDraftUrl", "draftUrl")):
        errors.append(f"{label}: private Medium draft URLs must not be stored")
    if action in {"draft_revised", "story_scheduled", "story_published"}:
        if action in {"story_scheduled", "story_published"}:
            url = result.get("mediumUrl")
            if not medium_url(url):
                errors.append(f"{label}: scheduled or published story requires an HTTPS medium.com URL")
        if action == "story_published":
            record = publications.get(story_slug, {})
            if record.get("status") != "published" or record.get("mediumUrl") != url:
                errors.append(f"{label}: publication registry must match the verified public URL")
        settings = result.get("settings")
        if not isinstance(settings, dict):
            errors.append(f"{label}: scheduled or published story requires final settings")
        else:
            allowed_settings = {"topics", "publication", "subscriberEmail", "paywall", "scheduleAt", "canonicalUrl"}
            if set(settings) - allowed_settings:
                errors.append(f"{label}: final settings contain unexpected fields")
            topics = settings.get("topics")
            if not isinstance(topics, list) or not 1 <= len(topics) <= 5 or not all(isinstance(item, str) and item.strip() for item in topics):
                errors.append(f"{label}: final topics must contain one to five values")
            for flag in ("subscriberEmail", "paywall"):
                if not isinstance(settings.get(flag), bool):
                    errors.append(f"{label}: settings.{flag} must be boolean")
            if not isinstance(settings.get("canonicalUrl"), str):
                errors.append(f"{label}: settings.canonicalUrl is required")
            if action in {"draft_revised", "story_scheduled"}:
                require_datetime(settings.get("scheduleAt"), f"{label}.settings.scheduleAt", errors)
    if action == "draft_revised":
        content = result.get("content")
        if not isinstance(content, dict):
            errors.append(f"{label}: revised draft requires verified content details")
        else:
            allowed_content = {
                "mediumWordCount",
                "mediumReadTime",
                "figureCount",
                "captionCount",
                "altTextCount",
                "decisionFormat",
                "featuredImage",
                "sourceSha256",
            }
            if set(content) - allowed_content:
                errors.append(f"{label}: content contains unexpected fields")
            for field in ("mediumWordCount", "figureCount", "captionCount", "altTextCount"):
                if not nonnegative_int(content.get(field)):
                    errors.append(f"{label}: content.{field} must be a non-negative integer")
            if not isinstance(content.get("mediumReadTime"), str) or not content["mediumReadTime"].strip():
                errors.append(f"{label}: content.mediumReadTime must be non-empty")
            if content.get("decisionFormat") != "medium_native_structured_list":
                errors.append(f"{label}: content.decisionFormat must record the Medium-native adaptation")
            if content.get("featuredImage") != "figure-01":
                errors.append(f"{label}: content.featuredImage must preserve figure-01")
            source_hash = content.get("sourceSha256")
            source_path = ROOT / "stories" / f"{story_slug}.md"
            if not isinstance(source_hash, str) or len(source_hash) != 64:
                errors.append(f"{label}: content.sourceSha256 must be a SHA-256 digest")
            elif source_path.is_file() and hashlib.sha256(source_path.read_bytes()).hexdigest() != source_hash:
                errors.append(f"{label}: content.sourceSha256 does not match the canonical story")
    if action == "stats_captured":
        snapshot_path = result.get("snapshotPath")
        if not isinstance(snapshot_path, str) or not snapshot_path.startswith("analytics/snapshots/"):
            errors.append(f"{label}: stats receipt needs an analytics/snapshots path")
        elif not (ROOT / snapshot_path).is_file():
            errors.append(f"{label}: referenced analytics snapshot does not exist")
    if action == "response_posted":
        candidate_id = result.get("candidateId")
        target_url = result.get("targetUrl")
        response_url = result.get("responseUrl")
        candidates = {item.get("id"): item for item in queue.get("candidates", []) if isinstance(item, dict)}
        candidate = candidates.get(candidate_id, {})
        if not medium_url(target_url) or not medium_url(response_url):
            errors.append(f"{label}: response receipt requires target and response Medium URLs")
        if candidate.get("state") != "posted" or candidate.get("receiptOperationId") != operation_id:
            errors.append(f"{label}: engagement queue must mark the candidate posted with this receipt")
        if candidate.get("platform") != "medium" or candidate.get("action") != "response":
            errors.append(f"{label}: response receipt must reference a Medium response candidate")
        if candidate.get("targetUrl") != target_url or candidate.get("responseUrl") != response_url:
            errors.append(f"{label}: response receipt and queue URLs must match")
    return receipt, errors


def build_report(
    snapshots: list[dict[str, Any]],
    receipts: list[dict[str, Any]],
    queue: dict[str, Any],
    output_dir: Path,
) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    latest = snapshots[-1]
    current = latest["scopes"]["currentMonth"]
    audience = latest["scopes"]["audienceLifetime"]
    action_counts = Counter(receipt["action"] for receipt in receipts)
    state_counts = Counter(candidate["state"] for candidate in queue["candidates"])
    report = [
        "# Medium signed-in bridge report",
        "",
        "GitHub Actions validated repository state only. It did not sign in to Medium or perform an account action.",
        "",
        "## Latest aggregate snapshot",
        "",
        f"- Captured: {latest['capturedAt']}",
        f"- Period: {current['label']}",
        f"- Presentations: {current['presentations']}",
        f"- Views: {current['views']}",
        f"- Reads: {current['reads']}",
        f"- Followers: {audience['followers']}",
        f"- Email subscribers: {audience['emailSubscribers']}",
        "",
        "## Continuation state",
        "",
        f"- Verified receipts: {len(receipts)}",
        f"- Draft imports: {action_counts['draft_imported']}",
        f"- Draft revisions: {action_counts['draft_revised']}",
        f"- Scheduled stories: {action_counts['story_scheduled']}",
        f"- Publications: {action_counts['story_published']}",
        f"- Stats captures: {action_counts['stats_captured']}",
        f"- Responses posted: {action_counts['response_posted']}",
        f"- Engagement candidates: {len(queue['candidates'])}",
        f"- Awaiting confirmation: {state_counts['ready_for_confirmation']}",
    ]
    if len(snapshots) > 1:
        previous = snapshots[-2]
        before = previous["scopes"]["currentMonth"]
        report.extend([
            "",
            "## Change from previous snapshot",
            "",
            f"- Presentations: {current['presentations'] - before['presentations']:+d}",
            f"- Views: {current['views'] - before['views']:+d}",
            f"- Reads: {current['reads'] - before['reads']:+d}",
        ])
    else:
        report.extend(["", "Only one snapshot exists; trend deltas begin after the next signed-in capture."])
    (output_dir / "summary.md").write_text("\n".join(report) + "\n", encoding="utf-8")

    with (output_dir / "snapshot-history.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(["captured_at", "period", "presentations", "views", "reads", "followers", "email_subscribers"])
        for snapshot in snapshots:
            month = snapshot["scopes"]["currentMonth"]
            snapshot_audience = snapshot["scopes"]["audienceLifetime"]
            writer.writerow([
                snapshot["capturedAt"],
                month["label"],
                month["presentations"],
                month["views"],
                month["reads"],
                snapshot_audience["followers"],
                snapshot_audience["emailSubscribers"],
            ])

    with (output_dir / "engagement-queue.csv").open("w", newline="", encoding="utf-8") as handle:
        fields = ["id", "platform", "action", "direction", "priorityScore", "state", "title", "author", "targetUrl", "responseUrl", "receiptOperationId"]
        writer = csv.DictWriter(handle, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(queue["candidates"])


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", type=Path)
    args = parser.parse_args()
    stories = load_stories()
    story_slugs = {story["slug"] for story in stories}
    errors: list[str] = []

    queue, queue_errors = validate_queue()
    errors.extend(queue_errors)
    snapshot_pairs = [validate_snapshot(path, story_slugs) for path in sorted(SNAPSHOTS_DIR.glob("*.json"))]
    if not snapshot_pairs:
        errors.append("at least one analytics snapshot is required")
    snapshots = [snapshot for snapshot, _ in snapshot_pairs]
    for _, snapshot_errors in snapshot_pairs:
        errors.extend(snapshot_errors)

    baseline = load_json(BASELINE_PATH)
    if snapshots:
        latest = snapshots[-1]
        if baseline.get("capturedAt") != latest.get("capturedAt") or baseline.get("profile") != latest.get("profile") or baseline.get("scopes") != latest.get("scopes"):
            errors.append("engagement-baseline.json must match the latest dated analytics snapshot")

    publications = publication_map()
    receipt_pairs = [
        validate_receipt(path, story_slugs, publications, queue)
        for path in sorted(EXECUTIONS_DIR.glob("*.json"))
    ]
    receipts = [receipt for receipt, _ in receipt_pairs]
    for _, receipt_errors in receipt_pairs:
        errors.extend(receipt_errors)
    operation_ids = [receipt.get("operationId") for receipt in receipts]
    duplicates = [operation_id for operation_id, count in Counter(operation_ids).items() if count > 1]
    if duplicates:
        errors.append(f"duplicate execution operationIds: {', '.join(duplicates)}")

    if errors:
        print("Medium bridge validation failed:")
        for error in errors:
            print(f"- {error}")
        raise SystemExit(1)
    if args.output_dir:
        build_report(snapshots, receipts, queue, args.output_dir)
    print(f"validated signed-in Medium bridge: {len(snapshots)} snapshots, {len(receipts)} receipts, {len(queue['candidates'])} engagement candidates")


if __name__ == "__main__":
    main()
