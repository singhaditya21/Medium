#!/usr/bin/env python3
"""Generate 18 deep-dive figures for the production agent kill-switch story."""

from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.colors import LinearSegmentedColormap
from matplotlib.patches import Circle, Rectangle

from technical_figure_framework import (
    BLUE, BLUE_LIGHT, GOLD, GOLD_LIGHT, GREEN, GREEN_LIGHT, INK, LINE, MUTED,
    PAPER, PURPLE, PURPLE_LIGHT, RUST, RUST_LIGHT, SURFACE, TEAL, TEAL_LIGHT,
    FigureSpec, FigureSystem, arrow, box,
)

ROOT = Path(__file__).resolve().parents[1]
SLUG = "your-ai-agent-needs-a-real-kill-switch"
OUT = ROOT / "assets" / "images" / SLUG
MAP_PATH = ROOT / "stories" / f"{SLUG}-figure-map.md"


def S(n, title, form, takeaway, domain, insights, contract,
      assumption="Reference architecture; no observed production data.", core=True):
    return FigureSpec(n, title, form, takeaway, domain, tuple(insights), tuple(contract), assumption, core)


SPECS = [
    S(1, "Dashboard toggle versus real containment", "Control comparison",
      "A UI state changes intent; a real kill switch removes authority and reachability, fences stale workers, resolves in-flight effects, and proves the stop.",
      "CONTAINMENT MODEL", ["A control-plane flag cannot recall cached credentials or disconnected workers.", "Independent enforcement layers prevent one failed dependency from preserving authority.", "Containment ends with evidence and reconciliation, not a green dashboard badge."],
      [("TRIGGER", "incident commander"), ("ENFORCE", "identity · network · tools"), ("PROOF", "receipts + probes")]),
    S(2, "Multi-layer kill-switch architecture", "Reference architecture",
      "One signed containment epoch fans out to identity, scheduler, workload, network, tool, data, and effect gateways while an independent observer measures convergence.",
      "CONTROL PLANE", ["The coordinator declares scope and epoch; it does not become the sole enforcement point.", "Every effect boundary rejects stale authority locally.", "Evidence flows to a write-once incident ledger even when execution networks are isolated."],
      [("COMMAND", "signed containment epoch"), ("LAYERS", "7 enforcement planes"), ("VERIFY", "independent observer")]),
    S(3, "Authority revocation graph", "Dependency graph",
      "Revocation must traverse grants, sessions, leases, credentials, queues, tool bindings, and delegated child agents—not merely the initiating user token.",
      "AUTHORITY", ["Each derived capability retains a parent, subject, resource scope, epoch, and expiry.", "Graph closure identifies what must be revoked for the selected incident scope.", "Unknown or untraceable edges are containment defects and default to quarantine."],
      [("ROOT", "agent principal"), ("EDGES", "delegation + derivation"), ("CLOSURE", "all live descendants")]),
    S(4, "Security-event propagation sequence", "Sequence diagram",
      "A signed security event starts containment, but each receiver must authenticate, deduplicate, persist, enforce, acknowledge, and expose its local proof time.",
      "SIGNAL DELIVERY", ["Event issuance and enforcement acknowledgement are distinct milestones.", "Replay protection uses event identity, issuer, audience, issue time, and monotonic scope epoch.", "Missed push delivery requires polling, short leases, or deny-on-stale compensating controls."],
      [("FORMAT", "SET / SSF profile"), ("DELIVERY", "push + recovery poll"), ("ACK", "durable local enforcement")]),
    S(5, "Revocation latency budget", "Latency waterfall",
      "The stop-time objective is a sum of detection, command, distribution, local enforcement, and verification tails; improving only the dashboard response does not bound exposure.",
      "STOP-TIME OBJECTIVE", ["Use P95 and P99 component budgets plus an end-to-end incident clock.", "Parallel layers converge at different speeds, so the slowest material path controls containment.", "Offline workers need authority expiry short enough to bound worst-case continued effects."],
      [("START", "credible trigger"), ("END", "verified containment"), ("TARGET", "synthetic P99 ≤ 90 s")],
      "Synthetic latency budget in seconds; values are illustrative, not measured performance."),
    S(6, "Fencing-epoch timeline", "Distributed timeline",
      "A monotonic epoch lets resource and effect gateways reject work from stale processes even when those processes never receive the kill command.",
      "FENCING", ["Revocation changes the accepted epoch at the enforcement boundary.", "Workers must present the epoch on every effectful request, not only at startup.", "Epoch comparison requires a strongly ordered authority for the protected scope."],
      [("TOKEN", "scope + epoch + expiry"), ("CHECK", "request epoch ≥ current"), ("STALE", "reject before effect")]),
    S(7, "Stale-worker rejection path", "Request architecture",
      "A disconnected worker may continue computing, but it cannot create an external effect after the gateway advances the containment epoch.",
      "EFFECT FENCING", ["Local generation is not the security boundary; tool and data gateways are.", "The gateway checks principal, scope, epoch, lease, policy, idempotency, and resource version.", "Rejected proposals enter quarantine for evidence, never an automatic retry loop."],
      [("REQUEST", "proposal + authority envelope"), ("DECISION", "atomic gate check"), ("RESULT", "deny + evidence")]),
    S(8, "Default-deny egress containment", "Network map",
      "Quarantine denies new egress by default and selectively preserves only incident telemetry, time, identity validation, and approved recovery channels.",
      "NETWORK", ["Identity revocation cannot stop a process holding another usable secret or unauthenticated path.", "DNS, service mesh, NAT, proxies, and direct IP paths need consistent policy coverage.", "Existing connections and connection tracking require explicit termination or bounded expiry."],
      [("BASELINE", "allowlisted egress"), ("QUARANTINE", "deny new + sever old"), ("EXCEPT", "incident evidence only")]),
    S(9, "Tool-specific kill matrix", "Control matrix",
      "Different tools require different stop controls: credential revocation, gateway deny, connection termination, queue purge, transaction cancellation, or downstream freeze.",
      "TOOL CONTAINMENT", ["A universal SDK flag cannot cover vendor sessions, asynchronous jobs, and already accepted work.", "Each tool declares command, acknowledgement, residual effect, and reconciliation method.", "Unsupported hard-stop cells become explicit business risk and constrain agent authority."],
      [("TOOLS", "8 effect classes"), ("CONTROLS", "7 stop mechanisms"), ("GRADE", "none · partial · strong")],
      "Synthetic control-coverage assessment; not a vendor capability claim."),
    S(10, "In-flight drain state machine", "State machine",
      "Containment distinguishes proposed, authorized, dispatched, accepted, committed, and verified actions so each can be cancelled, fenced, reconciled, or compensated correctly.",
      "WORKFLOW DRAIN", ["Stopping intake is safe only for work that has not crossed an effect boundary.", "Accepted-but-unconfirmed operations are ambiguous until reconciled with the system of record.", "Compensation is a governed action with its own authority and verification."],
      [("NEW WORK", "reject"), ("IN FLIGHT", "classify by boundary"), ("EXIT", "known terminal state")]),
    S(11, "In-flight action inventory", "Incident inventory",
      "An incident commander needs a live inventory grouped by effect state, reversibility, impact, and deadline—not a raw list of running pods.",
      "RECONCILIATION", ["Stable action, attempt, tool-call, and idempotency identities join every layer.", "Priority follows loss exposure and ambiguity, not queue age alone.", "The inventory remains append-only while reconciliation adds authoritative outcomes."],
      [("ACTIONS", "synthetic n=1,240"), ("AXES", "state × reversibility"), ("QUEUE", "loss-ranked review")],
      "Synthetic action inventory for one containment event; counts and values are illustrative."),
    S(12, "Ambiguous-effect decision tree", "Decision tree",
      "When a timeout or disconnect hides whether an effect committed, query authoritative state before retrying, compensating, or asking a human to decide.",
      "AMBIGUOUS OUTCOME", ["Transport failure is not evidence that the business operation failed.", "Idempotency lookup and resource-version checks prevent duplicate mutation.", "If truth cannot be established, freeze the resource and escalate with evidence."],
      [("INPUT", "accepted, no receipt"), ("ORACLE", "system of record"), ("DEFAULT", "freeze · do not replay")]),
    S(13, "Containment blast-radius model", "Exposure curves",
      "Blast radius grows with effect rate and stop time; independent local fencing bends the exposure curve before every worker receives the central command.",
      "BUSINESS EXPOSURE", ["Report effects attempted, rejected, committed, ambiguous, and compensated separately.", "High-value or irreversible effects require lower stop-time and lease bounds.", "One aggregate action count can hide concentrated account or customer exposure."],
      [("RATE", "synthetic effects/s"), ("X", "verified stop time"), ("Y", "committed exposure")],
      "Synthetic scenario curves; no forecast or production incident data."),
    S(14, "Recovery authorization chain", "Dual-control chain",
      "Re-entry requires evidence that cause, authority, workload, network, tools, data, and ambiguous effects are controlled—then a new epoch and bounded canary.",
      "RECOVERY", ["The person who triggers emergency containment need not have unilateral restart authority.", "Recovery creates fresh credentials and workload instances; it does not re-enable compromised state.", "Each approval binds to scope, evidence digest, expiration, and rollback target."],
      [("REVIEW", "security + domain + platform"), ("ISSUE", "fresh recovery epoch"), ("RESTORE", "bounded canary")]),
    S(15, "Containment drill timeline", "Exercise timeline",
      "A kill switch is credible only when drills exercise disconnected workers, cached authority, open connections, asynchronous tools, ambiguous effects, and controlled recovery.",
      "RESILIENCE TEST", ["Measure both technical convergence and business reconciliation.", "Inject partial delivery and stale-state conditions, not only a cooperative shutdown.", "Every drill produces control gaps, owners, due dates, and a retest."],
      [("SCENARIO", "synthetic revenue agent"), ("DURATION", "120-minute exercise"), ("OUTPUT", "evidence + remediations")]),
    S(16, "Containment control coverage", "Coverage matrix",
      "Coverage must be demonstrated across execution locations and effect boundaries; one uncovered path invalidates a broad stop claim.",
      "ASSURANCE", ["Test connected, partitioned, restarted, and delayed workers separately.", "Evidence strength differs among configuration, simulation, integration test, and observed drill.", "Critical gaps block expansion of agent authority until remediated or explicitly constrained."],
      [("ROWS", "8 containment controls"), ("COLUMNS", "7 failure contexts"), ("EVIDENCE", "config → observed drill")],
      "Synthetic coverage ratings for explanation; not an assessment of a deployed system."),
    S(17, "Containment service objectives", "SLO scorecard",
      "Stop command acceptance, local enforcement, effect rejection, inventory completeness, reconciliation, evidence durability, and drill success need independent objectives.",
      "OPERATIONS", ["A fast command API can pass while stale effects continue.", "Measure from the first credible trigger through independent proof at each material boundary.", "Breach freezes recovery or authority expansion and invokes incident governance."],
      [("WINDOW", "synthetic 90 days"), ("STATUS", "6 pass · 2 breach"), ("OWNERS", "Security · Platform · Domain")],
      "Synthetic operating scorecard with deliberate breaches."),
    S(18, "Rollout to a provable kill switch", "Maturity roadmap",
      "Teams progress from inventory and effect gateways to short-lived authority, layered containment, reconciliation, drills, and independently verified recovery.",
      "ROLLOUT", ["Begin with the effect and authority graph, not the emergency button design.", "No phase claims containment beyond the paths it can test and prove.", "Authority expands only after stop-time, ambiguity, and recovery gates pass."],
      [("PHASES", "0 through 5"), ("GATES", "coverage + STO + drill"), ("END STATE", "bounded, provable control")]),
]

SYSTEM = FigureSystem(SLUG, OUT, MAP_PATH, "Your AI Agent Needs a Real Kill Switch", SPECS)


def f01():
    fig, ax = SYSTEM.setup(1, "Intent is not containment; the effect boundaries determine whether the agent is truly stopped")
    rows = [
        ("CONTROL", "database boolean", "signed scope + monotonic epoch"),
        ("AUTHORITY", "future login blocked", "tokens, sessions, leases, delegates revoked"),
        ("WORKERS", "cooperative poll", "stale epoch rejected at every effect gate"),
        ("NETWORK", "unchanged", "deny new egress + sever risky sessions"),
        ("TOOLS", "generic disable", "tool-specific stop and acknowledgement"),
        ("IN FLIGHT", "assumed cancelled", "drain, reconcile, compensate, or freeze"),
        ("RECOVERY", "toggle on", "fresh state + dual approval + bounded canary"),
        ("PROOF", "UI says disabled", "independent probes + durable receipts"),
    ]
    for x, title, c, fill in [(2, "DASHBOARD TOGGLE", RUST, RUST_LIGHT), (52, "REAL KILL SWITCH", TEAL, TEAL_LIGHT)]:
        box(ax, x, 76, 44, 9, title, "claimed stop", edge=c, fill=fill, title_color=c, fs=7.0)
    for i, (label, left, right) in enumerate(rows):
        y = 68 - i * 7.6
        ax.text(49, y + 2.5, label, ha="center", va="center", color=MUTED, fontsize=5.0, fontweight="bold")
        box(ax, 2, y, 44, 5.5, left, edge=LINE, fill=SURFACE, fs=5.5)
        box(ax, 52, y, 44, 5.5, right, edge=LINE, fill=SURFACE, fs=5.5)
    SYSTEM.save(fig, 1)


def f02():
    fig, ax = SYSTEM.setup(2, "One command, independent local enforcement, and an observer outside the execution trust domain")
    box(ax, 34, 69, 32, 12, "CONTAINMENT COORDINATOR", "scope · epoch · reason · expiry · signer", edge=RUST, fill=RUST_LIGHT, title_color=RUST, fs=6.5)
    layers = [
        ("IDENTITY", "revoke grants + sessions", 2, 50, PURPLE),
        ("SCHEDULER", "stop intake + dequeue", 26, 50, BLUE),
        ("WORKLOAD", "quarantine + replace", 50, 50, GOLD),
        ("NETWORK", "deny egress + sever", 74, 50, RUST),
        ("TOOL GATE", "epoch + policy reject", 2, 28, TEAL),
        ("DATA GATE", "writes + export freeze", 26, 28, PURPLE),
        ("EFFECT STORE", "reconcile + compensate", 50, 28, GOLD),
        ("EVIDENCE LEDGER", "append receipts + ack", 74, 28, BLUE),
    ]
    for title, body, x, y, c in layers:
        box(ax, x, y, 20, 13, title, body, edge=c, fill=SURFACE, title_color=c, fs=5.8)
        arrow(ax, (50, 69), (x + 10, y + 13), color=c, lw=.65)
    box(ax, 27, 8, 46, 11, "INDEPENDENT CONTAINMENT OBSERVER", "probe each boundary · compare epoch · measure convergence · alert gaps", edge=TEAL, fill=TEAL_LIGHT, title_color=TEAL, fs=6.5)
    for _, _, x, y, c in layers:
        arrow(ax, (x + 10, y), (50, 19), color=c, lw=.45)
    SYSTEM.save(fig, 2)


def f03():
    fig, ax = SYSTEM.setup(3, "Revocation computes transitive closure over every derived source of agent authority")
    nodes = {
        "AGENT\nPRINCIPAL": (8, 41, BLUE), "ACCESS\nGRANT": (28, 69, PURPLE), "SESSION": (28, 47, PURPLE),
        "WORK LEASE": (28, 25, GOLD), "CHILD AGENT": (51, 72, BLUE), "TOOL TOKEN": (51, 53, RUST),
        "QUEUE CLAIM": (51, 34, GOLD), "DB SESSION": (51, 15, PURPLE), "CRM": (76, 71, TEAL),
        "CPQ": (76, 54, TEAL), "EMAIL": (76, 37, TEAL), "EXPORT": (76, 20, TEAL),
    }
    for name, (x, y, c) in nodes.items():
        box(ax, x, y, 16, 10, name, "live descendant", edge=c, fill=SURFACE, title_color=c, fs=5.4)
    edges = [
        ("AGENT\nPRINCIPAL", "ACCESS\nGRANT"), ("AGENT\nPRINCIPAL", "SESSION"), ("AGENT\nPRINCIPAL", "WORK LEASE"),
        ("ACCESS\nGRANT", "CHILD AGENT"), ("ACCESS\nGRANT", "TOOL TOKEN"), ("SESSION", "TOOL TOKEN"),
        ("WORK LEASE", "QUEUE CLAIM"), ("SESSION", "DB SESSION"), ("CHILD AGENT", "CRM"),
        ("TOOL TOKEN", "CPQ"), ("TOOL TOKEN", "EMAIL"), ("DB SESSION", "EXPORT"),
    ]
    for a, b in edges:
        xa, ya, _ = nodes[a]; xb, yb, _ = nodes[b]
        arrow(ax, (xa + 16, ya + 5), (xb, yb + 5), color=RUST if xb > 50 else MUTED, lw=.8)
    ax.text(50, 5, "REVOCATION SET = ROOT ∪ ALL LIVE DESCENDANTS ∪ UNATTRIBUTED CAPABILITIES IN SCOPE", ha="center", color=RUST, fontsize=6.2, fontweight="bold")
    SYSTEM.save(fig, 3)


def f04():
    fig, ax = SYSTEM.setup(4, "The event is durable and replay-safe; acknowledgement means local enforcement, not message receipt")
    lanes = ["INCIDENT\nCOMMAND", "EVENT\nTRANSMITTER", "IDENTITY", "RUNTIME", "TOOL GATE", "OBSERVER"]
    xs = np.linspace(5, 95, len(lanes))
    for x, lane in zip(xs, lanes):
        ax.text(x, 82, lane, ha="center", va="center", fontsize=5.5, fontweight="bold", color=INK)
        ax.plot([x, x], [10, 77], color=LINE, lw=.8, ls="--")
    events = [
        (0, 1, 73, "signed scope + epoch 42", RUST),
        (1, 2, 63, "SET: revoke / attenuate", PURPLE),
        (1, 3, 54, "SET: quarantine", BLUE),
        (1, 4, 45, "SET: reject epoch < 42", GOLD),
        (2, 5, 34, "ack: grants closed", TEAL),
        (3, 5, 25, "ack: intake drained", TEAL),
        (4, 5, 16, "ack: stale effects denied", TEAL),
    ]
    for a, b, y, label, c in events:
        arrow(ax, (xs[a] + 1, y), (xs[b] - 1, y), color=c, lw=1.1)
        ax.text((xs[a] + xs[b]) / 2, y + 2.2, label, ha="center", color=c, fontsize=5.2, fontweight="bold")
    ax.add_patch(Rectangle((xs[1] - 5, 12), xs[4] - xs[1] + 10, 54, facecolor=BLUE_LIGHT, edgecolor="none", alpha=.18))
    ax.text(50, 7, "RECEIVERS: VERIFY SIGNATURE + ISSUER + AUDIENCE + EVENT ID + SCOPE EPOCH → PERSIST → ENFORCE → ACK", ha="center", color=INK, fontsize=6.0, fontweight="bold")
    SYSTEM.save(fig, 4)


def f05():
    fig, ax = SYSTEM.setup(5, "Synthetic P99 containment budget from credible trigger to independent proof", plot=True)
    labels = ["DETECT + DECLARE", "SIGN COMMAND", "DISTRIBUTE", "IDENTITY ENFORCE", "NETWORK ENFORCE", "TOOL ENFORCE", "PROBE + PROVE"]
    values = np.array([18, 4, 9, 12, 14, 17, 11])
    colors = [RUST, PURPLE, BLUE, PURPLE, RUST, GOLD, TEAL]
    starts = np.r_[0, values.cumsum()[:-1]]
    for y, (label, value, start, c) in enumerate(zip(labels, values, starts, colors)):
        ax.barh(y, value, left=start, color=c, edgecolor=INK, linewidth=.45, height=.62)
        ax.text(start + value / 2, y, f"{value}s", ha="center", va="center", color="white" if c not in (GOLD,) else INK, fontsize=5.4, fontweight="bold")
    ax.set_yticks(range(len(labels)), labels, fontsize=5.4); ax.invert_yaxis()
    ax.set_xlim(0, 100); ax.set_xlabel("Seconds from credible containment trigger · synthetic P99 budget", fontsize=6.1, color=MUTED)
    ax.axvline(90, color=RUST, ls="--", lw=1.2); ax.text(90, -.8, "STO 90s", ha="right", color=RUST, fontsize=6, fontweight="bold")
    ax.grid(axis="x", color=LINE, lw=.5); ax.set_axisbelow(True); ax.tick_params(axis="x", labelsize=5.3, colors=MUTED); ax.tick_params(axis="y", length=0, colors=MUTED)
    ax.text(85, 6.7, "TOTAL 85s", ha="right", color=TEAL, fontsize=6.5, fontweight="bold")
    SYSTEM.save(fig, 5)


def f06():
    fig, ax = SYSTEM.setup(6, "An epoch change fences disconnected or delayed workers at the protected resource boundary")
    lanes = [("CONTROL AUTHORITY", 76, RUST), ("CONNECTED WORKER", 57, BLUE), ("PARTITIONED WORKER", 38, GOLD), ("EFFECT GATEWAY", 19, TEAL)]
    for name, y, c in lanes:
        ax.text(2, y, name, va="center", color=c, fontsize=5.7, fontweight="bold")
        ax.plot([22, 96], [y, y], color=LINE, lw=.8)
    ticks = [(27, "t0\nepoch 41"), (49, "t1\nKILL"), (70, "t2\nepoch 42"), (91, "t3\nproof")]
    for x, label in ticks:
        ax.plot([x, x], [11, 83], color=LINE, lw=.5, ls="--"); ax.text(x, 7, label, ha="center", fontsize=5.2, color=MUTED)
    arrow(ax, (49, 76), (70, 19), color=RUST, lw=1.2); ax.text(59, 53, "advance accepted epoch", color=RUST, fontsize=5.5, fontweight="bold", rotation=-34)
    arrow(ax, (32, 57), (45, 19), color=BLUE, lw=1.0); ax.text(35, 40, "request e41", color=BLUE, fontsize=5.2)
    arrow(ax, (76, 38), (84, 19), color=GOLD, lw=1.0); ax.text(74, 31, "late request e41", color=GOLD, fontsize=5.2)
    box(ax, 38, 12, 15, 8, "ALLOW", "41 = current", edge=TEAL, fill=TEAL_LIGHT, title_color=TEAL, fs=5.2)
    box(ax, 80, 12, 15, 8, "REJECT", "41 < 42", edge=RUST, fill=RUST_LIGHT, title_color=RUST, fs=5.2)
    ax.add_patch(Rectangle((70, 10), 26, 74, facecolor=RUST_LIGHT, edgecolor="none", alpha=.18))
    SYSTEM.save(fig, 6)


def f07():
    fig, ax = SYSTEM.setup(7, "Disconnected computation is harmless only when every external effect is fenced")
    box(ax, 2, 58, 20, 18, "STALE WORKER", "partitioned since epoch 41\ncontinues local inference", edge=GOLD, fill=GOLD_LIGHT, title_color=GOLD, fs=6.1)
    box(ax, 31, 58, 30, 18, "AUTHORITY ENVELOPE", "principal · action · scope · epoch 41\nlease expiry · idempotency · resource version", edge=PURPLE, fill=PURPLE_LIGHT, title_color=PURPLE, fs=6.0)
    box(ax, 70, 50, 26, 30, "EFFECT GATEWAY", "1 authenticate\n2 current epoch = 42\n3 validate lease + scope\n4 enforce policy + version\n5 atomically record decision", edge=TEAL, fill=TEAL_LIGHT, title_color=TEAL, fs=6.1)
    arrow(ax, (22, 67), (31, 67), color=GOLD); arrow(ax, (61, 67), (70, 67), color=PURPLE)
    box(ax, 69, 25, 28, 14, "DENY BEFORE EFFECT", "reason: STALE_EPOCH\nquarantine proposal + receipt", edge=RUST, fill=RUST_LIGHT, title_color=RUST, fs=6.2)
    arrow(ax, (83, 50), (83, 39), color=RUST, lw=1.2)
    resources = [("CRM", 3, 15), ("CPQ", 25, 15), ("EMAIL", 47, 15)]
    for name, x, y in resources:
        box(ax, x, y, 17, 9, name, "no request", edge=LINE, fill=SURFACE, fs=5.6)
    ax.text(39, 8, "NO DIRECT RESOURCE CREDENTIALS OR NETWORK PATH FROM WORKER", ha="center", color=RUST, fontsize=6.1, fontweight="bold")
    SYSTEM.save(fig, 7)


def f08():
    fig, ax = SYSTEM.setup(8, "Quarantine removes outbound reachability while preserving a narrow, observable incident channel")
    box(ax, 35, 57, 28, 19, "QUARANTINED WORKLOAD", "no new tasks · stale epoch\nfilesystem preserved · process isolated", edge=RUST, fill=RUST_LIGHT, title_color=RUST, fs=6.4)
    destinations = [
        ("IDENTITY VALIDATION", 2, 69, TEAL, "ALLOW mTLS"), ("INCIDENT LEDGER", 2, 43, TEAL, "ALLOW append"),
        ("TIME SERVICE", 2, 17, TEAL, "ALLOW signed"), ("CRM / CPQ", 72, 69, RUST, "DENY"),
        ("EMAIL / WEB", 72, 43, RUST, "DENY"), ("DATA EXPORT", 72, 17, RUST, "DENY"),
    ]
    for title, x, y, c, body in destinations:
        fill = TEAL_LIGHT if c == TEAL else RUST_LIGHT
        box(ax, x, y, 24, 12, title, body, edge=c, fill=fill, title_color=c, fs=5.7)
        if x < 35:
            arrow(ax, (35, 66), (x + 24, y + 6), color=c, lw=.9)
        else:
            arrow(ax, (63, 66), (x, y + 6), color=c, lw=.9, style="-[")
    box(ax, 35, 27, 28, 14, "EGRESS POLICY + CONNECTION KILL", "default deny · DNS control · proxy policy\nterminate risky established flows", edge=PURPLE, fill=PURPLE_LIGHT, title_color=PURPLE, fs=6.0)
    arrow(ax, (49, 57), (49, 41), color=PURPLE)
    ax.text(49, 11, "POLICY APPLIES TO NEW FLOWS · CONNECTION STATE · DIRECT IP · PROXY · SERVICE MESH · IPV4 / IPV6", ha="center", color=INK, fontsize=5.8, fontweight="bold")
    SYSTEM.save(fig, 8)


def f09():
    fig, ax = SYSTEM.setup(9, "Each effect class needs an explicit control, acknowledgement, and residual-risk contract", plot=True)
    fig.subplots_adjust(left=.13, right=.745, top=.82, bottom=.15)
    rows = ["CRM MUTATION", "CPQ JOB", "EMAIL SEND", "PAYMENT API", "DB WRITE", "OBJECT EXPORT", "MESSAGE QUEUE", "BROWSER SESSION"]
    cols = ["REVOKE", "GATE DENY", "SEVER", "PURGE", "CANCEL", "FREEZE", "RECONCILE"]
    data = np.array([
        [2, 3, 1, 0, 1, 3, 3], [2, 3, 1, 2, 2, 2, 3], [2, 3, 1, 2, 0, 2, 3], [3, 3, 2, 0, 2, 3, 3],
        [2, 3, 3, 0, 1, 3, 3], [2, 3, 2, 2, 2, 3, 3], [1, 3, 2, 3, 2, 2, 3], [2, 2, 3, 0, 0, 1, 2],
    ])
    cmap = LinearSegmentedColormap.from_list("kill", [RUST_LIGHT, GOLD_LIGHT, BLUE_LIGHT, TEAL])
    ax.imshow(data, cmap=cmap, vmin=0, vmax=3, aspect="auto")
    labels = ["NONE", "WEAK", "PARTIAL", "STRONG"]
    for i in range(len(rows)):
        for j in range(len(cols)):
            ax.text(j, i, labels[data[i, j]], ha="center", va="center", fontsize=5.0, color=INK, fontweight="bold")
    ax.set_xticks(range(len(cols)), cols, fontsize=5.2, rotation=25, ha="right")
    ax.set_yticks(range(len(rows)), rows, fontsize=5.3); ax.tick_params(length=0, colors=MUTED)
    SYSTEM.save(fig, 9)


def f10():
    fig, ax = SYSTEM.setup(10, "Containment routes each action according to the last authoritative effect boundary crossed")
    states = [
        ("PROPOSED", 2, 61, BLUE), ("AUTHORIZED", 20, 61, PURPLE), ("DISPATCHED", 38, 61, GOLD),
        ("ACCEPTED", 56, 61, GOLD), ("COMMITTED", 74, 61, TEAL),
    ]
    for title, x, y, c in states:
        box(ax, x, y, 15, 12, title, "action state", edge=c, fill=SURFACE, title_color=c, fs=5.5)
    for i in range(len(states) - 1):
        arrow(ax, (states[i][1] + 15, 67), (states[i + 1][1], 67), color=MUTED, lw=.9)
    outcomes = [
        ("REJECT", "no effect", 2, 31, RUST), ("REVOKE", "authority removed", 20, 31, RUST),
        ("CANCEL", "if not accepted", 38, 31, GOLD), ("RECONCILE", "query authoritative state", 56, 31, PURPLE),
        ("VERIFY / COMPENSATE", "governed recovery", 74, 31, TEAL),
    ]
    for title, body, x, y, c in outcomes:
        fill = {RUST: RUST_LIGHT, GOLD: GOLD_LIGHT, PURPLE: PURPLE_LIGHT, TEAL: TEAL_LIGHT}[c]
        box(ax, x, y, 15, 13, title, body, edge=c, fill=fill, title_color=c, fs=5.3)
        arrow(ax, (x + 7.5, 61), (x + 7.5, 44), color=c, lw=1.0)
    box(ax, 37, 9, 34, 11, "VERIFIED TERMINAL", "not attempted · cancelled · committed correct · compensated · frozen", edge=TEAL, fill=TEAL_LIGHT, title_color=TEAL, fs=5.8)
    for _, _, x, y, c in outcomes:
        arrow(ax, (x + 7.5, y), (54, 20), color=c, lw=.45)
    SYSTEM.save(fig, 10)


def f11():
    fig, ax = SYSTEM.setup(11, "Synthetic containment inventory by effect state and reversibility", plot=True)
    states = ["PROPOSED", "AUTHORIZED", "DISPATCHED", "ACCEPTED", "COMMITTED", "AMBIGUOUS"]
    rev = np.array([310, 205, 126, 91, 62, 48])
    bounded = np.array([140, 104, 63, 41, 26, 18])
    irreversible = np.array([9, 7, 5, 4, 3, 2])
    y = np.arange(len(states))
    ax.barh(y, rev, color=BLUE_LIGHT, edgecolor=BLUE, label="Reversible")
    ax.barh(y, bounded, left=rev, color=GOLD_LIGHT, edgecolor=GOLD, label="Bounded compensation")
    ax.barh(y, irreversible, left=rev + bounded, color=RUST_LIGHT, edgecolor=RUST, label="Irreversible")
    totals = rev + bounded + irreversible
    for yi, total in zip(y, totals):
        ax.text(total + 7, yi, str(total), va="center", fontsize=5.5, color=INK, fontweight="bold")
    ax.set_yticks(y, states, fontsize=5.5); ax.invert_yaxis(); ax.set_xlim(0, 500)
    ax.set_xlabel("Actions requiring disposition · synthetic incident inventory", fontsize=6.1, color=MUTED)
    ax.grid(axis="x", color=LINE, lw=.5); ax.set_axisbelow(True); ax.tick_params(axis="x", labelsize=5.3, colors=MUTED); ax.tick_params(axis="y", length=0, colors=MUTED)
    ax.legend(loc="lower right", frameon=False, fontsize=5.4)
    ax.text(490, 5.55, "TOTAL 1,264", ha="right", color=INK, fontsize=6.2, fontweight="bold")
    SYSTEM.save(fig, 11)


def f12():
    fig, ax = SYSTEM.setup(12, "Never replay an accepted request until authoritative state proves that no effect occurred")
    box(ax, 38, 74, 25, 10, "ACCEPTED, NO RECEIPT", "timeout · disconnect · lost callback", edge=RUST, fill=RUST_LIGHT, title_color=RUST, fs=5.8)
    box(ax, 38, 57, 25, 10, "QUERY SYSTEM OF RECORD", "idempotency key + resource version", edge=PURPLE, fill=PURPLE_LIGHT, title_color=PURPLE, fs=5.8)
    arrow(ax, (50.5, 74), (50.5, 67), color=RUST)
    branches = [
        ("COMMITTED", "verify postcondition\nrecord receipt", 3, 35, TEAL),
        ("NOT FOUND", "safe retry only with\nsame idempotency key", 28, 35, BLUE),
        ("PARTIAL", "freeze resource\nreconcile + compensate", 53, 35, GOLD),
        ("UNKNOWN", "freeze · human decision\ndo not replay", 78, 35, RUST),
    ]
    for title, body, x, y, c in branches:
        fill = {TEAL: TEAL_LIGHT, BLUE: BLUE_LIGHT, GOLD: GOLD_LIGHT, RUST: RUST_LIGHT}[c]
        box(ax, x, y, 19, 14, title, body, edge=c, fill=fill, title_color=c, fs=5.6)
        arrow(ax, (50.5, 57), (x + 9.5, y + 14), color=c, lw=.75)
    box(ax, 27, 12, 47, 10, "DURABLE DISPOSITION RECEIPT", "action · attempt · query evidence · outcome · reviewer · next authority", edge=TEAL, fill=TEAL_LIGHT, title_color=TEAL, fs=6.0)
    for _, _, x, y, c in branches:
        arrow(ax, (x + 9.5, y), (50.5, 22), color=c, lw=.45)
    SYSTEM.save(fig, 12)


def f13():
    fig, ax = SYSTEM.setup(13, "Synthetic committed effects as verified stop time increases", plot=True)
    t = np.linspace(0, 180, 19)
    central = np.minimum(14 * t, 2200)
    fenced = 14 * 32 * (1 - np.exp(-t / 27))
    layered = 14 * 17 * (1 - np.exp(-t / 16))
    ax.plot(t, central, color=RUST, lw=1.6, marker="o", markersize=3, label="Central toggle only")
    ax.plot(t, fenced, color=GOLD, lw=1.6, marker="s", markersize=3, label="Epoch fencing")
    ax.plot(t, layered, color=TEAL, lw=1.8, marker="^", markersize=3, label="Layered containment")
    ax.fill_between(t, layered, central, color=RUST_LIGHT, alpha=.28, label="Exposure avoided")
    ax.axvline(90, color=BLUE, ls="--", lw=1.0); ax.text(92, 2050, "90s STO", color=BLUE, fontsize=5.8, fontweight="bold")
    ax.set_xlim(0, 180); ax.set_ylim(0, 2400); ax.grid(color=LINE, lw=.5); ax.set_axisbelow(True)
    ax.set_xlabel("Seconds to verified containment", fontsize=6.1, color=MUTED); ax.set_ylabel("Cumulative committed effects · synthetic", fontsize=6.1, color=MUTED)
    ax.tick_params(labelsize=5.3, colors=MUTED); ax.legend(loc="upper left", frameon=False, fontsize=5.3)
    SYSTEM.save(fig, 13)


def f14():
    fig, ax = SYSTEM.setup(14, "Restart authority is separate from emergency stop authority and binds to fresh evidence")
    reviews = [
        ("SECURITY", "cause contained\nforensics preserved", 2, 58, RUST),
        ("PLATFORM", "fresh image + credentials\ngates and telemetry healthy", 27, 58, BLUE),
        ("DOMAIN OWNER", "effects reconciled\nresidual risk accepted", 52, 58, GOLD),
    ]
    for title, body, x, y, c in reviews:
        box(ax, x, y, 20, 16, title, body, edge=c, fill=SURFACE, title_color=c, fs=5.8)
        arrow(ax, (x + 10, y), (62, 45), color=c, lw=.75)
    box(ax, 77, 58, 20, 16, "INCIDENT COMMANDER", "scope + evidence digest\ndual-control decision", edge=PURPLE, fill=PURPLE_LIGHT, title_color=PURPLE, fs=5.8)
    arrow(ax, (87, 58), (62, 45), color=PURPLE, lw=.75)
    box(ax, 48, 35, 28, 12, "RECOVERY AUTHORIZATION", "epoch 43 · traffic cap · expiry · rollback", edge=TEAL, fill=TEAL_LIGHT, title_color=TEAL, fs=6.0)
    phases = [("FRESH WORKLOAD", 5, 13, BLUE), ("SHADOW", 27, 13, PURPLE), ("CANARY", 49, 13, GOLD), ("BOUNDED RESTORE", 71, 13, TEAL)]
    for i, (title, x, y, c) in enumerate(phases):
        box(ax, x, y, 18, 10, title, "evidence gate", edge=c, fill=SURFACE, title_color=c, fs=5.2)
        if i < len(phases) - 1: arrow(ax, (x + 18, y + 5), (phases[i + 1][1], y + 5), color=c, lw=.8)
    arrow(ax, (62, 35), (58, 23), color=TEAL)
    SYSTEM.save(fig, 14)


def f15():
    fig, ax = SYSTEM.setup(15, "Synthetic 120-minute exercise tests technical stop, business truth, and controlled recovery", plot=True)
    lanes = ["INJECT", "COMMAND", "ENFORCE", "RECONCILE", "RECOVER"]
    segments = [
        (0, 8, 0, "anomalous CRM + email", RUST), (8, 13, 1, "declare + epoch 42", PURPLE),
        (13, 24, 2, "revoke + fence", BLUE), (14, 33, 2, "deny egress + tools", RUST),
        (20, 58, 3, "inventory 1,264 actions", GOLD), (34, 76, 3, "resolve ambiguous effects", GOLD),
        (62, 85, 4, "fresh workload + shadow", BLUE), (85, 103, 4, "bounded canary", PURPLE),
        (103, 120, 4, "verified recovery", TEAL),
    ]
    for start, end, lane, label, c in segments:
        ax.barh(lane, end - start, left=start, height=.55, color=c, edgecolor=INK, linewidth=.4)
        if end - start > 13:
            ax.text((start + end) / 2, lane, label, ha="center", va="center", fontsize=4.9, color="white" if c not in (GOLD,) else INK, fontweight="bold")
    ax.set_yticks(range(len(lanes)), lanes, fontsize=5.5); ax.invert_yaxis(); ax.set_xlim(0, 120)
    ax.set_xlabel("Exercise minute", fontsize=6.1, color=MUTED); ax.grid(axis="x", color=LINE, lw=.5); ax.set_axisbelow(True)
    ax.tick_params(axis="x", labelsize=5.3, colors=MUTED); ax.tick_params(axis="y", length=0, colors=MUTED)
    for x, label in [(13, "KILL"), (33, "LAYERED STOP"), (76, "TRUTH KNOWN"), (103, "CANARY PASS")]:
        ax.axvline(x, color=INK, lw=.7, ls="--"); ax.text(x + 1, -.65, label, color=INK, fontsize=5.0, fontweight="bold")
    SYSTEM.save(fig, 15)


def f16():
    fig, ax = SYSTEM.setup(16, "Synthetic evidence strength across failure contexts", plot=True)
    fig.subplots_adjust(left=.14, right=.745, top=.82, bottom=.17)
    rows = ["TOKEN REVOKE", "EPOCH FENCE", "QUEUE DRAIN", "EGRESS DENY", "TOOL DISABLE", "CONNECTION KILL", "RECONCILIATION", "RECOVERY GATE"]
    cols = ["CONNECTED", "PARTITIONED", "RESTARTED", "DELAYED EVENT", "OPEN SESSION", "ASYNC JOB", "CONTROL OUTAGE"]
    data = np.array([
        [4,2,4,2,2,1,1], [4,4,4,4,4,3,3], [4,2,3,2,1,3,1], [4,4,4,4,3,3,3],
        [4,3,4,3,3,2,2], [4,3,4,3,4,2,2], [4,4,4,4,4,4,3], [4,4,4,4,4,4,3],
    ])
    cmap = LinearSegmentedColormap.from_list("coverage", [RUST_LIGHT, GOLD_LIGHT, BLUE_LIGHT, TEAL_LIGHT, TEAL])
    ax.imshow(data, cmap=cmap, vmin=0, vmax=4, aspect="auto")
    labels = ["NONE", "CONFIG", "SIM", "INTEGRATION", "DRILL"]
    for i in range(len(rows)):
        for j in range(len(cols)):
            ax.text(j, i, labels[data[i, j]], ha="center", va="center", fontsize=4.8, color=INK, fontweight="bold")
    ax.set_xticks(range(len(cols)), cols, fontsize=4.9, rotation=26, ha="right")
    ax.set_yticks(range(len(rows)), rows, fontsize=5.2); ax.tick_params(length=0, colors=MUTED)
    SYSTEM.save(fig, 16)


def f17():
    fig, ax = SYSTEM.setup(17, "Synthetic 90-day scorecard; local enforcement and ambiguity closure deliberately breach", plot=False)
    headers = ["OBJECTIVE", "TARGET", "OBSERVED", "STATUS", "OWNER"]
    xs = [3, 45, 61, 76, 87]
    for x, h in zip(xs, headers): ax.text(x, 80, h, color=INK, fontsize=5.7, fontweight="bold")
    rows = [
        ("COMMAND ACCEPTANCE P99", "≤ 3 s", "2.1 s", "PASS", "Platform"),
        ("LOCAL ENFORCEMENT P99", "≤ 30 s", "41 s", "BREACH", "Security"),
        ("STALE EFFECT REJECTION", "100%", "100%", "PASS", "Tools"),
        ("IN-FLIGHT INVENTORY", "≥ 99.9%", "99.96%", "PASS", "Workflow"),
        ("AMBIGUITY CLOSED IN 4H", "≥ 99%", "96.8%", "BREACH", "Domain"),
        ("EVIDENCE LEDGER COVERAGE", "100%", "100%", "PASS", "Security"),
        ("QUARTERLY DRILL PASS", "100%", "100%", "PASS", "Risk"),
        ("RECOVERY GATE BYPASS", "0", "0", "PASS", "Incident Cmd"),
    ]
    for i, row in enumerate(rows):
        y = 70 - i * 7.6
        ax.add_patch(Rectangle((2, y - 2.5), 94, 6.2, facecolor=SURFACE if i % 2 == 0 else "#EEF2F8", edgecolor=LINE, linewidth=.45))
        for x, value in zip(xs, row): ax.text(x, y + .4, value, color=INK, fontsize=5.3, va="center", fontweight="bold" if value in ("PASS", "BREACH") else None)
        c = TEAL if row[3] == "PASS" else RUST
        ax.add_patch(Circle((79, y + .4), 1.2, facecolor=c, edgecolor="none"))
    ax.text(49, 5, "A BREACH BLOCKS RECOVERY OR AUTHORITY EXPANSION UNTIL AN OWNER ACCEPTS OR REMEDIATES THE GAP", ha="center", color=RUST, fontsize=6.0, fontweight="bold")
    SYSTEM.save(fig, 17)


def f18():
    fig, ax = SYSTEM.setup(18, "Authority expands only after each phase proves containment, reconciliation, and recovery")
    phases = [
        ("0 INVENTORY", "principals · tools\neffect graph", 2, 10, BLUE),
        ("1 EFFECT GATES", "stable IDs · receipts\nidempotency", 18, 22, PURPLE),
        ("2 SHORT AUTHORITY", "leases · epochs\nrevocation", 34, 34, GOLD),
        ("3 LAYERED STOP", "network · tools\ndrain", 50, 46, RUST),
        ("4 DRILLS", "partitions · ambiguity\nmeasured STO", 66, 58, TEAL),
        ("5 GOVERNED RECOVERY", "dual approval\ncanary + rollback", 82, 70, BLUE),
    ]
    for i, (title, body, x, y, c) in enumerate(phases):
        fill = {BLUE: BLUE_LIGHT, PURPLE: PURPLE_LIGHT, GOLD: GOLD_LIGHT, RUST: RUST_LIGHT, TEAL: TEAL_LIGHT}[c]
        box(ax, x, y, 15, 12, title, body, edge=c, fill=fill, title_color=c, fs=5.3)
        if i < len(phases) - 1:
            nx, ny = phases[i + 1][3], phases[i + 1][4]
            arrow(ax, (x + 15, y + 6), (phases[i + 1][2], phases[i + 1][3] + 6), color=c, lw=.9)
    gates = [(14, "effect coverage"), (30, "receipt completeness"), (46, "expiry + fence test"), (62, "stop-time objective"), (78, "drill + truth closure")]
    for x, label in gates:
        ax.plot([x, x], [7, 84], color=LINE, lw=.55, ls="--"); ax.text(x, 5, label, ha="center", color=MUTED, fontsize=4.7, rotation=15)
    ax.text(50, 87, "INCREASING PRODUCTION AUTHORITY →", ha="center", color=INK, fontsize=6.5, fontweight="bold")
    SYSTEM.save(fig, 18)


if __name__ == "__main__":
    SYSTEM.render([f01, f02, f03, f04, f05, f06, f07, f08, f09, f10, f11, f12, f13, f14, f15, f16, f17, f18])
