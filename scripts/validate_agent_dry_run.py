#!/usr/bin/env python3
"""Deterministically exercise the agent control plane without a browser or model call."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any

from build_site import ROOT


STRATEGY_PATH = ROOT / "engagement" / "strategy.json"
MATRIX_PATH = ROOT / "engagement" / "agents" / "evaluations" / "dry-run-matrix.json"

EXPECTED_ROLE_LABELS = {
    "linkedin": [
        "Signal triage",
        "Relationship context",
        "Relationship allocator",
        "Network adjacency mapper",
        "Opportunity research",
        "Conversation-quality verifier",
        "Comment and reply drafting",
        "DM drafting",
        "Post-format strategist",
        "Post drafting",
        "Reputation-risk editor",
        "Performance analysis",
        "Approval and receipts",
    ],
    "medium": [
        "Catalog and gap analysis",
        "Scheduled-story and release audit",
        "Source and story opportunity research",
        "Story architecture and visual planning",
        "Editorial, claims, and policy review",
        "Performance and retention audit",
        "Read-through engineering",
        "Distribution and publication fit",
        "Conversation research and response drafting",
        "Growth experiment planning",
        "Approval, receipts, and reporting",
    ],
    "shared": [
        "Content intelligence graph",
        "Evidence supply chain",
        "Experiment manager",
        "Technical-art director",
        "Portfolio conversion",
    ],
}


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def role_document_errors() -> list[str]:
    errors: list[str] = []
    documents = {
        "linkedin": ROOT / "linkedin" / "agents" / "roles.md",
        "medium": ROOT / "medium" / "agents" / "roles.md",
        "shared": ROOT / "engagement" / "agents" / "README.md",
    }
    for platform, path in documents.items():
        text = path.read_text(encoding="utf-8") if path.is_file() else ""
        for label in EXPECTED_ROLE_LABELS[platform]:
            if label not in text:
                errors.append(f"{path.relative_to(ROOT)} is missing the {label!r} role contract")
    return errors


def policy_errors() -> list[str]:
    errors: list[str] = []
    checks = {
        ROOT / "linkedin" / "agents" / "policy.md": [
            "never post, comment, reply, message, react, follow, connect, repost, publish, or schedule without exact action-time user approval",
            "Do not retain private conversation text",
        ],
        ROOT / "medium" / "agents" / "policy.md": [
            "never publish, schedule, send subscriber email, materially edit a public story, submit to a publication, respond, clap, highlight, follow, or change a paywall/profile without exact action-time user approval",
            "Do not automate or optimize for volume of Medium interactions",
        ],
        ROOT / "engagement" / "agents" / "policy.md": [
            "Do not create a daemon, a third schedule, an API service, or another signed-in browser session",
            "exact, source-specific, visible to the user, and separately approved at action time",
        ],
    }
    for path, required_fragments in checks.items():
        text = path.read_text(encoding="utf-8") if path.is_file() else ""
        for fragment in required_fragments:
            if fragment not in text:
                errors.append(f"{path.relative_to(ROOT)} is missing a required safety control")
    return errors


def runbook_errors() -> list[str]:
    errors: list[str] = []
    checks = {
        ROOT / "linkedin" / "agents" / "runbooks" / "two-hourly-cycle.md": [
            "idle-first gate",
            "approval queue is at capacity",
            "no action is recommended",
        ],
        ROOT / "medium" / "agents" / "runbooks" / "overnight-cycle.md": [
            "idle-first gate",
            "Inspect **every scheduled story**",
            "no action is recommended",
        ],
    }
    for path, required_fragments in checks.items():
        text = path.read_text(encoding="utf-8") if path.is_file() else ""
        for fragment in required_fragments:
            if fragment not in text:
                errors.append(f"{path.relative_to(ROOT)} is missing {fragment!r}")
    return errors


def decide(case: dict[str, Any]) -> str:
    """Apply the repository's deterministic guardrails to one fixture."""

    platform = case.get("platform")
    scenario = case.get("scenario")
    if scenario == "idle":
        return "quiet_status"
    if scenario == "discovery_request":
        return "quiet_status" if case.get("approvalQueueAtCapacity") else "research"
    if scenario == "scheduled_story_audit":
        return "audit_only"
    if scenario == "qualified_candidate":
        if (
            case.get("score", 0) < 0.70
            or case.get("sourceSpecific") is not True
            or case.get("duplicate") is True
            or case.get("exactDraft") is not True
            or (platform == "linkedin" and case.get("awaitingInboundReply") is True)
        ):
            return "reject"
        return "approval_brief"
    if scenario == "retention_check":
        views = case.get("views", 0)
        reads = case.get("reads", 0)
        hours = case.get("hoursSincePublication", 0)
        if views < 20 or hours < 168:
            return "observe_until_checkpoint"
        return "approval_brief" if reads / views < 0.20 else "observe_until_checkpoint"
    if scenario == "story_brief":
        return "reject" if case.get("primarySources", 0) > 5 else "research"
    if scenario == "claim_review":
        return "evidence_ready" if case.get("primaryEvidence") is True else "evidence_gap"
    if scenario == "experiment":
        complete = all(case.get(key) is True for key in ("hasMetric", "hasDecisionThreshold", "hasCheckpoint"))
        return "experiment_packet" if complete else "reject"
    return "reject"


def matrix_errors() -> tuple[list[str], list[dict[str, Any]]]:
    matrix = load_json(MATRIX_PATH)
    errors: list[str] = []
    results: list[dict[str, Any]] = []
    if matrix.get("schemaVersion") != 1 or not isinstance(matrix.get("cases"), list):
        return ["dry-run matrix must have schemaVersion 1 and a cases array"], results
    for case in matrix["cases"]:
        if not isinstance(case, dict) or not isinstance(case.get("id"), str):
            errors.append("dry-run matrix contains an invalid case")
            continue
        observed = decide(case)
        expected = case.get("expectedDisposition")
        passed = observed == expected and case.get("expectedExternalAction") is False and case.get("expectedExternalSources") == 0
        results.append({"id": case["id"], "observedDisposition": observed, "expectedDisposition": expected, "passed": passed})
        if observed != expected:
            errors.append(f"{case['id']}: expected {expected}, observed {observed}")
        if case.get("expectedExternalAction") is not False:
            errors.append(f"{case['id']}: fixture must prohibit external action")
        if case.get("expectedExternalSources") != 0:
            errors.append(f"{case['id']}: fixture must use zero external sources")
    return errors, results


def automation_errors(config_path: Path, strategy: dict[str, Any]) -> list[str]:
    """Validate the local heartbeat contract without persisting its private runtime state."""

    errors: list[str] = []
    text = config_path.read_text(encoding="utf-8")
    rrule = re.search(r'^rrule = "([^"]+)"$', text, flags=re.MULTILINE)
    if not rrule:
        return ["automation config has no readable schedule"]
    hours_match = re.search(r"BYHOUR=([^;]+)", rrule.group(1))
    observed_hours = sorted(int(hour) for hour in hours_match.group(1).split(",")) if hours_match else []
    expected_hours = sorted(set(strategy["linkedinAgentSystem"]["scheduledHoursIST"] + strategy["mediumAgentSystem"]["scheduledHoursIST"]))
    if observed_hours != expected_hours:
        errors.append("automation schedule does not match the protected LinkedIn and Medium hours")
    if 'status = "ACTIVE"' not in text:
        errors.append("automation is not active")
    required_fragments = [
        "five shared roles",
        "approved thirteen-role workflow",
        "approved eleven-role workflow",
        "obtaining action-time user confirmation",
        "No OpenAI API",
    ]
    for fragment in required_fragments:
        if fragment not in text:
            errors.append(f"automation prompt is missing {fragment!r}")
    return errors


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--automation-config", type=Path, help="Optional local heartbeat TOML to validate without copying it into the repository.")
    parser.add_argument("--output", type=Path, help="Optional JSON result path.")
    args = parser.parse_args()

    strategy = load_json(STRATEGY_PATH)
    errors = role_document_errors() + policy_errors() + runbook_errors()
    matrix_validation_errors, results = matrix_errors()
    errors.extend(matrix_validation_errors)
    if args.automation_config:
        errors.extend(automation_errors(args.automation_config, strategy))

    report = {
        "schemaVersion": 1,
        "mode": "deterministic_no_browser_no_model",
        "cases": results,
        "passed": not errors,
        "errors": errors,
    }
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    if errors:
        raise SystemExit("agent dry-run validation failed:\n- " + "\n- ".join(errors))
    print(f"validated agent dry run: {len(results)} control cases, zero browser calls, zero model calls")


if __name__ == "__main__":
    main()
