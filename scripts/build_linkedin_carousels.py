#!/usr/bin/env python3
"""Build feed-readable LinkedIn document carousels for the ten-post AI series."""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Iterable, Sequence

from reportlab.lib.colors import Color, HexColor
from reportlab.pdfbase.pdfmetrics import stringWidth
from reportlab.pdfgen.canvas import Canvas


PAGE_W = 1080
PAGE_H = 1350
MARGIN = 72

INK = HexColor("#0B1F3A")
INK_2 = HexColor("#334155")
MUTED = HexColor("#64748B")
BG = HexColor("#F5F8FC")
WHITE = HexColor("#FFFFFF")
BLUE = HexColor("#1F5FBF")
BLUE_LIGHT = HexColor("#EAF2FF")
TEAL = HexColor("#087F75")
TEAL_LIGHT = HexColor("#E7F7F4")
GOLD = HexColor("#A96800")
GOLD_LIGHT = HexColor("#FFF3D9")
PURPLE = HexColor("#6842A6")
PURPLE_LIGHT = HexColor("#F1EBFF")
RED = HexColor("#B74235")
RED_LIGHT = HexColor("#FDECEA")
LINE = HexColor("#D8E2EF")


POSTS = [
    {
        "id": "01",
        "slug": "permission-leases",
        "short": "PERMISSION LEASES",
        "title": "Authority should exist only for the transaction",
        "subtitle": "The same CRM update can have radically different loss surfaces.",
        "metric": "100% -> 0.35%",
        "metric_label": "Modeled reachable authority after scope, value, time and use constraints",
        "flow": ["Evidence", "Policy", "Approval", "Lease", "Execute", "Verify"],
        "lanes": [
            ("DECISION", ["Evidence", "Policy", "Risk", "Approval"]),
            ("AUTHORITY", ["Bound lease", "Signer", "One-use token"]),
            ("EXECUTION", ["Effect gateway", "CRM", "Verifier", "Recovery"]),
        ],
        "principle": "Identity says who is present. A lease proves what may happen now.",
        "evidence_title": "The lease is narrow; the control path stays complete",
        "evidence_banner": "90 seconds, one resource, one approved delta, one use",
        "score_rows": [
            ("Credential lifetime", "90 s", "BOUND"),
            ("Resources", "1 quote", "BOUND"),
            ("Permitted uses", "1", "BOUND"),
            ("End-to-end p95", "307 ms", "PASS <= 350"),
            ("Mutation + verify", "185 ms", "60% OF PATH"),
            ("Standing-role reach", "100%", "REMOVED"),
        ],
        "decision_rule": "Issue authority only after evidence, policy and approval bind the exact field delta.",
    },
    {
        "id": "02",
        "slug": "human-approval-queue",
        "short": "HUMAN APPROVAL",
        "title": "Approval is a capacity-constrained risk service",
        "subtitle": "A 97% approval rate can coexist with an unstable review system.",
        "metric": "42 / 50 = 84%",
        "metric_label": "Illustrative arrival rate, hourly capacity and reviewer utilization",
        "flow": ["Proposal", "Risk", "Eligibility", "Queue", "Reviewer", "Outcome"],
        "lanes": [
            ("INTAKE", ["Proposal", "Risk score", "Policy class"]),
            ("QUEUE", ["Priority", "Eligibility", "Deadline", "Assignment"]),
            ("DECISION", ["Evidence packet", "Reviewer", "Outcome ledger"]),
        ],
        "principle": "Risk-weighted waiting time matters more than the aggregate approval rate.",
        "evidence_title": "Two more arrivals can change the operating regime",
        "evidence_banner": "At 52 arrivals/hour, five reviewers cannot stabilize the queue",
        "score_rows": [
            ("Proposals/day", "12,000", "SYNTHETIC"),
            ("Waiting at 11:00", "1,900", "BACKLOG"),
            ("Review service time", "6 min", "MEAN"),
            ("Wait at 42/hour", "4.8 min", "ERLANG-C"),
            ("Value of review", "$505", "PER ACTION"),
            ("Modeled cost minimum", "~60%", "REVIEW RATE"),
        ],
        "decision_rule": "Route by loss, deadline and reviewer qualification; expire authority when the SLA expires.",
    },
    {
        "id": "03",
        "slug": "action-receipts",
        "short": "ACTION RECEIPTS",
        "title": "A trace is not proof of the business effect",
        "subtitle": "HTTP 200 and a successful span do not establish one authoritative outcome.",
        "metric": "31 min > 15 min",
        "metric_label": "Illustrative p99 ambiguity age versus the operating objective",
        "flow": ["Intent", "Evidence", "Authority", "Request", "Observe", "Seal"],
        "lanes": [
            ("PREPARE", ["Intent", "Evidence", "Policy", "Approval"]),
            ("EXECUTE", ["Authority", "Stable action ID", "Effect boundary"]),
            ("PROVE", ["Verifier", "Receipt chain", "Recovery"]),
        ],
        "principle": "Timeout is an ambiguous state, not permission to repeat the side effect.",
        "evidence_title": "Receipt coverage can pass while ambiguity control fails",
        "evidence_banner": "One stable action ID from proposal through verified terminal state",
        "score_rows": [
            ("Receipt coverage", "100%", "PASS"),
            ("Seal latency p95", "38 ms", "PASS <= 45"),
            ("Effect verification", "99.995%", "PASS"),
            ("Ambiguity age p99", "31 min", "BREACH > 15"),
            ("Signed core", "3.2 KB", "PER ACTION"),
            ("Monthly actions", "10M", "MODEL"),
        ],
        "decision_rule": "Seal only after independent observation; otherwise reconcile, compensate or freeze.",
    },
    {
        "id": "04",
        "slug": "multi-agent-coordination",
        "short": "MULTI-AGENT SYSTEMS",
        "title": "Fluent agents do not create reliable coordination",
        "subtitle": "Distributed workflows need invariants, fenced ownership and explicit recovery.",
        "metric": "8 invariants",
        "metric_label": "Ownership, uniqueness, causality, durability, authority, proof, lineage and recovery",
        "flow": ["Event", "Workflow", "Owner epoch", "Domain API", "Verify", "Recover"],
        "lanes": [
            ("CONTROL", ["Durable workflow", "Owner epoch", "Fencing token"]),
            ("MESSAGING", ["Version", "Causal precondition", "Idempotency"]),
            ("EFFECTS", ["Domain API", "Verifier", "Saga recovery"]),
        ],
        "principle": "Agents propose. Durable coordination owns state, ordering and terminal truth.",
        "evidence_title": "Average success hides the unsafe tail",
        "evidence_banner": "Zero duplicates is not enough when ambiguity and compensation miss their gates",
        "score_rows": [
            ("Duplicate effects", "0", "PASS"),
            ("Stale-owner accepts", "0", "PASS"),
            ("Causal rejects", "100%", "PASS"),
            ("Receipt coverage", "100%", "PASS"),
            ("Saga recovery", "99.7%", "PASS"),
            ("Ambiguity age p99", "24 min", "BREACH > 10"),
        ],
        "decision_rule": "No action commits without the current owner epoch, idempotency key and verified postcondition.",
    },
    {
        "id": "05",
        "slug": "model-routing",
        "short": "MODEL ROUTING",
        "title": "Model routing is a portfolio decision",
        "subtitle": "Difficulty is not exposure; optimize the whole route bundle.",
        "metric": "$0.186 / workflow",
        "metric_label": "Illustrative completed-workflow cost across model, tools, verification, retries and recovery",
        "flow": ["Action", "Policy", "Evidence", "Route", "Execute", "Verify"],
        "lanes": [
            ("FILTER", ["Privacy", "Authority", "Quality floor", "Deadline"]),
            ("OPTIMIZE", ["Model", "Context", "Tools", "Retries"]),
            ("ACCOUNT", ["Verification", "Expected loss", "CVaR95"]),
        ],
        "principle": "Eliminate noncompliant routes first; optimize value only inside the feasible set.",
        "evidence_title": "Token price is only one line in the route ledger",
        "evidence_banner": "Critical quality can pass while calibration and tail loss breach",
        "score_rows": [
            ("Input + output", "$0.049", "26%"),
            ("Tools", "$0.047", "25%"),
            ("Verification", "$0.039", "21%"),
            ("Retries", "$0.025", "13%"),
            ("ECE calibration", "0.047", "BREACH > .030"),
            ("CVaR95 loss", "24", "BREACH > 18"),
        ],
        "decision_rule": "Choose the lowest-risk feasible route per task class, then recalibrate on verified outcomes.",
    },
    {
        "id": "06",
        "slug": "kill-switch",
        "short": "CONTAINMENT",
        "title": "A kill switch must stop effects, not dashboards",
        "subtitle": "Fast command acceptance is irrelevant if stale authority still commits.",
        "metric": "200 ms != containment",
        "metric_label": "A responsive API can coexist with minutes of continued business exposure",
        "flow": ["Trigger", "Epoch", "Propagate", "Fence", "Inventory", "Prove"],
        "lanes": [
            ("REVOKE", ["Signed epoch", "Identity", "Scheduler", "Workload"]),
            ("ENFORCE", ["Network", "Tool gateway", "Queue", "Data"]),
            ("RECONCILE", ["Inventory", "Verifier", "Recovery owner"]),
        ],
        "principle": "Stopping new authority and establishing business truth are different clocks.",
        "evidence_title": "Containment ends only when every effect has a disposition",
        "evidence_banner": "The modeled stop path fits 90 seconds, but local enforcement still breaches",
        "score_rows": [
            ("In-flight actions", "1,264", "INVENTORY"),
            ("Command accept p99", "2.1 s", "PASS <= 3"),
            ("Total stop budget", "85 s", "PASS <= 90"),
            ("Local enforcement", "41 s", "BREACH > 30"),
            ("Inventory complete", "99.96%", "PASS"),
            ("Ambiguity closure", "96.8%", "BREACH < 99"),
        ],
        "decision_rule": "Fence every effect boundary, then reconcile committed, cancelled and unresolved actions separately.",
    },
    {
        "id": "07",
        "slug": "production-evaluation",
        "short": "PRODUCTION EVALUATION",
        "title": "Benchmark accuracy is not production authority",
        "subtitle": "Promote the deployable system, not an isolated model score.",
        "metric": "92.6% -> 85.6%",
        "metric_label": "Point estimate versus 95% Wilson lower bound for 88 successes in 95 cases",
        "flow": ["Artifact", "Scenario", "Evidence", "Gate", "Canary", "Contract"],
        "lanes": [
            ("VERSION", ["Model", "Prompt", "Retrieval", "Policy"]),
            ("EVALUATE", ["Scenario suite", "Adversarial", "Recovery"]),
            ("PROMOTE", ["Evidence packet", "Authority stage", "Rollback"]),
        ],
        "principle": "A point estimate cannot authorize risk when the uncertainty bound misses the floor.",
        "evidence_title": "Zero observed failures is not zero risk",
        "evidence_banner": "The rule of three gives an approximate upper failure rate of 3/n",
        "score_rows": [
            ("Benchmark headline", "94%", "INSUFFICIENT"),
            ("Critical cohort", "88 / 95", "OBSERVED"),
            ("Point estimate", "92.6%", "PASS"),
            ("95% lower bound", "85.6%", "FAIL < 92"),
            ("10,000 clean trials", "~0.03%", "UPPER RATE"),
            ("Authority stages", "6", "PROGRESSIVE"),
        ],
        "decision_rule": "Expand authority only when cohort evidence, uncertainty and recovery gates all pass.",
    },
    {
        "id": "08",
        "slug": "agent-memory",
        "short": "AGENT MEMORY",
        "title": "Memory needs freshness and deletion SLOs",
        "subtitle": "Fast retrieval says nothing about truth, permission or reversibility.",
        "metric": "104 ms + 31 h",
        "metric_label": "Retrieval passes while deletion p99 breaches the 24-hour objective",
        "flow": ["Ingest", "Provenance", "Trust", "Retrieve", "Decide", "Delete"],
        "lanes": [
            ("WRITE", ["Sources", "Version", "Provenance", "Trust"]),
            ("READ", ["Purpose", "Freshness", "Conflict", "Retrieval"]),
            ("LIFECYCLE", ["Decision artifact", "Reverse lineage", "Deletion receipt"]),
        ],
        "principle": "Memory is governed state with provenance, purpose and lifecycle controls.",
        "evidence_title": "One freshness threshold cannot govern every memory class",
        "evidence_banner": "Six-hour prices and 180-day contract terms decay on different clocks",
        "score_rows": [
            ("Price half-life", "6 h", "CLASS"),
            ("Case status", "24 h", "CLASS"),
            ("Account risk", "7 d", "CLASS"),
            ("Contract term", "180 d", "CLASS"),
            ("Poison admission", "1", "BREACH"),
            ("Deletion p99", "31 h", "BREACH > 24"),
        ],
        "decision_rule": "Retrieve only assertions that are current, attributable, permitted and conflict-resolved.",
    },
    {
        "id": "09",
        "slug": "crm-risk-workflow",
        "short": "AGENTIC CRM",
        "title": "A $288,000 delta is not tool use",
        "subtitle": "A model recommendation becomes a commercial decision at the effect boundary.",
        "metric": "$288K in 108 min",
        "metric_label": "Twelve percent of a $2.4M renewal inside the illustrative response window",
        "flow": ["Signals", "Evidence", "Risk", "Approval", "Execute", "Verify"],
        "lanes": [
            ("PREPARE", ["Support", "Contract", "Quote", "Customer"]),
            ("DECIDE", ["Conflict set", "Risk model", "Policy", "Approval"]),
            ("ACT", ["One-use lease", "Version check", "Verifier", "Recovery"]),
        ],
        "principle": "Model confidence informs the proposal; it never becomes commercial authority.",
        "evidence_title": "Nine observable states separate recommendation from commitment",
        "evidence_banner": "Approve the exact field delta, resource version, validity window and recovery path",
        "score_rows": [
            ("Renewal value", "$2.4M", "EXPOSURE"),
            ("Requested discount", "12%", "PROPOSAL"),
            ("Proposed delta", "$288K", "AT RISK"),
            ("Decision window", "108 min", "DEADLINE"),
            ("Approved example", "8%", "EXACT DELTA"),
            ("Control states", "9", "OBSERVABLE"),
        ],
        "decision_rule": "If evidence or quote version changes, invalidate the approval and recompute the decision.",
    },
    {
        "id": "10",
        "slug": "verified-outcome-economics",
        "short": "AGENT ECONOMICS",
        "title": "Price the verified outcome, not the model call",
        "subtitle": "The denominator and control plane dominate the economics of production agents.",
        "metric": "20.8% vs 68.4%",
        "metric_label": "Inference share versus human review plus always-on control-plane share",
        "flow": ["Attempt", "Model", "Tools", "Review", "Verify", "Unit cost"],
        "lanes": [
            ("ATTEMPT", ["Evidence", "Inference", "Tools", "Retries"]),
            ("CONTROL", ["Evaluation", "Approval", "Containment", "Platform"]),
            ("OUTCOME", ["Postcondition", "Verified count", "Unit economics"]),
        ],
        "principle": "Every attempt is billed; only independently verified outcomes enter the denominator.",
        "evidence_title": "Verification rate is the largest modeled cost lever",
        "evidence_banner": "$0.9502 per attempt becomes $1.135 per verified outcome",
        "score_rows": [
            ("Monthly attempts", "40,000", "MODEL"),
            ("Inference", "$0.1980", "20.8%"),
            ("Human review", "$0.4125", "43.4%"),
            ("Tier-0 platform", "$0.2375", "25.0%"),
            ("Verified rate", "83.7%", "DENOMINATOR"),
            ("Unit cost", "$1.135", "VERIFIED"),
        ],
        "decision_rule": "Optimize verification, reviewer minutes and route quality before negotiating token price.",
    },
]


def _wrap(text: str, font: str, size: float, max_width: float) -> list[str]:
    words = text.split()
    lines: list[str] = []
    current = ""
    for word in words:
        candidate = word if not current else f"{current} {word}"
        if stringWidth(candidate, font, size) <= max_width:
            current = candidate
        else:
            if current:
                lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines


def _text(
    c: Canvas,
    text: str,
    x: float,
    y: float,
    max_width: float,
    font: str = "Helvetica",
    size: float = 24,
    leading: float | None = None,
    color=INK,
    max_lines: int | None = None,
) -> float:
    lines = _wrap(text, font, size, max_width)
    if max_lines is not None:
        lines = lines[:max_lines]
    leading = leading or size * 1.22
    c.setFont(font, size)
    c.setFillColor(color)
    cursor = y
    for line in lines:
        c.drawString(x, cursor, line)
        cursor -= leading
    return cursor


def _card(c: Canvas, x: float, y: float, w: float, h: float, fill=WHITE, stroke=LINE, radius=18) -> None:
    c.setFillColor(fill)
    c.setStrokeColor(stroke)
    c.setLineWidth(1.4)
    c.roundRect(x, y, w, h, radius, fill=1, stroke=1)


def _page_base(c: Canvas, post: dict, page: int, section: str) -> None:
    c.setFillColor(BG)
    c.rect(0, 0, PAGE_W, PAGE_H, fill=1, stroke=0)
    c.setFillColor(INK)
    c.setFont("Helvetica-Bold", 16)
    c.drawString(MARGIN, PAGE_H - 54, f"PRODUCTION AI OPERATING SYSTEM | {post['id']}/10")
    c.setFillColor(BLUE)
    c.roundRect(PAGE_W - 278, PAGE_H - 70, 206, 31, 15, fill=1, stroke=0)
    c.setFillColor(WHITE)
    c.setFont("Helvetica-Bold", 12)
    c.drawCentredString(PAGE_W - 175, PAGE_H - 59, section)
    c.setStrokeColor(LINE)
    c.setLineWidth(1)
    c.line(MARGIN, 68, PAGE_W - MARGIN, 68)
    c.setFillColor(MUTED)
    c.setFont("Helvetica", 12)
    c.drawString(MARGIN, 43, "Aditya Singh | Production AI control systems")
    c.drawRightString(PAGE_W - MARGIN, 43, f"{page} / 3 | Illustrative model - not production data")


def _arrow(c: Canvas, x1: float, y1: float, x2: float, y2: float, color=BLUE) -> None:
    c.setStrokeColor(color)
    c.setFillColor(color)
    c.setLineWidth(2.2)
    c.line(x1, y1, x2, y2)
    angle = 8
    c.line(x2, y2, x2 - angle, y2 + angle / 2)
    c.line(x2, y2, x2 - angle, y2 - angle / 2)


def _draw_cover(c: Canvas, post: dict) -> None:
    _page_base(c, post, 1, post["short"])
    y = PAGE_H - 134
    y = _text(c, post["title"], MARGIN, y, PAGE_W - 2 * MARGIN, "Helvetica-Bold", 48, 57, INK, 3)
    y -= 18
    _text(c, post["subtitle"], MARGIN, y, PAGE_W - 2 * MARGIN, "Helvetica", 24, 32, INK_2, 2)

    _card(c, MARGIN, 666, PAGE_W - 2 * MARGIN, 275, BLUE_LIGHT, HexColor("#BCD3F5"), 24)
    c.setFillColor(BLUE)
    c.setFont("Helvetica-Bold", 18)
    c.drawString(MARGIN + 34, 889, "THE OPERATING NUMBER")
    c.setFillColor(INK)
    c.setFont("Helvetica-Bold", 62)
    c.drawString(MARGIN + 34, 796, post["metric"])
    _text(c, post["metric_label"], MARGIN + 36, 744, PAGE_W - 2 * MARGIN - 72, "Helvetica", 20, 27, INK_2, 3)

    c.setFillColor(INK)
    c.setFont("Helvetica-Bold", 18)
    c.drawString(MARGIN, 594, "CONTROL PATH")
    nodes = post["flow"]
    gap = 14
    width = (PAGE_W - 2 * MARGIN - gap * (len(nodes) - 1)) / len(nodes)
    y0 = 438
    for i, node in enumerate(nodes):
        x = MARGIN + i * (width + gap)
        fill = [BLUE_LIGHT, TEAL_LIGHT, GOLD_LIGHT, PURPLE_LIGHT][i % 4]
        stroke = [BLUE, TEAL, GOLD, PURPLE][i % 4]
        _card(c, x, y0, width, 112, fill, stroke, 16)
        lines = _wrap(node, "Helvetica-Bold", 16, width - 22)
        c.setFont("Helvetica-Bold", 16)
        c.setFillColor(INK)
        yy = y0 + 62 + (len(lines) - 1) * 9
        for line in lines:
            c.drawCentredString(x + width / 2, yy, line)
            yy -= 20
        if i < len(nodes) - 1:
            _arrow(c, x + width, y0 + 56, x + width + gap - 4, y0 + 56, MUTED)

    _card(c, MARGIN, 150, PAGE_W - 2 * MARGIN, 210, WHITE, LINE, 20)
    c.setFillColor(TEAL)
    c.setFont("Helvetica-Bold", 16)
    c.drawString(MARGIN + 30, 314, "DESIGN PRINCIPLE")
    _text(c, post["principle"], MARGIN + 30, 266, PAGE_W - 2 * MARGIN - 60, "Helvetica-Bold", 28, 36, INK, 3)


def _draw_architecture(c: Canvas, post: dict) -> None:
    _page_base(c, post, 2, "TECHNICAL ARCHITECTURE")
    y = PAGE_H - 135
    y = _text(c, f"{post['short'].title()} control architecture", MARGIN, y, PAGE_W - 2 * MARGIN, "Helvetica-Bold", 43, 51, INK, 2)
    _text(c, "Explicit planes separate decision, authority, execution and proof.", MARGIN, y - 10, PAGE_W - 2 * MARGIN, "Helvetica", 22, 29, INK_2, 2)

    lane_y = [875, 590, 305]
    fills = [BLUE_LIGHT, GOLD_LIGHT, TEAL_LIGHT]
    strokes = [BLUE, GOLD, TEAL]
    for row, (lane, nodes) in enumerate(post["lanes"]):
        y0 = lane_y[row]
        _card(c, MARGIN, y0, PAGE_W - 2 * MARGIN, 205, WHITE, LINE, 20)
        c.setFillColor(strokes[row])
        c.roundRect(MARGIN + 20, y0 + 131, 155, 46, 15, fill=1, stroke=0)
        c.setFillColor(WHITE)
        c.setFont("Helvetica-Bold", 13)
        c.drawCentredString(MARGIN + 97.5, y0 + 147, lane)
        n = len(nodes)
        gap = 20
        start_x = MARGIN + 205
        available = PAGE_W - MARGIN - 34 - start_x
        node_w = (available - gap * (n - 1)) / n
        for i, node in enumerate(nodes):
            x = start_x + i * (node_w + gap)
            _card(c, x, y0 + 55, node_w, 91, fills[row], strokes[row], 14)
            lines = _wrap(node, "Helvetica-Bold", 15, node_w - 20)
            yy = y0 + 103 + (len(lines) - 1) * 8
            c.setFillColor(INK)
            c.setFont("Helvetica-Bold", 15)
            for line in lines:
                c.drawCentredString(x + node_w / 2, yy, line)
                yy -= 19
            if i < n - 1:
                _arrow(c, x + node_w, y0 + 100, x + node_w + gap - 5, y0 + 100, strokes[row])
        if row < len(post["lanes"]) - 1:
            c.setStrokeColor(MUTED)
            c.setLineWidth(2)
            c.line(PAGE_W / 2, y0, PAGE_W / 2, lane_y[row + 1] + 205)
            c.setFillColor(MUTED)
            c.circle(PAGE_W / 2, lane_y[row + 1] + 205, 4, fill=1, stroke=0)

    _card(c, MARGIN, 110, PAGE_W - 2 * MARGIN, 130, PURPLE_LIGHT, HexColor("#C7B5EA"), 20)
    c.setFillColor(PURPLE)
    c.setFont("Helvetica-Bold", 15)
    c.drawString(MARGIN + 28, 201, "CONTROL CONTRACT")
    _text(c, post["principle"], MARGIN + 28, 165, PAGE_W - 2 * MARGIN - 56, "Helvetica-Bold", 21, 28, INK, 2)


def _status_colors(status: str):
    if "BREACH" in status or "FAIL" in status or "REMOVED" in status:
        return RED_LIGHT, RED
    if "PASS" in status or "BOUND" in status or "VERIFIED" in status:
        return TEAL_LIGHT, TEAL
    if "AT RISK" in status or "BACKLOG" in status or "INSUFFICIENT" in status:
        return GOLD_LIGHT, GOLD
    return BLUE_LIGHT, BLUE


def _draw_evidence(c: Canvas, post: dict) -> None:
    _page_base(c, post, 3, "OPERATING EVIDENCE")
    y = PAGE_H - 135
    y = _text(c, post["evidence_title"], MARGIN, y, PAGE_W - 2 * MARGIN, "Helvetica-Bold", 42, 50, INK, 3)
    y -= 16
    _card(c, MARGIN, y - 115, PAGE_W - 2 * MARGIN, 118, BLUE_LIGHT, HexColor("#BCD3F5"), 18)
    _text(c, post["evidence_banner"], MARGIN + 28, y - 43, PAGE_W - 2 * MARGIN - 56, "Helvetica-Bold", 23, 30, BLUE, 3)

    rows = post["score_rows"]
    card_w = (PAGE_W - 2 * MARGIN - 24) / 2
    card_h = 190
    top = y - 164
    for i, (label, value, status) in enumerate(rows):
        col = i % 2
        row = i // 2
        x = MARGIN + col * (card_w + 24)
        y0 = top - (row + 1) * card_h - row * 22
        fill, accent = _status_colors(status)
        _card(c, x, y0, card_w, card_h, WHITE, LINE, 18)
        c.setFillColor(accent)
        c.roundRect(x + 20, y0 + 142, card_w - 40, 30, 12, fill=1, stroke=0)
        c.setFillColor(WHITE)
        c.setFont("Helvetica-Bold", 11)
        c.drawCentredString(x + card_w / 2, y0 + 153, status)
        c.setFillColor(INK)
        c.setFont("Helvetica-Bold", 34)
        c.drawString(x + 24, y0 + 86, value)
        _text(c, label, x + 24, y0 + 49, card_w - 48, "Helvetica", 17, 22, INK_2, 2)

    _card(c, MARGIN, 106, PAGE_W - 2 * MARGIN, 154, PURPLE_LIGHT, HexColor("#C7B5EA"), 20)
    c.setFillColor(PURPLE)
    c.setFont("Helvetica-Bold", 15)
    c.drawString(MARGIN + 28, 221, "DECISION RULE")
    _text(c, post["decision_rule"], MARGIN + 28, 183, PAGE_W - 2 * MARGIN - 56, "Helvetica-Bold", 21, 28, INK, 3)


def build_carousel(post: dict, output_dir: Path) -> Path:
    output = output_dir / f"production-ai-operating-system-{post['id']}-{post['slug']}.pdf"
    c = Canvas(str(output), pagesize=(PAGE_W, PAGE_H), pageCompression=1)
    c.setTitle(f"Production AI Operating System {post['id']}: {post['title']}")
    c.setAuthor("Aditya Singh")
    c.setSubject("Technical LinkedIn document carousel")
    c.setKeywords("enterprise AI, agentic systems, architecture, governance, operations")
    for draw in (_draw_cover, _draw_architecture, _draw_evidence):
        draw(c, post)
        c.showPage()
    c.save()
    return output


def _assert_ascii(values: Iterable[object]) -> None:
    for value in values:
        if isinstance(value, str):
            if not value.isascii():
                raise ValueError(f"Non-ASCII text in PDF content: {value!r}")
        elif isinstance(value, dict):
            _assert_ascii(value.values())
        elif isinstance(value, (list, tuple)):
            _assert_ascii(value)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", default="output/pdf/linkedin")
    args = parser.parse_args()

    _assert_ascii(POSTS)
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    outputs = [build_carousel(post, output_dir) for post in POSTS]
    for output in outputs:
        print(output)


if __name__ == "__main__":
    main()
