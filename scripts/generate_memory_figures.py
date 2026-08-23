#!/usr/bin/env python3
"""Generate the 18 reproducible deep-dive figures for the governed agent-memory story."""

from __future__ import annotations

import math
import textwrap
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.colors import LinearSegmentedColormap
from matplotlib.patches import Circle, FancyArrowPatch, FancyBboxPatch, Polygon, Rectangle


ROOT = Path(__file__).resolve().parents[1]
SLUG = "your-ai-agents-memory-is-a-database-not-a-prompt"
OUT = ROOT / "assets" / "images" / SLUG
MAP_PATH = ROOT / "stories" / f"{SLUG}-figure-map.md"

PAPER = "#F5F7FB"
SURFACE = "#FFFFFF"
INK = "#091631"
MUTED = "#52627A"
LINE = "#C8D2E1"
BLUE = "#1357A6"
BLUE_LIGHT = "#DCEAF8"
TEAL = "#04776E"
TEAL_LIGHT = "#D5EFEB"
GOLD = "#A26808"
GOLD_LIGHT = "#F8E8BE"
RUST = "#AF4237"
RUST_LIGHT = "#F6D8D3"
PURPLE = "#6241A5"
PURPLE_LIGHT = "#E8DFF7"
GREEN = "#2E7D4F"
GREEN_LIGHT = "#DAEEDD"
WHITE = "#FFFFFF"


FIGURES = [
    (1, "Memory is governed state—not appended text", "Comparison", "A prompt fragment lacks the provenance, time, purpose, and lifecycle controls required for consequential decisions."),
    (2, "Enterprise agent-memory control plane", "Architecture", "Six independently operated planes convert heterogeneous evidence into policy-filtered, revocable decision context."),
    (3, "Source trust zones and admissible influence", "Trust-zone map", "Source identity and control history determine how strongly a memory may influence an action."),
    (4, "Provenance graph for a renewal assertion", "Lineage graph", "Every derived assertion should remain connected to sources, transformations, reviewers, and invalidation events."),
    (5, "Bitemporal memory-envelope contract", "Structured schema", "A memory record needs business validity, system knowledge time, provenance, trust, purpose, retention, and policy fields."),
    (6, "Bitemporal truth: what was true versus what was known", "Timeline", "Valid time and transaction time answer different audit questions and prevent later corrections from rewriting history."),
    (7, "Ingestion validation and promotion pipeline", "Stage pipeline", "Untrusted input becomes decision-eligible only after parsing, instruction stripping, provenance binding, policy, and corroboration."),
    (8, "Indirect memory-poisoning attack graph", "Attack graph", "One malicious attachment can survive summarization and retrieval unless each transformation preserves provenance and trust boundaries."),
    (9, "Quarantine and adjudication state machine", "State machine", "Suspicious memory must remain non-influential until independently validated, corrected, or terminally rejected."),
    (10, "Freshness decay by memory class", "Scenario curves", "Freshness is domain-specific: prices decay faster than contract terms, while immutable events may not decay at all."),
    (11, "Trust, corroboration, and uncertainty model", "Formula decomposition", "A decision-use score should expose source trust, corroboration, freshness, transformation loss, and contradiction penalties."),
    (12, "Retrieval-time admissibility decision tree", "Decision tree", "Semantic similarity is only a candidate generator; policy, purpose, time, trust, and contradiction gates decide admissibility."),
    (13, "Policy-filtered vector retrieval architecture", "Retrieval architecture", "Access and purpose filters must constrain candidate generation and re-ranking before content reaches the model."),
    (14, "Conflict resolution by source authority and time", "Decision matrix", "Conflicts should resolve through deterministic source authority and temporal rules—not whichever chunk ranks highest."),
    (15, "Deletion and correction propagation", "Sequence", "A deletion request is incomplete until derivatives, indexes, caches, prompts, and decision artifacts are reconciled."),
    (16, "Retention policy by memory class and purpose", "Retention heatmap", "Retention should be purpose- and class-specific, with legal holds and cryptographic erasure modeled explicitly."),
    (17, "Memory control-plane operating objectives", "SLO scorecard", "Quality, freshness, provenance, deletion, poisoning, and retrieval-policy failures require separate measurable objectives."),
    (18, "Migration from prompt memory to governed memory", "Maturity roadmap", "Teams should introduce provenance and read-only retrieval before allowing learned memory to influence consequential actions."),
]

CORE = {1, 2, 4, 5, 6, 7, 8, 10, 11, 12, 13, 15, 17, 18}

ASSUMPTIONS = {
    10: "Illustrative half-lives: price 6 h, case status 24 h, account risk 7 d, contract term 180 d; immutable events do not decay.",
    11: "Synthetic example: source .82, corroboration .75, freshness .88, transform .92, contradiction .20; weights declared in story.",
    14: "Ordinal reference matrix; authority and recency rules are illustrative and must be replaced by a governed source hierarchy.",
    16: "Illustrative policy periods only; legal, contractual, privacy, and records-management owners must set production values.",
    17: "Synthetic 30-day operating window with two deliberate breaches to demonstrate escalation behavior.",
}

SIDECARS = {
    1: ("MEMORY CONTRACT", ["Prompt text optimizes token assembly; governed memory optimizes durable decision evidence.", "A vector score cannot prove source identity, current validity, or permitted purpose.", "Action-grade memory must be corrigible, deletable, and independently auditable."], [("OBJECT", "typed memory envelope"), ("BOUNDARY", "retrieval policy PEP"), ("EXIT", "evidence-bound context")]),
    2: ("CONTROL PLANE", ["Ingestion and retrieval are separate security decisions.", "Provenance and trust survive every derivation, chunk, embedding, and summary.", "Deletion is a first-class plane with completion evidence."], [("INPUT", "5 source classes"), ("PLANES", "6 governed controls"), ("OUTPUT", "decision context")]),
    3: ("TRUST ZONES", ["Control history matters more than storage location.", "User-authored and machine-derived evidence are not equivalent.", "Cross-zone promotion requires validation and explicit policy."], [("HIGH", "signed systems of record"), ("MEDIUM", "reviewed collaboration"), ("LOW", "external / generated")]),
    4: ("PROVENANCE", ["A summary is a new entity, not a replacement for its sources.", "Derivation edges identify exactly which transformation produced each claim.", "Invalidation can propagate without deleting the historical audit graph."], [("MODEL", "W3C PROV concepts"), ("ROOTS", "CRM · email · ticket"), ("RESULT", "renewal assertion")]),
    5: ("DATA CONTRACT", ["Valid time and transaction time are both mandatory.", "Trust is decomposed; it is not one unexplained confidence number.", "Purpose and retention fields travel with the content."], [("KEY", "memory_id + version"), ("TIME", "valid + transaction"), ("POLICY", "purpose + retention")]),
    6: ("TEMPORAL TRUTH", ["A late correction should not erase what the agent knew earlier.", "As-of queries support incident replay and audit.", "Decision time must bind the exact memory versions retrieved."], [("VALID", "business-world time"), ("TRANSACTION", "system knowledge time"), ("QUERY", "valid_at + known_at")]),
    7: ("INGESTION GATE", ["Parsing and malware checks do not make content trustworthy.", "Instruction-like text is data, never control, outside the orchestration boundary.", "Promotion requires a provenance-complete record and policy outcome."], [("ENTRY", "raw source object"), ("GATES", "8 independent stages"), ("EXIT", "eligible or quarantine")]),
    8: ("POISONING PATH", ["Indirect instructions can be amplified by summarization.", "Embedding preserves semantic influence while obscuring origin.", "Policy must break influence before decision-time context assembly."], [("FOOTHOLD", "support attachment"), ("AMPLIFIER", "summary + vector index"), ("BREAK", "trust + purpose PEP")]),
    9: ("QUARANTINE", ["Suspicion is a durable state, not a log message.", "Revalidation requires a distinct trusted source or eligible reviewer.", "Rejected records retain minimal forensic metadata under policy."], [("START", "candidate"), ("HOLD", "non-influential"), ("END", "promote · reject · expire")]),
    10: ("FRESHNESS", ["A universal TTL is both unsafe and wasteful.", "Decay changes decision weight before hard expiry.", "Event-sourced facts may remain valid while interpretations decay."], [("MODEL", "exp(−ln2·age/half-life)"), ("UNITS", "hours to days"), ("LIMIT", "synthetic curves")]),
    11: ("DECISION SCORE", ["The formula is a routing heuristic, not calibrated truth.", "Contradiction is a penalty—not negative evidence hidden in an average.", "High-risk actions need score thresholds plus minimum source requirements."], [("OUTPUT", "D ∈ [0,1]"), ("PENALTY", "contradiction × λ"), ("GUARD", "source-class floor")]),
    12: ("ADMISSIBILITY", ["Similarity produces candidates; it never grants influence.", "Every deny result has a machine-readable reason.", "Conflicts route to abstention, corroboration, or human review."], [("CANDIDATE", "top-k semantic match"), ("POLICY", "7 fail-closed gates"), ("EXIT", "admit or exclude")]),
    13: ("RETRIEVAL", ["Pre-filtering prevents unauthorized candidates from entering rankers.", "A policy-aware re-ranker optimizes decision usefulness, not relevance alone.", "The context assembler emits citations and memory-version bindings."], [("INDEX", "partitioned by tenant"), ("FILTER", "ACL + purpose + time"), ("OUTPUT", "bound evidence pack")]),
    14: ("CONFLICTS", ["Source authority is action- and field-specific.", "Recency wins only inside the same authority tier.", "Unresolved high-impact conflict forces abstention or review."], [("ROWS", "incoming source"), ("COLS", "stored source"), ("RESULT", "replace · coexist · review")]),
    15: ("ERASURE", ["Primary deletion is only the beginning of propagation.", "Derived artifacts carry reverse lineage for targeted invalidation.", "Decision receipts retain non-content proof when law and policy permit."], [("TRIGGER", "delete / correct request"), ("FANOUT", "6 derivative stores"), ("PROOF", "completion receipt")]),
    16: ("RETENTION", ["Purpose changes retention even for the same source class.", "Legal hold suspends disposal without silently broadening access.", "Key destruction can erase encrypted derivatives at scale."], [("DIMENSIONS", "class × purpose"), ("OVERRIDE", "legal hold"), ("DISPOSE", "delete + evidence")]),
    17: ("OPERATIONS", ["Coverage, latency, and correctness are not interchangeable.", "Poison admission and deletion breaches freeze affected action classes.", "Every SLO has an owner, window, and incident policy."], [("WINDOW", "synthetic 30 days"), ("STATUS", "6 pass · 2 breach"), ("ACTION", "contain + reconcile")]),
    18: ("MIGRATION", ["Start by inventorying hidden memory and decision dependencies.", "Shadow mode measures retrieval without granting influence.", "Consequential autonomy requires evidence, deletion, and rollback gates."], [("PHASES", "0 through 5"), ("PROMOTION", "measured gate"), ("ROLLBACK", "action-class level")]),
}


def wrap(value: str, width: int = 24) -> str:
    return "\n".join(textwrap.wrap(value, width=width))


def chip(fig, x: float, y: float, width: float, label: str, value: str, color: str) -> None:
    fig.add_artist(FancyBboxPatch((x, y), width, .024, transform=fig.transFigure,
                                  boxstyle="round,pad=.0015,rounding_size=.003",
                                  facecolor=WHITE, edgecolor=color, linewidth=.75))
    fig.text(x + .006, y + .012, f"{label}  {value}", va="center", color=color,
             fontsize=6.4, fontweight="bold")


def sidecar(fig, number: int) -> None:
    domain, insights, contract = SIDECARS[number]
    takeaway = FIGURES[number - 1][3]
    assumption = ASSUMPTIONS.get(number, "Reference architecture; no observed production data.")
    rail = fig.add_axes([.765, .075, .21, .755])
    rail.set_xlim(0, 100)
    rail.set_ylim(0, 100)
    rail.axis("off")
    rail.text(3, 97, domain, color=BLUE, fontsize=8.5, fontweight="bold", va="center")
    rail.plot([3, 97], [94, 94], color=BLUE, lw=1.2)

    def panel(y, height, title, edge, fill):
        rail.add_patch(FancyBboxPatch((1, y), 98, height, boxstyle="round,pad=.22,rounding_size=1.5",
                                      facecolor=fill, edgecolor=edge, linewidth=.85))
        rail.add_patch(Rectangle((1, y + height - 5), 98, 5, facecolor=edge, edgecolor="none", alpha=.12))
        rail.text(5, y + height - 2.5, title, color=edge, fontsize=7.0, fontweight="bold", va="center")

    panel(76, 16, "DECISION TAKEAWAY", BLUE, "#F7FAFE")
    rail.text(5, 83, wrap(takeaway, 42), color=INK, fontsize=7.0, va="center", linespacing=1.18)
    panel(43, 31, "TECHNICAL READING", TEAL, "#F5FBFA")
    for i, insight in enumerate(insights, 1):
        y = 66 - (i - 1) * 8.5
        rail.add_patch(Circle((7, y), 2.1, facecolor=WHITE, edgecolor=TEAL, linewidth=.8))
        rail.text(7, y, str(i), ha="center", va="center", color=TEAL, fontsize=6.1, fontweight="bold")
        rail.text(12, y, wrap(insight, 38), color=INK, fontsize=6.7, va="center", linespacing=1.12)
    panel(18, 23, "CONTROL CONTRACT", GOLD, "#FFFBF3")
    for i, (label, value) in enumerate(contract):
        y = 32.5 - i * 6.5
        rail.text(5, y, label, color=GOLD, fontsize=6.2, fontweight="bold", va="center")
        rail.text(96, y, value, color=INK, fontsize=6.5, ha="right", va="center")
        if i < 2:
            rail.plot([5, 96], [y - 3.1, y - 3.1], color=LINE, lw=.5)
    panel(1, 15, "INPUTS / LIMITS", PURPLE, "#FAF8FE")
    rail.text(5, 7.3, wrap(assumption, 42), color=INK, fontsize=6.4, va="center", linespacing=1.12)


def setup(number: int, title: str, subtitle: str, plot: bool = False):
    fig, ax = plt.subplots(figsize=(12, 8), dpi=200)
    fig.patch.set_facecolor(PAPER)
    ax.set_facecolor(SURFACE)
    fig.subplots_adjust(left=.055, right=.745, top=.82, bottom=.10)
    tier = "CORE" if number in CORE else "SUPPLEMENTAL"
    form = FIGURES[number - 1][2].upper()
    fig.text(.035, .968, f"FIGURE {number:02d}", color=BLUE, fontsize=8.0, fontweight="bold")
    fig.text(.035, .925, title, color=INK, fontsize=19.5, fontweight="bold")
    fig.text(.035, .889, subtitle, color=MUTED, fontsize=8.4)
    chip(fig, .035, .846, .172, "DOMAIN", SIDECARS[number][0], BLUE)
    chip(fig, .213, .846, .092, "TIER", tier, TEAL)
    chip(fig, .311, .846, .145, "FORM", form, PURPLE)
    chip(fig, .462, .846, .205, "EVIDENCE", "SYNTHETIC / REFERENCE", GOLD)
    sidecar(fig, number)
    fig.text(.055, .032, "LEGEND", color=INK, fontsize=6.2, fontweight="bold", va="center")
    x = .105
    for color, label in [(BLUE, "trusted / observed"), (TEAL, "governed / allowed"), (GOLD, "decision / review"), (RUST, "risk / denied")]:
        fig.add_artist(Circle((x, .032), .0035, transform=fig.transFigure, facecolor=color, edgecolor=color))
        fig.text(x + .006, .032, label, color=MUTED, fontsize=6.0, va="center")
        x += .12
    fig.text(.975, .032, "AI-assisted design · reference architecture / synthetic values · not production data",
             ha="right", color=MUTED, fontsize=5.8, va="center")
    if not plot:
        ax.set_xlim(0, 100)
        ax.set_ylim(0, 90)
        ax.axis("off")
    return fig, ax


def save(fig, number: int) -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    fig.savefig(OUT / f"figure-{number:02d}.png", facecolor=PAPER, dpi=200)
    plt.close(fig)


def box(ax, x, y, w, h, title, body="", edge=LINE, fill=SURFACE, title_color=INK, fs=8.2):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=.25,rounding_size=.8",
                                facecolor=fill, edgecolor=edge, linewidth=1.05))
    if h >= 10:
        ax.add_patch(Rectangle((x, y + h - 1.3), w, 1.3, facecolor=edge, edgecolor="none", alpha=.13))
    ax.text(x + w * .06, y + h * .66, title, color=title_color, fontsize=fs, fontweight="bold", va="center")
    if body:
        ax.text(x + w * .06, y + h * .30, body, color=MUTED, fontsize=fs - 1.5, va="center", linespacing=1.25)


def arrow(ax, start, end, color=MUTED, lw=1.4, connectionstyle="arc3"):
    ax.add_patch(FancyArrowPatch(start, end, arrowstyle="-|>", mutation_scale=11, color=color,
                                 linewidth=lw, connectionstyle=connectionstyle))


def label(ax, x, y, text, color=BLUE, fs=6.5):
    ax.text(x, y, text.upper(), color=color, fontsize=fs, fontweight="bold", va="center")


def f01():
    fig, ax = setup(1, FIGURES[0][1], "Same words; radically different control properties")
    rows = ["Identity", "Time semantics", "Provenance", "Purpose", "Access", "Correction", "Deletion", "Audit replay"]
    cols = [(4, "PROMPT FRAGMENT", RUST, RUST_LIGHT, ["implicit", "now only", "usually absent", "unbound", "inherits context", "overwrite", "best effort", "weak"]),
            (50, "GOVERNED MEMORY", TEAL, TEAL_LIGHT, ["typed source", "bitemporal", "derivation graph", "bound", "policy filtered", "versioned", "propagated", "as-of query"])]
    for x, title, color, fill, values in cols:
        box(ax, x, 75, 42, 10, title, "control surface", edge=color, fill=fill, title_color=color, fs=9)
        for i, (row, value) in enumerate(zip(rows, values)):
            y = 66 - i * 7.3
            box(ax, x, y, 42, 5.7, row, edge=LINE, fill=WHITE, fs=7.2)
            ax.text(x + 39.5, y + 2.85, value, color=color, fontsize=7.3, fontweight="bold", ha="right", va="center")
    ax.text(48, 39, "≠", fontsize=30, color=GOLD, fontweight="bold", ha="center", va="center")
    save(fig, 1)


def f02():
    fig, ax = setup(2, FIGURES[1][1], "Six planes govern the full memory lifecycle")
    sources = [("CRM", "signed records"), ("EMAIL", "human text"), ("TICKETS", "mixed trust"), ("DOCS", "external"), ("MODEL", "derived")]
    for i, (t, b) in enumerate(sources):
        box(ax, 2, 74 - i * 14, 14, 9, t, b, edge=[BLUE, TEAL, GOLD, RUST, PURPLE][i], fs=7.2)
    planes = [("1 INGEST", "parse · classify · sanitize", BLUE), ("2 PROVENANCE", "entity · activity · agent", PURPLE),
              ("3 TRUST", "zone · corroborate · decay", GOLD), ("4 RETRIEVE", "ACL · purpose · rank", TEAL),
              ("5 DECIDE", "bind · cite · abstain", BLUE), ("6 LIFECYCLE", "correct · retain · delete", RUST)]
    for i, (t, b, c) in enumerate(planes):
        x = 22 + (i % 3) * 23
        y = 60 - (i // 3) * 30
        box(ax, x, y, 19, 20, t, b, edge=c, fill=WHITE, title_color=c, fs=8)
        if i % 3 < 2:
            arrow(ax, (x + 19, y + 10), (x + 23, y + 10), color=c)
    for i in range(len(sources)):
        arrow(ax, (16, 78.5 - i * 14), (22, 70), color=MUTED, lw=.8)
    box(ax, 27, 6, 54, 11, "DECISION CONTEXT", "version-bound memories · citations · deny reasons · expiry", edge=TEAL, fill=TEAL_LIGHT, title_color=TEAL, fs=9)
    for x in [31.5, 54.5, 77.5]:
        arrow(ax, (x, 30), (x, 17), color=TEAL)
    save(fig, 2)


def f03():
    fig, ax = setup(3, FIGURES[2][1], "Promotion requires stronger evidence as influence increases")
    zones = [("ZONE 0", "SIGNED SYSTEMS", "CRM ledger · contract store", BLUE, 82),
             ("ZONE 1", "REVIEWED INTERNAL", "approved email · curated KB", TEAL, 62),
             ("ZONE 2", "UNREVIEWED INTERNAL", "chat · notes · uploads", GOLD, 42),
             ("ZONE 3", "EXTERNAL / GENERATED", "web · model summaries", RUST, 22)]
    for i, (z, title, body, c, y) in enumerate(zones):
        ax.add_patch(FancyBboxPatch((5 + i * 4, y - i * 2), 78 - i * 8, 12, boxstyle="round,pad=.3,rounding_size=1",
                                    facecolor=[BLUE_LIGHT, TEAL_LIGHT, GOLD_LIGHT, RUST_LIGHT][i], edgecolor=c, linewidth=1.3))
        ax.text(9 + i * 4, y + 7 - i * 2, z, color=c, fontsize=7, fontweight="bold")
        ax.text(26 + i * 4, y + 7 - i * 2, title, color=INK, fontsize=8.2, fontweight="bold")
        ax.text(26 + i * 4, y + 2.7 - i * 2, body, color=MUTED, fontsize=6.6)
    ax.text(86, 70, "INFLUENCE", rotation=90, color=TEAL, fontsize=7, fontweight="bold", ha="center")
    arrow(ax, (86, 22), (86, 82), color=TEAL, lw=2)
    ax.text(92, 49, "Promotion needs\ncorroboration +\npolicy decision", color=GOLD, fontsize=7, fontweight="bold", ha="center")
    save(fig, 3)


def f04():
    fig, ax = setup(4, FIGURES[3][1], "Entities, activities, agents, derivation, and invalidation remain connected")
    nodes = {
        "CRM v41": (6, 65, BLUE), "Email e17": (6, 38, GOLD), "Ticket t8": (6, 11, RUST),
        "Normalize a1": (34, 65, PURPLE), "Extract a2": (34, 38, PURPLE), "Summarize a3": (34, 11, PURPLE),
        "Claim m52": (62, 52, TEAL), "Decision d9": (62, 20, BLUE), "Correction c2": (62, 76, RUST),
        "Agent svc": (84, 52, GOLD), "Reviewer u7": (84, 20, GOLD),
    }
    for name, (x, y, c) in nodes.items():
        shape = Circle((x + 6, y + 4), 4.8, facecolor=WHITE, edgecolor=c, linewidth=1.2) if "a" in name and name.startswith(("Normalize", "Extract", "Summarize")) else FancyBboxPatch((x, y), 12, 8, boxstyle="round,pad=.2", facecolor=WHITE, edgecolor=c, linewidth=1.2)
        ax.add_patch(shape)
        ax.text(x + 6, y + 4, name, ha="center", va="center", color=INK, fontsize=6.5, fontweight="bold")
    edges = [((18,69),(34,69),"used"),((18,42),(34,42),"used"),((18,15),(34,15),"used"),((46,69),(62,56),"derived"),((46,42),(62,56),"derived"),((46,15),(62,56),"derived"),((68,52),(68,28),"informed"),((74,80),(68,60),"invalidated"),((84,56),(74,56),"attributed"),((84,24),(74,24),"approved")]
    for start, end, txt in edges:
        arrow(ax, start, end, color=RUST if txt == "invalidated" else MUTED, lw=1)
        ax.text((start[0]+end[0])/2, (start[1]+end[1])/2+2, txt, color=MUTED, fontsize=5.5, ha="center")
    save(fig, 4)


def f05():
    fig, ax = setup(5, FIGURES[4][1], "A versioned envelope binds content to time, source, trust, purpose, and lifecycle")
    groups = [("IDENTITY", BLUE, [("memory_id", "mem_01J…"), ("version", "7"), ("tenant", "acme")]),
              ("CONTENT", TEAL, [("type", "account.assertion"), ("payload_ref", "blob:sha256…"), ("schema", "v3")]),
              ("TIME", PURPLE, [("valid", "[t1, t2)"), ("known", "[t3, ∞)"), ("observed", "t0")]),
              ("PROVENANCE", GOLD, [("source", "crm/account/42"), ("activity", "extractor@9"), ("parents", "[m40,m41]")]),
              ("TRUST", RUST, [("zone", "Z1"), ("score", "0.82"), ("conflict", "0.20")]),
              ("POLICY", TEAL, [("purpose", "renewal"), ("retention", "P365D"), ("delete_key", "dk_991")])]
    for i, (title, c, fields) in enumerate(groups):
        x = 4 + (i % 3) * 30.5
        y = 52 - (i // 3) * 39
        box(ax, x, y, 27, 31, title, edge=c, fill=WHITE, title_color=c, fs=8)
        for j, (k, v) in enumerate(fields):
            yy = y + 18 - j * 6.2
            ax.text(x + 2, yy, k, color=MUTED, fontsize=6.2, fontweight="bold")
            ax.text(x + 25, yy, v, color=INK, fontsize=6.2, ha="right", family="monospace")
            if j < 2: ax.plot([x+2,x+25],[yy-2.5,yy-2.5],color=LINE,lw=.5)
    save(fig, 5)


def f06():
    fig, ax = setup(6, FIGURES[5][1], "Late-arriving corrections preserve both business history and system knowledge")
    ax.axhline(28, xmin=.08, xmax=.93, color=INK, lw=1)
    ax.axhline(62, xmin=.08, xmax=.93, color=INK, lw=1)
    ax.text(3, 62, "VALID TIME", color=BLUE, fontsize=7, fontweight="bold", va="center")
    ax.text(3, 28, "TRANSACTION\nTIME", color=PURPLE, fontsize=7, fontweight="bold", va="center")
    xs = [18, 40, 63, 85]
    for x, t in zip(xs, ["01 AUG", "05 AUG", "08 AUG", "12 AUG"]):
        for y in [28,62]: ax.plot([x,x],[y-2,y+2],color=INK,lw=1)
        ax.text(x, 20, t, color=MUTED, fontsize=6, ha="center")
    ax.add_patch(Rectangle((18, 55), 45, 14, facecolor=RUST_LIGHT, edgecolor=RUST))
    ax.text(40.5, 62, "Discount = 12% (later corrected)", ha="center", va="center", color=RUST, fontsize=7, fontweight="bold")
    ax.add_patch(Rectangle((63, 55), 22, 14, facecolor=TEAL_LIGHT, edgecolor=TEAL))
    ax.text(74, 62, "8%", ha="center", va="center", color=TEAL, fontsize=8, fontweight="bold")
    ax.add_patch(Rectangle((18, 21), 45, 14, facecolor=RUST_LIGHT, edgecolor=RUST))
    ax.text(40.5, 28, "System knows 12%", ha="center", va="center", color=RUST, fontsize=7, fontweight="bold")
    ax.add_patch(Rectangle((63, 21), 22, 14, facecolor=TEAL_LIGHT, edgecolor=TEAL))
    ax.text(74, 28, "Correction arrives", ha="center", va="center", color=TEAL, fontsize=7, fontweight="bold")
    box(ax, 18, 75, 67, 10, "AS-OF QUERY", "What did the agent know on 06 Aug about the term valid on 03 Aug? → 12%, version 4", edge=GOLD, fill=GOLD_LIGHT, title_color=GOLD, fs=7.2)
    save(fig, 6)


def f07():
    fig, ax = setup(7, FIGURES[6][1], "Eight fail-closed gates before a record may influence a decision")
    stages = [("1", "ACQUIRE", "object + source", BLUE), ("2", "PARSE", "safe renderer", BLUE), ("3", "CLASSIFY", "type + sensitivity", PURPLE),
              ("4", "NEUTRALIZE", "instructions → data", RUST), ("5", "PROVENANCE", "bind source + hash", GOLD), ("6", "VALIDATE", "schema + semantics", TEAL),
              ("7", "CORROBORATE", "independent support", GOLD), ("8", "PROMOTE", "policy decision", TEAL)]
    for i, (n, title, body, c) in enumerate(stages):
        x = 2 + (i % 4) * 23.5
        y = 55 - (i // 4) * 30
        box(ax, x, y, 20, 19, f"{n}  {title}", body, edge=c, fill=WHITE, title_color=c, fs=7.8)
        if i % 4 < 3: arrow(ax, (x+20,y+9.5),(x+23.5,y+9.5), color=c)
        elif i == 3: arrow(ax, (x+10,y),(x+10,44), color=RUST, connectionstyle="arc3,rad=.25")
    box(ax, 26, 5, 43, 9, "QUARANTINE BUS", "any failed gate → durable reason + non-influential state", edge=RUST, fill=RUST_LIGHT, title_color=RUST, fs=7.2)
    for x in [12,35.5,59,82.5]: arrow(ax,(x,55),(47.5,14),color=RUST,lw=.55)
    save(fig, 7)


def f08():
    fig, ax = setup(8, FIGURES[7][1], "Attack influence survives transformation unless provenance and trust survive too")
    chain = [(4, "MALICIOUS PDF", "hidden instruction", RUST), (23, "TICKET", "trusted channel", GOLD), (42, "SUMMARY", "model amplifies", PURPLE),
             (61, "EMBEDDING", "origin obscured", PURPLE), (80, "RETRIEVAL", "high similarity", RUST)]
    for x, t, b, c in chain:
        box(ax, x, 56, 15, 15, t, b, edge=c, fill=WHITE, title_color=c, fs=7)
        if x < 80: arrow(ax,(x+15,63.5),(x+19,63.5),color=RUST)
    branches = [(23,38,"source laundering"),(42,25,"summary authority"),(61,12,"semantic persistence")]
    for x,y,t in branches:
        arrow(ax,(x+7.5,56),(x+7.5,y+8),color=RUST,lw=1)
        box(ax,x,y,15,8,t.upper(),edge=RUST,fill=RUST_LIGHT,title_color=RUST,fs=6.2)
    ax.add_patch(Rectangle((74, 5), 21, 39, facecolor=TEAL_LIGHT, edgecolor=TEAL, linewidth=1.4))
    ax.text(84.5, 39, "CONTROL BREAK", color=TEAL, fontsize=7.5, fontweight="bold", ha="center")
    for i, t in enumerate(["provenance required","purpose allowed","trust floor","conflict scan"]):
        ax.text(84.5, 31-i*6, f"✓ {t}", color=TEAL, fontsize=6.5, ha="center")
    save(fig, 8)


def f09():
    fig, ax = setup(9, FIGURES[8][1], "Suspicious content cannot silently return to an influential state")
    states = [(7,62,"CANDIDATE",BLUE_LIGHT,BLUE),(36,62,"QUARANTINED",RUST_LIGHT,RUST),(66,62,"UNDER REVIEW",GOLD_LIGHT,GOLD),
              (7,20,"PROMOTED",TEAL_LIGHT,TEAL),(36,20,"REJECTED",RUST_LIGHT,RUST),(66,20,"EXPIRED",PURPLE_LIGHT,PURPLE)]
    for x,y,t,fill,c in states: box(ax,x,y,22,13,t,"durable state",edge=c,fill=fill,title_color=c,fs=8)
    edges=[((29,68.5),(36,68.5),"risk signal",RUST),((58,68.5),(66,68.5),"assign",GOLD),((77,62),(18,33),"corroborated",TEAL),((66,62),(47,33),"invalid",RUST),((77,62),(77,33),"deadline",PURPLE),((36,26.5),(29,26.5),"appeal + new evidence",GOLD)]
    for s,e,t,c in edges:
        arrow(ax,s,e,color=c,connectionstyle="arc3,rad=.08")
        ax.text((s[0]+e[0])/2,(s[1]+e[1])/2+2,t,color=c,fontsize=5.8,ha="center",fontweight="bold")
    save(fig, 9)


def f10():
    fig, ax = setup(10, FIGURES[9][1], "Domain-specific half-lives govern soft decay before hard expiry", plot=True)
    hours=np.linspace(0,720,300)
    series=[("PRICE",6,RUST),("CASE STATUS",24,GOLD),("ACCOUNT RISK",168,PURPLE),("CONTRACT TERM",4320,BLUE)]
    for name,half,c in series:
        score=np.exp(-math.log(2)*hours/half)
        ax.plot(hours/24,score,label=f"{name} · t½={half/24:g}d",color=c,lw=2.2)
    ax.axhline(.5,color=MUTED,lw=.8,ls="--")
    ax.axhspan(0,.35,color=RUST_LIGHT,alpha=.55)
    ax.text(29,.18,"REVALIDATE / EXCLUDE",color=RUST,fontsize=7,fontweight="bold",ha="right")
    ax.set_xlim(0,30); ax.set_ylim(0,1.03); ax.set_xlabel("AGE (DAYS)",color=MUTED,fontsize=7); ax.set_ylabel("FRESHNESS WEIGHT",color=MUTED,fontsize=7)
    ax.grid(axis="both",color=LINE,lw=.5); ax.legend(frameon=False,fontsize=6.5,ncol=2,loc="upper right")
    ax.tick_params(colors=MUTED,labelsize=6)
    save(fig,10)


def f11():
    fig, ax = setup(11, FIGURES[10][1], "A transparent routing heuristic exposes every contribution and penalty")
    factors=[("SOURCE",.82,.25,BLUE),("CORROBORATION",.75,.25,TEAL),("FRESHNESS",.88,.20,PURPLE),("TRANSFORM",.92,.15,GOLD),("POLICY FIT",1.0,.15,TEAL)]
    x=3
    weighted=0
    for name,val,w,c in factors:
        box(ax,x,54,15,20,name,f"{val:.2f} × {w:.2f}",edge=c,fill=WHITE,title_color=c,fs=6.8)
        contrib=val*w; weighted+=contrib
        ax.text(x+7.5,59,f"{contrib:.3f}",ha="center",color=INK,fontsize=9,fontweight="bold")
        if x<80: ax.text(x+17,64,"+",color=MUTED,fontsize=14,fontweight="bold")
        x+=18.5
    penalty=.20*.35
    box(ax,18,23,28,13,"WEIGHTED SUPPORT",f"Σ wᵢxᵢ = {weighted:.3f}",edge=TEAL,fill=TEAL_LIGHT,title_color=TEAL,fs=8)
    box(ax,52,23,28,13,"CONTRADICTION",f"λC = .35 × .20 = {penalty:.3f}",edge=RUST,fill=RUST_LIGHT,title_color=RUST,fs=8)
    ax.text(49,29.5,"−",color=RUST,fontsize=18,fontweight="bold",ha="center")
    result=max(0,min(1,weighted-penalty))
    box(ax,28,4,44,11,"DECISION-USE SCORE",f"D = clamp({weighted:.3f} − {penalty:.3f}) = {result:.3f}",edge=BLUE,fill=BLUE_LIGHT,title_color=BLUE,fs=8)
    save(fig,11)


def f12():
    fig, ax = setup(12, FIGURES[11][1], "Seven gates turn a semantic candidate into admissible decision evidence")
    steps=[("TENANT + ACL?",BLUE),("PURPOSE?",PURPLE),("VALID NOW?",GOLD),("TRUST FLOOR?",TEAL),("PROVENANCE?",BLUE),("CONFLICT?",RUST),("ACTION FIT?",TEAL)]
    for i,(t,c) in enumerate(steps):
        x=3+i*13.3; y=60-(i%2)*10
        ax.add_patch(Polygon([[x,y+6],[x+6,y+12],[x+12,y+6],[x+6,y]],closed=True,facecolor=WHITE,edgecolor=c,linewidth=1.2))
        ax.text(x+6,y+6,wrap(t,14),ha="center",va="center",color=c,fontsize=6.4,fontweight="bold")
        if i<len(steps)-1: arrow(ax,(x+12,y+6),(x+13.3,y+6),color=c,lw=.9)
        arrow(ax,(x+6,y),(x+6,27),color=RUST,lw=.6)
    box(ax,3,17,91,10,"EXCLUDE LEDGER", "deny reason · policy version · memory version · request id · timestamp",edge=RUST,fill=RUST_LIGHT,title_color=RUST,fs=7.5)
    box(ax,30,2,39,9,"ADMIT", "citation + version + score + expiry",edge=TEAL,fill=TEAL_LIGHT,title_color=TEAL,fs=7.5)
    arrow(ax,(89,56),(69,11),color=TEAL,lw=1.4)
    save(fig,12)


def f13():
    fig, ax = setup(13, FIGURES[12][1], "Policy constrains candidate generation, ranking, and context assembly")
    stages=[(2,"QUERY", "intent · action · user",BLUE),(20,"POLICY PEP", "tenant · ACL · purpose",GOLD),(38,"PARTITIONED INDEX", "vector + metadata",PURPLE),
            (56,"POLICY RERANKER", "similarity × admissibility",TEAL),(74,"CONTEXT PACK", "citations · versions",BLUE)]
    for x,t,b,c in stages:
        box(ax,x,52,16,20,t,b,edge=c,fill=WHITE,title_color=c,fs=7)
        if x<74: arrow(ax,(x+16,62),(x+18,62),color=c)
    controls=[("PIP", "roles · consent"),("TIME SERVICE", "valid + known"),("TRUST GRAPH", "zone + support"),("CONFLICT", "field authority")]
    for i,(t,b) in enumerate(controls):
        x=11+i*21
        box(ax,x,18,17,13,t,b,edge=GOLD,fill=GOLD_LIGHT,title_color=GOLD,fs=6.8)
        arrow(ax,(x+8.5,31),(28 if i<2 else 64,52),color=GOLD,lw=.8)
    box(ax,30,3,40,8,"DENY BY DEFAULT", "unknown metadata or policy version never falls back to similarity-only retrieval",edge=RUST,fill=RUST_LIGHT,title_color=RUST,fs=6.5)
    save(fig,13)


def f14():
    fig, ax = setup(14, FIGURES[13][1], "Deterministic resolution rules by incoming and stored source class", plot=True)
    classes=["SIGNED\nRECORD","REVIEWED\nDOC","USER\nNOTE","MODEL\nSUMMARY","EXTERNAL\nWEB"]
    data=np.array([[4,4,4,4,4],[3,3,4,4,4],[2,2,3,4,4],[1,1,2,3,4],[1,1,2,3,3]])
    cmap=LinearSegmentedColormap.from_list("conflict",[RUST_LIGHT,GOLD_LIGHT,BLUE_LIGHT,TEAL_LIGHT,TEAL])
    im=ax.imshow(data,cmap=cmap,vmin=0,vmax=4,aspect="auto")
    labels={1:"KEEP\nSTORED",2:"COEXIST",3:"REVIEW",4:"INCOMING\nWINS"}
    for i in range(5):
        for j in range(5): ax.text(j,i,labels[data[i,j]],ha="center",va="center",fontsize=6.2,color=INK,fontweight="bold")
    ax.set_xticks(range(5),classes,fontsize=6); ax.set_yticks(range(5),classes,fontsize=6)
    ax.set_xlabel("STORED SOURCE CLASS",fontsize=7,color=MUTED); ax.set_ylabel("INCOMING SOURCE CLASS",fontsize=7,color=MUTED)
    ax.tick_params(length=0,colors=MUTED)
    save(fig,14)


def f15():
    fig, ax = setup(15, FIGURES[14][1], "Reverse lineage drives correction and deletion through every derivative")
    actors=[("REQUESTER",5,BLUE),("CONTROL PLANE",24,GOLD),("PRIMARY STORE",43,TEAL),("DERIVATIVE BUS",62,PURPLE),("VERIFIER",81,BLUE)]
    for name,x,c in actors:
        ax.text(x,82,name,ha="center",color=c,fontsize=6.5,fontweight="bold")
        ax.plot([x,x],[12,78],color=LINE,lw=.9,ls="--")
    msgs=[(5,24,72,"1 signed request"),(24,43,63,"2 tombstone + version"),(43,62,54,"3 reverse-lineage fanout"),(62,62,43,"4 indexes · caches · summaries"),(62,81,34,"5 completion evidence"),(81,24,25,"6 reconcile stragglers"),(24,5,16,"7 deletion receipt")]
    for s,e,y,t in msgs:
        arrow(ax,(s,y),(e,y),color=RUST if "stragglers" in t else TEAL,lw=1.2)
        ax.text((s+e)/2,y+2,t,ha="center",color=INK,fontsize=5.8,fontweight="bold")
    save(fig,15)


def f16():
    fig, ax = setup(16, FIGURES[15][1], "Illustrative retention days before policy overrides", plot=True)
    rows=["IDENTITY FACT","CONTRACT TERM","COMMUNICATION","DERIVED CLAIM","EMBEDDING","DECISION RECEIPT"]
    cols=["SERVICE","RENEWAL","SUPPORT","RISK","TRAINING"]
    data=np.array([[365,365,365,365,0],[2555,2555,2555,2555,0],[90,365,730,365,0],[30,180,180,365,0],[30,90,90,180,0],[2555,2555,2555,2555,0]])
    cmap=LinearSegmentedColormap.from_list("retention",[WHITE,BLUE_LIGHT,TEAL_LIGHT,GOLD_LIGHT,PURPLE_LIGHT])
    ax.imshow(np.log1p(data),cmap=cmap,aspect="auto")
    for i in range(len(rows)):
        for j in range(len(cols)):
            txt="DENY" if data[i,j]==0 else f"{data[i,j]} d"
            ax.text(j,i,txt,ha="center",va="center",fontsize=6.6,fontweight="bold",color=RUST if txt=="DENY" else INK)
    ax.set_xticks(range(len(cols)),cols,fontsize=6); ax.set_yticks(range(len(rows)),rows,fontsize=6)
    ax.tick_params(length=0,colors=MUTED); ax.set_xlabel("PERMITTED PURPOSE",fontsize=7,color=MUTED)
    save(fig,16)


def f17():
    fig, ax = setup(17, FIGURES[16][1], "Each objective has a target, actual, owner, and breach response")
    metrics=[("PROVENANCE COVERAGE","≥99.95%","99.98%","DATA","PASS"),("P95 RETRIEVAL","≤120 ms","104 ms","PLATFORM","PASS"),
             ("STALE ADMISSION","≤0.10%","0.07%","DATA","PASS"),("POLICY BYPASS","0","0","SECURITY","PASS"),
             ("POISON ADMISSION","0","1","SECURITY","BREACH"),("DELETE P99","≤24 h","31 h","PRIVACY","BREACH"),
             ("CONFLICT ABSTENTION","≥99%","99.4%","RISK","PASS"),("AS-OF REPLAY","≥99.9%","99.94%","AUDIT","PASS")]
    headers=[("OBJECTIVE",3),("TARGET",47),("ACTUAL",62),("OWNER",76),("STATE",89)]
    for h,x in headers: ax.text(x,81,h,color=BLUE,fontsize=6.5,fontweight="bold",ha="left")
    for i,row in enumerate(metrics):
        y=70-i*8.2; state=row[4]; c=TEAL if state=="PASS" else RUST
        ax.add_patch(Rectangle((2,y-3),94,7,facecolor=WHITE if i%2==0 else PAPER,edgecolor=LINE,lw=.4))
        for txt,x in zip(row,[3,47,62,76,89]): ax.text(x,y,txt,color=c if x==89 else INK,fontsize=6.4,fontweight="bold" if x in [3,89] else "normal",va="center")
        ax.add_patch(Circle((86,y),1.5,facecolor=c,edgecolor=c))
    save(fig,17)


def f18():
    fig, ax = setup(18, FIGURES[17][1], "Promotion gates increase memory influence only after controls are proven")
    phases=[("0","INVENTORY","find hidden state","owner + map",BLUE),("1","ENVELOPE","type + provenance","≥99.9% coverage",PURPLE),
            ("2","SHADOW","retrieve, no influence","offline lift + safety",GOLD),("3","READ-ONLY","cite to humans","deletion + replay",TEAL),
            ("4","BOUNDED","low-risk actions","error budget",TEAL),("5","CONSEQUENTIAL","approval + receipts","independent review",BLUE)]
    for i,(n,t,b,g,c) in enumerate(phases):
        x=2+i*15.7; y=18+i*9
        box(ax,x,y,14,23,f"{n}  {t}",b,edge=c,fill=WHITE,title_color=c,fs=6.7)
        ax.text(x+7,y+4,wrap("GATE: "+g,18),ha="center",va="center",color=GOLD,fontsize=5.8,fontweight="bold")
        if i<5: arrow(ax,(x+14,y+11.5),(x+15.7,y+20.5),color=c)
    ax.plot([2,95],[11,11],color=RUST,lw=1.2)
    ax.text(48.5,7,"ANY BREACH → ROLLBACK THE AFFECTED MEMORY CLASS AND ACTION CLASS",ha="center",color=RUST,fontsize=6.8,fontweight="bold")
    save(fig,18)


def write_map() -> None:
    lines = [
        "# Figure map — Your AI Agent's Memory Is a Database, Not a Prompt",
        "",
        "All quantitative values are synthetic. Diagrams are reference architectures, not claims about a deployed system.",
        "",
        "Renderer: reproducible Matplotlib PNG at 2400×1600. Each figure includes a technical analysis rail, control contract, assumptions, semantic legend, and evidence label.",
        "",
        "| Figure | Tier | Analytical question / form | Supported takeaway | Inputs / assumptions |",
        "|---:|---|---|---|---|",
    ]
    for number, title, form, takeaway in FIGURES:
        assumption = ASSUMPTIONS.get(number, "Reference architecture; no observed production data.")
        lines.append(f"| {number} | {'Core' if number in CORE else 'Supplemental'} | {title} · {form} | {takeaway} | {assumption} |")
    lines.extend(["", "Palette: blue/teal for trusted or governed paths, gold for decisions, rust for risk/denial, purple for transformation or policy context. Shape, position, and labels duplicate every color encoding.", ""])
    MAP_PATH.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    generators = [f01,f02,f03,f04,f05,f06,f07,f08,f09,f10,f11,f12,f13,f14,f15,f16,f17,f18]
    for fn in generators:
        fn()
    write_map()
    print(f"Generated {len(generators)} figures in {OUT}")


if __name__ == "__main__":
    main()
