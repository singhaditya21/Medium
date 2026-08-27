#!/usr/bin/env python3
"""Validate the unified Medium + LinkedIn engagement control plane."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
from collections import Counter
from pathlib import Path
from typing import Any

from build_site import ROOT
from validate_medium_bridge import (
    linkedin_url,
    load_json,
    require_datetime,
    sensitive_key_paths,
    validate_queue,
)


STRATEGY_PATH = ROOT / "engagement" / "strategy.json"
EXECUTIONS_DIR = ROOT / "linkedin" / "executions"
MESSAGE_EXECUTIONS_DIR = ROOT / "linkedin" / "message-executions"
ACTION_TO_CANDIDATE = {
    "comment_posted": "comment",
    "reply_posted": "reply",
    "author_comment_posted": "author_comment",
}


def validate_strategy() -> tuple[dict[str, Any], list[str]]:
    strategy = load_json(STRATEGY_PATH)
    errors: list[str] = []
    if strategy.get("schemaVersion") != 1:
        errors.append("engagement strategy schemaVersion must be 1")
    if strategy.get("status") != "active":
        errors.append("engagement strategy must be active")
    if strategy.get("timezone") != "Asia/Kolkata":
        errors.append("engagement strategy timezone must be Asia/Kolkata")
    pillars = strategy.get("contentPillars")
    if not isinstance(pillars, list) or len(pillars) < 3 or not all(isinstance(item, str) and item.strip() for item in pillars):
        errors.append("engagement strategy needs at least three non-empty content pillars")

    scoring = strategy.get("candidateScoring", {})
    weights = scoring.get("weights", {})
    expected_weights = {"relevance", "discussionQuality", "uniqueContribution", "recency"}
    if set(weights) != expected_weights or not all(isinstance(value, (int, float)) and not isinstance(value, bool) for value in weights.values()):
        errors.append("candidate scoring weights are incomplete")
    elif abs(sum(weights.values()) - 1.0) > 1e-9:
        errors.append("candidate scoring weights must sum to one")
    threshold = scoring.get("minimumPriorityScore")
    if not isinstance(threshold, (int, float)) or isinstance(threshold, bool) or not 0 <= threshold <= 1:
        errors.append("minimumPriorityScore must be between zero and one")

    cadence = strategy.get("weeklyCadence", {})
    for platform in ("medium", "linkedin"):
        values = cadence.get(platform, {})
        if not isinstance(values, dict) or not values:
            errors.append(f"weekly cadence is missing {platform}")
        elif any(not isinstance(value, int) or isinstance(value, bool) or value < 0 or value > 5 for value in values.values()):
            errors.append(f"weekly cadence values for {platform} must be integers from zero to five")

    standards = strategy.get("responseStandards", {})
    for platform in ("medium", "linkedin"):
        standard = standards.get(platform, {})
        minimum = standard.get("minimumCharacters")
        maximum = standard.get("maximumCharacters")
        if not isinstance(minimum, int) or not isinstance(maximum, int) or minimum < 1 or maximum < minimum:
            errors.append(f"invalid response character bounds for {platform}")
        if standard.get("requireSourceSpecificEvidence") is not True:
            errors.append(f"{platform} responses must require source-specific evidence")
        if standard.get("allowSelfPromotionalLink") is not False:
            errors.append(f"{platform} comments must prohibit self-promotional links")

    measurement = strategy.get("measurement", {})
    if measurement.get("windowsHours") != [48, 168, 672]:
        errors.append("measurement windows must remain 48 hours, 7 days, and 28 days")
    baseline_path = measurement.get("baselinePath")
    if not isinstance(baseline_path, str) or not (ROOT / baseline_path).is_file():
        errors.append("measurement baselinePath must reference a repository file")

    expected_policy = {
        "prepareAndPrioritizeAutomatically": True,
        "packageReviewedDraftsAutomatically": True,
        "generateMeasurementCheckpointsAutomatically": True,
        "openAndRefreshGitHubIssuesAutomatically": True,
        "accessSignedInAccountsFromGitHubActions": False,
        "publishPublicInteractionsAutomatically": False,
        "requireExactActionTimeConfirmation": True,
        "requireVisibleResultVerification": True,
        "storeCredentialsOrBrowserState": False,
    }
    if strategy.get("automationPolicy") != expected_policy:
        errors.append("automationPolicy must preserve the signed-in confirmation and credential boundary")
    return strategy, errors


def validate_candidate_standards(queue: dict[str, Any], strategy: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    threshold = strategy.get("candidateScoring", {}).get("minimumPriorityScore", 1)
    standards = strategy.get("responseStandards", {})
    for candidate in queue.get("candidates", []):
        if not isinstance(candidate, dict):
            continue
        candidate_id = candidate.get("id", "unknown")
        platform = candidate.get("platform")
        standard = standards.get(platform, {})
        draft = candidate.get("draftResponse", "")
        if isinstance(draft, str):
            minimum = standard.get("minimumCharacters", 1)
            maximum = standard.get("maximumCharacters", 0)
            if not minimum <= len(draft.strip()) <= maximum:
                errors.append(f"{candidate_id}: draftResponse length is outside the {platform} standard")
            if standard.get("allowSelfPromotionalLink") is False and re.search(r"https?://", draft):
                errors.append(f"{candidate_id}: engagement drafts cannot contain promotional links")
            if platform == "linkedin" and standard.get("allowHashtagsInComments") is False and re.search(r"(?<!\w)#[A-Za-z]", draft):
                errors.append(f"{candidate_id}: LinkedIn comments cannot contain hashtags")
        if candidate.get("state") == "ready_for_confirmation" and candidate.get("priorityScore", 0) < threshold:
            errors.append(f"{candidate_id}: priority score is below the confirmation threshold")
        if platform == "linkedin" and len(candidate.get("intendedMentions", [])) > standard.get("maximumMentions", 0):
            errors.append(f"{candidate_id}: too many LinkedIn mentions")
    return errors


def validate_linkedin_receipt(path: Path, candidates: dict[str, dict[str, Any]]) -> tuple[dict[str, Any], list[str]]:
    receipt = load_json(path)
    errors: list[str] = []
    label = str(path.relative_to(ROOT))
    allowed_fields = {
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
        "githubActionsPerformedLinkedInAction",
    }
    if set(receipt) - allowed_fields:
        errors.append(f"{label}: unexpected receipt fields")
    if receipt.get("schemaVersion") != 1:
        errors.append(f"{label}: schemaVersion must be 1")
    operation_id = receipt.get("operationId")
    if operation_id != path.stem:
        errors.append(f"{label}: operationId must match the filename")
    action = receipt.get("action")
    if action not in ACTION_TO_CANDIDATE:
        errors.append(f"{label}: unsupported LinkedIn action")
    require_datetime(receipt.get("recordedAt"), f"{label}.recordedAt", errors)
    if receipt.get("executionSurface") != "user_initiated_signed_in_linkedin_ui":
        errors.append(f"{label}: invalid executionSurface")
    if receipt.get("initiatedBy") != "user":
        errors.append(f"{label}: initiatedBy must be user")
    if not isinstance(receipt.get("githubIssueNumber"), int) or receipt.get("githubIssueNumber", 0) < 1:
        errors.append(f"{label}: githubIssueNumber must be positive")
    confirmation = receipt.get("userConfirmation", {})
    if not isinstance(confirmation, dict) or set(confirmation) != {"obtained", "confirmedAt", "scope"}:
        errors.append(f"{label}: userConfirmation must contain obtained, confirmedAt, and scope")
        confirmation = {}
    if confirmation.get("obtained") is not True or not isinstance(confirmation.get("scope"), str) or not confirmation.get("scope", "").strip():
        errors.append(f"{label}: exact user confirmation must be recorded")
    require_datetime(confirmation.get("confirmedAt"), f"{label}.userConfirmation.confirmedAt", errors)
    if receipt.get("secretsStored") is not False:
        errors.append(f"{label}: secretsStored must be false")
    if receipt.get("githubActionsPerformedLinkedInAction") is not False:
        errors.append(f"{label}: GitHub Actions must not perform the LinkedIn action")
    exposed = sensitive_key_paths(receipt)
    if exposed:
        errors.append(f"{label}: prohibited credential/session fields: {', '.join(exposed)}")

    result = receipt.get("result", {})
    expected_result_fields = {
        "status",
        "candidateId",
        "targetUrl",
        "publicUrl",
        "publishedTextSha256",
        "verifiedAt",
        "verification",
    }
    if not isinstance(result, dict) or set(result) != expected_result_fields:
        errors.append(f"{label}: result fields do not match the LinkedIn receipt contract")
        result = result if isinstance(result, dict) else {}
    if action in ACTION_TO_CANDIDATE and result.get("status") != action:
        errors.append(f"{label}: result status must match action")
    require_datetime(result.get("verifiedAt"), f"{label}.result.verifiedAt", errors)
    if not isinstance(result.get("verification"), str) or not result.get("verification", "").strip():
        errors.append(f"{label}: result verification must be non-empty")
    if not linkedin_url(result.get("targetUrl")) or not linkedin_url(result.get("publicUrl")):
        errors.append(f"{label}: targetUrl and publicUrl must be HTTPS linkedin.com URLs")

    candidate = candidates.get(result.get("candidateId"), {})
    if candidate.get("platform") != "linkedin" or candidate.get("action") != ACTION_TO_CANDIDATE.get(action):
        errors.append(f"{label}: receipt does not reference the matching LinkedIn candidate action")
    if candidate.get("state") != "posted" or candidate.get("receiptOperationId") != operation_id:
        errors.append(f"{label}: queue must mark the candidate posted with this receipt")
    if candidate.get("targetUrl") != result.get("targetUrl") or candidate.get("responseUrl") != result.get("publicUrl"):
        errors.append(f"{label}: queue and receipt URLs must match")
    draft = candidate.get("draftResponse")
    expected_hash = hashlib.sha256(draft.encode("utf-8")).hexdigest() if isinstance(draft, str) else None
    if result.get("publishedTextSha256") != expected_hash:
        errors.append(f"{label}: publishedTextSha256 must match the approved queue text")
    return receipt, errors


def validate_linkedin_message_receipt(path: Path) -> tuple[dict[str, Any], list[str]]:
    receipt = load_json(path)
    errors: list[str] = []
    label = str(path.relative_to(ROOT))
    allowed_fields = {
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
        "githubActionsPerformedLinkedInAction",
    }
    if set(receipt) - allowed_fields:
        errors.append(f"{label}: unexpected receipt fields")
    if receipt.get("schemaVersion") != 1:
        errors.append(f"{label}: schemaVersion must be 1")
    operation_id = receipt.get("operationId")
    if operation_id != path.stem:
        errors.append(f"{label}: operationId must match the filename")
    if receipt.get("action") != "message_posted":
        errors.append(f"{label}: action must be message_posted")
    require_datetime(receipt.get("recordedAt"), f"{label}.recordedAt", errors)
    if receipt.get("executionSurface") != "user_initiated_signed_in_linkedin_ui":
        errors.append(f"{label}: invalid executionSurface")
    if receipt.get("initiatedBy") != "user":
        errors.append(f"{label}: initiatedBy must be user")
    if not isinstance(receipt.get("githubIssueNumber"), int) or receipt.get("githubIssueNumber", 0) < 1:
        errors.append(f"{label}: githubIssueNumber must be positive")
    confirmation = receipt.get("userConfirmation", {})
    if not isinstance(confirmation, dict) or set(confirmation) != {"obtained", "confirmedAt", "scope"}:
        errors.append(f"{label}: userConfirmation must contain obtained, confirmedAt, and scope")
        confirmation = {}
    if confirmation.get("obtained") is not True or not isinstance(confirmation.get("scope"), str) or not confirmation.get("scope", "").strip():
        errors.append(f"{label}: exact user confirmation must be recorded")
    require_datetime(confirmation.get("confirmedAt"), f"{label}.userConfirmation.confirmedAt", errors)
    if receipt.get("secretsStored") is not False:
        errors.append(f"{label}: secretsStored must be false")
    if receipt.get("githubActionsPerformedLinkedInAction") is not False:
        errors.append(f"{label}: GitHub Actions must not perform the LinkedIn action")
    exposed = sensitive_key_paths(receipt)
    if exposed:
        errors.append(f"{label}: prohibited credential/session fields: {', '.join(exposed)}")

    result = receipt.get("result", {})
    expected_result_fields = {
        "status",
        "recipientProfileUrl",
        "messageTextSha256",
        "verifiedAt",
        "verification",
    }
    if not isinstance(result, dict) or set(result) != expected_result_fields:
        errors.append(f"{label}: result fields do not match the LinkedIn message receipt contract")
        result = result if isinstance(result, dict) else {}
    if result.get("status") != "message_posted":
        errors.append(f"{label}: result status must be message_posted")
    require_datetime(result.get("verifiedAt"), f"{label}.result.verifiedAt", errors)
    if not isinstance(result.get("verification"), str) or not result.get("verification", "").strip():
        errors.append(f"{label}: result verification must be non-empty")
    if not linkedin_url(result.get("recipientProfileUrl")) or "/in/" not in result.get("recipientProfileUrl", ""):
        errors.append(f"{label}: recipientProfileUrl must be a public LinkedIn profile URL")
    if not re.fullmatch(r"[0-9a-f]{64}", result.get("messageTextSha256", "")):
        errors.append(f"{label}: messageTextSha256 must be 64 lowercase hexadecimal characters")
    return receipt, errors


def build_report(queue: dict[str, Any], receipts: list[dict[str, Any]], message_receipts: list[dict[str, Any]], output_dir: Path) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    candidates = queue["candidates"]
    platform_counts = Counter(candidate["platform"] for candidate in candidates)
    state_counts = Counter(candidate["state"] for candidate in candidates)
    lines = [
        "# Cross-platform engagement validation",
        "",
        "Repository preparation is automated. No GitHub-hosted runner signed in to Medium or LinkedIn or performed a public interaction.",
        "",
        f"- Queue entries: {len(candidates)}",
        f"- Medium entries: {platform_counts['medium']}",
        f"- LinkedIn entries: {platform_counts['linkedin']}",
        f"- Ready for exact confirmation: {state_counts['ready_for_confirmation']}",
        f"- Posted: {state_counts['posted']}",
        f"- Verified LinkedIn receipts: {len(receipts)}",
        f"- Verified LinkedIn private-message receipts: {len(message_receipts)}",
    ]
    (output_dir / "validation-summary.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    with (output_dir / "queue.csv").open("w", newline="", encoding="utf-8") as handle:
        fields = ["id", "platform", "action", "direction", "priorityScore", "state", "title", "author", "targetUrl", "responseUrl"]
        writer = csv.DictWriter(handle, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(candidates)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", type=Path)
    args = parser.parse_args()
    strategy, strategy_errors = validate_strategy()
    queue, queue_errors = validate_queue()
    errors = [*strategy_errors, *queue_errors, *validate_candidate_standards(queue, strategy)]
    candidates = {item.get("id"): item for item in queue.get("candidates", []) if isinstance(item, dict)}
    receipt_pairs = [validate_linkedin_receipt(path, candidates) for path in sorted(EXECUTIONS_DIR.glob("*.json"))]
    receipts = [receipt for receipt, _ in receipt_pairs]
    for _, receipt_errors in receipt_pairs:
        errors.extend(receipt_errors)
    message_receipt_pairs = [validate_linkedin_message_receipt(path) for path in sorted(MESSAGE_EXECUTIONS_DIR.glob("*.json"))]
    message_receipts = [receipt for receipt, _ in message_receipt_pairs]
    for _, receipt_errors in message_receipt_pairs:
        errors.extend(receipt_errors)
    operation_ids = [receipt.get("operationId") for receipt in [*receipts, *message_receipts]]
    duplicates = [value for value, count in Counter(operation_ids).items() if count > 1]
    if duplicates:
        errors.append(f"duplicate LinkedIn operationIds: {', '.join(duplicates)}")
    receipt_ids = set(operation_ids)
    for candidate in candidates.values():
        if candidate.get("platform") == "linkedin" and candidate.get("state") == "posted" and candidate.get("receiptOperationId") not in receipt_ids:
            errors.append(f"{candidate.get('id')}: posted LinkedIn candidate has no matching receipt")
    if errors:
        print("Cross-platform engagement validation failed:")
        for error in errors:
            print(f"- {error}")
        raise SystemExit(1)
    if args.output_dir:
        build_report(queue, receipts, message_receipts, args.output_dir)
    print(
        f"validated cross-platform engagement: {len(candidates)} candidates, "
        f"{len(receipts)} LinkedIn public receipts, {len(message_receipts)} LinkedIn message receipts"
    )


if __name__ == "__main__":
    main()
