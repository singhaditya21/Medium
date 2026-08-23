#!/usr/bin/env python3
"""Generate 18 deep-dive figures for the model-routing capital-allocation story."""

from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.colors import LinearSegmentedColormap
from matplotlib.patches import Circle, Polygon, Rectangle

from technical_figure_framework import (
    BLUE, BLUE_LIGHT, GOLD, GOLD_LIGHT, INK, LINE, MUTED, PAPER, PURPLE,
    PURPLE_LIGHT, RUST, RUST_LIGHT, SURFACE, TEAL, TEAL_LIGHT, FigureSpec,
    FigureSystem, arrow, box,
)

ROOT = Path(__file__).resolve().parents[1]
SLUG = "model-routing-is-capital-allocation"
OUT = ROOT / "assets" / "images" / SLUG
MAP_PATH = ROOT / "stories" / f"{SLUG}-figure-map.md"


def S(n, title, form, takeaway, domain, insights, contract,
      assumption="Reference architecture; no observed production data.", core=True):
    return FigureSpec(n, title, form, takeaway, domain, tuple(insights), tuple(contract), assumption, core)


SPECS = [
    S(1, "Static routing versus capital allocation", "Comparison",
      "A production router allocates scarce quality, latency, verification, and loss budgets per action rather than mapping vague difficulty to model size.",
      "ROUTING MODEL", ["Cheapest-always ignores loss and escalation cost.", "Largest-always spends scarce capacity where it has little marginal value.", "Risk-adjusted routing selects an entire execution and verification path."],
      [("NAIVE", "cheap or large"), ("ECONOMIC", "utility under constraints"), ("OUTPUT", "route + controls")]),
    S(2, "Risk-aware routing control plane", "Architecture",
      "Policy filters infeasible routes before an optimizer ranks eligible model, tool, context, retry, and verification bundles.",
      "CONTROL PLANE", ["The router consumes action and evidence features, not raw prompt text alone.", "Policy removes routes that violate privacy, authority, latency, or assurance floors.", "Receipts and outcomes close the learning loop without automatic policy drift."],
      [("INPUT", "action + evidence"), ("DECISION", "eligible route bundle"), ("FEEDBACK", "outcome + cost")]),
    S(3, "Workflow cost ledger", "Cost decomposition",
      "Input and output tokens are only the visible portion of workflow cost; retries, tools, verification, delay, and recovery can dominate.",
      "UNIT ECONOMICS", ["Allocate cost to a stable workflow and action identity.", "Measure realized attempts and tool effects rather than quoted token price.", "Keep expected loss separate from booked infrastructure expense."],
      [("UNIT", "completed workflow"), ("COMPONENTS", "8 cost pools"), ("VALUES", "synthetic USD")],
      "Synthetic per-workflow cost allocation; values are illustrative, not vendor prices."),
    S(4, "Risk-adjusted route utility", "Formula map",
      "The optimal route maximizes expected business value net of execution cost, delay, verification, and tail loss subject to hard policy constraints.",
      "OBJECTIVE", ["Quality is valuable only through the decision it improves.", "Expected loss and tail constraints capture different risk views.", "Hard policy floors remain outside the weighted score."],
      [("MAX", "expected utility"), ("RISK", "EL + CVaR"), ("GUARDS", "privacy · SLO · policy")]),
    S(5, "Model-route capability matrix", "Capability matrix",
      "Route eligibility depends on task, tool, context, privacy, determinism, latency, and verification support—not one global model rank.",
      "MODEL PORTFOLIO", ["No model is uniformly best across every enterprise constraint.", "A route includes deployment and control configuration, not only a model name.", "Unknown or untested cells are ineligible for consequential traffic."],
      [("ROUTES", "6 bundles"), ("FACTORS", "7 capabilities"), ("SCALE", "0 unfit → 4 strong")],
      "Synthetic ordinal capability assessment; not a benchmark comparison."),
    S(6, "Quality-cost Pareto frontier", "Scatter frontier",
      "Dominated model routes consume more cost without delivering more evaluated quality and should not receive traffic absent another constraint.",
      "EFFICIENCY", ["Compare routes on the same task cohort and evaluation contract.", "The Pareto frontier changes by domain, version, and context length.", "Average quality alone does not capture high-impact error cost."],
      [("POINTS", "12 synthetic routes"), ("AXES", "cost · quality"), ("FRONTIER", "non-dominated")],
      "Synthetic route-level costs and evaluation scores; no provider benchmark claims."),
    S(7, "Risk-adjusted efficient frontier", "Portfolio frontier",
      "Adding action-weighted loss can reverse the ranking produced by average quality and token cost alone.",
      "RISK ECONOMICS", ["Weight errors by business consequence and reversibility.", "Use uncertainty intervals or conservative bounds for sparse action classes.", "Select a frontier point consistent with explicit risk tolerance."],
      [("X", "realized route cost"), ("Y", "quality-adjusted loss"), ("CHOICE", "minimum feasible")],
      "Synthetic scenario model with illustrative costs, probabilities, and loss weights."),
    S(8, "Policy-constrained route decision tree", "Decision tree",
      "Privacy, authority, action impact, novelty, and deadline gates narrow the portfolio before economic ranking.",
      "POLICY", ["Infeasible routes are rejected rather than penalized softly.", "Out-of-distribution inputs escalate or abstain.", "The selected leaf declares model, context, verification, and retry policy."],
      [("GATES", "5 decision layers"), ("LEAVES", "4 route classes"), ("DEFAULT", "abstain safely")]),
    S(9, "Router feature and policy pipeline", "Feature pipeline",
      "A reproducible feature contract joins task, evidence, risk, runtime, and portfolio state before policy and optimization.",
      "FEATURES", ["Feature timestamps and versions prevent training-serving skew.", "Sensitive attributes require purpose and access controls.", "The decision receipt stores features, candidates, exclusions, scores, and policy version."],
      [("GROUPS", "5 feature families"), ("FILTER", "hard feasibility"), ("RECORD", "route receipt")]),
    S(10, "Router calibration curve", "Reliability curve",
      "A router probability is decision-useful only when predicted suitability aligns with observed cohort outcomes and uncertainty is visible.",
      "CALIBRATION", ["Global calibration can hide domain and impact-class error.", "Sparse bins need intervals and minimum support.", "Thresholds should use calibrated probability plus action economics."],
      [("BINS", "10 probability bands"), ("SAMPLE", "synthetic n=20k"), ("CHECK", "ideal diagonal")],
      "Synthetic calibration sample of 20,000 routed tasks; not measured model performance."),
    S(11, "Out-of-distribution routing map", "Embedding map",
      "Requests far from evaluated support should abstain or use a conservative route instead of receiving a confident cheapest-model decision.",
      "NOVELTY", ["Distance is one signal, not proof of semantic novelty.", "Known hard cases and novel cases require different controls.", "Log OOD rate and downstream outcome by action class."],
      [("POINTS", "synthetic embeddings"), ("BOUNDARY", "support region"), ("ROUTE", "abstain · verify · normal")],
      "Synthetic two-dimensional projection for explanation; not a production embedding analysis."),
    S(12, "Cascaded inference and escalation", "Sequence",
      "A cascade spends additional inference only when uncertainty, policy, or verification evidence justifies the marginal call.",
      "CASCADE", ["The first model returns a typed proposal and uncertainty evidence.", "Escalation uses fresh governed context rather than copying untrusted reasoning blindly.", "Verification may be deterministic, model-based, human, or combined."],
      [("STAGES", "route · propose · verify"), ("ESCALATE", "conditional"), ("STOP", "verified or abstain")]),
    S(13, "Retry and tool-cost inflation", "Waterfall",
      "A nominal model call can become a much larger workflow expense after retries, context replay, tools, verification, and recovery.",
      "COST INFLATION", ["Count attempts and replayed context at the workflow level.", "Tool and human costs need the same allocation key.", "A failed route can consume budget without creating a completed unit."],
      [("START", "$0.041 nominal"), ("END", "$0.186 realized"), ("MULTIPLE", "4.5× synthetic")],
      "Synthetic cost waterfall for one completed workflow; not current provider pricing."),
    S(14, "Verification budget allocation", "Allocation bars",
      "Verification capacity should follow marginal expected loss reduction rather than equal sampling or model confidence alone.",
      "ASSURANCE", ["High-impact reversible and irreversible actions use different verification paths.", "Deterministic checks can dominate expensive model review for structured invariants.", "Human review is reserved for judgments with positive decision value or policy duty."],
      [("CLASSES", "6 action cohorts"), ("BUDGET", "synthetic 100 units"), ("OBJECTIVE", "loss reduction")],
      "Synthetic verification budget and expected-loss-reduction estimates."),
    S(15, "Budget shadow-price curve", "Marginal value curve",
      "The shadow price shows where one more unit of inference budget creates enough expected business value to justify allocation.",
      "BUDGET", ["Tight budgets make opportunity cost explicit.", "Marginal value falls as the highest-value escalations are funded first.", "A policy floor can require spend even below the economic cutoff."],
      [("RANGE", "$25k–$250k"), ("POINTS", "10 budget levels"), ("CUTOFF", "synthetic λ")],
      "Synthetic monthly budget and marginal-value curve; not a forecast."),
    S(16, "Counterfactual router evaluation", "Evaluation architecture",
      "A new policy needs logged candidate outcomes, randomized exploration, or defensible estimators; replaying only chosen routes creates selection bias.",
      "EVALUATION", ["Production logs reveal outcomes only for the selected route.", "Shadow execution improves coverage but adds cost and exposure controls.", "Promotion requires cohort, tail-risk, latency, and budget guardrails."],
      [("LOG", "context + propensity"), ("ESTIMATE", "IPS · DR · shadow"), ("GATE", "policy promotion")]),
    S(17, "Routing service objectives", "SLO scorecard",
      "Quality floors, tail latency, budget, calibration, policy violations, OOD abstention, and loss exposure need independent objectives.",
      "OPERATIONS", ["Aggregate cost can pass while a critical cohort fails quality.", "Budget exhaustion is not permission to weaken hard controls.", "Drift and candidate-set changes trigger recalibration and rollback review."],
      [("WINDOW", "synthetic 30 days"), ("STATUS", "6 pass · 2 breach"), ("OWNER", "ML · FinOps · Risk")],
      "Synthetic operating scorecard with deliberate calibration and tail-loss breaches."),
    S(18, "Migration to governed model routing", "Maturity roadmap",
      "Teams should build cost and outcome evidence before moving from fixed routes to constrained optimization and adaptive portfolios.",
      "MIGRATION", ["Start with route receipts and workflow cost allocation.", "Shadow and canary policies before granting economic autonomy.", "Add online adaptation only behind drift, risk, and rollback controls."],
      [("PHASES", "0 through 5"), ("GATE", "quality + risk + cost"), ("ROLLBACK", "policy version")]),
]

SYSTEM = FigureSystem(SLUG, OUT, MAP_PATH, "Model Routing Is Capital Allocation", SPECS)


def f01():
    fig, ax = SYSTEM.setup(1, "The route is an execution portfolio, not a model-size label")
    rows = [
        ("DECISION UNIT", "prompt", "workflow action"),
        ("OBJECTIVE", "token cost", "risk-adjusted utility"),
        ("CANDIDATE", "model name", "model + context + tools + checks"),
        ("CONSTRAINT", "difficulty", "policy + privacy + SLO + capacity"),
        ("FAILURE COST", "ignored", "priced by action consequence"),
        ("EVIDENCE", "single benchmark", "cohort outcomes + uncertainty"),
        ("OUTPUT", "cheap / large", "route bundle + receipt"),
    ]
    for x, title, color, fill in [(3, "STATIC ROUTER", RUST, RUST_LIGHT), (52, "CAPITAL ALLOCATOR", TEAL, TEAL_LIGHT)]:
        box(ax, x, 75, 43, 9, title, "routing contract", edge=color, fill=fill, title_color=color, fs=7.4)
    for i, (label, left, right) in enumerate(rows):
        y = 66 - i * 8
        ax.text(49, y + 3, label, ha="center", va="center", color=MUTED, fontsize=5.4, fontweight="bold")
        box(ax, 3, y, 43, 6, left, edge=LINE, fill=SURFACE, fs=6.1)
        box(ax, 52, y, 43, 6, right, edge=LINE, fill=SURFACE, fs=6.1)
    SYSTEM.save(fig, 1)


def f02():
    fig, ax = SYSTEM.setup(2, "Hard feasibility precedes economic ranking; receipts and outcomes close the loop")
    inputs = [("ACTION", "type · impact · reversibility", BLUE), ("EVIDENCE", "coverage · novelty · conflict", PURPLE),
              ("RUNTIME", "deadline · capacity · outage", GOLD), ("PORTFOLIO", "models · price · limits", TEAL)]
    for i, (t, b, c) in enumerate(inputs):
        box(ax, 2, 70 - i * 17, 20, 12, t, b, edge=c, fill=SURFACE, title_color=c, fs=6.2)
        arrow(ax, (22, 76 - i * 17), (30, 48), color=c, lw=.7)
    box(ax, 30, 59, 25, 19, "POLICY FILTER", "privacy · authority · quality floor\nlatency · geography · assurance", edge=RUST, fill=RUST_LIGHT, title_color=RUST, fs=6.7)
    box(ax, 30, 28, 25, 19, "UTILITY OPTIMIZER", "expected value − cost − delay\n− expected loss − tail penalty", edge=PURPLE, fill=PURPLE_LIGHT, title_color=PURPLE, fs=6.7)
    arrow(ax, (42.5, 59), (42.5, 47), color=RUST)
    routes = [("ROUTE BUNDLE", "model · context · tools", BLUE), ("VERIFICATION", "checks · judge · human", TEAL),
              ("RETRY POLICY", "fresh context · cap · abstain", GOLD), ("ROUTE RECEIPT", "features · candidates · scores", PURPLE)]
    for i, (t, b, c) in enumerate(routes):
        box(ax, 65, 69 - i * 17, 29, 12, t, b, edge=c, fill=SURFACE, title_color=c, fs=6.1)
        arrow(ax, (55, 38), (65, 75 - i * 17), color=c, lw=.65)
    ax.text(48, 10, "OUTCOME + REALIZED COST + INCIDENT LABEL → GOVERNED EVALUATION STORE", ha="center", color=TEAL, fontsize=6.2, fontweight="bold")
    SYSTEM.save(fig, 2)


def f03():
    fig, ax = SYSTEM.setup(3, "Synthetic allocation per completed workflow", plot=True)
    labels = ["INPUT", "OUTPUT", "ROUTER", "TOOLS", "RETRIES", "VERIFY", "DELAY", "RECOVERY"]
    values = np.array([.018, .031, .004, .047, .025, .039, .012, .010])
    colors = [BLUE, BLUE, PURPLE, TEAL, RUST, GOLD, GOLD, RUST]
    bars = ax.barh(range(len(labels)), values, color=colors, edgecolor=INK, linewidth=.45)
    ax.set_yticks(range(len(labels)), labels, fontsize=5.8)
    ax.invert_yaxis(); ax.set_xlim(0, .055)
    ax.set_xlabel("USD per completed workflow · synthetic", fontsize=6.2, color=MUTED)
    ax.tick_params(axis="x", labelsize=5.4, colors=MUTED); ax.tick_params(axis="y", length=0, colors=MUTED)
    ax.grid(axis="x", color=LINE, lw=.5); ax.set_axisbelow(True)
    for bar, value in zip(bars, values):
        ax.text(value + .001, bar.get_y() + bar.get_height()/2, f"${value:.3f}", va="center", fontsize=5.6, color=INK, family="monospace")
    ax.text(.053, 7.55, f"TOTAL  ${values.sum():.3f}", ha="right", color=INK, fontsize=6.5, fontweight="bold")
    SYSTEM.save(fig, 3)


def f04():
    fig, ax = SYSTEM.setup(4, "One objective joins business value, spend, delay, and risk without weakening hard floors")
    box(ax, 6, 66, 88, 14, "MAXIMIZE  U(r | x)", "E[value of correct action] − Cexec − Cverify − Cdelay − E[loss] − λtail·CVaRα(loss)", edge=PURPLE, fill=PURPLE_LIGHT, title_color=PURPLE, fs=8)
    terms = [("VALUE", "decision uplift", BLUE), ("EXECUTION", "tokens · tools · infra", TEAL), ("DELAY", "deadline · queue", GOLD),
             ("EXPECTED LOSS", "p(error) × impact", RUST), ("TAIL LOSS", "CVaRα", RUST)]
    for i, (t, b, c) in enumerate(terms):
        x = 2 + i * 19.2
        box(ax, x, 39, 17, 16, t, b, edge=c, fill=SURFACE, title_color=c, fs=6.1)
        arrow(ax, (x + 8.5, 55), (50, 66), color=c, lw=.65)
    guards = [("QUALITY FLOOR", BLUE), ("P95 / P99 SLO", GOLD), ("PRIVACY", PURPLE), ("AUTHORITY", RUST), ("CAPACITY", TEAL)]
    for i, (t, c) in enumerate(guards):
        box(ax, 2 + i * 19.2, 13, 17, 10, t, "hard feasibility", edge=c, fill=SURFACE, title_color=c, fs=5.7)
    ax.text(49, 6, "INFEASIBLE ROUTES ARE REMOVED · THEY ARE NOT RESCUED BY A HIGH WEIGHTED SCORE", ha="center", color=RUST, fontsize=6.4, fontweight="bold")
    SYSTEM.save(fig, 4)


def f05():
    fig, ax = SYSTEM.setup(5, "Each bundle is assessed on the governed workload, not a universal leaderboard", plot=True)
    fig.subplots_adjust(left=.12, right=.745, top=.82, bottom=.145)
    rows = ["LOCAL 8B + RULES", "LOCAL 32B + CHECKS", "HOSTED FAST + TOOLS", "HOSTED DEEP + VERIFY", "DUAL MODEL + JUDGE", "HUMAN ESCALATION"]
    cols = ["EXTRACT", "REASON", "TOOL", "LONG CTX", "PRIVACY", "P99", "ASSURANCE"]
    data = np.array([[4,1,2,1,4,4,2],[4,3,3,3,4,3,3],[4,3,4,3,2,4,3],[4,4,4,4,2,1,4],[4,4,4,4,2,1,4],[3,4,2,4,4,0,4]])
    cmap = LinearSegmentedColormap.from_list("cap", [RUST_LIGHT, GOLD_LIGHT, BLUE_LIGHT, TEAL_LIGHT, TEAL])
    ax.imshow(data, cmap=cmap, vmin=0, vmax=4, aspect="auto")
    labels = ["UNFIT", "WEAK", "LIMIT", "FIT", "STRONG"]
    for i in range(len(rows)):
        for j in range(len(cols)):
            ax.text(j, i, labels[data[i,j]], ha="center", va="center", fontsize=5.3, color=INK, fontweight="bold")
    ax.set_xticks(range(len(cols)), cols, fontsize=5.2, rotation=25, ha="right")
    ax.set_yticks(range(len(rows)), rows, fontsize=5.5); ax.tick_params(length=0, colors=MUTED)
    SYSTEM.save(fig, 5)


def f06():
    fig, ax = SYSTEM.setup(6, "Synthetic route outcomes for one governed action cohort", plot=True)
    cost = np.array([.02,.03,.04,.05,.06,.075,.09,.11,.14,.18,.23,.30])
    quality = np.array([.70,.76,.74,.81,.79,.84,.83,.88,.87,.90,.895,.91])
    names = ["R1","R2","R3","R4","R5","R6","R7","R8","R9","R10","R11","R12"]
    frontier = [0,1,3,5,7,9,11]
    ax.scatter(cost, quality, s=90, color=BLUE_LIGHT, edgecolor=BLUE, linewidth=.8, zorder=3)
    ax.plot(cost[frontier], quality[frontier], color=TEAL, lw=1.5, marker="o", markersize=3.5, zorder=4)
    for x, y, name in zip(cost, quality, names): ax.text(x, y+.006, name, ha="center", fontsize=5.2, color=INK, fontweight="bold")
    ax.fill_between(cost[frontier], quality[frontier]-.008, quality[frontier]+.008, color=TEAL_LIGHT, alpha=.45)
    ax.set_xlim(0,.32); ax.set_ylim(.67,.94); ax.grid(color=LINE,lw=.5); ax.set_axisbelow(True)
    ax.set_xlabel("Realized route cost · USD / action · synthetic", fontsize=6.2, color=MUTED)
    ax.set_ylabel("Evaluated task utility · 0–1", fontsize=6.2, color=MUTED)
    ax.tick_params(labelsize=5.4, colors=MUTED)
    ax.text(.205,.72,"DOMINATED ROUTES",color=RUST,fontsize=6.2,fontweight="bold")
    SYSTEM.save(fig, 6)


def f07():
    fig, ax = SYSTEM.setup(7, "Action-weighted loss changes which routes remain efficient", plot=True)
    cost = np.array([.03,.05,.07,.09,.12,.16,.20,.26,.31,.38])
    avg_loss = np.array([52,39,34,30,26,22,19,17,15,14])
    tail = np.array([91,69,54,43,35,28,25,22,21,20])
    ax.plot(cost, avg_loss, color=BLUE, marker="o", markersize=4, lw=1.3, label="Expected loss")
    ax.plot(cost, tail, color=RUST, marker="s", markerfacecolor=SURFACE, markersize=4, lw=1.3, label="CVaR95 loss")
    feasible = cost >= .12
    ax.fill_between(cost, tail, 100, where=~feasible, color=RUST_LIGHT, alpha=.5)
    ax.axvline(.12, color=GOLD, lw=1.2, ls="--"); ax.text(.125,86,"POLICY FLOOR",color=GOLD,fontsize=5.7,fontweight="bold")
    ax.scatter([.20],[25],s=110,color=TEAL,edgecolor=INK,zorder=4); ax.text(.205,27,"SELECTED",color=TEAL,fontsize=6,fontweight="bold")
    ax.set_xlim(.015,.40); ax.set_ylim(0,100); ax.grid(color=LINE,lw=.5); ax.set_axisbelow(True)
    ax.set_xlabel("Realized route cost · synthetic USD",fontsize=6.2,color=MUTED); ax.set_ylabel("Loss index · lower is better",fontsize=6.2,color=MUTED)
    ax.tick_params(labelsize=5.4,colors=MUTED); ax.legend(loc="upper right",frameon=False,fontsize=5.7)
    SYSTEM.save(fig, 7)


def f08():
    fig, ax = SYSTEM.setup(8, "Feasibility gates precede optimization and produce an explicit safe default")
    nodes = [("DATA BOUNDARY", "may this deployment see it?", 45, 76, PURPLE), ("AUTHORITY", "may this route support the action?", 45, 61, RUST),
             ("IMPACT", "reversible and bounded?", 45, 46, GOLD), ("NOVELTY", "inside evaluated support?", 45, 31, BLUE), ("DEADLINE", "can assurance finish in time?", 45, 16, TEAL)]
    for t,b,x,y,c in nodes: box(ax,x,y,24,10,t,b,edge=c,fill=SURFACE,title_color=c,fs=5.9)
    for i in range(len(nodes)-1): arrow(ax,(57,nodes[i][3]),(57,nodes[i+1][3]+10),color=INK,lw=.8)
    leaves = [("LOCAL PRIVATE",4,70,PURPLE),("FAST + CHECK",4,49,BLUE),("DEEP + VERIFY",74,49,GOLD),("HUMAN / ABSTAIN",74,20,RUST)]
    for t,x,y,c in leaves: box(ax,x,y,21,11,t,"model · context · checks",edge=c,fill={PURPLE:PURPLE_LIGHT,BLUE:BLUE_LIGHT,GOLD:GOLD_LIGHT,RUST:RUST_LIGHT}[c],title_color=c,fs=5.7)
    for start,end,c,label in [((45,81),(25,75),PURPLE,"restricted"),((45,66),(25,54),BLUE,"bounded"),((69,51),(74,54),GOLD,"material"),((69,36),(74,25),RUST,"novel / late")]:
        arrow(ax,start,end,color=c,lw=.8); ax.text((start[0]+end[0])/2,(start[1]+end[1])/2+2,label,ha="center",fontsize=5.2,color=c,fontweight="bold")
    SYSTEM.save(fig, 8)


def f09():
    fig, ax = SYSTEM.setup(9, "Versioned features, feasibility, scoring, and evidence produce one auditable decision")
    groups = [("TASK", "intent · domain · schema", BLUE), ("EVIDENCE", "coverage · conflict · age", PURPLE), ("RISK", "impact · reversibility · rights", RUST),
              ("RUNTIME", "deadline · queue · outage", GOLD), ("PORTFOLIO", "price · capacity · version", TEAL)]
    for i,(t,b,c) in enumerate(groups):
        x=2+i*19.1; box(ax,x,70,17,13,t,b,edge=c,fill=SURFACE,title_color=c,fs=5.8); arrow(ax,(x+8.5,70),(50,58),color=c,lw=.6)
    box(ax,31,46,38,12,"FEATURE CONTRACT", "event time · source · transform version · missingness · access purpose",edge=BLUE,fill=BLUE_LIGHT,title_color=BLUE,fs=6.3)
    arrow(ax,(50,46),(50,38),color=BLUE)
    box(ax,8,22,23,13,"FEASIBILITY", "exclude + reason codes",edge=RUST,fill=RUST_LIGHT,title_color=RUST,fs=6.2)
    box(ax,38,22,23,13,"UTILITY SCORE", "value − cost − risk",edge=PURPLE,fill=PURPLE_LIGHT,title_color=PURPLE,fs=6.2)
    box(ax,68,22,23,13,"ROUTE RECEIPT", "candidates · scores · chosen",edge=TEAL,fill=TEAL_LIGHT,title_color=TEAL,fs=6.2)
    arrow(ax,(50,38),(19.5,35),color=RUST); arrow(ax,(31,28.5),(38,28.5),color=RUST); arrow(ax,(61,28.5),(68,28.5),color=PURPLE)
    ax.text(49,9,"TRAINING–SERVING SKEW CHECK · FEATURE DRIFT · DECISION / OUTCOME JOIN",ha="center",color=GOLD,fontsize=6.2,fontweight="bold")
    SYSTEM.save(fig, 9)


def f10():
    fig, ax = SYSTEM.setup(10, "Predicted route suitability versus observed success in equal-support bins", plot=True)
    pred=np.arange(.05,1.0,.10); observed=np.array([.07,.14,.22,.31,.43,.55,.65,.76,.83,.89]); n=np.array([1600,1900,2100,2300,2500,2500,2300,2000,1600,1300])
    err=1.96*np.sqrt(np.maximum(observed*(1-observed)/n,.00001))
    ax.plot([0,1],[0,1],color=INK,lw=1,ls="--",label="Ideal")
    ax.errorbar(pred,observed,yerr=err,fmt="o-",color=BLUE,ecolor=BLUE_LIGHT,elinewidth=2,capsize=2,markersize=4,label="Router")
    ax.fill_between(pred,observed-err,observed+err,color=BLUE_LIGHT,alpha=.55)
    ax.set_xlim(0,1);ax.set_ylim(0,1);ax.set_aspect("equal",adjustable="box");ax.grid(color=LINE,lw=.5);ax.set_axisbelow(True)
    ax.set_xlabel("Predicted probability strong route adds value",fontsize=6.2,color=MUTED);ax.set_ylabel("Observed suitability rate",fontsize=6.2,color=MUTED)
    ax.tick_params(labelsize=5.5,colors=MUTED);ax.legend(loc="upper left",frameon=False,fontsize=5.7)
    ax.text(.58,.48,"OVERCONFIDENT",color=RUST,fontsize=6,fontweight="bold")
    SYSTEM.save(fig, 10)


def f11():
    fig, ax = SYSTEM.setup(11, "Distance from evaluated support triggers conservative handling", plot=True)
    rng=np.random.default_rng(19)
    known=rng.normal([0,0],[.85,.55],size=(120,2)); hard=rng.normal([1.7,.8],[.35,.30],size=(28,2)); ood=rng.normal([3.2,2.1],[.45,.38],size=(18,2))
    ax.scatter(known[:,0],known[:,1],s=13,color=BLUE_LIGHT,edgecolor=BLUE,linewidth=.25,label="Evaluated support")
    ax.scatter(hard[:,0],hard[:,1],s=22,color=GOLD_LIGHT,edgecolor=GOLD,linewidth=.4,marker="s",label="Known hard")
    ax.scatter(ood[:,0],ood[:,1],s=28,color=RUST_LIGHT,edgecolor=RUST,linewidth=.5,marker="^",label="OOD / abstain")
    theta=np.linspace(0,2*np.pi,200);ax.plot(1.8*np.cos(theta),1.25*np.sin(theta),color=TEAL,lw=1.2,ls="--")
    ax.text(-1.7,1.45,"EVALUATED SUPPORT BOUNDARY",color=TEAL,fontsize=5.6,fontweight="bold")
    ax.set_xlim(-2.5,4.2);ax.set_ylim(-2,3);ax.grid(color=LINE,lw=.4);ax.set_axisbelow(True);ax.tick_params(labelsize=5.2,colors=MUTED)
    ax.set_xlabel("Embedding projection 1 · explanatory",fontsize=6,color=MUTED);ax.set_ylabel("Embedding projection 2 · explanatory",fontsize=6,color=MUTED)
    ax.legend(loc="lower right",frameon=False,fontsize=5.4)
    SYSTEM.save(fig, 11)


def f12():
    fig, ax = SYSTEM.setup(12, "Every escalation spends marginal budget against an explicit uncertainty or policy trigger")
    actors=[("ROUTER",7,BLUE),("FAST MODEL",27,TEAL),("CHECKS",47,GOLD),("DEEP MODEL",68,PURPLE),("APPROVER",90,RUST)]
    for t,x,c in actors: ax.text(x,82,t,ha="center",color=c,fontsize=5.9,fontweight="bold");ax.plot([x,x],[12,78],color=LINE,lw=.8,ls="--")
    msgs=[(7,27,71,"typed proposal",BLUE),(27,47,62,"answer + uncertainty",TEAL),(47,7,53,"fail / conflict",GOLD),(7,68,44,"fresh governed context",PURPLE),(68,47,35,"candidate + evidence",PURPLE),(47,90,26,"policy judgment",RUST),(90,7,17,"approve / deny / abstain",RUST)]
    for s,e,y,t,c in msgs: arrow(ax,(s,y),(e,y),color=c,lw=.8);ax.text((s+e)/2,y+2,t,ha="center",fontsize=5.2,color=c,fontweight="bold")
    SYSTEM.save(fig, 12)


def f13():
    fig, ax = SYSTEM.setup(13, "Focused scale · synthetic USD per completed workflow", plot=True)
    labels=["NOMINAL","RETRY","CTX REPLAY","TOOLS","VERIFY","RECOVERY","REALIZED"]
    deltas=[.041,.018,.022,.047,.039,.019]
    cumulative=[deltas[0]]
    for d in deltas[1:]: cumulative.append(cumulative[-1]+d)
    starts=[0]+cumulative[:-1]
    for i,(label,start,delta) in enumerate(zip(labels[:-1],starts,deltas)):
        c=BLUE if i==0 else (RUST if label in ["RETRY","RECOVERY"] else GOLD if label in ["CTX REPLAY","VERIFY"] else TEAL)
        ax.bar(i,delta,bottom=start,color={BLUE:BLUE_LIGHT,RUST:RUST_LIGHT,GOLD:GOLD_LIGHT,TEAL:TEAL_LIGHT}[c],edgecolor=c,linewidth=.8)
        ax.text(i,start+delta+.004,f"+${delta:.3f}" if i else f"${delta:.3f}",ha="center",fontsize=5.3,color=c,fontweight="bold")
        if i<len(deltas)-1: ax.plot([i+.4,i+1-.4],[start+delta,start+delta],color=LINE,lw=.7,ls="--")
    ax.bar(6,cumulative[-1],color=PURPLE_LIGHT,edgecolor=PURPLE,linewidth=.9);ax.text(6,cumulative[-1]+.004,f"${cumulative[-1]:.3f}",ha="center",fontsize=5.6,color=PURPLE,fontweight="bold")
    ax.set_xticks(range(7),labels,fontsize=5.2,rotation=18,ha="right");ax.set_ylim(0,.215);ax.grid(axis="y",color=LINE,lw=.5);ax.set_axisbelow(True);ax.tick_params(axis="y",labelsize=5.3,colors=MUTED)
    ax.set_ylabel("USD per completed workflow · synthetic",fontsize=6.1,color=MUTED);ax.text(5.2,.202,"4.5× NOMINAL",color=RUST,fontsize=6.4,fontweight="bold")
    SYSTEM.save(fig, 13)


def f14():
    fig, ax = SYSTEM.setup(14, "Synthetic 100-unit assurance budget allocated by marginal loss reduction", plot=True)
    fig.subplots_adjust(left=.115, right=.745, top=.82, bottom=.11)
    cohorts=["ACCOUNT CLOSE","PRICE EXCEPTION","DATA EXPORT","CUSTOMER MESSAGE","CONTRACT EXTRACT","CRM ENRICH"]
    det=np.array([6,6,7,7,8,6]); model=np.array([7,7,5,6,4,2]); human=np.array([12,9,6,2,0,0])
    y=np.arange(len(cohorts));ax.barh(y,det,color=BLUE_LIGHT,edgecolor=BLUE,label="Deterministic")
    ax.barh(y,model,left=det,color=GOLD_LIGHT,edgecolor=GOLD,label="Model verify")
    ax.barh(y,human,left=det+model,color=RUST_LIGHT,edgecolor=RUST,label="Human")
    ax.set_yticks(y,cohorts,fontsize=5.5);ax.invert_yaxis();ax.set_xlim(0,28);ax.grid(axis="x",color=LINE,lw=.5);ax.set_axisbelow(True);ax.tick_params(axis="x",labelsize=5.3,colors=MUTED);ax.tick_params(axis="y",length=0,colors=MUTED)
    ax.set_xlabel("Assurance budget units · synthetic",fontsize=6.1,color=MUTED);ax.legend(loc="lower right",frameon=False,fontsize=5.4)
    for i,total in enumerate(det+model+human):ax.text(total+.4,i,str(total),va="center",fontsize=5.4,color=INK,fontweight="bold")
    SYSTEM.save(fig, 14)


def f15():
    fig, ax = SYSTEM.setup(15, "Marginal value declines as the highest-value escalations are funded", plot=True)
    budget=np.arange(25,251,25);value=np.array([4.8,4.1,3.5,2.9,2.4,2.0,1.65,1.4,1.2,1.05]);cutoff=1.6
    ax.plot(budget,value,color=BLUE,lw=1.5,marker="o",markersize=4);ax.fill_between(budget,value,0,color=BLUE_LIGHT,alpha=.55)
    ax.axhline(cutoff,color=GOLD,lw=1.2,ls="--");ax.text(29,cutoff+.12,"SHADOW-PRICE CUTOFF λ",color=GOLD,fontsize=5.8,fontweight="bold")
    ax.axvspan(25,187.5,color=TEAL_LIGHT,alpha=.25);ax.axvspan(187.5,250,color=RUST_LIGHT,alpha=.25)
    ax.text(92,4.5,"FUND",color=TEAL,fontsize=6.2,fontweight="bold");ax.text(205,4.5,"DEFER / REPRICE",color=RUST,fontsize=6.2,fontweight="bold")
    ax.set_xlim(20,255);ax.set_ylim(0,5.2);ax.grid(color=LINE,lw=.5);ax.set_axisbelow(True);ax.tick_params(labelsize=5.4,colors=MUTED)
    ax.set_xlabel("Monthly inference + verification budget · synthetic $k",fontsize=6.1,color=MUTED);ax.set_ylabel("Marginal expected value / budget unit",fontsize=6.1,color=MUTED)
    SYSTEM.save(fig, 15)


def f16():
    fig, ax = SYSTEM.setup(16, "Estimate policy value without confusing chosen-route outcomes for every candidate")
    box(ax,3,63,21,17,"LOGGED DECISION", "context · candidates\nchosen route · propensity",edge=BLUE,fill=BLUE_LIGHT,title_color=BLUE,fs=6.3)
    branches=[("REPLAY", "deterministic checks", BLUE), ("IPS / DR", "counterfactual estimator", PURPLE), ("SHADOW", "execute without effect", GOLD)]
    for i,(t,b,c) in enumerate(branches):
        x=31+i*22;box(ax,x,63,19,17,t,b,edge=c,fill=SURFACE,title_color=c,fs=6.2);arrow(ax,(24,71.5),(x,71.5),color=c,lw=.7)
    box(ax,20,35,58,14,"COHORT EVALUATION", "quality floor · cost · TTFT / E2E · calibration · OOD · expected loss · CVaR",edge=TEAL,fill=TEAL_LIGHT,title_color=TEAL,fs=6.6)
    for i in range(3):arrow(ax,(40.5+i*22,63),(49,49),color=[BLUE,PURPLE,GOLD][i],lw=.7)
    gates=[("PROMOTE",5,13,TEAL),("HOLD",29,13,GOLD),("REJECT",53,13,RUST),("MORE COVERAGE",77,13,PURPLE)]
    for t,x,y,c in gates:box(ax,x,y,18,11,t,"policy decision",edge=c,fill=SURFACE,title_color=c,fs=5.8);arrow(ax,(49,35),(x+9,y+11),color=c,lw=.6)
    SYSTEM.save(fig, 16)


def f17():
    fig, ax = SYSTEM.setup(17, "Synthetic 30-day operating window with two deliberate breaches")
    rows=[("CRITICAL QUALITY","≥98.0%","98.4%","ML","PASS"),("P99 E2E","≤8.0s","7.6s","SRE","PASS"),("COST / SUCCESS","≤$0.22","$0.19","FINOPS","PASS"),("ECE CALIBRATION","≤0.030","0.047","ML","BREACH"),("POLICY VIOLATION","0","0","RISK","PASS"),("OOD ABSTENTION","≥99.5%","99.7%","ML","PASS"),("CVaR95 LOSS","≤18","24","RISK","BREACH"),("RECEIPT COVERAGE","100%","100%","AUDIT","PASS")]
    for h,x in [("OBJECTIVE",3),("TARGET",46),("ACTUAL",61),("OWNER",76),("STATE",90)]:ax.text(x,81,h,color=BLUE,fontsize=6.4,fontweight="bold")
    for i,row in enumerate(rows):
        y=70-i*8.2;c=TEAL if row[4]=="PASS" else RUST;ax.add_patch(Rectangle((2,y-3),95,7,facecolor=SURFACE if i%2==0 else PAPER,edgecolor=LINE,lw=.4))
        for txt,x in zip(row,[3,46,61,76,90]):ax.text(x,y,txt,color=c if x==90 else INK,fontsize=6.1,fontweight="bold" if x in [3,90] else "normal",va="center")
        ax.add_patch(Circle((87,y),1.5,facecolor=c,edgecolor=c))
    SYSTEM.save(fig, 17)


def f18():
    fig, ax = SYSTEM.setup(18, "Economic autonomy expands only after outcome, risk, and cost evidence survives deployment gates")
    phases=[("0","INVENTORY","models + workflows","cost ledger",BLUE),("1","RECEIPTS","decision evidence","join outcomes",PURPLE),("2","RULES","fixed safe cohorts","quality floor",GOLD),("3","SHADOW","new policy","counterfactual",TEAL),("4","CANARY","bounded traffic","risk + SLO",TEAL),("5","ADAPT","portfolio learning","drift + rollback",BLUE)]
    for i,(n,t,b,g,c) in enumerate(phases):
        x=2+i*15.7;y=17+i*9;box(ax,x,y,14,23,f"{n}  {t}",b,edge=c,fill=SURFACE,title_color=c,fs=6.2);ax.text(x+7,y+4,SYSTEM.wrap("GATE: "+g,18),ha="center",va="center",color=GOLD,fontsize=5.6,fontweight="bold")
        if i<5:arrow(ax,(x+14,y+11),(x+15.7,y+20),color=c)
    ax.plot([2,95],[10,10],color=RUST,lw=1.2);ax.text(48.5,5,"BREACH → FREEZE POLICY VERSION · FALL BACK TO LAST SAFE ROUTE · RECONCILE COHORTS",ha="center",color=RUST,fontsize=6.1,fontweight="bold")
    SYSTEM.save(fig, 18)


def main():
    SYSTEM.render([f01,f02,f03,f04,f05,f06,f07,f08,f09,f10,f11,f12,f13,f14,f15,f16,f17,f18])


if __name__ == "__main__":
    main()
