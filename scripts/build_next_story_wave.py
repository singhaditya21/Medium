#!/usr/bin/env python3
"""Build the September 2026 control-plane story draft wave and its diagrams."""

from __future__ import annotations

import hashlib
import json
import textwrap
from html import escape
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
IMAGES = ROOT / "assets" / "images"
EDITORIAL = ROOT / "editorial" / "next-wave"
SITE = "https://singhaditya21.github.io/Medium/articles"
CREATED = "2026-09-03T12:00:00.000Z"


def p(text: str) -> dict:
    return {"type": "html", "tag": "p", "html": text, "text": strip_html(text)}


def h2(text: str) -> dict:
    return {"type": "html", "tag": "h2", "html": text, "text": text}


def quote(text: str) -> dict:
    return {"type": "html", "tag": "blockquote", "html": text, "text": strip_html(text)}


def pre(text: str, language: str = "text") -> dict:
    return {"type": "html", "tag": "pre", "html": "", "text": text.strip(), "language": language}


def table(headers: list[str], rows: list[list[str]]) -> dict:
    return {"type": "table", "headers": headers, "rows": rows}


def strip_html(value: str) -> str:
    import re
    return re.sub(r"<[^>]+>", "", value).replace("&lt;", "<").replace("&gt;", ">").replace("&amp;", "&")


def wrap(value: str, width: int = 26) -> list[str]:
    return textwrap.wrap(value, width=width, break_long_words=False) or [value]


def text_lines(x: int, y: int, value: str, *, size: int = 26, weight: int = 600, color: str = "#0d2425", width: int = 28, line: int = 34) -> str:
    lines = wrap(value, width)
    return "".join(
        f'<text x="{x}" y="{y + i * line}" font-size="{size}" font-weight="{weight}" fill="{color}">{escape(part)}</text>'
        for i, part in enumerate(lines)
    )


def architecture_svg(story: dict, path: Path) -> None:
    nodes = story["architecture_nodes"]
    colors = ["#dff4ef", "#e8efff", "#fff1d6", "#f2e9ff", "#e7f2fa", "#ffe7e2"]
    parts = [
        '<svg xmlns="http://www.w3.org/2000/svg" width="1600" height="1000" viewBox="0 0 1600 1000" role="img">',
        '<defs><marker id="arrow" markerWidth="10" markerHeight="10" refX="9" refY="3" orient="auto"><path d="M0,0 L0,6 L9,3 z" fill="#2a6f68"/></marker><filter id="shadow"><feDropShadow dx="0" dy="8" stdDeviation="12" flood-opacity=".12"/></filter></defs>',
        '<rect width="1600" height="1000" fill="#f8faf9"/>',
        '<rect x="50" y="42" width="1500" height="136" rx="22" fill="#0d2425"/>',
        text_lines(88, 95, story["title"], size=40, weight=760, color="#ffffff", width=55, line=48),
        text_lines(90, 153, "REFERENCE ARCHITECTURE · CONTROL AND EVIDENCE PATH", size=19, weight=650, color="#9fe1d5", width=80),
    ]
    positions = [(90, 250), (565, 250), (1040, 250), (90, 590), (565, 590), (1040, 590)]
    for i, node in enumerate(nodes):
        x, y = positions[i]
        if i in (0, 1, 3, 4):
            nx, ny = positions[i + 1]
            parts.append(f'<line x1="{x+390}" y1="{y+115}" x2="{nx-25}" y2="{ny+115}" stroke="#2a6f68" stroke-width="5" marker-end="url(#arrow)"/>')
        if i == 2:
            nx, ny = positions[3]
            parts.append(f'<path d="M {x+195} {y+240} C {x+195} {y+300}, {nx+195} {ny-70}, {nx+195} {ny-18}" fill="none" stroke="#2a6f68" stroke-width="5" marker-end="url(#arrow)"/>')
        parts.append(f'<rect x="{x}" y="{y}" width="390" height="230" rx="24" fill="{colors[i]}" stroke="#b7cbc7" stroke-width="2" filter="url(#shadow)"/>')
        parts.append(f'<circle cx="{x+48}" cy="{y+48}" r="25" fill="#0d2425"/><text x="{x+39}" y="{y+57}" font-size="24" font-weight="750" fill="#fff">{i+1}</text>')
        parts.append(text_lines(x+88, y+48, node[0], size=27, weight=750, width=20, line=32))
        parts.append(text_lines(x+35, y+132, node[1], size=21, weight=520, color="#34514e", width=35, line=29))
    parts.append('<rect x="90" y="880" width="1410" height="70" rx="18" fill="#ffffff" stroke="#cad8d5"/><text x="125" y="925" font-size="23" font-weight="650" fill="#0d2425">DESIGN RULE</text>')
    parts.append(text_lines(320, 924, story["design_rule"], size=22, weight=580, color="#234b47", width=88, line=26))
    parts.append('</svg>')
    path.write_text("".join(parts), encoding="utf-8")


def flow_svg(story: dict, path: Path) -> None:
    states = story["flow_states"]
    parts = [
        '<svg xmlns="http://www.w3.org/2000/svg" width="1600" height="1000" viewBox="0 0 1600 1000" role="img">',
        '<defs><marker id="a" markerWidth="10" markerHeight="10" refX="9" refY="3" orient="auto"><path d="M0,0 L0,6 L9,3 z" fill="#1f6d65"/></marker></defs>',
        '<rect width="1600" height="1000" fill="#fbfaf7"/>',
        text_lines(72, 76, story["flow_title"], size=42, weight=760, width=58, line=48),
        text_lines(74, 145, story["flow_subtitle"], size=23, weight=500, color="#526562", width=90),
        '<rect x="70" y="210" width="1460" height="610" rx="28" fill="#ffffff" stroke="#cad8d5" stroke-width="2"/>',
    ]
    xs = [120, 475, 830, 1185]
    ys = [270, 555]
    for i, state in enumerate(states):
        row, col = divmod(i, 4)
        x, y = xs[col], ys[row]
        if i < len(states)-1:
            if col < 3:
                parts.append(f'<line x1="{x+265}" y1="{y+86}" x2="{xs[col+1]-28}" y2="{y+86}" stroke="#1f6d65" stroke-width="5" marker-end="url(#a)"/>')
            else:
                parts.append(f'<path d="M {x+132} {y+172} C {x+132} {y+230}, {xs[0]+132} {ys[1]-65}, {xs[0]+132} {ys[1]-22}" fill="none" stroke="#1f6d65" stroke-width="5" marker-end="url(#a)"/>')
        fill = "#0d2425" if i in (0, len(states)-1) else "#e8f3f0"
        color = "#ffffff" if i in (0, len(states)-1) else "#0d2425"
        parts.append(f'<rect x="{x}" y="{y}" width="265" height="172" rx="22" fill="{fill}" stroke="#2a6f68" stroke-width="2"/>')
        parts.append(text_lines(x+28, y+52, state[0], size=25, weight=740, color=color, width=16, line=30))
        parts.append(text_lines(x+28, y+118, state[1], size=18, weight=500, color=("#cce9e3" if color == "#ffffff" else "#3b5b57"), width=24, line=24))
    parts.append('<rect x="70" y="855" width="1460" height="92" rx="20" fill="#fff0d3" stroke="#dfbe70"/>')
    parts.append(text_lines(108, 902, story["flow_guard"], size=23, weight=650, color="#6b4b11", width=92, line=29))
    parts.append('</svg>')
    path.write_text("".join(parts), encoding="utf-8")


def scorecard_svg(story: dict, path: Path) -> None:
    metrics = story["metrics"]
    parts = [
        '<svg xmlns="http://www.w3.org/2000/svg" width="1600" height="1000" viewBox="0 0 1600 1000" role="img">',
        '<rect width="1600" height="1000" fill="#f6f8fb"/>',
        '<rect x="55" y="48" width="1490" height="125" rx="24" fill="#10233f"/>',
        text_lines(90, 100, story["scorecard_title"], size=40, weight=760, color="#ffffff", width=56, line=46),
        text_lines(92, 154, "ILLUSTRATIVE OPERATING GATE · REPLACE WITH MEASURED PRODUCTION EVIDENCE", size=18, weight=650, color="#a8c9ff", width=92),
        '<text x="85" y="244" font-size="20" font-weight="700" fill="#536579">METRIC</text><text x="820" y="244" font-size="20" font-weight="700" fill="#536579">OBSERVED</text><text x="1085" y="244" font-size="20" font-weight="700" fill="#536579">TARGET</text><text x="1355" y="244" font-size="20" font-weight="700" fill="#536579">GATE</text>',
    ]
    for i, metric in enumerate(metrics):
        y = 275 + i * 124
        bg = "#ffffff" if i % 2 == 0 else "#edf2f7"
        gate_color = "#b42318" if metric[3] == "BREACH" else "#067647"
        gate_bg = "#fee4e2" if metric[3] == "BREACH" else "#dcfae6"
        parts.append(f'<rect x="70" y="{y}" width="1460" height="100" rx="18" fill="{bg}" stroke="#dbe3ea"/>')
        parts.append(text_lines(96, y+58, metric[0], size=24, weight=650, width=43, line=27))
        parts.append(text_lines(820, y+58, metric[1], size=25, weight=720, color="#10233f", width=15, line=28))
        parts.append(text_lines(1085, y+58, metric[2], size=24, weight=620, color="#3d536b", width=16, line=28))
        parts.append(f'<rect x="1340" y="{y+25}" width="145" height="50" rx="25" fill="{gate_bg}"/><text x="{1372 if metric[3]=="PASS" else 1361}" y="{y+59}" font-size="21" font-weight="780" fill="{gate_color}">{metric[3]}</text>')
    parts.append('<rect x="70" y="905" width="1460" height="52" rx="14" fill="#ffffff" stroke="#dbe3ea"/><text x="95" y="939" font-size="18" font-weight="560" fill="#536579">Synthetic values test the decision rule; they are not account performance claims.</text>')
    parts.append('</svg>')
    path.write_text("".join(parts), encoding="utf-8")


def figure(slug: str, number: int, alt: str, caption: str) -> dict:
    return {
        "type": "figure",
        "src": f"assets/images/{slug}/figure-{number:02d}.svg",
        "alt": alt,
        "caption": f"Figure {number}. {caption} AI-assisted editorial architecture diagram; illustrative values; not production data.",
    }


def story_blocks(story: dict) -> list[dict]:
    slug = story["slug"]
    blocks = [
        p("This story was developed with AI writing and visualization assistance. All incidents, thresholds, workloads, and operating values are illustrative unless a source is explicitly cited."),
        p(story["hook"][0]),
        p(story["hook"][1]),
        quote(story["thesis"]),
        figure(slug, 1, story["figure_alts"][0], story["figure_captions"][0]),
        h2(story["failure_heading"]),
        *[p(item) for item in story["failure"]],
        h2(story["architecture_heading"]),
        *[p(item) for item in story["architecture"]],
        figure(slug, 2, story["figure_alts"][1], story["figure_captions"][1]),
        h2(story["model_heading"]),
        p(story["model_intro"]),
        pre(story["formula"]),
        p(story["model_explanation"]),
        table(story["control_table"][0], story["control_table"][1]),
        h2(story["contract_heading"]),
        p(story["contract_intro"]),
        pre(story["code"], story["code_language"]),
        p(story["contract_explanation"]),
        h2(story["operations_heading"]),
        *[p(item) for item in story["operations"]],
        figure(slug, 3, story["figure_alts"][2], story["figure_captions"][2]),
        table(["Operating signal", "Decision use", "Failure interpretation"], story["metrics_table"]),
        h2("Failure-injection before production"),
        p(
            f"A design review cannot prove <strong>{story['design_rule']}</strong> The pre-production harness must interrupt the system at the transitions where ownership, authority, evidence, and business state can disagree. The objective is not to maximize a generic pass rate. It is to demonstrate that every material fault produces a bounded state, a named owner, and an admissible recovery transition."
        ),
        table(
            ["Injected fault", "Experiment", "Required evidence"],
            [
                ["Delayed or reordered work", f"Pause the path after {story['flow_states'][1][0]} and release it after {story['flow_states'][4][0]}", "The stale path cannot manufacture terminal success"],
                ["Authority becomes stale", "Advance policy, mode, ownership, or resource version before effect commit", "The final gateway rejects the old decision context"],
                ["Evidence is missing or corrupted", "Remove one authoritative observation or change its digest", "The outcome remains violated, inconclusive, or owned—never guessed"],
                ["Recovery itself fails", "Interrupt compensation, handoff, or receipt closure", "The action stays visible with an owner, deadline, and next legal transition"],
            ],
        ),
        p(
            "Run the matrix at concurrency, with realistic dependency lag and with the same policy and gateway versions used in the candidate release. Report p95 and p99 resolution alongside the worst unresolved example. Averages can demonstrate throughput; they cannot erase a single material breach. Promotion should require replayable evidence for the controls, not a slide stating that the team considered the risk."
        ),
        h2("Three questions for the architecture review"),
        p("<strong>Where is truth decided?</strong> Name the authoritative source and the exact component permitted to advance the workflow into a terminal state. If the answer is ‘the agent interprets the tool response,’ the boundary is not yet independent."),
        p("<strong>Where is authority finally enforced?</strong> Follow the command through every queue, adapter, cache, provider, and downstream effect. A policy decision is useful only when the last material write boundary can reject a stale, changed, or excessive action."),
        p("<strong>What blocks promotion?</strong> Convert the scorecard into executable gates with owners and expiry. A breached tail metric must reduce scope, hold the cohort, or enter an approved exception path; it cannot remain decorative telemetry."),
        h2("A practical implementation sequence"),
        *[p(f"<strong>{i+1}. {step[0]}</strong> {step[1]}") for i, step in enumerate(story["implementation"])],
        h2("Primary references and boundaries"),
        p(story["references"]),
        p(story["boundary"]),
        h2("The operating conclusion"),
        p(story["conclusion"]),
        quote(story["question"]),
    ]
    return blocks


STORIES = [
    {
        "slug": "your-ai-agent-needs-a-transaction-boundary",
        "title": "Your AI Agent Needs a Transaction Boundary",
        "subtitle": "How idempotency, version checks, durable intent, and compensation keep one plan from becoming several business effects.",
        "description": "A production blueprint for binding AI-agent intent to one durable transaction across prepare, authorize, execute, verify, and compensate phases.",
        "tags": ["AI agents", "Distributed systems", "Transactions", "Enterprise architecture", "Reliability"],
        "hook": [
            "An agent approves one concession, calls one CRM API, times out once, retries once, and creates two downstream credits. Every model response can be reasonable while the business result is wrong.",
            "The defect is not primarily linguistic. The system let a probabilistic planner cross a transactional boundary without a stable action identity, a version precondition, or a durable record of whether the first effect committed. A production agent needs a transaction protocol around its tools, even when the underlying business systems cannot participate in one database transaction.",
        ],
        "thesis": "The agent may propose a transaction. It must not be the component that decides whether an ambiguous transaction happened, retries it, and certifies its own result.",
        "failure_heading": "The dangerous state is neither success nor failure",
        "failure": [
            "Remote calls have a third outcome: <strong>unknown</strong>. A client can lose the response after the server commits. Treating that timeout as failure causes a duplicate; treating it as success may conceal a rejected action. The workflow must preserve ambiguity as a first-class state until authoritative observation resolves it.",
            "A transaction boundary also needs semantic stability. Reusing an idempotency key with a changed amount is not a retry; it is a different intent. The gateway should hash the normalized command and reject the same action identifier when principal, resource, expected version, policy digest, or material payload changes.",
        ],
        "architecture_heading": "Put a durable action coordinator between planning and effects",
        "architecture": [
            "The coordinator stores a prepared intent before it exposes an execution token. It binds the accountable principal, agent workload, target resource, expected version, normalized payload hash, policy decision, approval reference, deadline, and compensation class. The effect gateway then accepts only a current, unused transaction capability.",
            "After the call, an independent observer reads the authoritative postcondition. A matching effect closes the action as committed. A proven absence can permit a policy-controlled retry. A divergent effect enters compensation or manual reconciliation. The planner receives the outcome; it does not manufacture it.",
        ],
        "architecture_nodes": [["Proposal", "Typed intent and expected business delta"], ["Prepare", "Persist action ID, digest and preconditions"], ["Authorize", "Policy and approval bind one capability"], ["Execute", "Effect gateway enforces version and use"], ["Observe", "Independent read resolves business state"], ["Close", "Commit, retry, compensate or freeze"]],
        "design_rule": "Persist intent before authority; observe the effect before declaring success.",
        "flow_title": "Transaction state machine",
        "flow_subtitle": "Ambiguity is retained until authoritative evidence resolves it.",
        "flow_states": [["PROPOSED", "Planner emits typed intent"], ["PREPARED", "Intent and digest durable"], ["AUTHORIZED", "One-use capability issued"], ["EXECUTING", "Gateway holds fencing token"], ["UNKNOWN", "Timeout; do not infer"], ["OBSERVED", "Postcondition independently read"], ["COMPENSATING", "Reverse or reconcile"], ["CLOSED", "Receipt seals terminal state"]],
        "flow_guard": "Retry only after the same-intent digest matches and policy says the observed state permits another attempt.",
        "model_heading": "Price ambiguity, not just failure",
        "model_intro": "For action <code>a</code>, a useful retry decision compares the expected cost of waiting, retrying, and escalating:",
        "formula": "choose d* = argmin_d { C_delay(d) + P_dup(d) × L_dup + P_miss(d) × L_miss + C_review(d) }\nsubject to: digest_same ∧ authority_current ∧ version_valid",
        "model_explanation": "The probabilities are calibrated from gateway and reconciliation evidence, not model confidence. A $5 internal task and a binding $250,000 credit should have different ambiguity deadlines, duplicate-loss estimates, and escalation paths.",
        "control_table": [["Boundary object", "Required field", "Why it exists"], [["Intent", "action_id + payload_digest", "Separates a retry from changed intent"], ["Concurrency", "expected_resource_version", "Rejects stale writes"], ["Authority", "single_use capability + expiry", "Bounds when the effect may occur"], ["Outcome", "observed_postcondition", "Proves business state independently"], ["Recovery", "compensation_class + owner", "Prevents ownerless ambiguity"]]],
        "contract_heading": "Make the gateway contract explicit",
        "contract_intro": "A tool wrapper should require the transaction context rather than accepting an unstructured instruction:",
        "code_language": "json",
        "code": '{\n  "action_id": "act_01K...",\n  "principal": "seller:4821",\n  "resource": "quote:771",\n  "expected_version": 42,\n  "command": {"set_discount_bps": 800},\n  "command_digest": "sha256:...",\n  "authority": {"lease_id": "lease_91", "max_uses": 1},\n  "postcondition": {"discount_bps": 800, "version": 43}\n}',
        "contract_explanation": "The gateway must atomically claim the action identifier before mutation, retain the first result, compare subsequent payload digests, and expose an observation endpoint. An HTTP 200 is transport evidence; the postcondition is business evidence.",
        "operations_heading": "Operate the boundary with tail metrics",
        "operations": [
            "The core SLOs are duplicate-effect rate, stale-version rejection, p95 and p99 ambiguity age, compensation completion, and receipt closure. Mean latency is secondary when the economic exposure sits in a small tail of unresolved actions.",
            "The illustrative scorecard deliberately contains one breach: p99 ambiguity age. A system can achieve zero observed duplicates in a small window and still be unsafe because unresolved actions remain economically live for too long.",
        ],
        "scorecard_title": "Transaction-boundary operating scorecard",
        "metrics": [["Duplicate material effects", "0", "0", "PASS"], ["Stale-version rejects", "100%", "100%", "PASS"], ["p95 ambiguity age", "6.2 min", "≤ 10 min", "PASS"], ["p99 ambiguity age", "27 min", "≤ 15 min", "BREACH"], ["Compensation closed in 4 h", "99.4%", "≥ 99%", "PASS"]],
        "metrics_table": [["Duplicate-effect rate", "Stop autonomy when non-zero for material actions", "Idempotency or reconciliation defect"], ["Ambiguity age by risk", "Escalate before economic deadline", "Unknown effects are accumulating"], ["Version-conflict rate", "Diagnose stale planning and contention", "Evidence-to-execution gap is too long"], ["Compensation completion", "Gate wider rollout", "Recovery is not keeping pace"]],
        "implementation": [["Wrap one material command.", "Choose a single CRM or billing mutation and require action IDs, expected versions, and postconditions."], ["Build the ambiguity ledger.", "Persist unknown outcomes with owners, deadlines, evidence, and allowed next transitions."], ["Prove recovery under fault injection.", "Drop responses after commit, reorder observations, replay requests, and show that the same intent never becomes two effects."]],
        "references": "<a href=\"https://www.rfc-editor.org/rfc/rfc9110.html\">RFC 9110</a> defines HTTP idempotency semantics. AWS's <a href=\"https://aws.amazon.com/builders-library/making-retries-safe-with-idempotent-APIs/\">Making retries safe with idempotent APIs</a> explains client request identifiers, semantic equivalence, and atomic recording. These sources do not prescribe this agent protocol; they support its distributed-systems foundations.",
        "boundary": "This design does not claim a general exactly-once network guarantee. It creates an auditable, domain-specific effect contract using deduplication, concurrency control, observation, and compensation.",
        "conclusion": "Agent reliability begins where generated text ends. If the system cannot distinguish prepared intent, granted authority, attempted execution, observed effect, and completed recovery, it does not have a transaction boundary. It has optimism distributed across APIs.",
        "question": "Which agent action in your estate currently turns a timeout into an unsafe guess?",
        "figure_alts": ["Six-stage AI-agent transaction architecture separating proposal, preparation, authorization, execution, observation, and closure.", "Eight-state transaction flow retaining unknown outcomes until independent observation or compensation closes the action.", "Five-row transaction control scorecard comparing duplicate effects, version rejection, ambiguity age, and compensation targets."],
        "figure_captions": ["The transaction coordinator encloses a probabilistic planner with deterministic authority and effect controls.", "Unknown is a durable state rather than an excuse for an immediate retry.", "Tail ambiguity can breach even when duplicate-effect and compensation measures pass."],
    },
    {
        "slug": "an-agent-retry-is-a-new-risk-decision",
        "title": "An Agent Retry Is a New Risk Decision",
        "subtitle": "Why exponential backoff is insufficient when the first attempt may already have changed the business.",
        "description": "A risk-priced retry architecture for AI agents using semantic idempotency, ambiguity budgets, retry amplification limits, and effect-aware escalation.",
        "tags": ["AI agents", "Reliability", "Retries", "Distributed systems", "Risk management"],
        "hook": [
            "Retries look like resilience because most retry libraries count calls, not consequences. For a read, another attempt may be cheap. For a quote change, refund, outreach message, or access grant, another attempt can be a second decision with a second loss distribution.",
            "An agent therefore should not inherit a generic SDK retry policy at the moment it crosses an effect boundary. The retry controller must know the action semantics, whether the first result is ambiguous, what duplicate and omission would cost, and how much traffic amplification the dependency can absorb.",
        ],
        "thesis": "Backoff protects infrastructure. A risk-aware retry policy protects the business effect.",
        "failure_heading": "Automatic retry hides two independent hazards",
        "failure": [
            "The first hazard is <strong>semantic duplication</strong>: the remote system committed but the acknowledgement disappeared. The second is <strong>load amplification</strong>: correlated agents retry a degraded dependency, increasing contention and extending the outage. Jitter reduces synchronization, but it does not prove whether a material action is safe to repeat.",
            "The controller must separate transport retry from business retry. It may repeat a safe read after backoff. It may replay an idempotent command with the same key and immutable digest. It must reconcile an ambiguous non-idempotent effect or ask an accountable operator before producing a new command.",
        ],
        "architecture_heading": "Route retries through an effect-aware controller",
        "architecture": [
            "The controller classifies each tool contract as safe read, idempotent write, conditionally idempotent write, or non-repeatable effect. It joins dependency health, action exposure, attempt history, action identity, resource version, and remaining deadline into one decision.",
            "A global retry budget caps additional calls across the fleet; a per-action ambiguity budget caps how long the system may remain uncertain. Circuit breakers and load shedding protect the dependency. An effect observer and idempotency ledger protect business state.",
        ],
        "architecture_nodes": [["Classify", "Read, idempotent, conditional or non-repeatable"], ["Sense", "Dependency health and fleet retry pressure"], ["Price", "Duplicate, omission, delay and review loss"], ["Decide", "Retry, reconcile, escalate or abandon"], ["Enforce", "Budget, jitter, token and version guards"], ["Observe", "Close the effect and update calibration"]],
        "design_rule": "A retry is permitted by effect semantics and current risk, not by exception type alone.",
        "flow_title": "Effect-aware retry decision",
        "flow_subtitle": "The same timeout can lead to four different actions.",
        "flow_states": [["TIMEOUT", "First attempt unresolved"], ["CLASSIFY", "Read or material write"], ["MATCH", "Same identity and digest?"], ["SENSE", "Dependency and budget state"], ["RETRY", "Safe, bounded replay"], ["RECONCILE", "Observe before repeat"], ["ESCALATE", "Human owns material ambiguity"], ["CLOSE", "Outcome and evidence sealed"]],
        "flow_guard": "Never create a fresh action ID merely to make an uncertain operation look retryable.",
        "model_heading": "Use a retry utility, not a retry count",
        "model_intro": "For attempt <code>k</code>, retry only when expected incremental utility is positive and hard gates pass:",
        "formula": "U_retry(k) = P_transient(k) × V_recovery\n             - P_duplicate(k) × L_duplicate\n             - C_delay(k) - C_load(k) - C_review_avoided(k)\nretry iff U_retry(k) > 0 ∧ fleet_budget > 0 ∧ semantic_gate = allow",
        "model_explanation": "The decision changes after every attempt. Dependency health, deadline slack, and ambiguity evidence move. A fixed three-retry policy assumes the third call has the same value and risk as the first; consequential workflows rarely satisfy that assumption.",
        "control_table": [["Effect class", "Default response to timeout", "Required evidence"], [["Safe read", "Backoff + jitter", "Dependency health and deadline"], ["Idempotent write", "Replay same key", "Same payload digest"], ["Conditional write", "Observe version, then decide", "Resource state and precondition"], ["Non-repeatable", "Reconcile or escalate", "Authoritative effect observation"]]],
        "contract_heading": "Declare retry semantics in the tool contract",
        "contract_intro": "The orchestration layer should consume machine-readable semantics rather than reverse-engineering endpoint names:",
        "code_language": "yaml",
        "code": "operation: issue_credit\neffect_class: conditional_write\nidempotency:\n  key: action_id\n  immutable_fields: [account_id, amount, currency]\nambiguity:\n  observe: GET /credits/by-action/{action_id}\n  deadline_seconds: 180\nretry:\n  max_attempts: 2\n  requires_same_resource_version: true\n  global_budget_pool: billing-material-writes",
        "contract_explanation": "The declaration belongs under version control and must be tested against the actual provider behavior. A nominal idempotency field is insufficient if its retention window is shorter than replay, or if downstream side effects are not deduplicated.",
        "operations_heading": "Measure amplification and unresolved consequence",
        "operations": [
            "Track retry amplification as total attempts divided by original actions, segmented by dependency and effect class. Pair it with ambiguous material value, duplicate effects, omission loss, and p99 resolution time. A low error rate can coexist with an expensive unresolved tail.",
            "In the synthetic gate, the global amplification ratio breaches while safe replay and duplicate-effect measures pass. That is an infrastructure warning before it becomes a business incident.",
        ],
        "scorecard_title": "Risk-aware retry operating scorecard",
        "metrics": [["Material duplicate effects", "0", "0", "PASS"], ["Safe replay success", "99.7%", "≥ 99.5%", "PASS"], ["Retry amplification", "1.42×", "≤ 1.20×", "BREACH"], ["p99 ambiguity resolution", "11 min", "≤ 15 min", "PASS"], ["Budget bypass events", "0", "0", "PASS"]],
        "metrics_table": [["Retry amplification", "Open or tighten fleet circuit", "Retries are worsening dependency pressure"], ["Ambiguous value at risk", "Prioritize reconciliation by consequence", "Unknown business effects are accumulating"], ["Same-key mismatch", "Reject and investigate caller", "A changed intent is masquerading as retry"], ["Resolution latency", "Tune observation and escalation", "Recovery capacity is insufficient"]],
        "implementation": [["Inventory tool semantics.", "Classify every mutating integration and document whether idempotency is end-to-end or only local."], ["Centralize retry budgets.", "Prevent fifty agent workers from each believing they are below an individual limit."], ["Inject ambiguous outcomes.", "Commit the server effect, drop the response, and prove the controller observes before deciding."]],
        "references": "AWS's <a href=\"https://aws.amazon.com/builders-library/making-retries-safe-with-idempotent-APIs/\">idempotent API guidance</a> distinguishes repeated requests from changed intent. <a href=\"https://aws.amazon.com/blogs/architecture/exponential-backoff-and-jitter/\">Exponential Backoff and Jitter</a> addresses correlated retry contention. <a href=\"https://www.rfc-editor.org/rfc/rfc9110.html\">RFC 9110</a> defines idempotent HTTP method semantics.",
        "boundary": "The formula is a decision framework, not a universal probability model. Loss values and transient-failure estimates must be calibrated by domain and tested under dependency-specific fault modes.",
        "conclusion": "A retry policy becomes production-grade when it can explain why this action, with this immutable intent, against this observed state, deserves another attempt now. Everything else is a loop with good intentions.",
        "question": "Which of your agent tools inherits retries from an SDK even though the endpoint creates a material effect?",
        "figure_alts": ["Six-stage effect-aware retry controller architecture spanning classification, sensing, pricing, decision, enforcement, and observation.", "Eight-state retry decision flow separating safe replay, reconciliation, escalation, and evidence-based closure after a timeout.", "Five-metric retry scorecard showing an amplification breach despite passing business-effect safeguards."],
        "figure_captions": ["Retry authority is computed from effect semantics, dependency state, and economic exposure.", "Timeout is an input to classification, not an automatic instruction to call again.", "Fleet amplification can breach before material duplicates appear."],
    },
    {
        "slug": "your-verifier-must-not-trust-the-agent",
        "title": "Your Verifier Must Not Trust the Agent",
        "subtitle": "Independent postcondition evidence is the boundary between a claimed success and a proven business effect.",
        "description": "A technical design for independent AI-agent verification using separate identities, data paths, assertions, evidence quality, and recovery gates.",
        "tags": ["AI agents", "Verification", "AI governance", "Reliability", "Enterprise architecture"],
        "hook": [
            "The agent says the customer record was updated, the tool says the call succeeded, and the trace shows no exception. None of those statements proves that the approved business state exists.",
            "A verifier that consumes the agent's summary, uses the same credential, calls the same abstraction, and asks the same model whether the outcome looks right is not independent. It is a second opinion produced inside the first failure domain.",
        ],
        "thesis": "Verification should share the approved intent with execution—but not its identity, evidence path, implementation, or incentive to call the action successful.",
        "failure_heading": "Correlated verification creates confident false closure",
        "failure": [
            "Execution and verification fail together when they share cached data, a tool adapter, a parsing assumption, or a broad principal. A malformed adapter can translate both the write and the read incorrectly. A compromised agent can shape the verifier's prompt. A stale replica can confirm a state that never reached the authoritative ledger.",
            "The verification contract must therefore name the assertion, evidence authority, observation deadline, acceptable lag, and independence class. The verifier evaluates a structured postcondition—not the persuasiveness of the agent's explanation.",
        ],
        "architecture_heading": "Separate the proposal, effect, and evidence planes",
        "architecture": [
            "The proposal plane defines the intended delta. The effect plane executes through a narrow gateway. The evidence plane uses a different service identity and, where material, a different authoritative interface such as an immutable ledger, database change feed, or provider reconciliation API.",
            "A verification service compares intended and observed state, checks freshness and provenance, and emits one of four outcomes: verified, violated, inconclusive, or expired. Only verified closes success. Violation invokes recovery; inconclusive preserves ambiguity; expiry transfers ownership to a defined human queue.",
        ],
        "architecture_nodes": [["Intent", "Approved assertion and expected delta"], ["Effect", "Narrow gateway commits the mutation"], ["Evidence", "Independent identity reads authority"], ["Compare", "Typed assertion evaluates state"], ["Decide", "Verified, violated or inconclusive"], ["Recover", "Compensate, freeze or escalate"]],
        "design_rule": "The component that performs an effect cannot be the sole source that proves it.",
        "flow_title": "Independent verification lifecycle",
        "flow_subtitle": "Proof quality is evaluated before success is closed.",
        "flow_states": [["ASSERT", "Expected postcondition frozen"], ["EXECUTE", "Effect path writes"], ["OBSERVE", "Separate identity and path"], ["QUALIFY", "Freshness and provenance"], ["VERIFIED", "Assertion holds"], ["VIOLATED", "Observed state diverges"], ["INCONCLUSIVE", "Evidence is insufficient"], ["RESOLVE", "Receipt or recovery closes"]],
        "flow_guard": "A tool response can start verification; it cannot substitute for authoritative observation.",
        "model_heading": "Score verification independence explicitly",
        "model_intro": "A simple independence score makes correlated controls visible:",
        "formula": "I_verify = w_id × sep(identity) + w_path × sep(data_path)\n         + w_impl × sep(implementation) + w_auth × authority(source)\n         - w_corr × shared_failure_modes\nclose_success only if I_verify ≥ I_min ∧ freshness ≤ F_max ∧ assertion = true",
        "model_explanation": "The score is ordinal unless its weights are empirically calibrated. Its value is architectural: a verifier using the same model, adapter, cache, and credential should not silently receive a high-assurance label.",
        "control_table": [["Independence dimension", "Weak pattern", "Stronger pattern"], [["Identity", "Agent reuses executor token", "Verifier-only read principal"], ["Path", "Same tool wrapper", "Authoritative reconciliation endpoint"], ["Implementation", "Same generated parser", "Typed, separately tested assertion"], ["Evidence", "Agent narrative", "Versioned source observation"], ["Ownership", "Agent closes itself", "Control service owns terminal state"]]],
        "contract_heading": "Compile verification into an assertion",
        "contract_intro": "The expected outcome should be machine-testable and bound to the approved action:",
        "code_language": "yaml",
        "code": "assertion_id: verify_quote_771_v43\naction_id: act_01K...\nsource:\n  system: billing-ledger\n  interface: adjustment-by-action-id\n  max_lag_seconds: 45\nexpect:\n  account_id: A-1902\n  discount_bps: 800\n  occurrences: 1\noutcomes: [verified, violated, inconclusive, expired]\non_violation: freeze_and_compensate",
        "contract_explanation": "Assertions should be generated from a reviewed schema, not free-form reasoning. Property-based tests can vary versions, delays, duplicates, and partial state to confirm the verifier fails closed when evidence is missing or contradictory.",
        "operations_heading": "Measure proof coverage and correlation",
        "operations": [
            "Receipt coverage alone is insufficient if most receipts close on low-quality evidence. Track independent verification coverage by risk tier, inconclusive age, false closure discovered by later reconciliation, shared-dependency concentration, and assertion drift after schema changes.",
            "The illustrative gate shows perfect receipt creation but a breach in high-independence coverage. That is exactly the condition a receipt-count dashboard would hide.",
        ],
        "scorecard_title": "Independent verification operating scorecard",
        "metrics": [["Receipt creation", "100%", "100%", "PASS"], ["High-risk independent proof", "96.2%", "≥ 99.5%", "BREACH"], ["False closure", "0", "0", "PASS"], ["p99 inconclusive age", "8.4 min", "≤ 10 min", "PASS"], ["Assertion schema tests", "100%", "100%", "PASS"]],
        "metrics_table": [["Independent proof coverage", "Gate authority by risk tier", "Execution is closing on correlated evidence"], ["False closure", "Trigger incident and retrospective", "Verifier accepted an incorrect outcome"], ["Inconclusive age", "Escalate unresolved actions", "Observation path or recovery capacity is weak"], ["Shared-failure concentration", "Add alternate evidence paths", "Verifier is not meaningfully independent"]],
        "implementation": [["Name the business postcondition.", "Replace ‘tool succeeded’ with one typed assertion on authoritative state."], ["Create a separate verifier identity.", "Grant read-only access only to the evidence required for that assertion."], ["Break the shared failure modes.", "Use fault injection to corrupt adapters, delay replicas, and forge executor responses while proving the verifier refuses false closure."]],
        "references": "The <a href=\"https://airc.nist.gov/\">NIST AI Resource Center</a> supports testing, evaluation, verification, and validation practices, while the <a href=\"https://airc.nist.gov/airmf-resources/airmf/5-sec-core/\">AI RMF Core</a> calls for documented validity, reliability, safety, monitoring, and response. The independence model here is a proposed engineering pattern, not a NIST requirement.",
        "boundary": "Independent does not mean infallible. Every evidence source has lag, compromise, and modeling risk. The design makes those dependencies explicit and prevents the agent from being judge of its own effect.",
        "conclusion": "A production agent should be able to say, ‘I attempted the action.’ Only an independent control path should be allowed to say, ‘The approved state now exists, exactly once, in the authoritative system.’",
        "question": "If your agent's tool adapter lied, which separate system would detect the lie?",
        "figure_alts": ["Six-stage independent verifier architecture separating approved intent, effect execution, evidence acquisition, comparison, decision, and recovery.", "Eight-state verification lifecycle distinguishing verified, violated, inconclusive, and expired outcomes before resolution.", "Five-metric verification scorecard showing a breach in high-risk independent proof despite complete receipt creation."],
        "figure_captions": ["Execution and proof share intent but use different identities and evidence paths.", "Inconclusive evidence preserves uncertainty instead of manufacturing success.", "Receipt count passes while meaningful proof coverage fails."],
    },
    {
        "slug": "the-agent-policy-engine-is-a-compiler",
        "title": "The Agent Policy Engine Is a Compiler, Not a Prompt",
        "subtitle": "Turn governance prose into typed, testable, versioned action constraints before an agent reaches production.",
        "description": "A policy-as-code architecture for compiling enterprise AI-agent rules into typed decisions, obligations, tests, and enforceable capabilities.",
        "tags": ["AI agents", "Policy as code", "Authorization", "AI governance", "Enterprise architecture"],
        "hook": [
            "‘Do not offer excessive discounts’ sounds like a policy until two teams implement ‘excessive’ differently. One prompt treats 12% as high, another compares it with account value, and a third never receives the regional exception table.",
            "Natural-language policy is necessary for accountability, but it is not an execution format. Production control needs a compilation pipeline that resolves vocabulary, types inputs, detects conflicts, emits deterministic decisions and obligations, and packages the result for enforcement.",
        ],
        "thesis": "The model may explain policy. The policy engine must decide authority from structured facts and a versioned executable artifact.",
        "failure_heading": "Prompt-level governance has no stable semantics",
        "failure": [
            "Policies fail when terms are undefined, inputs are missing, precedence is implicit, or two rules permit and forbid the same effect. A language model can produce a plausible interpretation without proving which clause, data version, exception, or conflict rule determined the outcome.",
            "Treating policy as a compiler problem creates explicit stages: parse, type-check, link data, resolve precedence, evaluate tests, optimize, sign, distribute, and enforce. A rejected build is safer than a syntactically fluent ambiguity reaching a tool call.",
        ],
        "architecture_heading": "Build a policy supply chain",
        "architecture": [
            "Policy authors work in a governed source repository. Schemas define principals, actions, resources, context, evidence, risk classes, and obligations. Continuous integration runs type checks, conflict analysis, unit tests, scenario tests, and differential tests against the current bundle.",
            "The released bundle receives a digest and effective interval. At runtime the decision point returns permit, deny, or review plus obligations such as maximum value, required approver class, verifier level, lease duration, and receipt retention. Enforcement points reject missing or stale bundle digests.",
        ],
        "architecture_nodes": [["Author", "Human policy and domain vocabulary"], ["Type", "Schemas for principal, action and context"], ["Test", "Conflicts, scenarios and regressions"], ["Compile", "Signed immutable decision bundle"], ["Decide", "Permit, deny, review and obligations"], ["Enforce", "Gateway applies constraints and records digest"]],
        "design_rule": "No production authority without a reproducible policy build and an enforceable decision artifact.",
        "flow_title": "Policy compilation and runtime path",
        "flow_subtitle": "Governance moves from prose to an immutable execution decision.",
        "flow_states": [["SOURCE", "Policy and rationale reviewed"], ["SCHEMA", "Inputs and entities typed"], ["ANALYZE", "Conflict and reachability tests"], ["TEST", "Golden and adversarial cases"], ["BUNDLE", "Version, sign and release"], ["EVALUATE", "Structured runtime request"], ["OBLIGATE", "Limits and controls returned"], ["ENFORCE", "Effect gateway verifies digest"]],
        "flow_guard": "A missing fact, unknown enum, evaluation error, or expired bundle fails to deny or review—not to an improvised model interpretation.",
        "model_heading": "Treat coverage like a compiler quality problem",
        "model_intro": "A deployment gate can combine policy test evidence without pretending all tests are equally important:",
        "formula": "Coverage_risk = Σ_i w_i × pass_i / Σ_i w_i\nConflict_escape = conflicts_found_after_release / policy_decisions\nrelease iff Coverage_risk ≥ τ ∧ Conflict_escape = 0 ∧ breaking_schema_changes = 0",
        "model_explanation": "Weights represent action consequence and rule criticality. Mutation testing—deliberately changing limits or removing forbids—helps reveal suites that pass without actually protecting the intended boundary.",
        "control_table": [["Compiler stage", "Artifact", "Hard failure"], [["Schema", "Typed entity/action model", "Unknown or incompatible field"], ["Analysis", "Conflict and reachability report", "Unresolved forbid/permit overlap"], ["Testing", "Risk-weighted scenario results", "Critical mutation survives"], ["Release", "Signed bundle + digest", "Unsigned or expired artifact"], ["Runtime", "Decision + obligations", "Enforcement cannot prove bundle"]]],
        "contract_heading": "Return obligations, not only a boolean",
        "contract_intro": "An action decision needs enough structure for downstream enforcement:",
        "code_language": "json",
        "code": '{\n  "decision": "review",\n  "policy_bundle": "pricing-2026.09.3",\n  "digest": "sha256:...",\n  "determining_rules": ["discount.material", "region.apac"],\n  "obligations": {\n    "max_discount_bps": 800,\n    "approver_role": "regional_vp",\n    "lease_seconds": 90,\n    "verification": "independent_high"\n  }\n}',
        "contract_explanation": "The gateway must enforce these obligations even if the planner asks for more. Diagnostics should be visible to policy owners and receipts, while sensitive policy data is minimized for the agent.",
        "operations_heading": "Run policy as a production dependency",
        "operations": [
            "Track decision latency, unknown-input rate, deny/review drift, policy rollback frequency, critical test coverage, bundle adoption lag, and post-release conflict escapes. Changes to policy can alter authority as materially as application code.",
            "The synthetic gate shows a bundle-adoption breach: decision quality can pass in the control plane while stale enforcement points continue applying old authority.",
        ],
        "scorecard_title": "Policy compiler operating scorecard",
        "metrics": [["Critical mutation kill rate", "100%", "100%", "PASS"], ["Unresolved conflicts", "0", "0", "PASS"], ["p95 decision latency", "18 ms", "≤ 25 ms", "PASS"], ["Bundle adoption in 5 min", "97.8%", "≥ 99.9%", "BREACH"], ["Unknown-input fail-open", "0", "0", "PASS"]],
        "metrics_table": [["Bundle adoption lag", "Block or constrain writes on stale points", "Control plane and enforcement disagree"], ["Unknown-input rate", "Repair schemas or producers", "Runtime context is incomplete"], ["Decision drift", "Review policy/data change", "Authority distribution shifted unexpectedly"], ["Conflict escape", "Incident and rollback", "Compiler or review gate missed ambiguity"]],
        "implementation": [["Define the action vocabulary.", "Start with ten material actions and type principal, resource, context, and consequence fields."], ["Build golden and mutation tests.", "Prove critical forbids and review boundaries fail when altered."], ["Bind enforcement to bundle digests.", "Every gateway decision and receipt must identify the exact released policy artifact."]],
        "references": "<a href=\"https://www.openpolicyagent.org/docs\">Open Policy Agent</a> separates policy decision-making from enforcement and evaluates structured data using Rego. <a href=\"https://docs.cedarpolicy.com/\">Cedar</a> models authorization over principal, action, resource, and context. These products are examples; the architecture is vendor-neutral.",
        "boundary": "Not every governance statement should become code. Ethical commitments, legal interpretation, and novel exceptions may require accountable judgment. The compiler should route those cases to review rather than invent certainty.",
        "conclusion": "A policy prompt can be persuasive. A policy build can be inspected, tested, versioned, rolled back, and enforced. Agents that create material effects need the latter around the former.",
        "question": "Could your team reproduce yesterday's agent authorization decision from the exact policy bundle and input facts?",
        "figure_alts": ["Six-stage agent policy supply-chain architecture from human authoring and schemas through testing, signed bundles, decisions, and enforcement.", "Eight-stage policy compilation flow converting reviewed source into runtime obligations enforced at the effect gateway.", "Five-metric policy scorecard showing a bundle adoption breach despite passing tests and decision latency."],
        "figure_captions": ["Policy is compiled into a signed artifact before it grants production authority.", "Typed inputs and conflict tests precede runtime evaluation and enforcement.", "Stale enforcement points can undermine an otherwise healthy policy control plane."],
    },
    {
        "slug": "ai-agent-observability-is-not-logging",
        "title": "AI Agent Observability Is Not Logging",
        "subtitle": "A trace explains execution; an effect graph explains what the agent changed, why, under whose authority, and whether it was right.",
        "description": "A business-effect observability architecture for AI agents linking traces, decisions, authority, evidence, outcomes, cost, and recovery.",
        "tags": ["AI agents", "Observability", "OpenTelemetry", "Enterprise architecture", "Reliability"],
        "hook": [
            "A million agent log lines can explain token counts, prompts, latency, and tool responses while leaving one executive question unanswered: what changed in the business, and was that change authorized and correct?",
            "Traditional telemetry follows requests through software. Agent observability must also follow intent through decisions, authority, effects, verification, economic outcomes, and recovery. The unit is not a model call. It is a consequential business action.",
        ],
        "thesis": "Instrument the agent as a distributed system, but operate it as a portfolio of business effects.",
        "failure_heading": "Technical success can conceal business failure",
        "failure": [
            "A green trace may end after the CRM returns success, before billing rejects the downstream adjustment. A red span may describe a harmless retry that the idempotency ledger safely absorbed. Without action identity and effect semantics, operational dashboards confuse software events with business outcomes.",
            "Telemetry also becomes dangerous when prompts, retrieved documents, and customer data are copied indiscriminately into logs. Observability needs a data contract: identifiers and digests by default, risk-tiered payload capture, purpose limits, access controls, retention, and redaction tests.",
        ],
        "architecture_heading": "Join four graphs around one action identifier",
        "architecture": [
            "The execution graph contains traces and spans. The decision graph contains evidence, model route, policy, approval, and authority. The effect graph contains intended and observed state changes. The economic graph contains cost, latency, conditional loss, and realized value. A durable action ID and versioned links connect them.",
            "Collectors transform high-volume telemetry into action-level facts. A receipt store holds the compact proof core; trace storage supports debugging; a metric pipeline produces SLOs; an investigation view reconstructs the causal path without exposing raw sensitive context to every operator.",
        ],
        "architecture_nodes": [["Instrument", "Traces, metrics, logs and events"], ["Correlate", "Stable action, workflow and resource IDs"], ["Enrich", "Policy, authority, cost and risk context"], ["Observe", "Authoritative business postconditions"], ["Aggregate", "Effect SLOs and tail distributions"], ["Investigate", "Causal reconstruction and recovery"]],
        "design_rule": "Every material span must resolve to an action; every material action must resolve to an observed effect or owned ambiguity.",
        "flow_title": "From request trace to effect evidence",
        "flow_subtitle": "Telemetry becomes operational only after correlation and verification.",
        "flow_states": [["INTENT", "Action identity created"], ["DECISION", "Evidence and route linked"], ["AUTHORITY", "Policy and lease recorded"], ["TRACE", "Calls and attempts emitted"], ["EFFECT", "Postcondition observed"], ["ECONOMICS", "Cost and exposure attributed"], ["SLO", "Tail and cohort gates evaluated"], ["RECOVERY", "Owner closes exceptions"]],
        "flow_guard": "Never use raw prompt capture as a substitute for typed provenance and action-level correlation.",
        "model_heading": "Define an effect observability coverage ratio",
        "model_intro": "Coverage should reward terminal business evidence, not log volume:",
        "formula": "Coverage_effect = Σ_a risk_weight(a) × 1[trace ∧ decision ∧ authority ∧ outcome] / Σ_a risk_weight(a)\nAmbiguity_load = Σ_{a ∈ unresolved} exposure(a) × age_weight(a)",
        "model_explanation": "A low-risk summary and a binding credit should not contribute equally. The second term prioritizes unresolved actions by both economic exposure and age, preventing thousands of trivial traces from hiding a few material unknowns.",
        "control_table": [["Graph", "Minimum node", "Join key"], [["Execution", "span + attempt", "trace_id + action_id"], ["Decision", "evidence + policy + route", "decision_id + action_id"], ["Authority", "lease + approver", "lease_id + action_id"], ["Effect", "expected + observed state", "resource_version + action_id"], ["Economic", "cost + value + loss", "action_id + outcome_window"]]],
        "contract_heading": "Use semantic attributes for agent actions",
        "contract_intro": "A span can carry safe correlation fields without copying the full prompt:",
        "code_language": "text",
        "code": "agent.action.id = act_01K...\nagent.workflow.id = renewal_771\nagent.action.class = material_write\nagent.policy.digest = sha256:...\nagent.authority.lease_id = lease_91\nagent.resource.type = crm.quote\nagent.resource.version.expected = 42\nagent.effect.status = inconclusive\nagent.evidence.bundle_digest = sha256:...",
        "contract_explanation": "Attribute names should be governed, cardinality-aware, and privacy-reviewed. High-cardinality IDs may belong in traces and logs rather than metric labels; metrics aggregate by bounded dimensions such as action class, risk tier, route, and outcome.",
        "operations_heading": "Build SLOs on effects, not calls",
        "operations": [
            "Useful SLOs include verified-effect rate, duplicate-effect rate, p99 ambiguity age, authority-to-effect latency, policy-denial accuracy, recovery completion, cost per verified outcome, and evidence coverage. Technical latency and error rate remain necessary drivers, not final outcomes.",
            "The illustrative scorecard shows a trace-coverage pass and an effect-coverage breach. This is the expected diagnostic value: observability can reveal that instrumentation is present while operational truth is incomplete.",
        ],
        "scorecard_title": "Business-effect observability scorecard",
        "metrics": [["Trace coverage", "99.99%", "≥ 99.9%", "PASS"], ["Risk-weighted effect coverage", "96.8%", "≥ 99.5%", "BREACH"], ["Authority linkage", "99.98%", "≥ 99.9%", "PASS"], ["p99 correlation lag", "42 s", "≤ 60 s", "PASS"], ["Sensitive payload violations", "0", "0", "PASS"]],
        "metrics_table": [["Effect coverage", "Gate higher autonomy", "Actions lack terminal business evidence"], ["Correlation lag", "Tune collectors and joins", "Incidents cannot be reconstructed quickly"], ["Ambiguity load", "Prioritize by exposure and age", "Unresolved consequence is accumulating"], ["Payload policy violations", "Stop capture and investigate", "Telemetry is creating privacy or security risk"]],
        "implementation": [["Create one action semantic convention.", "Standardize identifiers and bounded attributes across planner, policy, gateway, verifier, and recovery services."], ["Join one material workflow end to end.", "Show the trace, authority, intended delta, observed effect, cost, and owner in one investigation view."], ["Set effect SLOs.", "Use risk-weighted coverage and ambiguity age to control rollout rather than optimizing log completeness alone."]],
        "references": "<a href=\"https://opentelemetry.io/docs/concepts/signals/\">OpenTelemetry signals</a> cover traces, metrics, logs, and baggage; its <a href=\"https://opentelemetry.io/docs/concepts/observability-primer/\">observability primer</a> explains distributed traces and instrumentation. The effect, decision, authority, and economic graph is an extension proposed for agent operations.",
        "boundary": "This is not a recommendation to place sensitive evidence in telemetry. Store minimal correlation and policy-safe digests in operational signals; retrieve protected evidence through access-controlled systems when an investigation requires it.",
        "conclusion": "Logs tell you that software spoke. Traces tell you where the request travelled. Agent observability must tell you which approved business effect occurred, whether it matched intent, what it cost, and who owns what remains unknown.",
        "question": "Can your observability platform answer ‘what business state changed?’ without reading the agent's prose?",
        "figure_alts": ["Six-stage AI-agent observability architecture from instrumentation and correlation through business-effect observation, aggregation, and investigation.", "Eight-stage telemetry flow connecting intent, decision, authority, trace, business effect, economics, SLO evaluation, and recovery.", "Five-metric observability scorecard showing a risk-weighted effect coverage breach despite near-complete trace coverage."],
        "figure_captions": ["Execution telemetry is joined to decision, authority, effect, and economic evidence.", "Stable action identity turns distributed signals into a reconstructable business narrative.", "Technical trace coverage can pass while business-effect evidence remains below the production gate."],
    },
    {
        "slug": "every-agent-needs-a-safe-degradation-ladder",
        "title": "Every Agent Needs a Safe Degradation Ladder",
        "subtitle": "Production resilience means reducing authority deliberately before the system reaches an emergency stop.",
        "description": "A control-plane blueprint for moving AI agents through autonomous, reviewed, recommend-only, read-only, and contained operating modes.",
        "tags": ["AI agents", "Resilience", "Incident response", "AI governance", "Enterprise architecture"],
        "hook": [
            "Most agent platforms expose two operational modes: enabled and disabled. Real incidents do not arrive in binary form. Retrieval quality drifts, a verifier lags, a model route degrades, an approver queue saturates, or one tool starts returning ambiguous outcomes.",
            "A kill switch is essential for containment, but it is the last rung. A safe degradation ladder lets the control plane remove classes of authority as evidence weakens—preserving useful work without pretending the original autonomy contract still holds.",
        ],
        "thesis": "Degradation should reduce reachable consequence monotonically, with explicit entry signals, exit evidence, and independent enforcement.",
        "failure_heading": "Feature flags do not define a safety state",
        "failure": [
            "Turning off one planner while queued work, cached credentials, delegated agents, or direct tool tokens remain active can create the appearance of safety. A mode must be enforced at every effect boundary and attached to an epoch so stale workers cannot commit under an earlier state.",
            "Recovery is equally risky. If operators re-enable autonomy because error rate looks normal for five minutes, unresolved effects and verifier backlogs may return with it. Exit needs a proof bundle: root cause bounded, ambiguous actions reconciled, controls healthy, canary passed, and accountable authority recorded.",
        ],
        "architecture_heading": "Make operating mode a control-plane primitive",
        "architecture": [
            "A mode controller ingests effect SLOs, dependency health, policy changes, drift signals, incident commands, and reviewer capacity. It advances a signed mode epoch and distributes it to schedulers, workers, gateways, queues, and verifiers. Each enforcement point rejects authority issued under an older or more permissive epoch.",
            "A five-rung ladder is a useful start: autonomous bounded action; mandatory human review; recommend-only output; read-only investigation; and contained. Each action class maps to permitted effects in each mode. Higher-risk actions can degrade earlier than routine internal work.",
        ],
        "architecture_nodes": [["Sense", "Effect SLO, drift and dependency signals"], ["Decide", "Policy selects mode by action class"], ["Advance", "Signed mode epoch becomes current"], ["Propagate", "Workers, queues and gateways update"], ["Enforce", "Stale or excess authority is rejected"], ["Recover", "Reconcile, canary and promote safely"]],
        "design_rule": "Every downward transition removes authority; every upward transition requires new evidence.",
        "flow_title": "Five-rung agent degradation ladder",
        "flow_subtitle": "Utility continues while reachable consequence contracts.",
        "flow_states": [["AUTONOMOUS", "Bounded low-risk effects"], ["REVIEWED", "Human approves each material act"], ["RECOMMEND", "No direct mutation authority"], ["READ-ONLY", "Evidence and diagnosis only"], ["CONTAINED", "All effect commits rejected"], ["RECONCILE", "Unknown actions get owners"], ["CANARY", "Small cohort and strict gates"], ["RESTORE", "New epoch and staged authority"]],
        "flow_guard": "Promotion never reuses authority minted before degradation; new leases inherit the current mode epoch.",
        "model_heading": "Choose the least restrictive safe mode",
        "model_intro": "Mode selection can be expressed as constrained utility:",
        "formula": "m* = argmax_m Utility(m)\nsubject to: Exposure(m) ≤ RiskBudget\n            VerificationCapacity(m) ≥ RequiredProof(m)\n            AmbiguityAge(m) ≤ Deadline(m)\nand ReachableAuthority(m_down) ⊆ ReachableAuthority(m_up)",
        "model_explanation": "The subset condition prevents a lower rung from accidentally adding a path. Utility includes retained service value; exposure includes action scope, rate, reversibility, and dependency uncertainty.",
        "control_table": [["Mode", "Allowed behavior", "Default trigger"], [["Autonomous", "Bounded reversible effects", "All production gates healthy"], ["Reviewed", "Material effects after approval", "Drift or verifier pressure"], ["Recommend-only", "Plans and evidence packets", "Policy/data uncertainty"], ["Read-only", "Observe and diagnose", "Mutation path unreliable"], ["Contained", "Reject all effect commits", "Credible compromise or uncontrolled harm"]]],
        "contract_heading": "Bind every capability to a mode epoch",
        "contract_intro": "Enforcement should compare both authority and current operating mode:",
        "code_language": "json",
        "code": '{\n  "lease_id": "lease_91",\n  "action_class": "crm.material_write",\n  "mode": "reviewed",\n  "mode_epoch": 1842,\n  "issued_after_approval": "apr_52",\n  "max_uses": 1,\n  "expires_in_seconds": 90\n}\n\naccept iff lease.mode_epoch == control.current_epoch\n       and action in control.allowed[lease.mode]',
        "contract_explanation": "Queued work must be re-evaluated when the epoch changes. A message accepted under autonomous mode cannot remain pre-authorized after the system moves to recommend-only.",
        "operations_heading": "Measure transition quality, not just availability",
        "operations": [
            "Track time to effective degradation, stale-epoch rejection, residual reachable authority, work retained by lower modes, ambiguity closed before restoration, canary escape rate, and unplanned mode flapping. Availability without bounded consequence is not resilience.",
            "The synthetic scorecard shows transition speed passing while ambiguous-action closure breaches. Restoration should remain blocked even if the immediate error disappears.",
        ],
        "scorecard_title": "Safe degradation operating scorecard",
        "metrics": [["p99 mode propagation", "38 s", "≤ 60 s", "PASS"], ["Stale-epoch accepts", "0", "0", "PASS"], ["Useful work retained", "64%", "≥ 50%", "PASS"], ["Ambiguity closed before restore", "97.1%", "≥ 99.5%", "BREACH"], ["Canary escape events", "0", "0", "PASS"]],
        "metrics_table": [["Mode propagation", "Escalate to containment if late", "Effect boundaries disagree on state"], ["Residual authority", "Revoke paths not reduced", "Degradation is cosmetic"], ["Useful work retained", "Tune per-action mapping", "Lower mode may be unnecessarily destructive"], ["Restore evidence", "Block promotion", "Recovery is outrunning reconciliation"]],
        "implementation": [["Enumerate effect classes.", "Map each tool action to the five modes and prove lower modes never add authority."], ["Introduce mode epochs.", "Have every gateway reject stale leases and re-evaluate queued work."], ["Exercise the ladder.", "Run game days for verifier lag, model drift, approver saturation, and compromised credentials before relying on full containment."]],
        "references": "Google SRE's <a href=\"https://sre.google/sre-book/embracing-risk/\">risk and error-budget guidance</a> explains controlling release velocity with reliability evidence, and its <a href=\"https://sre.google/workbook/canarying-releases/\">canarying guidance</a> describes partial, time-limited rollout and evaluation. The agent-specific authority ladder is a proposed extension.",
        "boundary": "Degraded modes should not be used to bypass obligations owed to customers or regulators. They are technical safety states; business continuity and legal decisions still need accountable owners.",
        "conclusion": "The choice is not full autonomy or zero value. A mature control plane can retain analysis, evidence gathering, and recommendations while progressively withdrawing the authority that current evidence no longer justifies.",
        "question": "When one verifier or tool degrades, can your system reduce only the affected authority—or does it keep everything running until someone pulls the plug?",
        "figure_alts": ["Six-stage safe degradation control-plane architecture from sensing and mode decisions through epoch propagation, enforcement, and recovery.", "Eight-state degradation and restoration flow moving from bounded autonomy through reviewed, recommend-only, read-only, contained, reconciliation, canary, and restore.", "Five-metric degradation scorecard showing insufficient ambiguity closure before restoration despite fast mode propagation."],
        "figure_captions": ["A signed mode epoch coordinates the reduction of authority across effect boundaries.", "The ladder preserves useful work while consequence is reduced monotonically.", "Restoration remains unsafe when ambiguous actions have not been reconciled."],
    },
    {
        "slug": "who-owns-an-ai-agent-incident",
        "title": "Who Owns an AI Agent Incident?",
        "subtitle": "A production incident model for command, business truth, authority containment, customer impact, and evidence preservation.",
        "description": "An AI-agent incident-command architecture defining roles, clocks, decision rights, evidence, containment, reconciliation, and recovery gates.",
        "tags": ["AI agents", "Incident response", "AI governance", "SRE", "Enterprise operations"],
        "hook": [
            "At 02:13, an agent begins sending duplicate renewal notices. Security revokes the workload identity. Platform engineering stops the workers. Sales operations says forty-seven accounts may already be affected. Legal asks what customers received. Everyone owns part of the system; no one owns the incident truth.",
            "AI-agent incidents cross conventional boundaries because model behavior, data quality, policy, identity, workflow state, external tools, and business consequences can fail together. The response needs one command structure with separate technical and business workstreams.",
        ],
        "thesis": "Contain the authority quickly, but assign equal ownership to reconstructing and repairing the business effects already in motion.",
        "failure_heading": "Stopping compute does not close the incident",
        "failure": [
            "An agent incident can remain economically active after every process is dead. Messages may be queued, credits pending, quotes changed, downstream jobs scheduled, and customers acting on incorrect information. The response must track both time to containment and time to business truth.",
            "A generic severity label also hides scope. The commander needs a live action inventory by principal, resource, effect class, authority epoch, attempt state, observed postcondition, customer exposure, and recovery owner. If the inventory is incomplete, confidence must not be rounded up to certainty.",
        ],
        "architecture_heading": "Use incident command with five accountable cells",
        "architecture": [
            "One incident commander owns priorities and decisions. A containment lead advances epochs and blocks new effects. A truth-and-reconciliation lead inventories committed, rejected, duplicate, ambiguous, and compensating actions. A business-impact lead coordinates domain owners and customer remediation. An evidence lead preserves timelines, policy versions, approvals, traces, and receipts.",
            "Communications is a controlled output, not an improvised stream. Internal updates distinguish confirmed facts, hypotheses, unknowns, decision owners, and next checkpoints. External communication follows accountable business and legal review.",
        ],
        "architecture_nodes": [["Command", "One owner sets objectives and cadence"], ["Contain", "Revoke authority and reject stale epochs"], ["Establish truth", "Inventory every material business effect"], ["Remediate", "Compensate and coordinate domain owners"], ["Preserve", "Evidence, decisions and timelines immutable"], ["Recover", "Canary, validate and close learnings"]],
        "design_rule": "One commander; explicit workstream owners; two clocks—authority containment and business-truth closure.",
        "flow_title": "AI-agent incident lifecycle",
        "flow_subtitle": "Technical containment and business reconciliation advance in parallel.",
        "flow_states": [["DETECT", "Credible effect anomaly"], ["DECLARE", "Severity and commander named"], ["CONTAIN", "Authority epoch advances"], ["INVENTORY", "Actions and exposures enumerated"], ["RECONCILE", "Outcomes independently observed"], ["REMEDIATE", "Reverse, correct or communicate"], ["CANARY", "Bounded recovery evidence"], ["CLOSE", "Truth, controls and owners complete"]],
        "flow_guard": "The incident cannot close while material actions remain unowned, ambiguous, or outside the evidence inventory.",
        "model_heading": "Operate two independent recovery clocks",
        "model_intro": "A single mean-time-to-recovery metric conceals the difference between stopping new harm and resolving prior effects:",
        "formula": "MTTC = t(all material boundaries reject stale authority) - t(detection)\nMTTB = t(all material actions terminal or owned) - t(detection)\nResidualExposure(t) = Σ_a value_at_risk(a) × P_unresolved(a,t)",
        "model_explanation": "MTTC can be short while MTTB remains long. Residual exposure should drive staffing and communication cadence after containment, because an unresolved high-value customer action may matter more than hundreds of harmless aborted tasks.",
        "control_table": [["Role", "Decision right", "Evidence owned"], [["Incident commander", "Priority, severity, closure", "Decision log and objectives"], ["Containment lead", "Epoch, revocation, block", "Enforcement acknowledgements"], ["Truth lead", "Outcome classification", "Action inventory and observations"], ["Business-impact lead", "Remediation and customer path", "Exposure and communication record"], ["Evidence lead", "Preservation and access", "Immutable incident package"]]],
        "contract_heading": "Represent the incident as structured state",
        "contract_intro": "A machine-readable incident record keeps handoffs and automation bounded:",
        "code_language": "yaml",
        "code": "incident: AGENT-2026-014\ncommander: role:sre-incident-commander\ncontainment_epoch: 1842\nmaterial_actions:\n  total: 1264\n  committed: 811\n  rejected: 312\n  ambiguous: 41\n  compensating: 100\nobjectives:\n  mttc_seconds: 90\n  ambiguous_owner_minutes: 15\nclosure_requires: [zero_unowned_material_actions, canary_passed, evidence_sealed]",
        "contract_explanation": "The record should link to protected systems rather than duplicate sensitive payloads. Automated helpers may enrich it, but only named roles change severity, authorize remediation, or declare closure.",
        "operations_heading": "Measure command quality and business truth",
        "operations": [
            "Track detection-to-declaration, MTTC, action-inventory completeness, time to owner for ambiguity, residual exposure, compensation success, decision-log completeness, and repeat incidents from unclosed actions. These metrics reveal coordination debt, not only system downtime.",
            "The illustrative gate shows containment passing and business-truth ownership breaching. It is intentionally possible—and common—for the visible outage to end before the incident is actually controlled.",
        ],
        "scorecard_title": "AI-agent incident command scorecard",
        "metrics": [["p99 authority containment", "74 s", "≤ 90 s", "PASS"], ["Action inventory completeness", "99.96%", "≥ 99.9%", "PASS"], ["Ambiguities owned in 15 min", "93.4%", "100%", "BREACH"], ["Compensation success", "99.6%", "≥ 99%", "PASS"], ["Decision log completeness", "100%", "100%", "PASS"]],
        "metrics_table": [["MTTC", "Escalate containment paths", "New authority remains reachable"], ["Inventory completeness", "Widen discovery before closure", "Impact statement may be understated"], ["Ambiguity ownership", "Add domain responders", "Business truth has no accountable path"], ["Residual exposure", "Prioritize remediation and communication", "Contained incident is still economically active"]],
        "implementation": [["Pre-assign the command roles.", "Name backups and decision rights before the first incident."], ["Build the action inventory query.", "Join workflow, authority, gateway, verifier, and domain records by action ID."], ["Run a business-effect game day.", "Contain the fleet, then reconcile ambiguous customer and financial actions under a timed exercise."]],
        "references": "<a href=\"https://csrc.nist.gov/pubs/sp/800/61/r3/final\">NIST SP 800-61 Rev. 3</a> integrates incident response across cybersecurity risk management, detection, response, and recovery. The dual-clock and business-effect cells here adapt incident-command principles to agent systems.",
        "boundary": "This is an operating model, not legal advice. Notification duties, evidence holds, customer remedies, and regulatory escalation vary by organization and jurisdiction and require the relevant accountable functions.",
        "conclusion": "An AI-agent incident is closed only when authority is contained, material effects are known, harmed states are repaired or owned, evidence is preserved, and recovery has earned back its scope. Killing the process completes only the first sentence.",
        "question": "Who in your organization can declare both the agent stopped and the business state reconciled?",
        "figure_alts": ["Six-cell AI-agent incident command architecture covering command, containment, business truth, remediation, evidence preservation, and recovery.", "Eight-stage incident lifecycle from effect anomaly detection through authority containment, action reconciliation, remediation, canary, and closure.", "Five-metric incident scorecard showing an ambiguity-ownership breach despite successful authority containment."],
        "figure_captions": ["Incident command separates authority containment from reconstruction of business truth.", "Technical response and business reconciliation meet at an evidence-gated closure decision.", "Fast containment does not compensate for unowned ambiguous effects."],
    },
    {
        "slug": "your-ai-agent-needs-a-change-budget",
        "title": "Your AI Agent Needs a Change Budget",
        "subtitle": "Control rollout by cumulative authority and exposure—not only by how many requests received the new version.",
        "description": "A canary and change-budget model for AI agents using authority-weighted exposure, evidence windows, cohort controls, and automatic rollback.",
        "tags": ["AI agents", "Canary releases", "MLOps", "Risk management", "Enterprise AI"],
        "hook": [
            "A 1% agent canary sounds conservative until that 1% contains the largest customers, the broadest permissions, or the only irreversible actions in the workflow. Traffic percentage is a software deployment measure; authority-weighted exposure is the production safety measure.",
            "Every change—model, prompt, retrieval policy, tool adapter, authorization rule, verifier, or workflow graph—consumes a finite change budget. The control plane should allocate that budget across cohorts, action classes, and time while evidence accumulates.",
        ],
        "thesis": "Roll out agent capability in units of reachable consequence, and spend the budget only where counterfactual evidence can detect harm.",
        "failure_heading": "Request-count canaries misprice heterogeneous risk",
        "failure": [
            "Two actions can consume one request each while differing by six orders of magnitude in exposure. A summary draft and a binding commercial amendment should not contribute equally to canary size. Nor should a low-risk test population justify a high-risk rollout whose data and authority distribution is different.",
            "Agent changes also interact. A stronger model paired with a stale verifier or broader retrieval scope may increase effective authority even if each component passed in isolation. The release unit must name the full route bundle and the policies it depends on.",
        ],
        "architecture_heading": "Create an authority-weighted release controller",
        "architecture": [
            "A change manifest identifies model, prompts, tools, schemas, policies, verification, and recovery versions. A cohort planner samples by risk tier and action class. The budget service computes cumulative exposure. Shadow and counterfactual evaluators compare candidate and control before effect authority expands.",
            "At runtime, a gate tracks outcome quality, policy violations, ambiguous effects, tail loss, latency, cost, and distribution shift. It can hold, reduce, or roll back the cohort. Rollback advances an epoch so already-issued authority does not survive the release decision.",
        ],
        "architecture_nodes": [["Manifest", "Version the full agent route bundle"], ["Segment", "Cohorts by action, risk and data"], ["Allocate", "Authority-weighted change budget"], ["Evaluate", "Shadow, canary and counterfactual evidence"], ["Gate", "Quality, loss, ambiguity and drift"], ["Promote", "Expand, hold, reduce or rollback"]],
        "design_rule": "No cohort expansion unless its own risk-weighted evidence passes and cumulative exposure remains inside budget.",
        "flow_title": "Evidence-gated agent rollout",
        "flow_subtitle": "Authority expands only after each cohort earns promotion.",
        "flow_states": [["OFFLINE", "Claims and scenarios pass"], ["SHADOW", "No business effects"], ["CANARY-1", "Low-risk reversible cohort"], ["CANARY-2", "Representative bounded cohort"], ["HOLD", "Evidence window completes"], ["EXPAND", "Budget permits more authority"], ["ROLLBACK", "Epoch revokes candidate"], ["GENERAL", "Ongoing drift gates remain"]],
        "flow_guard": "A larger sample is not safer when it increases risk concentration faster than it increases diagnostic evidence.",
        "model_heading": "Define canary size as exposure",
        "model_intro": "Let every action contribute an authority-weighted exposure unit:",
        "formula": "Exposure(C) = Σ_{a∈C} value(a) × irreversibility(a) × scope(a) × uncertainty(a)\nBudget_remaining = B_period - Σ Exposure(changes)\npromote iff ΔQuality_LCB ≥ 0 ∧ ΔLoss_UCB ≤ L_max ∧ Exposure(next) ≤ Budget_remaining",
        "model_explanation": "LCB and UCB denote conservative confidence bounds. The equation prevents promotion on an attractive average when uncertainty around quality or loss still crosses the operating limit.",
        "control_table": [["Release dimension", "Evidence", "Promotion blocker"], [["Capability", "Scenario and mutation tests", "Critical invariant failure"], ["Cohort", "Representative risk distribution", "Coverage gap"], ["Effect", "Independent postconditions", "Ambiguity or duplicate"], ["Economics", "Cost and conditional loss", "Tail budget breach"], ["Control", "Rollback and epoch proof", "Stale authority accepted"]]],
        "contract_heading": "Version the entire change surface",
        "contract_intro": "The release manifest should make hidden coupling inspectable:",
        "code_language": "yaml",
        "code": "release: agent-route-2026.09.03-rc2\nmodel: route-bundle-17\nprompt: planner-42\nretrieval_policy: evidence-11\ntool_contracts: crm-v8\npolicy_bundle: pricing-2026.09.3\nverifier: quote-assertions-v6\nrecovery: compensation-v4\ncohort:\n  risk_tiers: [low, moderate]\n  exposure_budget_units: 250\nrollback:\n  advance_epoch: true",
        "contract_explanation": "Any material component change creates a new manifest. This makes causal analysis possible when performance moves and prevents a prompt rollback from leaving a changed policy or adapter in place.",
        "operations_heading": "Track budget burn and evidence quality",
        "operations": [
            "Monitor exposure consumed, evidence earned per exposure unit, cohort representativeness, worst-segment quality, ambiguity, conditional tail loss, rollback time, and stale-authority rejection. The best rollout maximizes learning per unit of consequence, not raw traffic.",
            "The synthetic gate shows overall quality passing while the worst-segment lower bound breaches. Global averages must not authorize expansion over an underserved or high-risk cohort.",
        ],
        "scorecard_title": "Authority-weighted change budget scorecard",
        "metrics": [["Overall quality delta", "+1.8 pp", "LCB ≥ 0", "PASS"], ["Worst-segment quality LCB", "-0.7 pp", "≥ 0", "BREACH"], ["Ambiguous material effects", "0", "0", "PASS"], ["Exposure budget consumed", "61%", "≤ 80%", "PASS"], ["p99 rollback enforcement", "44 s", "≤ 60 s", "PASS"]],
        "metrics_table": [["Exposure budget burn", "Hold competing changes", "Too much consequence changed at once"], ["Evidence per exposure", "Redesign cohort", "Canary is risky but uninformative"], ["Worst-segment bound", "Block expansion", "Average hides localized harm"], ["Rollback enforcement", "Contain on breach", "Candidate authority persists after decision"]],
        "implementation": [["Build manifests for current releases.", "Capture every component that can change agent behavior or authority."], ["Define exposure units.", "Start ordinal if needed, but include value, reversibility, scope, and uncertainty."], ["Run cohort-specific gates.", "Promote only when representative segments pass conservative outcome and rollback evidence."]],
        "references": "Google SRE defines <a href=\"https://sre.google/workbook/canarying-releases/\">canarying</a> as a partial, time-limited deployment evaluated against a control, and describes gradual rollout with verification in <a href=\"https://sre.google/sre-book/reliable-product-launches/\">reliable product launches</a>. Authority-weighted exposure is an agent-specific extension.",
        "boundary": "Exposure units need not claim exact monetary truth. An ordinal, documented model can still be superior to raw request percentage if it reliably distinguishes reversible internal work from concentrated material authority.",
        "conclusion": "The right question is not ‘what percentage of traffic has the new agent?’ It is ‘how much consequential authority has changed, what evidence has that exposure bought, and can we revoke it before the loss budget is exhausted?’",
        "question": "Would your current 1% canary still look small after weighting the actions by value, reversibility, and permission scope?",
        "figure_alts": ["Six-stage authority-weighted AI-agent release architecture covering manifest, cohort segmentation, change budget, evaluation, gating, and promotion.", "Eight-stage evidence-gated rollout flow from offline tests and shadowing through canaries, hold, expansion, rollback, and general availability.", "Five-metric change-budget scorecard showing a worst-segment quality breach despite positive overall quality."],
        "figure_captions": ["The release controller prices cumulative authority rather than raw request share.", "Each cohort earns expansion with outcome, risk, and rollback evidence.", "A favorable global average cannot override a failing segment-level confidence bound."],
    },
    {
        "slug": "an-agents-context-window-is-a-data-boundary",
        "title": "An Agent's Context Window Is a Data Boundary",
        "subtitle": "Every retrieved token crosses a purpose, provenance, residency, retention, and disclosure decision.",
        "description": "A governed context architecture for enterprise AI agents using purpose-bound retrieval, policy filtering, provenance, minimization, residency, and deletion evidence.",
        "tags": ["AI agents", "Data governance", "Privacy", "RAG", "Enterprise architecture"],
        "hook": [
            "A context window is often drawn as an empty rectangle waiting to be filled. In an enterprise, every token placed inside it came from a system, a person, a jurisdiction, a retention policy, and a purpose that may or may not permit this use.",
            "Retrieval quality therefore cannot be reduced to relevance. The context assembler must prove that the agent is allowed to use this specific data for this specific action, that the source is fresh and attributable, and that the prompt, cache, trace, and downstream provider do not silently become new retention systems.",
        ],
        "thesis": "Context is a governed, time-bounded data product assembled for one decision—not a bag of convenient text.",
        "failure_heading": "More relevant context can increase the wrong kind of accuracy",
        "failure": [
            "A retriever can improve answer relevance by adding an old contract, another region's customer data, a private manager note, or a support transcript collected for a different purpose. The model may become more confident while the system becomes less defensible.",
            "Context poisoning is also a governance problem. Retrieved instructions can attempt to redirect tools or exfiltrate data. The assembler must label content as evidence, not authority; isolate instructions; score trust and freshness; and prevent retrieved text from modifying policy or tool scope.",
        ],
        "architecture_heading": "Put a context policy plane before retrieval",
        "architecture": [
            "The request first becomes a typed purpose, principal, action, resource, jurisdiction, and retention class. A policy decision computes eligible sources and fields. Retrieval runs only over that allowed set. A trust layer scores provenance, freshness, conflict, and poisoning signals before minimization selects the smallest sufficient evidence bundle.",
            "The assembled context carries field-level lineage and expiry. The model receives tagged evidence and a separate trusted instruction channel. Caches use the same purpose and tenant partition. Telemetry stores digests and identifiers by default. A deletion ledger proves derived indexes and caches honored source deletion.",
        ],
        "architecture_nodes": [["Purpose", "Principal, action and jurisdiction typed"], ["Authorize", "Eligible sources and fields computed"], ["Retrieve", "Search only within allowed scope"], ["Qualify", "Provenance, freshness and poisoning"], ["Minimize", "Smallest sufficient evidence bundle"], ["Expire", "Cache, lineage and deletion verified"]],
        "design_rule": "No token enters context without a source, allowed purpose, trust label, and expiry path.",
        "flow_title": "Governed context assembly",
        "flow_subtitle": "Relevance is evaluated only inside an authorized source set.",
        "flow_states": [["REQUEST", "Purpose and action typed"], ["POLICY", "Source eligibility decided"], ["SEARCH", "Tenant and region constrained"], ["QUALIFY", "Trust, age and conflict scored"], ["MINIMIZE", "Evidence budget applied"], ["ASSEMBLE", "Lineage and labels attached"], ["EXECUTE", "Trusted instructions stay separate"], ["EXPIRE", "Caches and derivatives deleted"]],
        "flow_guard": "Retrieved content may inform a decision; it never grants itself authority or changes the retrieval policy.",
        "model_heading": "Optimize sufficient evidence under privacy constraints",
        "model_intro": "Context selection can be framed as a constrained set problem:",
        "formula": "S* = argmin_S Σ_{d∈S} privacy_cost(d) + token_cost(d) + staleness_cost(d)\nsubject to: EvidenceCoverage(S) ≥ τ\n            allowed(d, purpose, principal, region) = true ∀ d∈S\n            trust(d) ≥ trust_min",
        "model_explanation": "The objective discourages copying everything ‘just in case.’ Coverage is defined over claims required for the action, not semantic similarity alone. Hard policy constraints are never traded away for relevance.",
        "control_table": [["Context field", "Required control", "Failure response"], [["Source", "Stable record ID + version", "Exclude unattributed text"], ["Purpose", "Allowed-use decision", "Deny or route to review"], ["Trust", "Provenance and poisoning label", "Quarantine or down-rank"], ["Freshness", "Source-specific expiry", "Re-fetch or mark unknown"], ["Deletion", "Derivative lineage", "Purge and verify"]]],
        "contract_heading": "Make context items typed records",
        "contract_intro": "A context item should arrive with governance metadata, not only text:",
        "code_language": "json",
        "code": '{\n  "record_id": "contract:MSA-771",\n  "version": "2026-06-14T09:21:00Z",\n  "purpose": ["renewal_risk_review"],\n  "tenant": "customer:A-1902",\n  "region": "IN",\n  "trust": {"provenance": "authoritative", "poisoning": "low"},\n  "valid_until": "2026-09-03T13:00:00Z",\n  "content_digest": "sha256:...",\n  "deletion_lineage": ["index:revops-v7", "cache:ctx-91"]\n}',
        "contract_explanation": "The model can receive a rendered projection, but the control plane retains the record structure. Evidence citations resolve back to the exact source version, and deletion traverses the derivative lineage.",
        "operations_heading": "Measure context governance as an SLO",
        "operations": [
            "Track unauthorized retrieval attempts, purpose-coverage, field minimization, stale-evidence rate, provenance completeness, poisoning quarantine, cross-tenant isolation tests, cache expiry, and deletion verification. Token utilization alone rewards the wrong behavior.",
            "The synthetic gate shows strong provenance and isolation while deletion verification breaches. A system that removes a source but cannot prove derivative removal does not yet have a complete context lifecycle.",
        ],
        "scorecard_title": "Governed context operating scorecard",
        "metrics": [["Provenance completeness", "99.98%", "≥ 99.9%", "PASS"], ["Cross-tenant isolation tests", "100%", "100%", "PASS"], ["Stale critical evidence", "0.03%", "≤ 0.05%", "PASS"], ["Deletion verified in 24 h", "97.6%", "≥ 99.9%", "BREACH"], ["Raw prompt payload in logs", "0", "0", "PASS"]],
        "metrics_table": [["Unauthorized retrieval", "Block action and investigate", "Policy scope or tenant isolation failed"], ["Provenance completeness", "Prevent material decision", "Evidence cannot be defended"], ["Stale critical evidence", "Re-fetch or reapprove", "Decision moment is invalid"], ["Deletion completion", "Stop affected index/cache", "Derived stores outlived source rights"]],
        "implementation": [["Type one decision purpose.", "Name required claims, eligible sources, fields, region, and retention for a material workflow."], ["Separate evidence from instruction.", "Tag retrieved content and prevent it from changing policy, tools, or system prompts."], ["Prove deletion end to end.", "Delete a seeded source and verify indexes, caches, traces, and exported evidence honor the lineage."]],
        "references": "The <a href=\"https://www.nist.gov/privacy-framework\">NIST Privacy Framework</a> provides a voluntary enterprise approach to identifying and managing privacy risk. The <a href=\"https://airc.nist.gov/airmf-resources/airmf/5-sec-core/\">NIST AI RMF Core</a> includes privacy-risk examination, documented context, and ongoing risk tracking. The context-record design here is an engineering proposal.",
        "boundary": "This article is not legal advice and does not assert that one metadata schema satisfies any jurisdiction. Data-protection, residency, employment, and sector requirements need qualified organizational review.",
        "conclusion": "The context window is not outside the data architecture. It is a temporary, high-consequence integration surface. Govern it with the same seriousness as a database view—plus stronger controls for purpose, instruction isolation, and derivative deletion.",
        "question": "Can you identify the source, allowed purpose, and deletion path for every material token your agent used?",
        "figure_alts": ["Six-stage governed context architecture from typed purpose and authorization through constrained retrieval, qualification, minimization, and expiry.", "Eight-stage context assembly flow enforcing eligible sources, trust, freshness, minimization, instruction separation, and derivative deletion.", "Five-metric context governance scorecard showing a deletion-verification breach despite strong provenance and tenant isolation."],
        "figure_captions": ["Context assembly begins with purpose and policy before semantic search.", "Evidence remains distinct from trusted instructions throughout the action lifecycle.", "Derivative deletion is a production gate, not an archival afterthought."],
    },
    {
        "slug": "revenue-operations-needs-an-agent-decision-ledger",
        "title": "Revenue Operations Needs an Agent Decision Ledger",
        "subtitle": "Connect AI recommendations, approvals, CRM changes, customer outcomes, and economics without turning the CRM into an audit fiction.",
        "description": "A RevOps decision-ledger architecture linking evidence, agent proposals, human approvals, commercial authority, CRM effects, and revenue outcomes.",
        "tags": ["Revenue operations", "AI agents", "CRM", "Decision intelligence", "Enterprise architecture"],
        "hook": [
            "Revenue teams can often reconstruct what changed in CRM. They struggle to prove why it changed, which evidence the agent used, whether a human approved the exact commercial delta, what downstream systems observed, and whether the intervention improved revenue.",
            "Adding more fields to the opportunity record does not solve this. CRM is optimized for current operational state. An agent decision ledger is optimized for causality, authority, versioned evidence, outcome attribution, and retrospective learning.",
        ],
        "thesis": "Keep CRM as a system of operational record; add a decision ledger as the system of accountable commercial action.",
        "failure_heading": "The latest field value erases the decision path",
        "failure": [
            "An opportunity stage can move from commit to upside and back to commit in one day. The current row does not reveal which agent signal caused the first change, which seller overrode it, what quote version was approved, or whether the renewal closed because of the action or despite it.",
            "Without stable decisions and counterfactual cohorts, RevOps can confuse activity with value. High acceptance may indicate useful recommendations, compliant reviewers, or rubber-stamping. More pipeline movement may represent improved truth—or unstable automation rewriting the forecast.",
        ],
        "architecture_heading": "Separate operational state, decisions, and outcomes",
        "architecture": [
            "The evidence layer snapshots versioned CRM, support, product, finance, and conversation facts. The decision service records proposed action, alternatives, model route, policy, and uncertainty. Approval and permission services bind accountable authority. Domain gateways apply changes. Independent observers capture business effects. The outcome service joins later renewal, margin, retention, and customer signals.",
            "The ledger is append-only at the decision level. Corrections create superseding records rather than rewriting history. Sensitive source content remains in its governed system; the ledger stores typed claims, references, digests, and permitted analytical projections.",
        ],
        "architecture_nodes": [["Evidence", "Versioned revenue and customer facts"], ["Decision", "Proposal, alternatives and uncertainty"], ["Authority", "Policy, approval and commercial limits"], ["Effect", "CRM and downstream mutations observed"], ["Outcome", "Revenue, margin and retention windows"], ["Learn", "Attribution, calibration and policy updates"]],
        "design_rule": "Every material revenue action must link the evidence moment, accountable authority, observed effect, and outcome window.",
        "flow_title": "RevOps agent decision lifecycle",
        "flow_subtitle": "The ledger joins a decision to both immediate effects and delayed revenue outcomes.",
        "flow_states": [["SNAPSHOT", "Evidence moment versioned"], ["PROPOSE", "Action and alternatives recorded"], ["POLICY", "Limits and review path decided"], ["APPROVE", "Exact commercial delta bound"], ["EXECUTE", "Domain gateway mutates state"], ["VERIFY", "CRM and downstream effect read"], ["OBSERVE", "Outcome window matures"], ["LEARN", "Attribution and calibration update"]],
        "flow_guard": "No outcome claim is attached before its measurement window and attribution assumptions are explicit.",
        "model_heading": "Measure incremental value, not agent activity",
        "model_intro": "For a policy or intervention cohort, estimate risk-adjusted incremental value:",
        "formula": "V_incremental = (P_outcome|treat - P_outcome|control) × MarginValue\n              - C_action - C_review - C_delay - E[L_commercial_error]\nCalibration_gap = |predicted_lift - observed_lift| by segment",
        "model_explanation": "The control may be randomized where appropriate, staggered, matched, or constructed with causal methods. The ledger cannot manufacture causality; it supplies the stable treatment, decision, effect, and outcome records required to assess it.",
        "control_table": [["Ledger record", "Key fields", "RevOps question"], [["Evidence moment", "source versions + claims", "What was known then?"], ["Decision", "alternatives + predicted lift", "Why this action?"], ["Authority", "policy + approver + limit", "Who permitted the delta?"], ["Effect", "observed state + uniqueness", "What actually changed?"], ["Outcome", "window + margin + segment", "Did it create incremental value?"]]],
        "contract_heading": "Use one commercial action identifier across systems",
        "contract_intro": "The identifier should travel from recommendation to revenue outcome:",
        "code_language": "json",
        "code": '{\n  "commercial_action_id": "revact_01K...",\n  "account": "A-1902",\n  "evidence_moment": "ev_882",\n  "proposal": {"action": "discount", "bps": 800},\n  "predicted_incremental_margin": 42000,\n  "policy": "pricing-2026.09.3",\n  "approval": "apr_52",\n  "effects": ["crm:quote:771:v43", "billing:adj:991"],\n  "outcome_window_days": 90\n}',
        "contract_explanation": "CRM can store the current action link, but the ledger owns the immutable sequence. Finance and customer-success outcomes join later without overwriting the original prediction.",
        "operations_heading": "Build a decision-quality operating model",
        "operations": [
            "Track recommendation coverage, acceptance by risk tier, approval override reason, time to decision, effect verification, margin leakage, predicted-versus-observed calibration, incremental outcome by cohort, and unresolved commercial actions. Avoid ranking sellers on raw agent acceptance.",
            "The synthetic gate shows effect verification passing while calibration breaches. That tells RevOps to constrain or recalibrate the intervention—not to celebrate a high action count.",
        ],
        "scorecard_title": "RevOps agent decision-ledger scorecard",
        "metrics": [["Material effect verification", "99.97%", "≥ 99.9%", "PASS"], ["Approval override captured", "98.9%", "≥ 98%", "PASS"], ["Lift calibration error", "7.4 pp", "≤ 4 pp", "BREACH"], ["Margin leakage", "0.18%", "≤ 0.25%", "PASS"], ["Unowned commercial ambiguity", "0", "0", "PASS"]],
        "metrics_table": [["Lift calibration", "Recalibrate by segment", "Predicted value is not decision-grade"], ["Override reasons", "Improve policy or evidence", "Humans see systematic missing context"], ["Effect verification", "Stop outcome attribution if incomplete", "Treatment state is uncertain"], ["Margin leakage", "Tighten limits and approval", "Commercial authority is too broad"]],
        "implementation": [["Choose one revenue decision.", "Start with discount, renewal risk, forecast override, or next-best action—not every CRM event."], ["Propagate one action ID.", "Link evidence, recommendation, approval, permission, CRM effect, billing effect, and outcome window."], ["Run a decision review.", "Compare predicted and observed lift by segment, inspect overrides, and update policy without rewriting the ledger."]],
        "references": "The <a href=\"https://opentelemetry.io/docs/specs/otel/overview/\">OpenTelemetry specification overview</a> provides concepts for correlating distributed execution signals. The <a href=\"https://airc.nist.gov/airmf-resources/airmf/5-sec-core/\">NIST AI RMF Core</a> emphasizes documented context, benefits, risks, monitoring, and ongoing management. Neither defines this RevOps ledger; it is a domain architecture proposal.",
        "boundary": "Incremental revenue measurement requires careful experimental or causal design. The illustrative formula and metrics are not claims about a deployed account, and the ledger should not be used as a simplistic employee-surveillance or performance-ranking system.",
        "conclusion": "RevOps should be able to move from ‘the agent changed the CRM’ to ‘this approved decision used these facts, created this verified effect, consumed this commercial authority, and produced this measured outcome under these attribution assumptions.’ That is the foundation for scaling revenue agents responsibly.",
        "question": "Can your CRM explain the causal and authority path behind its most important automated field change?",
        "figure_alts": ["Six-layer revenue-operations decision ledger architecture linking evidence, proposals, commercial authority, verified effects, outcomes, and learning.", "Eight-stage RevOps agent action flow from evidence snapshot and proposal through approval, execution, outcome observation, and calibration.", "Five-metric RevOps decision scorecard showing a lift-calibration breach despite strong effect verification and margin control."],
        "figure_captions": ["The decision ledger complements CRM by preserving causality, authority, and outcome lineage.", "One commercial action identifier survives from evidence moment to delayed outcome analysis.", "High execution quality does not compensate for poorly calibrated value predictions."],
    },
    {
        "slug": "the-hardest-agent-failure-is-an-ambiguous-success",
        "title": "The Hardest Agent Failure Is an Ambiguous Success",
        "subtitle": "When the system says ‘done’ but the business state is partial, duplicated, delayed, or impossible to prove.",
        "description": "A production architecture for classifying and resolving ambiguous AI-agent outcomes across partial commits, asynchronous effects, stale reads, and compensation.",
        "tags": ["AI agents", "Failure engineering", "Distributed systems", "Verification", "Reliability"],
        "hook": [
            "Clear failures are operationally generous. They stop the workflow and give an operator something concrete to inspect. Ambiguous success is worse: the API accepted the request, part of the workflow progressed, downstream state will settle later, and every dashboard chooses a different definition of done.",
            "Agents amplify this ambiguity because they chain tools, reinterpret responses, and continue planning. A plausible success narrative can be generated before authoritative systems agree on the business outcome.",
        ],
        "thesis": "Success is not a status code. It is a verified postcondition reached before an economic deadline, with every partial effect accounted for.",
        "failure_heading": "One success label collapses four distinct states",
        "failure": [
            "A command can be accepted but not committed, committed but not propagated, partially committed across systems, or committed more than once. A stale read can make a good effect look absent; an optimistic tool adapter can make a rejected effect look complete. Collapsing these states prevents correct retry and recovery.",
            "The workflow needs an outcome taxonomy and evidence precedence. Provider acceptance, durable workflow state, authoritative resource version, downstream ledger state, and customer-visible effect are separate observations with different lag and authority.",
        ],
        "architecture_heading": "Create an outcome-resolution service",
        "architecture": [
            "The service starts with a typed intended postcondition and a completion deadline. It collects observations from independent systems, applies source-specific lag models, and classifies the action as confirmed success, confirmed failure, partial, duplicate, delayed, inconsistent, or unknown.",
            "A policy maps each class to wait, re-observe, reconcile, compensate, freeze, or human decision. The agent can provide hypotheses, but only the resolution service advances terminal state and seals the receipt.",
        ],
        "architecture_nodes": [["Expect", "Typed postcondition and deadline"], ["Collect", "Independent source observations"], ["Normalize", "Versions, lag and action identity"], ["Classify", "Success, partial, duplicate or unknown"], ["Resolve", "Wait, compensate, freeze or review"], ["Close", "Terminal evidence and receipt sealed"]],
        "design_rule": "A workflow cannot claim success while a material observation remains inconsistent or outside its evidence deadline.",
        "flow_title": "Ambiguous-success resolution",
        "flow_subtitle": "Partial and delayed outcomes retain distinct operational paths.",
        "flow_states": [["ACCEPTED", "Provider received request"], ["PENDING", "Commit not yet observable"], ["PARTIAL", "Some postconditions hold"], ["INCONSISTENT", "Sources disagree"], ["DUPLICATE", "More than one effect found"], ["CONFIRMED", "All assertions hold"], ["RECOVER", "Compensate or freeze"], ["CLOSED", "Evidence and owner complete"]],
        "flow_guard": "Do not let an agent convert ‘accepted’ or ‘no exception’ into a terminal business-success state.",
        "model_heading": "Use evidence age and consequence to choose the next observation",
        "model_intro": "For observation source <code>s</code>, prioritize information value net of delay and query cost:",
        "formula": "VOI(s,t) = ExpectedReduction[OutcomeEntropy | observe(s,t)]\n           - C_query(s) - C_delay(t)\nresolve when posterior confidence crosses class threshold AND required authoritative assertions hold",
        "model_explanation": "Confidence alone cannot override a mandatory assertion. The model helps order observations; policy defines which facts are indispensable for commercial or safety closure.",
        "control_table": [["Outcome class", "Evidence pattern", "Permitted transition"], [["Pending", "Within known propagation lag", "Wait and observe"], ["Partial", "Subset of assertions true", "Complete or compensate"], ["Inconsistent", "Authoritative sources disagree", "Freeze and reconcile"], ["Duplicate", "Count exceeds one", "Contain and compensate"], ["Confirmed", "All required assertions hold", "Seal success receipt"]]],
        "contract_heading": "Represent success as a set of assertions",
        "contract_intro": "A compound business action needs more than one boolean:",
        "code_language": "yaml",
        "code": "outcome_contract: renewal-adjustment-v3\ndeadline_seconds: 300\nassertions:\n  - source: crm-primary\n    expect: quote.version == 43 and quote.discount_bps == 800\n  - source: billing-ledger\n    expect: count(adjustment where action_id == A) == 1\n  - source: communication-log\n    expect: message.approval_ref == approval_id\nterminal_success: all(assertions)\non_deadline: freeze_and_assign_owner",
        "contract_explanation": "Each assertion carries an evidence source, lag allowance, and failure owner. The contract is versioned with the action so later schema changes cannot silently redefine success.",
        "operations_heading": "Make ambiguity visible as inventory",
        "operations": [
            "Track ambiguous actions by class, age, exposure, dependency, and owner; partial-to-terminal time; duplicate discovery lag; false closures reopened later; and compensation success. The backlog should behave like an incident queue, not a log-search exercise.",
            "The synthetic gate shows p95 resolution passing but false closure breaching. One action closed incorrectly is more serious than a slightly slower but honest unknown.",
        ],
        "scorecard_title": "Ambiguous-success resolution scorecard",
        "metrics": [["p95 ambiguity resolution", "7.8 min", "≤ 10 min", "PASS"], ["False closures", "1", "0", "BREACH"], ["Duplicate discovery in 5 min", "100%", "100%", "PASS"], ["Unowned material outcomes", "0", "0", "PASS"], ["Compensation success", "99.3%", "≥ 99%", "PASS"]],
        "metrics_table": [["False closure", "Incident and control review", "Success criteria or evidence path failed"], ["Partial duration", "Escalate domain owner", "Cross-system completion is stuck"], ["Source inconsistency", "Freeze related authority", "Authoritative systems disagree"], ["Ambiguous exposure", "Prioritize by consequence", "Unknown state is economically material"]],
        "implementation": [["Define one compound success contract.", "List each required business assertion and its authoritative source."], ["Preserve non-terminal states.", "Prevent adapters and agents from flattening accepted, pending, partial, and unknown into success."], ["Fault-test evidence lag.", "Delay replicas, duplicate downstream messages, and partially commit workflows while verifying correct classification and ownership."]],
        "references": "AWS's <a href=\"https://aws.amazon.com/builders-library/making-retries-safe-with-idempotent-APIs/\">idempotent API guidance</a> discusses late requests, retries, and semantic intent. <a href=\"https://www.rfc-editor.org/rfc/rfc9110.html\">RFC 9110</a> distinguishes request-method semantics from application-specific outcomes. The compound outcome taxonomy is a proposed agent control.",
        "boundary": "Evidence can remain uncertain beyond the deadline. The correct response is owned ambiguity and controlled recovery—not a fabricated terminal label.",
        "conclusion": "The most dangerous agent success is the one nobody can independently reproduce. Make success a contract over observable business state, preserve every non-terminal class, and let recovery begin before ambiguity becomes history.",
        "question": "Which of your agent workflows can return success before all downstream business assertions are observable?",
        "figure_alts": ["Six-stage outcome-resolution architecture from expected postconditions and independent evidence through classification, recovery, and receipt closure.", "Eight-state ambiguous-success flow distinguishing accepted, pending, partial, inconsistent, duplicate, confirmed, recovery, and closed outcomes.", "Five-metric ambiguity scorecard showing a false-closure breach despite fast typical resolution and complete ownership."],
        "figure_captions": ["Outcome resolution is an independent service, not a planner self-assessment.", "Accepted, pending, partial, inconsistent, and duplicate are separate operational states.", "One false closure can fail the gate even when latency and recovery averages pass."],
    },
    {
        "slug": "your-ai-agent-needs-a-fencing-token",
        "title": "Your AI Agent Needs a Fencing Token",
        "subtitle": "Leases expire in time; fencing tokens make stale authority lose at the effect boundary.",
        "description": "A production design for monotonic fencing tokens that prevent stale AI-agent workers, leases, queues, and retries from committing business effects.",
        "tags": ["AI agents", "Distributed systems", "Fencing tokens", "Authorization", "Reliability"],
        "hook": [
            "A worker pauses for ninety seconds, its lease expires, another worker takes ownership, and then the first worker resumes. If the CRM gateway validates only a signed token and wall-clock expiry, both workers may believe they are legitimate at different moments—and the stale one may still commit last.",
            "Lease expiry limits time. It does not guarantee that every downstream effect boundary agrees which owner is current. Fencing adds a monotonically increasing epoch that lets the resource reject commands from older owners, even when networks delay or processes resume.",
        ],
        "thesis": "A lease tells the holder when authority should end. A fencing token lets the resource prove that stale authority has already been superseded.",
        "failure_heading": "Clock validity is not ownership validity",
        "failure": [
            "Distributed workers do not share a perfect clock or failure view. A process can stop receiving heartbeats while continuing to run. A queued command can arrive after reassignment. A cached credential can remain cryptographically valid while operational ownership has advanced.",
            "The effect gateway therefore needs a resource-scoped epoch. It stores the highest accepted fence and rejects any lower value. Issuance must be linearizable for the ownership domain; comparison must happen atomically with the mutation or at the last authoritative write boundary.",
        ],
        "architecture_heading": "Fence ownership at the domain gateway",
        "architecture": [
            "An ownership service allocates monotonically increasing fences when work is acquired or authority is reissued. The workflow attaches the fence to every message, tool request, receipt, and compensation command. The domain gateway compares it with the resource's current fence before applying the versioned business mutation.",
            "Fences complement, rather than replace, idempotency keys and permission leases. The idempotency key prevents the same action from duplicating; the resource version prevents stale data writes; the lease bounds scope and time; the fence prevents a superseded owner from acting.",
        ],
        "architecture_nodes": [["Acquire", "Ownership service increments epoch"], ["Bind", "Lease and action carry fence"], ["Propagate", "Messages preserve fence unchanged"], ["Compare", "Gateway reads highest resource fence"], ["Commit", "Atomic fence, version and effect write"], ["Reject", "Stale owner receives terminal denial"]],
        "design_rule": "The final effect boundary—not the worker—decides whether an ownership epoch is current.",
        "flow_title": "Fenced ownership transition",
        "flow_subtitle": "Delayed work cannot overtake the current owner.",
        "flow_states": [["OWNER-41", "Worker A holds fence 41"], ["PAUSE", "Heartbeat lost; work may continue"], ["OWNER-42", "Worker B acquires fence 42"], ["COMMIT-42", "Gateway advances current fence"], ["RESUME-41", "Stale worker sends command"], ["COMPARE", "41 < current 42"], ["REJECT", "No business mutation"], ["RECONCILE", "Stale action receives closure"]],
        "flow_guard": "A valid signature and unexpired timestamp never override a lower fencing epoch.",
        "model_heading": "Define acceptance as a conjunction",
        "model_intro": "The gateway accepts an action only when every control is current:",
        "formula": "accept(a) = signature_valid(a)\n         ∧ lease_not_expired(a)\n         ∧ fence(a) ≥ fence_current(resource)\n         ∧ version(a) = version_current(resource)\n         ∧ idempotency_state(a.id) ∈ {new, same_result}",
        "model_explanation": "The exact fence comparison depends on whether a command may establish a new current epoch. What matters is atomicity: another writer cannot advance the fence between the check and the business mutation.",
        "control_table": [["Control", "Stops", "Does not stop"], [["Signature", "Forged commands", "Superseded signed owner"], ["Lease expiry", "Late use after time bound", "Delayed command accepted before expiry check divergence"], ["Fencing token", "Stale ownership epoch", "Duplicate from current owner"], ["Idempotency key", "Repeated same action", "Different stale action"], ["Resource version", "Lost update", "Authorized duplicate on new object"]]],
        "contract_heading": "Carry the fence through every hop",
        "contract_intro": "The command envelope must make ownership explicit:",
        "code_language": "json",
        "code": '{\n  "workflow_id": "renewal-771",\n  "action_id": "act_01K...",\n  "owner": "worker:B",\n  "fence": 42,\n  "lease_id": "lease_91",\n  "resource": "quote:771",\n  "expected_version": 42,\n  "command_digest": "sha256:..."\n}\n\ngateway: compare-and-set(highest_fence, resource_version, action_id, mutation)',
        "contract_explanation": "Brokers, workflow engines, and tool adapters must not strip or regenerate the fence. A compensation action may require a new action identity but still carries the current ownership epoch.",
        "operations_heading": "Test stale-owner rejection continuously",
        "operations": [
            "Track stale-fence attempts, stale-fence accepts, fence allocation latency, epoch gaps, resources without enforcement, ownership handoff duration, and commands missing fences. The non-negotiable SLO is zero material stale-fence accepts.",
            "The synthetic gate shows enforcement coverage below target. A perfect reject rate on the fenced subset does not justify production confidence while some gateways remain outside the protocol.",
        ],
        "scorecard_title": "Fenced authority operating scorecard",
        "metrics": [["Material stale-fence accepts", "0", "0", "PASS"], ["Effect gateways enforcing fence", "98.7%", "100%", "BREACH"], ["p99 fence allocation", "31 ms", "≤ 50 ms", "PASS"], ["Commands missing fence", "0", "0", "PASS"], ["Ownership handoff p99", "1.8 s", "≤ 3 s", "PASS"]],
        "metrics_table": [["Stale-fence accepts", "Contain affected domain", "Superseded owners can mutate state"], ["Enforcement coverage", "Block wider autonomy", "Protocol ends before some effects"], ["Epoch allocation", "Scale ownership service", "Handoffs delay or fail"], ["Missing-fence commands", "Reject and identify legacy caller", "Uncontrolled path bypasses ownership"]],
        "implementation": [["Choose one contested resource.", "Use a quote, case, account assignment, or workflow partition with concurrent workers."], ["Add monotonic epochs.", "Issue them from a consistency boundary appropriate to that resource scope."], ["Prove stale rejection.", "Pause an owner, reassign work, resume the stale process, and verify the domain gateway rejects every delayed command."]],
        "references": "This pattern builds on established distributed-systems fencing concepts and complements the idempotency concerns in AWS's <a href=\"https://aws.amazon.com/builders-library/making-retries-safe-with-idempotent-APIs/\">safe retry guidance</a>. The specific agent lease, fence, version, and idempotency composition is an architectural proposal.",
        "boundary": "A global fence service can become a bottleneck or single failure domain. Scope epochs to the smallest consistency domain that must reject stale ownership, and test allocation behavior under partitions and failover.",
        "conclusion": "Short-lived authority reduces exposure. Fencing makes revocation and reassignment real at the point where business state changes. Without it, a stale but valid worker can still write the last word.",
        "question": "If an agent worker resumes after its task was reassigned, which system proves its next command is stale?",
        "figure_alts": ["Six-stage fencing-token architecture from monotonic ownership acquisition and lease binding through propagation, gateway comparison, commit, and stale rejection.", "Eight-state ownership handoff flow demonstrating how fence 42 prevents a resumed worker holding fence 41 from committing.", "Five-metric fencing scorecard showing incomplete gateway enforcement despite zero observed stale-owner accepts."],
        "figure_captions": ["Fencing is enforced at the final domain write boundary.", "A resumed stale worker loses because the resource has already accepted a higher epoch.", "Observed rejection success is insufficient while any material gateway lacks fence enforcement."],
    },
]


LINKEDIN = {
    "your-ai-agent-needs-a-transaction-boundary": "A timeout is not a failure. For a material agent action, it is an economically live unknown.\n\nThe production pattern is prepare → authorize → execute → observe → commit, retry, compensate or freeze. One stable action ID, immutable payload digest, resource version and one-use capability make the boundary enforceable.\n\nThe metric I would put on the control-room wall is p99 ambiguity age—not API success rate.\n\nWhere does your agent stack turn an unknown outcome into a guess?\n\n#AgenticAI #DistributedSystems #ReliabilityEngineering #AIGovernance",
    "an-agent-retry-is-a-new-risk-decision": "Exponential backoff protects a dependency. It does not prove a business action is safe to repeat.\n\nFor every mutating agent tool, classify the effect as safe read, idempotent write, conditional write or non-repeatable action. Then price duplicate loss, omission loss, delay and fleet amplification before another attempt.\n\nA fixed three-retry policy assumes attempt three has the same risk as attempt one. It rarely does.\n\nWhich tool in your stack inherited SDK retries without an effect review?\n\n#AgenticAI #Reliability #DistributedSystems #RiskManagement",
    "your-verifier-must-not-trust-the-agent": "The agent says the action succeeded. The tool returned 200. The trace is green.\n\nNone of those proves the approved business state exists.\n\nA high-assurance verifier needs a separate identity, an authoritative evidence path, a typed postcondition and four honest outcomes: verified, violated, inconclusive or expired. The executor cannot be the sole source that certifies itself.\n\nIf your tool adapter lied, which independent system would catch it?\n\n#AIGovernance #AgenticAI #Verification #EnterpriseArchitecture",
    "the-agent-policy-engine-is-a-compiler": "‘Do not offer excessive discounts’ is governance prose, not an execution policy.\n\nA production policy path should parse and type inputs, detect conflicts, run scenario and mutation tests, compile a signed bundle, return obligations, and bind the bundle digest at the gateway.\n\nPermit/deny is not enough. The decision may also require an approver class, maximum value, lease duration, verification level and receipt retention.\n\nCould you reproduce yesterday's authorization from the exact policy artifact?\n\n#PolicyAsCode #AIGovernance #Authorization #AgenticAI",
    "ai-agent-observability-is-not-logging": "A million log lines can describe tokens, prompts and tool calls while failing one executive question: what changed in the business?\n\nAgent observability needs four joined graphs around one action ID: execution, decision, authority and effect—plus the economics and recovery path.\n\nTrace coverage can be 99.99% while risk-weighted effect coverage is below the production gate. That gap is where confident dashboards meet unknown outcomes.\n\nCan your platform answer ‘what business state changed?’ without reading the agent's prose?\n\n#Observability #OpenTelemetry #AgenticAI #ReliabilityEngineering",
    "every-agent-needs-a-safe-degradation-ladder": "Enabled versus disabled is too crude for production agents.\n\nA useful degradation ladder is: bounded autonomous → mandatory review → recommend-only → read-only → contained. Each downward step must remove reachable authority; each upward step must require new evidence and a new authority epoch.\n\nThis preserves useful analysis while reducing consequence before an emergency stop becomes necessary.\n\nCan your system degrade one action class—or only keep everything running until someone pulls the plug?\n\n#Resilience #AIGovernance #IncidentResponse #AgenticAI",
    "who-owns-an-ai-agent-incident": "An agent incident has two clocks.\n\nMTTC measures when every material effect boundary rejects stale authority. MTTB measures when every prior business action is terminal or has an accountable owner.\n\nThe workers can stop in 74 seconds while forty-one ambiguous customer actions remain economically active. Incident command needs separate leads for containment, business truth, remediation and evidence—not one generic technical queue.\n\nWho can declare both the agent stopped and the business state reconciled?\n\n#IncidentResponse #SRE #AIGovernance #AgenticAI",
    "your-ai-agent-needs-a-change-budget": "A 1% canary is not small when it contains the largest customers or the only irreversible actions.\n\nAgent rollout should be measured in authority-weighted exposure: value × irreversibility × scope × uncertainty. Promote only when cohort-specific evidence passes conservative quality and loss bounds—and rollback can revoke the candidate epoch.\n\nTraffic share measures deployment. Exposure measures consequence.\n\nWould your current 1% canary still look small after weighting the actions?\n\n#MLOps #CanaryRelease #RiskManagement #AgenticAI",
    "an-agents-context-window-is-a-data-boundary": "Every retrieved token came from a system, a person, a jurisdiction, a retention policy and a purpose.\n\nContext assembly should start with purpose and authorization, search only eligible sources, qualify provenance and freshness, minimize to sufficient evidence, isolate retrieved content from trusted instructions, and prove derivative deletion.\n\nRelevance is optimized inside policy—not traded against it.\n\nCan you name the source, allowed purpose and deletion path for every material token?\n\n#DataGovernance #PrivacyEngineering #RAG #AgenticAI",
    "revenue-operations-needs-an-agent-decision-ledger": "CRM tells Revenue Operations what the current field says. It rarely proves why an agent changed it, who approved the exact commercial delta, which downstream effect occurred or whether the intervention created incremental value.\n\nKeep CRM as the operational record. Add an append-only decision ledger linking evidence moment → proposal → authority → verified effect → outcome window.\n\nThe target metric is calibrated incremental margin—not agent activity or acceptance rate.\n\nCan your CRM reconstruct the causal path behind its most important automated change?\n\n#RevenueOperations #CRM #DecisionIntelligence #AgenticAI",
    "the-hardest-agent-failure-is-an-ambiguous-success": "The hardest agent failure is a success nobody can independently reproduce.\n\nAccepted, pending, partial, inconsistent, duplicate and confirmed are different business states. A production workflow should keep them separate, observe authoritative postconditions, and allow only the outcome-resolution service to close success.\n\nOne false closure should fail the gate even when average resolution time looks healthy.\n\nWhich workflow can return success before all downstream assertions are observable?\n\n#FailureEngineering #DistributedSystems #Verification #AgenticAI",
    "your-ai-agent-needs-a-fencing-token": "A permission lease can expire while a paused worker continues running. When it resumes, a signature and timestamp may still be insufficient to prove it is the current owner.\n\nAdd a monotonic fencing token. The resource gateway stores the highest accepted epoch and atomically rejects commands from superseded workers.\n\nLease bounds time. Idempotency bounds repetition. Version checks bound stale data. Fencing bounds stale ownership.\n\nWhich system rejects a resumed worker after its task was reassigned?\n\n#DistributedSystems #ZeroTrust #AgenticAI #Reliability",
}


def build_story(story: dict) -> None:
    slug = story["slug"]
    image_dir = IMAGES / slug
    image_dir.mkdir(parents=True, exist_ok=True)
    architecture_svg(story, image_dir / "figure-01.svg")
    flow_svg(story, image_dir / "figure-02.svg")
    scorecard_svg(story, image_dir / "figure-03.svg")
    blocks = story_blocks(story)
    word_count = 0
    for block in blocks:
        word_count += len(block.get("text", "").split())
        word_count += sum(len(strip_html(cell).split()) for cell in block.get("headers", []))
        word_count += sum(len(strip_html(cell).split()) for row in block.get("rows", []) for cell in row)
    payload = {
        "author": "Aditya Singh",
        "id": hashlib.sha256(slug.encode()).hexdigest()[:12],
        "slug": slug,
        "title": story["title"],
        "subtitle": story["subtitle"],
        "description": story["description"],
        "canonical": f"{SITE}/{slug}/",
        "sourceUrl": f"{SITE}/{slug}/",
        "publishedAt": CREATED,
        "modifiedAt": CREATED,
        "status": "editorial_draft",
        "statusLabel": "Editorial draft",
        "readTime": f"{max(6, round(word_count / 210))} min read",
        "wordCount": word_count,
        "tags": story["tags"],
        "heroImage": f"assets/images/{slug}/figure-01.svg",
        "heroAlt": story["figure_alts"][0],
        "blocks": blocks,
    }
    (DATA / f"{slug}.json").write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def build_editorial_files() -> None:
    EDITORIAL.mkdir(parents=True, exist_ok=True)
    rows = []
    for i, story in enumerate(STORIES, 1):
        rows.append(
            f"| {i} | [{story['title']}]({SITE}/{story['slug']}/) | {', '.join(story['tags'][:2])} | "
            f"Extends the existing production-agent control-plane and LinkedIn architecture campaign |"
        )
    readme = """# Next-wave Medium editorial drafts — September 2026

Status: **GitHub Pages editorial drafts; not imported, published, submitted, or scheduled on Medium.**

These ten stories extend the existing production-grade agent series and the September LinkedIn architecture campaign. Each draft has a distinct architecture, state model, decision formula, code contract, operating scorecard, three accessible SVG figures, and a primary-source boundary note. All examples and metrics are explicitly illustrative.

| # | Story and GitHub Pages canonical | Primary domain | Lineage |
|---:|---|---|---|
""" + "\n".join(rows) + """

## Editorial gates before Medium import

1. Aditya completes a human technical review and adds any personal experience he independently chooses to substantiate.
2. Verify each linked primary source and every technical claim against the implementation context.
3. Keep the AI-assistance disclosure because the current drafts were substantially AI-assisted.
4. Confirm title, subtitle, five Medium topics, featured image, canonical URL, paywall choice, subscriber-email setting, publication target, and schedule at action time.
5. Do not schedule these ten stories on top of the current September 7, 10, and 14 Medium commitments; use post-September 14 spacing after reviewing live performance.

## Proposed editorial order

1. Transaction Boundary
2. Ambiguous Success
3. Retry as a Risk Decision
4. Independent Verifier
5. Policy Engine as Compiler
6. Agent Observability
7. Safe Degradation Ladder
8. Fencing Token
9. Change Budget
10. RevOps Decision Ledger

The context-window story is a strong privacy/data-governance alternate and can replace a control-plane topic if Medium distribution indicates audience fatigue.
"""
    (EDITORIAL / "README.md").write_text(readme, encoding="utf-8")

    posts = [
        "# LinkedIn launch drafts for the next Medium story wave",
        "",
        "Status: **draft only — not approved, posted, or scheduled.**",
        "",
        "Each post must be reviewed after the corresponding story is human-reviewed and imported to Medium. Replace the GitHub URL with the final Medium canonical/share URL only if that is the approved cross-platform strategy. No native mentions are proposed without a source-specific relationship reason.",
        "",
    ]
    for i, story in enumerate(STORIES, 1):
        posts.extend([
            f"## NW-LI-{i:02d} — {story['title']}",
            "",
            f"GitHub Pages draft: {SITE}/{story['slug']}/",
            "",
            "Exact draft text:",
            "",
            "> " + LINKEDIN[story["slug"]].replace("\n", "\n> "),
            "",
        ])
    (EDITORIAL / "linkedin-launch-drafts.md").write_text("\n".join(posts) + "\n", encoding="utf-8")


def main() -> None:
    for story in STORIES:
        build_story(story)
        print(f"built draft source: {story['title']}")
    build_editorial_files()
    print(f"built {len(STORIES)} story drafts, {len(STORIES) * 3} SVG figures, and LinkedIn launch copy")


if __name__ == "__main__":
    main()
