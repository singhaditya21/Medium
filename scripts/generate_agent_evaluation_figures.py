#!/usr/bin/env python3
"""Generate 18 deep-dive figures for the production agent evaluation-gate story."""

from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.colors import LinearSegmentedColormap
from matplotlib.patches import Circle, Rectangle

from technical_figure_framework import (
    BLUE, BLUE_LIGHT, GOLD, GOLD_LIGHT, GREEN, GREEN_LIGHT, INK, LINE, MUTED,
    PURPLE, PURPLE_LIGHT, RUST, RUST_LIGHT, SURFACE, TEAL, TEAL_LIGHT,
    FigureSpec, FigureSystem, arrow, box,
)

ROOT = Path(__file__).resolve().parents[1]
SLUG = "do-not-let-an-ai-agent-touch-production-until-it-passes-this-evaluation"
OUT = ROOT / "assets" / "images" / SLUG
MAP_PATH = ROOT / "stories" / f"{SLUG}-figure-map.md"


def S(n, title, form, takeaway, domain, insights, contract,
      assumption="Reference architecture; no observed production data.", core=True):
    return FigureSpec(n, title, form, takeaway, domain, tuple(insights), tuple(contract), assumption, core)


SPECS = [
    S(1, "Benchmark score versus production readiness", "Control comparison",
      "A model score supports one bounded capability claim; production readiness requires system evidence across workflows, tools, policy, failure, recovery, and business outcomes.",
      "EVALUATION CLAIM", ["The evaluated unit is a versioned agent system, not a model family name.", "Task-average success can hide critical cohort and policy failures.", "Promotion binds evidence to a deployment contract and authority ceiling."],
      [("BENCHMARK", "component evidence"), ("READINESS", "system assurance case"), ("OUTPUT", "bounded authority")]),
    S(2, "Production evaluation architecture", "Reference architecture",
      "A governed evidence plane turns versioned artifacts and representative scenarios into reproducible runs, adjudicated outcomes, claims, gates, and signed promotion decisions.",
      "EVALUATION PLANE", ["The harness controls tools, faults, evidence snapshots, seeds, clocks, and side effects.", "An independent evidence store separates test execution from promotion authority.", "Production telemetry continuously challenges the assumptions behind the approval."],
      [("INPUT", "artifact + contract + scenarios"), ("RUN", "isolated deterministic harness"), ("DECIDE", "policy gate + attestation")]),
    S(3, "Claim-to-evidence graph", "Assurance graph",
      "Every production claim decomposes into measurable subclaims supported by versioned evidence and explicit limitations; one failed critical subclaim blocks the parent.",
      "ASSURANCE CASE", ["Claims state scope, metric, threshold, cohort, environment, and validity period.", "Evidence retains provenance, sample, evaluator, result, and uncertainty.", "Unsupported edges are visible gaps rather than optimistic prose."],
      [("ROOT", "safe bounded production"), ("SUPPORT", "claims → evidence"), ("RULE", "critical AND-gates")]),
    S(4, "Scenario taxonomy", "Risk taxonomy",
      "Representative evaluation crosses business tasks, data states, policies, tools, operating conditions, people, and adversarial stress—not a flat prompt collection.",
      "SCENARIO DESIGN", ["A scenario is a stateful trajectory with preconditions and expected business postconditions.", "Coverage follows risk and production prevalence, with dedicated rare critical cases.", "Taxonomy versions allow teams to explain what new evidence a product change requires."],
      [("DIMENSIONS", "7 scenario axes"), ("COMBINATION", "risk-based covering set"), ("UNIT", "workflow trajectory")]),
    S(5, "Scenario coverage matrix", "Coverage heatmap",
      "Coverage must be reported by action cohort and failure condition; a high aggregate pass rate cannot compensate for absent critical cells.",
      "COVERAGE", ["Cells contain executed support and evidence strength, not binary test existence.", "Production mix weights expected performance; risk tiers impose minimum coverage independently.", "Empty critical cells block promotion or constrain authority."],
      [("ROWS", "8 action cohorts"), ("COLUMNS", "9 operating conditions"), ("GRADE", "none → stress-tested")],
      "Synthetic coverage ratings; not an evaluation of a deployed agent."),
    S(6, "Executable test-case contract", "Schema anatomy",
      "A reproducible agent test specifies initial world state, inputs, policy, tools, injected faults, permitted effects, oracle, stop conditions, and evidence requirements.",
      "TEST CONTRACT", ["The expected answer alone is insufficient for a stateful tool-using system.", "Permitted and forbidden effects are first-class assertions.", "Scenario identity and artifact digests make failures replayable."],
      [("SETUP", "state + artifact + policy"), ("RUN", "trajectory + faults"), ("ASSERT", "postconditions + invariants")]),
    S(7, "Metric hierarchy", "Metric tree",
      "Component accuracy, workflow success, policy compliance, system reliability, human impact, and business outcome metrics answer different production questions.",
      "MEASUREMENT", ["Metrics require denominators, oracles, cohorts, windows, and uncertainty.", "Guardrails remain separate from the optimized business objective.", "A metric tree prevents one proxy score from becoming the entire release decision."],
      [("LEVELS", "6 metric layers"), ("GUARDS", "policy · safety · rights"), ("OUTCOME", "verified business effect")]),
    S(8, "Failure-injection map", "Fault architecture",
      "Evaluation must inject failures at model, context, memory, scheduler, tool, identity, network, data, verifier, and human boundaries while preserving safe isolation.",
      "RESILIENCE", ["Faults need activation proof; an unobserved injection is not a passed test.", "Correlated and sequential faults expose recovery assumptions hidden by one-at-a-time tests.", "The oracle judges both task outcome and containment behavior."],
      [("FAULTS", "10 boundaries"), ("MODES", "delay · error · stale · partial"), ("PROOF", "injection + observation receipt")]),
    S(9, "Stateful tool-simulator architecture", "Simulation architecture",
      "A high-fidelity simulator models business state, permissions, versions, idempotency, asynchronous jobs, latency, partial commits, and receipts—not just canned JSON responses.",
      "TOOL TESTBED", ["Contract equivalence matters more than copying every vendor implementation detail.", "Golden traces compare simulator and sandbox behavior on shared probes.", "Unsafe effects remain impossible because the simulator owns the test world."],
      [("WORLD", "versioned state machine"), ("API", "production-compatible contract"), ("CHECK", "state + effect receipts")]),
    S(10, "Adversarial evaluation pipeline", "Red-team pipeline",
      "Threat modeling generates controlled attacks that pass through sanitization, isolated execution, effect monitoring, adjudication, deduplication, and regression capture.",
      "ADVERSARIAL TEST", ["Attack coverage includes instructions, attachments, tools, memory, identity, and multi-turn social pressure.", "Success means preserving policy and business invariants, not merely refusing text.", "Every unique failure becomes a minimized, versioned regression case."],
      [("SOURCE", "threat model + mutations"), ("SANDBOX", "no real external effect"), ("OUTPUT", "failure cluster + regression")]),
    S(11, "Shadow-mode execution", "Sequence diagram",
      "Shadow evaluation replays production-like actions against frozen or simulated effects, compares decisions and trajectories, and never grants the candidate production authority.",
      "SHADOW", ["The incumbent path remains the only path allowed to affect business state.", "Candidate inputs obey privacy and minimization policy rather than copying all traffic blindly.", "Outcome comparison waits for the correct label-maturity window."],
      [("TRAFFIC", "eligible sampled envelopes"), ("CANDIDATE", "effectless authority"), ("COMPARE", "decision + cost + failure")]),
    S(12, "Canary authority ladder", "Authority ladder",
      "A canary expands along independent dimensions—population, action scope, effect value, tool access, volume, duration, and reversibility—only after each evidence gate passes.",
      "CANARY", ["Traffic percentage alone is an unsafe definition of canary authority.", "Every stage has an automatic ceiling and rollback path enforced outside the agent.", "Full production remains bounded by the approved deployment contract."],
      [("STAGES", "shadow → bounded production"), ("CEILINGS", "value · volume · tools"), ("ROLLBACK", "last safe policy")]),
    S(13, "Confidence intervals by cohort", "Interval chart",
      "Observed success is an estimate; lower confidence bounds expose which cohorts lack enough evidence to meet their production floor.",
      "STATISTICS", ["Use cohort-specific intervals and account for clustering or dependence.", "A point estimate above target can still fail the promotion gate.", "Practical significance and failure consequence matter alongside statistical confidence."],
      [("COHORTS", "8 synthetic cohorts"), ("INTERVAL", "Wilson 95%"), ("GATE", "lower bound ≥ floor")],
      "Synthetic binary outcomes and Wilson intervals; not measured agent performance."),
    S(14, "Zero-failure rare-event bound", "Uncertainty curve",
      "Zero observed critical failures does not prove zero risk; the one-sided upper bound falls only as representative exposure accumulates.",
      "RARE EVENTS", ["The rule-of-three approximates the 95% upper rate after zero events under simple independent trials.", "Dependence, drift, weak observability, and unrepresentative tests invalidate the naive bound.", "Critical harms may require structural controls even when statistical proof is infeasible."],
      [("OBSERVED", "0 critical failures"), ("BOUND", "≈ 3/n at 95%"), ("LIMIT", "iid + representative")],
      "Analytical curve under a simple independent Bernoulli model; not a risk forecast."),
    S(15, "Drift and evidence-expiry timeline", "Monitoring timeline",
      "Production evidence expires when inputs, actions, tools, policies, artifacts, users, or operating conditions move outside the validated envelope.",
      "CONTINUOUS EVAL", ["Detect feature, outcome, calibration, trajectory, latency, cost, and policy drift separately.", "Material change triggers targeted or full re-evaluation before authority expansion.", "Delayed labels require leading indicators without pretending they are final outcomes."],
      [("BASELINE", "approved evidence window"), ("SIGNALS", "7 drift families"), ("ACTION", "observe · constrain · rollback")]),
    S(16, "Production promotion decision", "Decision tree",
      "Promotion requires artifact provenance, scenario coverage, metric floors, guardrail integrity, shadow evidence, bounded canary, operations readiness, and rollback proof.",
      "RELEASE GATE", ["Each gate produces an explicit reason code and evidence reference.", "A waiver narrows scope and expires; it does not silently convert failure to pass.", "The final output is an authority contract, not a generic approved label."],
      [("INPUT", "signed evaluation bundle"), ("GATES", "6 grouped checks"), ("OUTPUT", "promote · constrain · reject")]),
    S(17, "Evaluation service objectives", "SLO scorecard",
      "Coverage, reproducibility, label quality, evidence freshness, critical-policy performance, shadow completeness, canary detection, and rollback drills need independent objectives.",
      "EVAL OPERATIONS", ["A large test count can coexist with stale or low-quality evidence.", "Critical policy violations have stricter objectives than average task quality.", "Breaches constrain production authority and prioritize the next evaluation investment."],
      [("WINDOW", "synthetic release cycle"), ("STATUS", "6 pass · 2 breach"), ("OWNERS", "Eval · Domain · Risk · SRE")],
      "Synthetic operating scorecard with deliberate breaches."),
    S(18, "Continuous evaluation roadmap", "Lifecycle roadmap",
      "Teams progress from deployment contracts and deterministic harnesses through coverage, fault testing, shadow, bounded canaries, and continuous evidence renewal.",
      "ROLLOUT", ["Production authority never outruns observable and testable effect boundaries.", "Each phase creates reusable evidence rather than one launch-day report.", "Rollback and re-evaluation are part of the release system from the beginning."],
      [("PHASES", "0 through 6"), ("GATES", "claims + coverage + confidence"), ("END STATE", "evidence-bound authority")]),
]

SYSTEM = FigureSystem(SLUG, OUT, MAP_PATH, "Do Not Let an AI Agent Touch Production Until It Passes This Evaluation", SPECS)


def f01():
    fig, ax = SYSTEM.setup(1, "A component score is one input; production authority requires a versioned system assurance case")
    rows = [
        ("EVALUATED UNIT", "model endpoint", "agent artifact + policy + tools + runtime"),
        ("INPUT", "prompt dataset", "stateful representative trajectories"),
        ("ENVIRONMENT", "fixed benchmark", "production-like latency, identity, and faults"),
        ("OUTPUT", "answer or score", "business postcondition + effect receipts"),
        ("FAILURES", "usually clean run", "timeouts, stale data, partial commits, recovery"),
        ("POLICY", "often implicit", "permitted and forbidden effects asserted"),
        ("STATISTICS", "aggregate mean", "cohorts, intervals, rare-event bounds, drift"),
        ("DECISION", "rank or compare", "bounded authority + rollback contract"),
    ]
    for x, title, c, fill in [(2, "BENCHMARK SCORE", BLUE, BLUE_LIGHT), (52, "PRODUCTION READINESS", TEAL, TEAL_LIGHT)]:
        box(ax, x, 76, 44, 9, title, "evidence claim", edge=c, fill=fill, title_color=c, fs=7.0)
    for i, (label, left, right) in enumerate(rows):
        y = 68 - i * 7.6
        ax.text(49, y + 2.5, label, ha="center", va="center", color=MUTED, fontsize=4.9, fontweight="bold")
        box(ax, 2, y, 44, 5.5, left, edge=LINE, fill=SURFACE, fs=5.4)
        box(ax, 52, y, 44, 5.5, right, edge=LINE, fill=SURFACE, fs=5.4)
    SYSTEM.save(fig, 1)


def f02():
    fig, ax = SYSTEM.setup(2, "Versioned execution, independent evidence, and policy gates connect development to production telemetry")
    inputs = [("AGENT ARTIFACT", "model · prompt · code · config", BLUE), ("DEPLOYMENT CONTRACT", "scope · tools · ceilings", PURPLE), ("SCENARIO REGISTRY", "taxonomy · cases · risk", GOLD)]
    for i, (title, body, c) in enumerate(inputs):
        box(ax, 2, 69 - i * 20, 22, 13, title, body, edge=c, fill=SURFACE, title_color=c, fs=5.7)
        arrow(ax, (24, 75 - i * 20), (33, 49), color=c, lw=.65)
    box(ax, 33, 58, 31, 21, "ISOLATED EVALUATION HARNESS", "world-state reset · tool simulators · fault controller\ntrajectory recorder · invariant monitor · deterministic seeds", edge=BLUE, fill=BLUE_LIGHT, title_color=BLUE, fs=6.1)
    box(ax, 33, 31, 31, 18, "EVIDENCE + ADJUDICATION", "receipts · labels · uncertainty · limitations\nprovenance · claim graph · reproducibility", edge=TEAL, fill=TEAL_LIGHT, title_color=TEAL, fs=6.1)
    arrow(ax, (48.5, 58), (48.5, 49), color=TEAL)
    outputs = [("PROMOTION GATE", "approve · constrain · reject", RUST), ("SIGNED ATTESTATION", "artifact + evidence + authority", PURPLE), ("PRODUCTION MONITOR", "drift · incidents · labels", GOLD)]
    for i, (title, body, c) in enumerate(outputs):
        y = 68 - i * 20
        box(ax, 73, y, 23, 13, title, body, edge=c, fill=SURFACE, title_color=c, fs=5.6)
        arrow(ax, (64, 40), (73, y + 6), color=c, lw=.65)
    arrow(ax, (85, 48), (64, 36), color=GOLD, lw=.75, connectionstyle="arc3,rad=-.22")
    box(ax, 31, 10, 36, 10, "INDEPENDENT EVIDENCE STORE", "append-only run manifests · immutable artifacts · evaluator identity", edge=PURPLE, fill=PURPLE_LIGHT, title_color=PURPLE, fs=5.7)
    arrow(ax, (48.5, 31), (48.5, 20), color=PURPLE)
    SYSTEM.save(fig, 2)


def f03():
    fig, ax = SYSTEM.setup(3, "The release claim is an AND of critical subclaims, each tied to current evidence and limits")
    box(ax, 35, 73, 31, 11, "SAFE BOUNDED PRODUCTION", "artifact A17 · policy P9 · authority contract C4", edge=TEAL, fill=TEAL_LIGHT, title_color=TEAL, fs=6.2)
    claims = [
        ("TASK EFFECTIVE", 2, 51, BLUE), ("POLICY SAFE", 21, 51, RUST), ("TOOL RELIABLE", 40, 51, GOLD),
        ("RECOVERABLE", 59, 51, PURPLE), ("OPERABLE", 78, 51, TEAL),
    ]
    for title, x, y, c in claims:
        box(ax, x, y, 17, 11, title, "scoped threshold", edge=c, fill=SURFACE, title_color=c, fs=5.2)
        arrow(ax, (50.5, 73), (x + 8.5, y + 11), color=c, lw=.65)
    evidence = [
        ("WORKFLOW SET", "n + cohort + CI", 2, 25, BLUE), ("POLICY TESTS", "invariants + attacks", 21, 25, RUST),
        ("FAULT RUNS", "tools + network", 40, 25, GOLD), ("ROLLBACK DRILL", "time + state proof", 59, 25, PURPLE),
        ("SLO READINESS", "owners + alerts", 78, 25, TEAL),
    ]
    for (title, body, x, y, c), (_, cx, _, cc) in zip(evidence, [("",2,0,BLUE),("",21,0,RUST),("",40,0,GOLD),("",59,0,PURPLE),("",78,0,TEAL)]):
        box(ax, x, y, 17, 12, title, body, edge=c, fill={BLUE:BLUE_LIGHT,RUST:RUST_LIGHT,GOLD:GOLD_LIGHT,PURPLE:PURPLE_LIGHT,TEAL:TEAL_LIGHT}[c], title_color=c, fs=5.3)
        arrow(ax, (x + 8.5, y + 12), (x + 8.5, 51), color=c, lw=.8)
    ax.text(50, 10, "EVERY EDGE: ARTIFACT DIGEST · SCENARIO VERSION · ENVIRONMENT · RESULT · UNCERTAINTY · EXPIRY · LIMITATION", ha="center", color=INK, fontsize=5.8, fontweight="bold")
    SYSTEM.save(fig, 3)


def f04():
    fig, ax = SYSTEM.setup(4, "Risk-based combinations turn seven dimensions into stateful production trajectories")
    center = (49, 45)
    box(ax, 38, 38, 22, 14, "SCENARIO", "initial state → trajectory\n→ verified postcondition", edge=TEAL, fill=TEAL_LIGHT, title_color=TEAL, fs=6.2)
    dims = [
        ("BUSINESS TASK", "collect · negotiate · mutate", 3, 69, BLUE), ("DATA STATE", "fresh · stale · conflicting", 38, 70, PURPLE),
        ("POLICY", "allowed · edge · forbidden", 73, 69, RUST), ("TOOL STATE", "healthy · timeout · partial", 75, 35, GOLD),
        ("OPERATING", "burst · outage · long context", 68, 9, BLUE), ("HUMAN", "approve · delay · override", 30, 8, TEAL),
        ("ADVERSARIAL", "injection · exfil · coercion", 2, 31, RUST),
    ]
    for title, body, x, y, c in dims:
        box(ax, x, y, 23, 11, title, body, edge=c, fill=SURFACE, title_color=c, fs=5.3)
        arrow(ax, (x + 11.5, y + 5.5), center, color=c, lw=.55)
    ax.text(49, 25, "COVERING SET = PREVALENCE WEIGHT + RISK MINIMUM + INTERACTION STRENGTH + REGRESSION HISTORY", ha="center", color=INK, fontsize=5.6, fontweight="bold")
    SYSTEM.save(fig, 4)


def f05():
    fig, ax = SYSTEM.setup(5, "Synthetic evidence strength by action cohort and operating condition", plot=True)
    fig.subplots_adjust(left=.15, right=.745, top=.82, bottom=.18)
    rows = ["CONTACT", "PROMISE", "DISPUTE", "PAYMENT PLAN", "FEE WAIVER", "ESCALATION", "LEGAL HOLD", "ACCOUNT CLOSE"]
    cols = ["NORMAL", "STALE DATA", "CONFLICT", "TOOL DOWN", "TIMEOUT", "POLICY CHANGE", "ADVERSARIAL", "BURST", "HUMAN DELAY"]
    data = np.array([
        [4,4,3,4,4,3,3,3,3], [4,4,4,3,4,3,3,3,4], [4,3,4,3,3,4,4,2,4], [4,4,3,3,4,3,3,3,3],
        [4,3,4,2,3,4,4,2,3], [4,3,4,3,3,4,4,2,4], [4,2,4,2,3,4,4,1,4], [4,2,3,2,3,4,4,1,3],
    ])
    cmap = LinearSegmentedColormap.from_list("coverage", [RUST_LIGHT, GOLD_LIGHT, BLUE_LIGHT, TEAL_LIGHT, TEAL])
    ax.imshow(data, cmap=cmap, vmin=0, vmax=4, aspect="auto")
    labels = ["NONE", "CASE", "REPLAY", "INTEGRATION", "STRESS"]
    for i in range(len(rows)):
        for j in range(len(cols)):
            ax.text(j, i, labels[data[i,j]], ha="center", va="center", fontsize=4.6, color=INK, fontweight="bold")
    ax.set_xticks(range(len(cols)), cols, fontsize=4.8, rotation=28, ha="right")
    ax.set_yticks(range(len(rows)), rows, fontsize=5.1); ax.tick_params(length=0, colors=MUTED)
    SYSTEM.save(fig, 5)


def f06():
    fig, ax = SYSTEM.setup(6, "The test artifact defines world state, execution controls, business assertions, and evidence")
    sections = [
        ("IDENTITY", "case_id · taxonomy · risk · owner", 2, 68, BLUE),
        ("ARTIFACT", "model · code · prompt · policy digests", 27, 68, PURPLE),
        ("INITIAL WORLD", "accounts · balances · promises · clocks", 52, 68, TEAL),
        ("INPUTS", "messages · attachments · evidence", 77, 68, GOLD),
        ("TOOLS", "contracts · permissions · simulator versions", 2, 43, TEAL),
        ("FAULT PLAN", "trigger · mode · duration · activation proof", 27, 43, RUST),
        ("LIMITS", "steps · tokens · time · value · authority", 52, 43, GOLD),
        ("ORACLE", "postconditions · invariants · allowed variance", 77, 43, BLUE),
        ("EVIDENCE", "trajectory · receipts · state diff · adjudication", 27, 18, PURPLE),
        ("STOP RULE", "success · abstain · safe failure · timeout", 52, 18, RUST),
    ]
    for title, body, x, y, c in sections:
        box(ax, x, y, 21, 13, title, body, edge=c, fill=SURFACE, title_color=c, fs=5.2)
    for x in [12.5, 37.5, 62.5, 87.5]: arrow(ax, (x, 68), (49, 56), color=MUTED, lw=.45)
    box(ax, 39, 52, 20, 8, "RUN CONTRACT", "immutable case digest", edge=TEAL, fill=TEAL_LIGHT, title_color=TEAL, fs=5.3)
    for x in [12.5, 37.5, 62.5, 87.5]: arrow(ax, (49, 52), (x, 56), color=MUTED, lw=.4)
    ax.text(50, 8, "REPRODUCIBLE ID = HASH(CASE + ARTIFACT + ENVIRONMENT + TOOL WORLD + FAULT PLAN + SEED)", ha="center", color=INK, fontsize=5.8, fontweight="bold")
    SYSTEM.save(fig, 6)


def f07():
    fig, ax = SYSTEM.setup(7, "Metrics form a hierarchy from component behavior to verified business outcome")
    levels = [
        ("6 BUSINESS OUTCOME", "resolution · retained value · customer remedy", 18, 72, 64, TEAL, TEAL_LIGHT),
        ("5 HUMAN + CUSTOMER", "review burden · override · fairness · appeal", 22, 61, 56, BLUE, BLUE_LIGHT),
        ("4 SYSTEM RELIABILITY", "latency · cost · availability · recovery", 26, 50, 48, PURPLE, PURPLE_LIGHT),
        ("3 POLICY + SAFETY", "prohibited effect · disclosure · escalation", 30, 39, 40, RUST, RUST_LIGHT),
        ("2 WORKFLOW", "verified postcondition · trajectory efficiency", 34, 28, 32, GOLD, GOLD_LIGHT),
        ("1 COMPONENT", "retrieval · model · tool · verifier accuracy", 38, 17, 24, BLUE, BLUE_LIGHT),
    ]
    for title, body, x, y, w, c, fill in levels:
        box(ax, x, y, w, 9, title, body, edge=c, fill=fill, title_color=c, fs=5.6)
    ax.text(50, 10, "PROMOTION = BUSINESS OBJECTIVE IMPROVES ∧ EVERY CRITICAL GUARDRAIL MEETS ITS OWN FLOOR", ha="center", color=RUST, fontsize=6.0, fontweight="bold")
    SYSTEM.save(fig, 7)


def f08():
    fig, ax = SYSTEM.setup(8, "Faults surround the agent system; activation and observation receipts make every injection auditable")
    box(ax, 38, 38, 24, 16, "AGENT WORKFLOW", "plan · retrieve · reason\ntool · verify · recover", edge=TEAL, fill=TEAL_LIGHT, title_color=TEAL, fs=6.2)
    faults = [
        ("MODEL", "refusal · malformed · drift", 2, 70, BLUE), ("CONTEXT", "missing · poisoned · long", 27, 70, PURPLE),
        ("MEMORY", "stale · conflict · leak", 52, 70, RUST), ("SCHEDULER", "duplicate · reorder · delay", 77, 70, GOLD),
        ("IDENTITY", "expire · revoke · wrong scope", 2, 14, PURPLE), ("NETWORK", "partition · jitter · reset", 27, 14, BLUE),
        ("TOOL", "timeout · partial · bad schema", 52, 14, GOLD), ("DATA", "version conflict · missing", 77, 14, RUST),
        ("VERIFIER", "false pass · unavailable", 2, 40, RUST), ("HUMAN", "delay · reject · override", 77, 40, TEAL),
    ]
    for title, body, x, y, c in faults:
        box(ax, x, y, 20, 11, title, body, edge=c, fill=SURFACE, title_color=c, fs=5.1)
        arrow(ax, (x + 10, y + 5.5), (50, 46), color=c, lw=.45)
    ax.text(50, 61, "FAULT CONTROLLER: SCHEDULE · ACTIVATE · VERIFY ACTIVATION · RESTORE · RECEIPT", ha="center", color=INK, fontsize=5.7, fontweight="bold")
    ax.text(50, 6, "ORACLE SCORES TASK OUTCOME + POLICY INVARIANTS + RECOVERY BEHAVIOR + EVIDENCE COMPLETENESS", ha="center", color=INK, fontsize=5.7, fontweight="bold")
    SYSTEM.save(fig, 8)


def f09():
    fig, ax = SYSTEM.setup(9, "A versioned world model reproduces tool contracts while making real external effects impossible")
    box(ax, 2, 58, 22, 16, "AGENT UNDER TEST", "production request schema\nscoped test authority", edge=BLUE, fill=BLUE_LIGHT, title_color=BLUE, fs=6.0)
    box(ax, 32, 58, 30, 16, "PRODUCTION-COMPATIBLE TOOL API", "auth · versions · idempotency · async jobs\nlatency · errors · receipts", edge=PURPLE, fill=PURPLE_LIGHT, title_color=PURPLE, fs=6.0)
    box(ax, 70, 58, 26, 16, "STATEFUL WORLD MODEL", "accounts · balances · promises\nqueues · clocks · event log", edge=TEAL, fill=TEAL_LIGHT, title_color=TEAL, fs=6.0)
    arrow(ax, (24, 66), (32, 66), color=BLUE); arrow(ax, (62, 66), (70, 66), color=PURPLE)
    controls = [
        ("FAULT ENGINE", "partial commit · timeout", 2, 31, RUST), ("CLOCK + SEED", "deterministic replay", 27, 31, GOLD),
        ("EFFECT MONITOR", "allowed · forbidden · duplicate", 52, 31, TEAL), ("STATE ORACLE", "diff + invariants + postcondition", 77, 31, BLUE),
    ]
    for title, body, x, y, c in controls:
        box(ax, x, y, 20, 13, title, body, edge=c, fill=SURFACE, title_color=c, fs=5.4)
        arrow(ax, (x + 10, y + 13), (49, 58), color=c, lw=.55)
    box(ax, 27, 10, 46, 10, "CONTRACT-EQUIVALENCE PROBES", "same request corpus → simulator vs vendor sandbox → field, state, error, timing, and receipt deltas", edge=GOLD, fill=GOLD_LIGHT, title_color=GOLD, fs=5.7)
    arrow(ax, (83, 58), (63, 20), color=GOLD, lw=.7, connectionstyle="arc3,rad=.18")
    SYSTEM.save(fig, 9)


def f10():
    fig, ax = SYSTEM.setup(10, "Controlled attack generation becomes safe, adjudicated regression evidence")
    stages = [
        ("THREAT MODEL", "assets · actors · abuse paths", 1, BLUE),
        ("CASE GENERATOR", "seed + mutation + composition", 17, PURPLE),
        ("SANITIZE", "secrets · legality · safety", 33, GOLD),
        ("ISOLATED RUN", "simulated effects · monitors", 49, RUST),
        ("ADJUDICATE", "policy + outcome + severity", 65, TEAL),
        ("CLUSTER + MINIMIZE", "dedupe · causal core", 81, BLUE),
    ]
    for title, body, x, c in stages:
        fill = {BLUE:BLUE_LIGHT,PURPLE:PURPLE_LIGHT,GOLD:GOLD_LIGHT,RUST:RUST_LIGHT,TEAL:TEAL_LIGHT}[c]
        box(ax, x, 58, 14, 15, title, body, edge=c, fill=fill, title_color=c, fs=5.1)
    for i in range(len(stages)-1): arrow(ax, (stages[i][2]+14,65.5),(stages[i+1][2],65.5),color=MUTED,lw=.8)
    surfaces = [("INSTRUCTION", 3, 31), ("ATTACHMENT", 19, 31), ("TOOL OUTPUT", 35, 31), ("MEMORY", 51, 31), ("IDENTITY", 67, 31), ("MULTI-TURN", 83, 31)]
    for title, x, y in surfaces:
        box(ax, x, y, 13, 9, title, "attack surface", edge=RUST, fill=SURFACE, title_color=RUST, fs=4.9)
        arrow(ax, (x+6.5,y+9),(40,58),color=RUST,lw=.35)
    box(ax, 32, 10, 36, 10, "VERSIONED REGRESSION CASE", "failure signature · minimized trace · expected safe behavior · owner · fix version", edge=TEAL, fill=TEAL_LIGHT, title_color=TEAL, fs=5.7)
    arrow(ax,(88,58),(68,20),color=TEAL,lw=.8)
    SYSTEM.save(fig, 10)


def f11():
    fig, ax = SYSTEM.setup(11, "The candidate observes eligible production-like envelopes but cannot cross an external effect boundary")
    lanes = ["TRAFFIC\nSAMPLER", "INCUMBENT", "CANDIDATE\nSHADOW", "TOOL WORLD", "OUTCOME\nJOINER", "EVAL STORE"]
    xs = np.linspace(5,95,len(lanes))
    for x, lane in zip(xs,lanes):
        ax.text(x,82,lane,ha="center",va="center",fontsize=5.3,fontweight="bold",color=INK); ax.plot([x,x],[10,77],color=LINE,lw=.8,ls="--")
    events = [
        (0,1,72,"approved production action",BLUE), (0,2,63,"minimized shadow envelope",PURPLE),
        (1,3,54,"real authorized effects",TEAL), (2,3,45,"simulate only · no authority",RUST),
        (3,4,35,"state + effect receipts",GOLD), (1,4,27,"incumbent decision",BLUE),
        (2,4,20,"candidate trajectory",PURPLE), (4,5,13,"matured comparison bundle",TEAL),
    ]
    for a,b,y,label,c in events:
        arrow(ax,(xs[a]+1,y),(xs[b]-1,y),color=c,lw=1.0); ax.text((xs[a]+xs[b])/2,y+2,label,ha="center",color=c,fontsize=5.0,fontweight="bold")
    ax.text(50,6,"SHADOW MAY DIFFER IN LATENCY, TOOL STATE, AND HUMAN RESPONSE · LIMITATIONS REMAIN IN THE EVIDENCE BUNDLE",ha="center",color=INK,fontsize=5.6,fontweight="bold")
    SYSTEM.save(fig, 11)


def f12():
    fig, ax = SYSTEM.setup(12, "Authority grows along seven ceilings; traffic share alone never defines the canary")
    stages = [
        ("0 SHADOW", "0 effect authority", 2, 8, BLUE), ("1 INTERNAL", "test tenants · reversible", 18, 20, PURPLE),
        ("2 REVIEWED", "human approves every effect", 34, 32, GOLD), ("3 LOW VALUE", "bounded tools + $ ceiling", 50, 44, RUST),
        ("4 COHORT", "eligible population + volume cap", 66, 56, TEAL), ("5 BOUNDED PROD", "contract ceiling + rollback", 82, 68, BLUE),
    ]
    for i,(title,body,x,y,c) in enumerate(stages):
        fill={BLUE:BLUE_LIGHT,PURPLE:PURPLE_LIGHT,GOLD:GOLD_LIGHT,RUST:RUST_LIGHT,TEAL:TEAL_LIGHT}[c]
        box(ax,x,y,15,12,title,body,edge=c,fill=fill,title_color=c,fs=5.2)
        if i<len(stages)-1: arrow(ax,(x+15,y+6),(stages[i+1][2],stages[i+1][3]+6),color=c,lw=.9)
    ceilings=["population","action","effect value","tool set","volume","duration","reversibility"]
    for i,label in enumerate(ceilings):
        x=8+i*13; ax.add_patch(Rectangle((x,4),10,3,facecolor=SURFACE,edgecolor=LINE,lw=.6)); ax.text(x+5,2,label,ha="center",fontsize=4.7,color=MUTED,rotation=12)
    ax.text(50,86,"EACH STAGE: LOWER-BOUND QUALITY + ZERO CRITICAL VIOLATION + SLO + LABEL WINDOW + ROLLBACK PROOF",ha="center",color=INK,fontsize=5.8,fontweight="bold")
    SYSTEM.save(fig, 12)


def _wilson(k, n, z=1.96):
    p=k/n; den=1+z*z/n; centre=(p+z*z/(2*n))/den
    half=z*np.sqrt(p*(1-p)/n+z*z/(4*n*n))/den
    return centre-half, centre+half


def f13():
    fig, ax = SYSTEM.setup(13, "Synthetic verified-success estimates with Wilson 95% intervals", plot=True)
    cohorts=["CONTACT","PROMISE","DISPUTE","PAYMENT","WAIVER","ESCALATION","LEGAL HOLD","CLOSE"]
    n=np.array([2400,1200,650,900,420,310,120,95]); k=np.array([2360,1160,621,866,399,291,113,88])
    p=k/n; ci=np.array([_wilson(int(a),int(b)) for a,b in zip(k,n)])
    low,high=ci[:,0],ci[:,1]; y=np.arange(len(cohorts))
    colors=[TEAL if l>=.92 else RUST for l in low]
    ax.errorbar(p,y,xerr=np.vstack([p-low,high-p]),fmt="none",ecolor=MUTED,elinewidth=1.2,capsize=3)
    ax.scatter(p,y,s=85,c=colors,edgecolor=INK,linewidth=.45,zorder=3)
    ax.axvline(.92,color=GOLD,ls="--",lw=1.2); ax.text(.921,-.65,"PRODUCTION FLOOR .92",color=GOLD,fontsize=5.5,fontweight="bold")
    for yi,(pp,nn,ll) in enumerate(zip(p,n,low)): ax.text(high[yi]+.003,yi,f"{pp:.3f} · n={nn:,} · LCB {ll:.3f}",va="center",fontsize=5.0,color=INK)
    ax.set_yticks(y,cohorts,fontsize=5.4); ax.invert_yaxis(); ax.set_xlim(.86,1.018); ax.grid(axis="x",color=LINE,lw=.5); ax.set_axisbelow(True)
    ax.set_xlabel("Verified workflow success proportion",fontsize=6.1,color=MUTED); ax.tick_params(axis="x",labelsize=5.3,colors=MUTED); ax.tick_params(axis="y",length=0,colors=MUTED)
    SYSTEM.save(fig, 13)


def f14():
    fig, ax = SYSTEM.setup(14, "One-sided approximate 95% upper failure-rate bound after zero observed events", plot=True)
    n=np.logspace(2,6,200); bound=3/n
    ax.loglog(n,bound,color=RUST,lw=1.8); ax.fill_between(n,bound,1,color=RUST_LIGHT,alpha=.28)
    points=np.array([100,1000,10000,100000,1000000]); vals=3/points
    ax.scatter(points,vals,s=55,color=TEAL,edgecolor=INK,zorder=3)
    for x,y in zip(points,vals):
        if x == points[-1]:
            ax.text(x*.90,y*1.12,f"{y:.1e}",fontsize=5.0,color=INK,ha="right")
        else:
            ax.text(x*1.08,y*1.12,f"{y:.1e}",fontsize=5.0,color=INK)
    for threshold,label in [(1e-3,"1 per 1k"),(1e-4,"1 per 10k"),(1e-5,"1 per 100k")]:
        ax.axhline(threshold,color=GOLD,lw=.7,ls="--"); ax.text(110,threshold*1.14,label,color=GOLD,fontsize=4.9,fontweight="bold")
    ax.set_xlim(100,1e6); ax.set_ylim(1e-6,.1); ax.grid(which="both",color=LINE,lw=.45); ax.set_axisbelow(True)
    ax.set_xlabel("Representative independent trials with zero observed critical failures",fontsize=6.0,color=MUTED); ax.set_ylabel("Approximate 95% upper failure-rate bound",fontsize=6.0,color=MUTED)
    ax.tick_params(labelsize=5.2,colors=MUTED)
    SYSTEM.save(fig, 14)


def f15():
    fig, ax = SYSTEM.setup(15, "Approved evidence weakens as production inputs and system components move", plot=True)
    days=np.arange(0,91,5)
    signals={
        "INPUT PSI":(.05+.0018*days,BLUE), "OUTCOME GAP":(.03+.0007*days+np.where(days>55,.0028*(days-55),0),RUST),
        "CALIBRATION":(.04+.0010*days,PURPLE), "TOOL ERROR":(.02+.0006*days+np.where(days>35,.0025*(days-35),0),GOLD),
    }
    for label,(values,c) in signals.items(): ax.plot(days,values,color=c,lw=1.4,marker="o",markersize=2.5,label=label)
    ax.axhline(.15,color=GOLD,ls="--",lw=1.0); ax.text(2,.155,"REVIEW",color=GOLD,fontsize=5.1,fontweight="bold")
    ax.axhline(.25,color=RUST,ls="--",lw=1.0); ax.text(2,.255,"CONSTRAIN / ROLLBACK",color=RUST,fontsize=5.1,fontweight="bold")
    ax.axvline(35,color=INK,lw=.7,ls=":"); ax.text(36,.34,"tool release",fontsize=4.9,color=INK)
    ax.axvline(55,color=INK,lw=.7,ls=":"); ax.text(56,.31,"policy change",fontsize=4.9,color=INK)
    ax.set_xlim(0,90); ax.set_ylim(0,.38); ax.grid(color=LINE,lw=.5); ax.set_axisbelow(True)
    ax.set_xlabel("Days since promotion",fontsize=6.1,color=MUTED); ax.set_ylabel("Synthetic normalized drift signal",fontsize=6.1,color=MUTED)
    ax.tick_params(labelsize=5.3,colors=MUTED); ax.legend(loc="upper left",frameon=False,fontsize=5.1,ncol=2)
    SYSTEM.save(fig, 15)


def f16():
    fig, ax = SYSTEM.setup(16, "The gate emits a scoped authority contract or an explicit evidence-backed refusal")
    nodes=[
        ("PROVENANCE", "artifact digest + trusted build?", 39, 76, PURPLE), ("CONTRACT", "scope and ceilings explicit?", 39, 64, BLUE),
        ("COVERAGE", "critical cells supported?", 39, 52, GOLD), ("METRICS", "LCBs and guardrails pass?", 39, 40, TEAL),
        ("SHADOW", "representative, effectless evidence?", 39, 28, BLUE), ("CANARY + OPS", "bounded run, alerts, rollback?", 39, 16, RUST),
    ]
    for title,body,x,y,c in nodes:
        box(ax,x,y,24,9,title,body,edge=c,fill=SURFACE,title_color=c,fs=5.3)
    for i in range(len(nodes)-1): arrow(ax,(51,nodes[i][3]),(51,nodes[i+1][3]+9),color=MUTED,lw=.75)
    leaves=[("REJECT",3,66,RUST,"failed critical gate"),("CONSTRAIN",3,37,GOLD,"narrow + expiring waiver"),("PROMOTE",72,23,TEAL,"signed authority contract")]
    for title,x,y,c,body in leaves:
        box(ax,x,y,23,12,title,body,edge=c,fill={RUST:RUST_LIGHT,GOLD:GOLD_LIGHT,TEAL:TEAL_LIGHT}[c],title_color=c,fs=5.7)
    arrow(ax,(39,56),(26,72),color=RUST,lw=.8); ax.text(27,67,"critical gap",color=RUST,fontsize=5.0,fontweight="bold")
    arrow(ax,(39,44),(26,43),color=GOLD,lw=.8); ax.text(27,47,"bounded exception",color=GOLD,fontsize=5.0,fontweight="bold")
    arrow(ax,(63,20),(72,29),color=TEAL,lw=1.0)
    ax.text(51,7,"EVERY DECISION: REASON CODE · EVIDENCE REFERENCES · ARTIFACT DIGEST · SCOPE · EXPIRY · ROLLBACK TARGET",ha="center",color=INK,fontsize=5.7,fontweight="bold")
    SYSTEM.save(fig, 16)


def f17():
    fig, ax = SYSTEM.setup(17, "Synthetic release-cycle scorecard; critical coverage and evidence freshness deliberately breach", plot=False)
    headers=["OBJECTIVE","TARGET","OBSERVED","STATUS","OWNER"]; xs=[3,45,61,76,87]
    for x,h in zip(xs,headers): ax.text(x,80,h,color=INK,fontsize=5.7,fontweight="bold")
    rows=[
        ("CRITICAL SCENARIO COVERAGE","100%","96.2%","BREACH","Eval"), ("RUN REPRODUCIBILITY","≥ 99%","99.7%","PASS","Platform"),
        ("ADJUDICATION AGREEMENT","≥ .90",".93","PASS","Domain"), ("EVIDENCE FRESHNESS","≤ 30 d","43 d","BREACH","Product"),
        ("CRITICAL POLICY VIOLATION","0","0","PASS","Risk"), ("SHADOW RECEIPT COMPLETENESS","≥ 99.9%","99.96%","PASS","Data"),
        ("CANARY DETECTION P95","≤ 5 min","3.8 min","PASS","SRE"), ("ROLLBACK DRILL SUCCESS","100%","100%","PASS","SRE"),
    ]
    for i,row in enumerate(rows):
        y=70-i*7.6; ax.add_patch(Rectangle((2,y-2.5),94,6.2,facecolor=SURFACE if i%2==0 else "#EEF2F8",edgecolor=LINE,linewidth=.45))
        for x,value in zip(xs,row): ax.text(x,y+.4,value,color=INK,fontsize=5.2,va="center",fontweight="bold" if value in ("PASS","BREACH") else None)
        c=TEAL if row[3]=="PASS" else RUST; ax.add_patch(Circle((79,y+.4),1.2,facecolor=c,edgecolor="none"))
    ax.text(49,5,"A BREACH NARROWS AUTHORITY OR BLOCKS RELEASE · TEST VOLUME ALONE NEVER OVERRIDES A CRITICAL GAP",ha="center",color=RUST,fontsize=6.0,fontweight="bold")
    SYSTEM.save(fig, 17)


def f18():
    fig, ax = SYSTEM.setup(18, "Evaluation evolves from a deployment contract into a continuously renewed production evidence system")
    phases=[
        ("0 CONTRACT", "actions · tools · ceilings", 1, 8, BLUE), ("1 HARNESS", "state · IDs · deterministic replay", 15, 18, PURPLE),
        ("2 COVERAGE", "taxonomy · oracles · cohorts", 29, 28, GOLD), ("3 RESILIENCE", "faults · adversarial · recovery", 43, 38, RUST),
        ("4 SHADOW", "representative effectless runs", 57, 48, BLUE), ("5 CANARY", "bounded authority + rollback", 71, 58, TEAL),
        ("6 CONTINUOUS", "drift · incidents · renewal", 85, 68, PURPLE),
    ]
    for i,(title,body,x,y,c) in enumerate(phases):
        fill={BLUE:BLUE_LIGHT,PURPLE:PURPLE_LIGHT,GOLD:GOLD_LIGHT,RUST:RUST_LIGHT,TEAL:TEAL_LIGHT}[c]
        box(ax,x,y,13,12,title,body,edge=c,fill=fill,title_color=c,fs=4.9)
        if i<len(phases)-1: arrow(ax,(x+13,y+6),(phases[i+1][2],phases[i+1][3]+6),color=c,lw=.8)
    gates=[(13,"scope"),(27,"replay"),(41,"coverage"),(55,"fault proof"),(69,"shadow labels"),(83,"canary SLO")]
    for x,label in gates:
        ax.plot([x,x],[6,84],color=LINE,lw=.5,ls="--"); ax.text(x,4,label,ha="center",fontsize=4.6,color=MUTED,rotation=15)
    ax.text(50,86,"INCREASING EVIDENCE STRENGTH AND PRODUCTION AUTHORITY →",ha="center",color=INK,fontsize=6.2,fontweight="bold")
    SYSTEM.save(fig, 18)


if __name__ == "__main__":
    SYSTEM.render([f01, f02, f03, f04, f05, f06, f07, f08, f09, f10, f11, f12, f13, f14, f15, f16, f17, f18])
