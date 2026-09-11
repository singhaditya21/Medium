#!/usr/bin/env python3
"""Offline checks for the pinned, Chrome-only LinkedIn skill installation.

Checks packaging and execution boundaries, not account access or editorial quality.
It never imports or runs code from the third-party skill bundle.
"""

from __future__ import annotations

import ast
import json
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
AGENTS = ROOT / ".agents"
NAMES = {
    "linkedin-comment-drafter", "linkedin-content-planner",
    "linkedin-employee-advocacy", "linkedin-engager-analytics",
    "linkedin-hook-extractor", "linkedin-humanizer", "linkedin-post-writer",
    "linkedin-profile-optimizer", "linkedin-reply-handler",
    "linkedin-repurposer", "linkedin-thread-monitor",
}
PIN = "c2864552259486aea10427d559b359226123504f"


def validate() -> list[str]:
    errors: list[str] = []
    entries = sorted((AGENTS / "skills").glob("*/SKILL.md"))
    if {entry.parent.name for entry in entries} != NAMES:
        errors.append("The 11 expected LinkedIn skill entrypoints do not match")
    contract_path = AGENTS / "LINKEDIN-INTEGRATION.md"
    if not contract_path.is_file() or PIN not in contract_path.read_text():
        errors.append("Pinned source provenance is missing")
    for required in (ROOT / "AGENTS.md", AGENTS / "SKILL.md",
                     AGENTS / "LICENSE.linkedin-skills"):
        if not required.is_file():
            errors.append(f"Missing {required.relative_to(ROOT)}")

    for entry in entries:
        content = entry.read_text()
        match = re.match(r"^---\nname: ([a-z0-9-]+)\ndescription: (.+)\n---\n", content)
        if not match or match.group(1) != entry.parent.name:
            errors.append(f"Invalid name/frontmatter: {entry.parent.name}")
            continue
        try:
            description = json.loads(match.group(2))
            if not isinstance(description, str) or not 1 <= len(description) <= 510:
                errors.append(f"Invalid description: {entry.parent.name}")
        except json.JSONDecodeError:
            errors.append(f"Description must be a valid quoted string: {entry.parent.name}")
        banner = content.split("## Upstream editorial guidance", 1)[0]
        if "../../LINKEDIN-INTEGRATION.md" not in banner:
            errors.append(f"Missing local contract routing: {entry.parent.name}")
        refs = set(re.findall(
            r"(?<![\w/])((?:\.\./)*(?:references|sub-skills)/[\w./-]+\.md)", content
        ))
        for ref in refs:
            target = (entry.parent / ref).resolve()
            if not target.is_relative_to(AGENTS) or not target.is_file():
                errors.append(f"Broken/escaping reference: {entry.parent.name}: {ref}")

    # The only executable bundled with the upstream leaves is replaced with an
    # unconditional SystemExit. Validate its complete AST without executing it.
    expected_runner = AGENTS / "skills/linkedin-humanizer/scripts/test_detectors.py"
    python_files = set((AGENTS / "skills").rglob("*.py"))
    if python_files != {expected_runner}:
        errors.append("Unexpected executable Python files in the skill bundle")
    if expected_runner.is_file():
        tree = ast.parse(expected_runner.read_text())
        statements = tree.body
        if statements and isinstance(statements[0], ast.Expr) and isinstance(
            statements[0].value, ast.Constant
        ) and isinstance(statements[0].value.value, str):
            statements = statements[1:]
        valid_stub = (
            len(statements) == 1 and isinstance(statements[0], ast.Raise)
            and isinstance(statements[0].exc, ast.Call)
            and isinstance(statements[0].exc.func, ast.Name)
            and statements[0].exc.func.id == "SystemExit"
            and len(statements[0].exc.args) == 1
            and isinstance(statements[0].exc.args[0], ast.Constant)
            and isinstance(statements[0].exc.args[0].value, str)
            and not statements[0].exc.keywords and statements[0].cause is None
        )
        if not valid_stub:
            errors.append("Detector runner is not a side-effect-free fail-closed stub")

    for path in AGENTS.rglob("*"):
        if path.name in {".git", ".env", "lib", "node_modules", ".venv"}:
            errors.append(f"Unexpected service/state path: {path.relative_to(ROOT)}")
        if path.is_file() and path.suffix in {".sh", ".js", ".ts"}:
            errors.append(f"Unexpected executable helper: {path.relative_to(ROOT)}")
    for filename in ("requirements.txt", "detectors.env.example"):
        path = expected_runner.parent / filename
        if any(line.strip() and not line.lstrip().startswith("#")
               for line in path.read_text().splitlines()):
            errors.append(f"External dependency or key configuration remains: {filename}")

    strategy = json.loads((ROOT / "engagement/strategy.json").read_text())
    for platform, hours in (("linkedin", [22, 0, 2, 4, 6]),
                            ("medium", [23, 1, 3, 5, 7])):
        system = strategy[f"{platform}AgentSystem"]
        if system["scheduledHoursIST"] != hours or system["usesOpenAIAPI"] is not False:
            errors.append(f"{platform} cadence/API boundary changed")
        if system["executionMode"] != "research_and_prepare_only":
            errors.append(f"{platform} research-only mode changed")
    policy = strategy["automationPolicy"]
    if policy["publishPublicInteractionsAutomatically"] is not False:
        errors.append("Automatic public interactions must remain disabled")
    if policy["requireExactActionTimeConfirmation"] is not True:
        errors.append("Exact action-time confirmation must remain required")
    if policy["storeCredentialsOrBrowserState"] is not False:
        errors.append("Credentials/browser-state storage must remain disabled")
    return errors


if __name__ == "__main__":
    failures = validate()
    if failures:
        print("\n".join(f"ERROR: {failure}" for failure in failures))
        sys.exit(1)
    print("Validated 11 local LinkedIn skills: frontmatter, references, pinned "
          "provenance, disabled detector runner, unchanged schedules and approvals. "
          "Live Chrome access is not tested by this check.")
