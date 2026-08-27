#!/usr/bin/env python3
"""Build reviewable Phase 2 Medium drafts from canonical stories and edit packages."""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
STORIES = ROOT / "stories"
PACKAGES = ROOT / "editorial" / "phase-2"
OUTPUT = PACKAGES / "drafts"


@dataclass(frozen=True)
class SectionSpec:
    heading: str
    before_subheading: str | None = None


@dataclass(frozen=True)
class DraftSpec:
    slug: str
    core: tuple[SectionSpec, ...]
    deep: tuple[SectionSpec, ...]
    deep_transition_figure: int | None = None


SPECS = (
    DraftSpec(
        slug="human-approval-is-a-queueing-system",
        core=(
            SectionSpec("Build an approval decision service"),
            SectionSpec("Decompose action-level risk"),
            SectionSpec("Review only when it changes the constrained decision"),
            SectionSpec("Create explicit service classes"),
            SectionSpec("Queueing theory reveals the saturation cliff", "Priority scheduling is a risk policy"),
            SectionSpec("Eligibility routing fragments capacity"),
            SectionSpec("Enforce separation of duties"),
            SectionSpec("The approval packet is a decision instrument"),
        ),
        deep=(
            SectionSpec("Optimize thresholds under capacity and risk constraints"),
            SectionSpec("Shadow review calibrates the boundary"),
        ),
        deep_transition_figure=1,
    ),
    DraftSpec(
        slug="your-multi-agent-system-is-a-distributed-system",
        core=(
            SectionSpec("Invariants are the real multi-agent interface"),
            SectionSpec("A lease is temporary ownership, not proof of exclusivity"),
            SectionSpec("Fencing makes ownership enforceable"),
            SectionSpec("Transport semantics do not guarantee business semantics"),
            SectionSpec("Build an idempotency ledger, not a cache"),
            SectionSpec("Concurrent agents create lost-update races"),
            SectionSpec("Cross-domain work is a saga, not a giant transaction"),
            SectionSpec("Recovery follows dependencies and customer impact"),
        ),
        deep=(SectionSpec("Chaos tests must assert business invariants"),),
        deep_transition_figure=1,
    ),
    DraftSpec(
        slug="model-routing-is-capital-allocation",
        core=(
            SectionSpec("Build a routing control plane"),
            SectionSpec("Account for the completed workflow", "Reconcile technical telemetry to financial truth"),
            SectionSpec("Optimize risk-adjusted utility"),
            SectionSpec("Add business loss before selecting the frontier"),
            SectionSpec("Filter policy before scoring economics"),
            SectionSpec("Calibrate predicted suitability"),
            SectionSpec("Detect unsupported requests and abstain"),
            SectionSpec("Allocate verification where it reduces loss"),
        ),
        deep=(SectionSpec("Evaluate counterfactual policy honestly", "Build an investment-grade evaluation dossier"),),
        deep_transition_figure=1,
    ),
    DraftSpec(
        slug="your-ai-agent-needs-a-real-kill-switch",
        core=(
            SectionSpec("Define what “stopped” means"),
            SectionSpec("Build independent containment layers"),
            SectionSpec("Revoke the entire authority graph"),
            SectionSpec("Fence stale workers with epochs"),
            SectionSpec("Drain by action state, not process state"),
            SectionSpec("Build the in-flight inventory", "Preserve evidence outside the compromised workload"),
            SectionSpec("Never retry an ambiguous effect blindly"),
            SectionSpec("Recovery is a fresh authorization event"),
        ),
        deep=(
            SectionSpec("Budget the time to stop"),
            SectionSpec("Model the business blast radius"),
        ),
        deep_transition_figure=1,
    ),
    DraftSpec(
        slug="do-not-let-an-ai-agent-touch-production-until-it-passes-this-evaluation",
        core=(
            SectionSpec("Define the deployment contract first"),
            SectionSpec("Build a governed evaluation plane", "Govern evaluation data as production evidence"),
            SectionSpec("Turn readiness into a claim graph"),
            SectionSpec("Design scenarios as trajectories"),
            SectionSpec("Make coverage visible"),
            SectionSpec("Specify executable test contracts"),
            SectionSpec("Use a metric hierarchy", "Diagnose the full trajectory"),
            SectionSpec("Inject failures throughout the system"),
            SectionSpec("Build stateful tool simulators"),
            SectionSpec("Convert adversarial testing into regression evidence"),
            SectionSpec("Use shadow mode without granting authority"),
            SectionSpec("Expand canary authority on multiple axes"),
        ),
        deep=(
            SectionSpec("Put uncertainty into the release decision"),
            SectionSpec("Treat zero observed failures honestly"),
            SectionSpec("Detect drift and expire evidence"),
            SectionSpec("Make promotion a machine-enforced gate"),
            SectionSpec("Operate evaluation with service objectives"),
            SectionSpec("Roll out evaluation maturity with authority"),
        ),
        deep_transition_figure=1,
    ),
)


def split_frontmatter(text: str) -> tuple[str, str]:
    match = re.match(r"\A(---\n.*?\n---\n)(.*)\Z", text, flags=re.S)
    if not match:
        raise ValueError("story is missing YAML frontmatter")
    return match.group(1).rstrip(), match.group(2).strip()


def sections(text: str) -> dict[str, str]:
    matches = list(re.finditer(r"(?m)^## (.+)$", text))
    result: dict[str, str] = {}
    for index, match in enumerate(matches):
        end = matches[index + 1].start() if index + 1 < len(matches) else len(text)
        result[match.group(1).strip()] = text[match.start():end].strip()
    return result


def package_section(text: str, heading: str) -> str:
    match = re.search(
        rf"(?ms)^## {re.escape(heading)}\n\n(.*?)(?=^## |\Z)",
        text,
    )
    if not match:
        raise ValueError(f"package section not found: {heading}")
    return match.group(1).strip()


def select_section(source_sections: dict[str, str], spec: SectionSpec) -> str:
    value = source_sections[spec.heading]
    if spec.before_subheading:
        marker = f"\n### {spec.before_subheading}"
        if marker not in value:
            raise ValueError(f"subheading not found in {spec.heading}: {spec.before_subheading}")
        value = value.split(marker, 1)[0].rstrip()
    return value


def find_figure(text: str, number: int) -> str:
    pattern = rf"(?m)^!\[[^\n]+\]\(assets/images/[^\n]+/figure-{number:02d}\.png[^\n]*\)$"
    match = re.search(pattern, text)
    if not match:
        raise ValueError(f"figure-{number:02d}.png not found")
    return match.group(0)


def without_figure(text: str, number: int) -> str:
    pattern = rf"(?m)^!\[[^\n]+\]\(assets/images/[^\n]+/figure-{number:02d}\.png[^\n]*\)\n?"
    return re.sub(pattern, "", text).strip()


def article_heading(title: str) -> str:
    return f"# {title}"


def title_from_frontmatter(frontmatter: str) -> str:
    match = re.search(r'(?m)^title: "(.+)"$', frontmatter)
    if not match:
        raise ValueError("title missing from frontmatter")
    return match.group(1)


def build(spec: DraftSpec) -> Path:
    source_path = STORIES / f"{spec.slug}.md"
    package_path = PACKAGES / f"{spec.slug}.md"
    source_text = source_path.read_text(encoding="utf-8")
    frontmatter, source_body = split_frontmatter(source_text)

    # Once an approved Phase 2 draft becomes canonical, keep this builder
    # idempotent by deriving the review copy directly from that exact body.
    # The longer source sections used for the first reduction no longer exist
    # in the canonical file after promotion.
    if "## Decision table" in source_body and "## Technical deep dive" in source_body:
        output_text = f"{frontmatter}\n\n{source_body.replace('](assets/', '](../../../assets/')}\n"
        OUTPUT.mkdir(parents=True, exist_ok=True)
        output_path = OUTPUT / f"{spec.slug}.md"
        output_path.write_text(output_text, encoding="utf-8")
        return output_path

    package_text = package_path.read_text(encoding="utf-8")
    source_sections = sections(source_body)
    title = title_from_frontmatter(frontmatter)

    opening = package_section(package_text, "Decision-oriented opening")
    production = package_section(package_text, "What this changes in production")
    decision_table = package_section(package_text, "Compact decision table")
    checklist = package_section(package_text, "Implementation checklist")
    related = package_section(package_text, "Related stories and CTA")
    first_figure = find_figure(source_body, 2)
    deep_transition_figure = (
        find_figure(source_body, spec.deep_transition_figure)
        if spec.deep_transition_figure is not None
        else ""
    )

    core = [without_figure(select_section(source_sections, item), 2) for item in spec.core]
    deep = [without_figure(select_section(source_sections, item), 2) for item in spec.deep]

    body_parts = [
        article_heading(title),
        opening,
        first_figure,
        "## What this changes in production",
        production,
        "## Decision table",
        decision_table,
        *core,
        "## Technical deep dive",
        "The following sections retain the quantitative and systems detail for readers implementing the control plane.",
        deep_transition_figure,
        *deep,
        "## Production implementation checklist",
        checklist,
        "## Continue the Production AI Control Plane series",
        related,
    ]
    body = "\n\n".join(part.strip() for part in body_parts if part.strip())
    body = body.replace("](assets/", "](../../../assets/")
    output_text = f"{frontmatter}\n\n{body}\n"

    OUTPUT.mkdir(parents=True, exist_ok=True)
    output_path = OUTPUT / f"{spec.slug}.md"
    output_path.write_text(output_text, encoding="utf-8")
    return output_path


def main() -> None:
    outputs = [build(spec) for spec in SPECS]
    for path in outputs:
        words = len(path.read_text(encoding="utf-8").split())
        print(f"{path.relative_to(ROOT)}\t{words} words")


if __name__ == "__main__":
    main()
