#!/usr/bin/env python3
"""Generate the 30 reproducible figures for the CRM escalation story."""

from __future__ import annotations

import math
import textwrap
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import Circle, FancyArrowPatch, FancyBboxPatch, Polygon, Rectangle


ROOT = Path(__file__).resolve().parents[1]
SLUG = "a-2-4m-account-is-escalating"
OUT = ROOT / "assets" / "images" / SLUG
MAP_PATH = ROOT / "stories" / f"{SLUG}-figure-map.md"

PAPER = "#F7F4EC"
SURFACE = "#FFFDF8"
INK = "#102526"
MUTED = "#667875"
LINE = "#D8D4C8"
TEAL = "#0B6B65"
TEAL_LIGHT = "#9FD2CB"
BLUE = "#2C6E9B"
BLUE_LIGHT = "#A9C9DD"
GOLD = "#B4842B"
GOLD_LIGHT = "#E8C77A"
RUST = "#B95C43"
RUST_LIGHT = "#E6B3A5"
OLIVE = "#6E7D45"
WHITE = "#FFFFFF"


FIGURE_META = [
    (1, "Account escalation snapshot", "Scorecard", "The account is commercially material, time-constrained, and evidentially conflicted."),
    (2, "Autonomy boundary by impact and uncertainty", "Decision matrix", "High-impact actions move to approval or denial as evidence uncertainty rises."),
    (3, "Production control architecture", "Architecture diagram", "The agent proposes; independent control services authorize, execute, verify, and recover."),
    (4, "Escalation event timeline", "Timeline", "The decision is shaped by a sequence of changing facts, not a single CRM record."),
    (5, "Evidence bundle anatomy", "Structured schema", "Every proposed action should carry a versioned, attributable evidence package."),
    (6, "Evidence provenance graph", "Directed graph", "Claims remain traceable to source records and contradictions stay visible."),
    (7, "Evidence freshness decay", "Multi-series line", "Different evidence types expire at different rates and should not share one freshness rule."),
    (8, "Evidence quality matrix", "Heatmap", "No source is uniformly trustworthy across provenance, freshness, completeness, and conflict."),
    (9, "CRM action taxonomy", "Ranked bar", "Risk rises sharply when the agent crosses from preparation into commercial commitment."),
    (10, "Action-level risk model", "Weighted decomposition", "Action risk combines impact, irreversibility, uncertainty, scope, and control strength."),
    (11, "Modeled loss distributions", "Distribution", "A bounded approval design compresses the tail even when median loss changes modestly."),
    (12, "Confidence threshold trade-off", "Dual line", "Model confidence is not authority; higher thresholds trade automation for lower exception risk."),
    (13, "Human approval policy matrix", "Heatmap", "Approval depends on action class and commercial exposure, not merely model confidence."),
    (14, "Maker-checker approval flow", "Swimlane", "The proposer, approver, credential issuer, and executor remain distinct."),
    (15, "Approval latency trade-off", "Line with benchmark", "Faster review helps the deal until rushed approvals create more expected loss."),
    (16, "Approval packet design", "Decision card", "Approvers need deltas, evidence conflicts, limits, and rollback—not a prose summary."),
    (17, "Authority envelope", "Structured control object", "Authority binds principal, actor, action, resource, purpose, limits, time, tool, and evidence."),
    (18, "Permission scope lattice", "Hierarchy", "Each step narrows standing CRM privilege into one permitted transaction."),
    (19, "Permission lease lifecycle", "State flow", "A leased permission is issued late, used narrowly, verified, and then revoked or expires."),
    (20, "TTL and scope exposure", "Heatmap", "Longer leases and broader account scope multiply modeled exposure."),
    (21, "Delegated token exchange", "Sequence diagram", "The downstream tool receives both the accountable subject and current agent actor."),
    (22, "Pre-action verification gates", "Stage progression", "The tool refuses execution until evidence, policy, approval, lease, and preconditions agree."),
    (23, "Post-action verification loop", "Control loop", "A successful API response is not proof that the intended business state exists."),
    (24, "Action receipt schema", "Structured record", "The receipt joins intent, authority, decision, execution, observation, and recovery pointers."),
    (25, "End-to-end observability trace", "Trace timeline", "One trace correlates agent planning, policy, approval, credential, tool, and verification events."),
    (26, "Failure-mode risk matrix", "Risk matrix", "The design prioritizes high-impact failures that can escape ordinary API monitoring."),
    (27, "Containment stack", "Layered decomposition", "Independent bounds reduce the blast radius even if one control fails."),
    (28, "Recovery state machine", "State machine", "Recovery is designed before action: freeze, revoke, compensate, reconcile, and close."),
    (29, "Operational reconciliation view", "Dashboard", "Operators need action, evidence, approval, verification, and recovery metrics together."),
    (30, "Production rollout roadmap", "Stage roadmap", "Autonomy expands only after evidence, controls, and recovery performance meet gates."),
]


def wrap(value: str, width: int = 24) -> str:
    return "\n".join(textwrap.wrap(value, width=width))


def setup(number: int, title: str, subtitle: str, plot: bool = False):
    fig, ax = plt.subplots(figsize=(10, 5.625), dpi=160)
    fig.patch.set_facecolor(PAPER)
    ax.set_facecolor(PAPER)
    fig.subplots_adjust(left=0.08, right=0.96, top=0.78, bottom=0.13)
    fig.text(0.08, 0.935, f"FIGURE {number:02d}", color=TEAL, fontsize=8, fontweight="bold", family="DejaVu Sans")
    fig.text(0.08, 0.87, title, color=INK, fontsize=20, fontweight="bold", family="DejaVu Sans")
    fig.text(0.08, 0.82, subtitle, color=MUTED, fontsize=9, family="DejaVu Sans")
    fig.text(0.96, 0.035, "Illustrative scenario · synthetic values · not production data", ha="right", color=MUTED, fontsize=6.8)
    if not plot:
        ax.set_xlim(0, 100)
        ax.set_ylim(0, 100)
        ax.axis("off")
    return fig, ax


def save(fig, number: int) -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    fig.savefig(OUT / f"figure-{number:02d}.png", facecolor=PAPER, dpi=160)
    plt.close(fig)


def box(ax, x, y, w, h, title, body="", color=SURFACE, edge=LINE, title_color=INK, radius=0.018, lw=1.1):
    patch = FancyBboxPatch((x, y), w, h, boxstyle=f"round,pad=0.012,rounding_size={radius}", facecolor=color, edgecolor=edge, linewidth=lw)
    ax.add_patch(patch)
    ax.text(x + w * 0.06, y + h * 0.66, title, color=title_color, fontsize=10, fontweight="bold", va="center")
    if body:
        ax.text(x + w * 0.06, y + h * 0.30, body, color=MUTED, fontsize=7.4, va="center", linespacing=1.35)
    return patch


def arrow(ax, start, end, color=MUTED, lw=1.4, style="-|>", connectionstyle="arc3"):
    ax.add_patch(FancyArrowPatch(start, end, arrowstyle=style, mutation_scale=11, color=color, linewidth=lw, connectionstyle=connectionstyle))


def f01():
    fig, ax = setup(1, "Account escalation snapshot", "Synthetic case state at T−21 days to renewal")
    cards = [
        ("$2.4M", "annual contract value", TEAL), ("21 days", "to renewal", GOLD),
        ("−23%", "90-day active usage", RUST), ("2", "priority-one incidents", RUST),
        ("Changed", "executive sponsor", BLUE), ("12%", "agent-proposed discount", GOLD),
    ]
    for i, (value, label, color) in enumerate(cards):
        col, row = i % 3, i // 3
        x, y = 4 + col * 32, 54 - row * 35
        box(ax, x, y, 28, 27, value, wrap(label, 22), color=SURFACE, edge=LINE, title_color=color)
    ax.text(4, 6, "Decision pressure", fontsize=8, fontweight="bold", color=INK)
    ax.plot([21, 94], [8, 8], color=LINE, lw=6, solid_capstyle="round")
    ax.plot([21, 81], [8, 8], color=RUST, lw=6, solid_capstyle="round")
    ax.text(21, 3, "low", fontsize=7, color=MUTED, ha="center")
    ax.text(94, 3, "high", fontsize=7, color=MUTED, ha="center")
    save(fig, 1)


def f02():
    fig, ax = setup(2, "Autonomy boundary by impact and uncertainty", "Policy zones for one proposed CRM action", plot=True)
    ax.set_xlim(0, 10); ax.set_ylim(0, 10)
    ax.add_patch(Rectangle((0, 0), 4.2, 4.2, color=TEAL_LIGHT, alpha=.62))
    ax.add_patch(Rectangle((4.2, 0), 5.8, 6.4, color=GOLD_LIGHT, alpha=.52))
    ax.add_patch(Rectangle((0, 4.2), 4.2, 5.8, color=GOLD_LIGHT, alpha=.52))
    ax.add_patch(Rectangle((4.2, 6.4), 5.8, 3.6, color=RUST_LIGHT, alpha=.58))
    ax.text(1.0, 1.0, "AUTO\nReversible preparation", color=TEAL, fontsize=12, fontweight="bold")
    ax.text(5.0, 2.0, "APPROVE\nHuman decision required", color=GOLD, fontsize=12, fontweight="bold")
    ax.text(6.4, 8.2, "DENY / DEFER\nInsufficient basis", color=RUST, fontsize=12, fontweight="bold")
    points = [(2.2, 2.1, "create task"), (4.9, 3.4, "schedule meeting"), (7.0, 4.5, "send proposal"), (8.2, 6.8, "commit 12% discount"), (6.6, 8.2, "change contract")]
    for x, y, label in points:
        ax.scatter(x, y, s=42, color=INK, zorder=5)
        ax.text(x + .15, y + .18, label, fontsize=7, color=INK)
    ax.set_xlabel("Business impact and irreversibility →", color=INK, fontsize=9)
    ax.set_ylabel("Evidence uncertainty →", color=INK, fontsize=9)
    ax.set_xticks([]); ax.set_yticks([])
    for spine in ax.spines.values(): spine.set_color(LINE)
    save(fig, 2)


def f03():
    fig, ax = setup(3, "Production control architecture", "The language model never receives standing commercial authority")
    stages = [
        (3, 57, 15, 22, "Signals", "CRM · product\nsupport · billing"),
        (22, 57, 15, 22, "Evidence", "provenance · freshness\nconflict checks"),
        (41, 57, 15, 22, "Planner", "options · rationale\nexpected outcomes"),
        (60, 57, 15, 22, "Policy", "risk · approval\ncontrol decision"),
        (79, 57, 15, 22, "Tool gateway", "leased credential\nallowlisted action"),
    ]
    for x, y, w, h, t, b in stages: box(ax, x, y, w, h, t, b)
    for x in [18, 37, 56, 75]: arrow(ax, (x, 68), (x + 4, 68))
    controls = [
        (9, 18, 19, 20, "Human approval", "maker-checker · SLA"),
        (31, 18, 19, 20, "Credential broker", "subject + actor · TTL"),
        (53, 18, 19, 20, "Verifier", "before/after · receipt"),
        (75, 18, 19, 20, "Recovery", "freeze · revoke · compensate"),
    ]
    for x, y, w, h, t, b in controls: box(ax, x, y, w, h, t, b, color="#EEF4F2", edge=TEAL_LIGHT)
    ax.plot([3, 94], [48, 48], color=LINE, lw=1)
    ax.text(3, 44, "Independent control plane", color=TEAL, fontsize=8, fontweight="bold")
    for x in [18.5, 40.5, 62.5, 84.5]: arrow(ax, (x, 57), (x, 38), color=TEAL, connectionstyle="arc3")
    save(fig, 3)


def f04():
    fig, ax = setup(4, "Escalation event timeline", "Synthetic signals arriving before the agent proposes a commercial action")
    ax.plot([6, 94], [48, 48], color=INK, lw=2)
    events = [
        (8, "T−90d", "Usage begins\nto decline", BLUE), (23, "T−45d", "P1 incident\nreopens", RUST),
        (38, "T−28d", "Sponsor\ndeparts", GOLD), (53, "T−24d", "Competitor\nmentioned", RUST),
        (68, "T−22d", "Forecast drops\nto 61%", GOLD), (83, "T−21d", "Agent proposes\n12% discount", TEAL),
        (94, "T−21d", "Policy requests\napproval", INK),
    ]
    for i, (x, when, label, color) in enumerate(events):
        ax.scatter(x, 48, s=80, color=color, edgecolor=WHITE, linewidth=1.5, zorder=3)
        top = i % 2 == 0
        y = 72 if top else 21
        ax.plot([x, x], [50 if top else 46, y - 6 if top else y + 9], color=LINE, lw=1)
        ax.text(x, y, when, ha="center", color=color, fontsize=8, fontweight="bold")
        ax.text(x, y - 8 if top else y - 7, label, ha="center", va="top", color=INK, fontsize=7.2, linespacing=1.35)
    save(fig, 4)


def f05():
    fig, ax = setup(5, "Evidence bundle anatomy", "Versioned evidence supplied to policy and human approvers")
    columns = [
        (3, "Commercial", ["ACV and margin", "renewal date", "contract terms", "open quote"]),
        (27, "Customer", ["usage trend", "support incidents", "stakeholder map", "sentiment"]),
        (51, "Authority", ["account owner", "approval limits", "maker-checker", "policy version"]),
        (75, "Integrity", ["source ID", "observed at", "hash/version", "conflicts"]),
    ]
    for x, title, items in columns:
        box(ax, x, 16, 21, 66, title, "", color=SURFACE, edge=LINE, title_color=TEAL)
        for j, item in enumerate(items):
            y = 62 - j * 12
            ax.add_patch(Circle((x + 3.5, y), 1.3, color=GOLD_LIGHT))
            ax.text(x + 7, y, item, va="center", fontsize=8, color=INK)
    ax.text(50, 7, "bundle_id + account_id + decision_time + schema_version", ha="center", color=MUTED, fontsize=8, family="monospace")
    save(fig, 5)


def f06():
    fig, ax = setup(6, "Evidence provenance graph", "Each conclusion retains a path back to source records")
    sources = [(7, 70, "CRM"), (7, 48, "Product"), (7, 26, "Support")]
    facts = [(37, 72, "Quote v18"), (37, 54, "Usage −23%"), (37, 34, "P1 unresolved"), (37, 16, "Sponsor changed")]
    claims = [(70, 64, "Renewal risk\nis elevated"), (70, 31, "A discount may\nnot fix the cause")]
    for x, y, t in sources: box(ax, x, y, 17, 13, t, "system of record", color="#EEF4F2", edge=TEAL_LIGHT)
    for x, y, t in facts: box(ax, x, y, 19, 12, t, "source + timestamp", color=SURFACE)
    for x, y, t in claims: box(ax, x, y, 24, 17, t, "derived claim", color="#FBF3E4", edge=GOLD_LIGHT)
    links = [((24,76),(37,78)),((24,54),(37,60)),((24,32),(37,40)),((24,76),(37,22)),((56,78),(70,70)),((56,60),(70,70)),((56,40),(70,39)),((56,22),(70,39))]
    for a,b in links: arrow(ax,a,b,color=MUTED,lw=1)
    ax.add_patch(FancyBboxPatch((61,45),30,9,boxstyle="round,pad=.02",facecolor=RUST_LIGHT,edgecolor=RUST,linewidth=1))
    ax.text(76,49.5,"CONFLICT: sentiment positive, usage falling",ha="center",va="center",fontsize=7,color=RUST,fontweight="bold")
    save(fig, 6)


def f07():
    fig, ax = setup(7, "Evidence freshness decay", "Modeled decision value after the source was observed", plot=True)
    days = np.linspace(0, 30, 61)
    series = [("incident state", 3, RUST, "-"), ("usage trend", 14, BLUE, "--"), ("contract terms", 180, TEAL, "-"), ("stakeholder role", 30, GOLD, ":")]
    for name, half_life, color, ls in series:
        value = np.exp(-np.log(2)*days/half_life)
        ax.plot(days,value,label=name,color=color,lw=2.2,ls=ls)
        ax.text(30.5,value[-1],name,fontsize=7,color=color,va="center")
    ax.axhline(.5,color=LINE,lw=1); ax.text(1,.52,"review threshold",fontsize=7,color=MUTED)
    ax.set_xlim(0,36); ax.set_ylim(0,1.04)
    ax.set_xlabel("days since observation",fontsize=8,color=INK); ax.set_ylabel("modeled decision value",fontsize=8,color=INK)
    ax.grid(axis="y",color=LINE,lw=.7); ax.spines[["top","right"]].set_visible(False)
    ax.tick_params(labelsize=7,colors=MUTED)
    save(fig, 7)


def f08():
    fig, ax = setup(8, "Evidence quality matrix", "Illustrative 0–100 control scores by source and evidence dimension", plot=True)
    fig.subplots_adjust(left=0.18, right=0.96, top=0.78, bottom=0.16)
    data=np.array([[96,92,88,90],[91,74,82,78],[88,58,76,71],[79,84,63,54],[85,67,70,62]])
    im=ax.imshow(data,cmap="YlGnBu",vmin=45,vmax=100,aspect="auto")
    rows=["contract","CRM opportunity","product telemetry","support record","meeting notes"]
    cols=["provenance","freshness","completeness","conflict control"]
    ax.set_xticks(range(4),cols,fontsize=7); ax.set_yticks(range(5),rows,fontsize=8)
    for i in range(data.shape[0]):
        for j in range(data.shape[1]): ax.text(j,i,str(data[i,j]),ha="center",va="center",fontsize=8,color=WHITE if data[i,j]>78 else INK,fontweight="bold")
    ax.tick_params(length=0,colors=INK); [s.set_visible(False) for s in ax.spines.values()]
    save(fig, 8)


def f09():
    fig, ax = setup(9, "CRM action taxonomy", "Illustrative action risk score; 0 = lowest, 100 = highest", plot=True)
    fig.subplots_adjust(left=0.28, right=0.96, top=0.78, bottom=0.15)
    labels=["create internal task","draft call plan","schedule customer meeting","send non-binding email","issue service credit","commit discount / terms"]
    values=[9,18,27,43,68,91]
    colors=[TEAL,TEAL,BLUE,GOLD,RUST,RUST]
    y=np.arange(len(labels))
    ax.barh(y,values,color=colors,edgecolor=INK,lw=.4)
    ax.set_yticks(y,labels,fontsize=8); ax.invert_yaxis(); ax.set_xlim(0,100)
    for yi,v in zip(y,values): ax.text(v+2,yi,str(v),va="center",fontsize=8,color=INK,fontweight="bold")
    ax.axvline(35,color=GOLD,lw=1,ls="--"); ax.axvline(70,color=RUST,lw=1,ls="--")
    ax.text(35,-.75,"approval begins",ha="center",fontsize=7,color=GOLD); ax.text(70,-.75,"dual control",ha="center",fontsize=7,color=RUST)
    ax.spines[["top","right","left"]].set_visible(False); ax.tick_params(axis="x",labelsize=7,colors=MUTED); ax.grid(axis="x",color=LINE,lw=.6)
    save(fig, 9)


def f10():
    fig, ax = setup(10, "Action-level risk model", "Example weighting for a commercial commitment action")
    ax.text(50,79,"R = I × (0.30U + 0.25V + 0.20S + 0.15T + 0.10C)",ha="center",fontsize=15,color=INK,fontweight="bold",family="monospace")
    ax.text(50,70,"impact × uncertainty, irreversibility, scope, time pressure, and control weakness",ha="center",fontsize=8,color=MUTED)
    factors=[("Evidence uncertainty",30,72),("Irreversibility",25,86),("Resource scope",20,64),("Time pressure",15,78),("Control weakness",10,35)]
    for i,(name,weight,score) in enumerate(factors):
        y=55-i*10
        ax.text(5,y,name,va="center",fontsize=8,color=INK)
        ax.plot([30,82],[y,y],color=LINE,lw=8,solid_capstyle="round")
        ax.plot([30,30+(52*score/100)],[y,y],color=TEAL if score<70 else GOLD,lw=8,solid_capstyle="round")
        ax.text(86,y,f"{weight}% × {score}",va="center",fontsize=8,color=MUTED,family="monospace")
    ax.add_patch(FancyBboxPatch((73,5),21,14,boxstyle="round,pad=.02",facecolor=RUST_LIGHT,edgecolor=RUST))
    ax.text(83.5,12,"ACTION RISK 81 / 100",ha="center",va="center",fontsize=9,color=RUST,fontweight="bold")
    save(fig, 10)


def f11():
    rng=np.random.default_rng(42)
    fig, ax = setup(11, "Modeled loss distributions", "10,000 synthetic escalations per control mode; loss shown in $000", plot=True)
    fig.subplots_adjust(left=0.11, right=0.96, top=0.78, bottom=0.15)
    role=np.clip(rng.lognormal(4.15,.75,10000),0,650)
    approval=np.clip(rng.lognormal(3.55,.58,10000),0,650)
    leased=np.clip(rng.lognormal(3.18,.48,10000),0,650)
    bins=np.linspace(0,500,55)
    ax.hist(role,bins=bins,density=True,histtype="step",lw=2,color=RUST,label="standing role")
    ax.hist(approval,bins=bins,density=True,histtype="step",lw=2,color=GOLD,label="approval only")
    ax.hist(leased,bins=bins,density=True,histtype="step",lw=2,color=TEAL,label="approval + leased permission")
    for arr,color,name,y in [(role,RUST,"standing role",.010),(approval,GOLD,"approval",.007),(leased,TEAL,"leased",.004)]:
        p95=np.percentile(arr,95); ax.axvline(p95,color=color,lw=1,ls="--"); ax.text(p95+4,y,f"p95 ${p95:.0f}k",fontsize=7,color=color,rotation=90,va="bottom")
    ax.set_xlabel("modeled loss per escalation ($000)",fontsize=8); ax.set_ylabel("density",fontsize=8); ax.set_xlim(0,500)
    ax.legend(frameon=False,fontsize=7,ncol=3,loc="upper right"); ax.grid(axis="y",color=LINE,lw=.5); ax.spines[["top","right"]].set_visible(False); ax.tick_params(labelsize=7)
    save(fig, 11)


def f12():
    fig, ax = setup(12, "Confidence threshold trade-off", "Synthetic decision set of 50,000 CRM proposals", plot=True)
    threshold=np.linspace(.50,.98,25)
    automation=92*(1-(threshold-.5)/.55)**1.35
    exception=8.8*np.exp(-6*(threshold-.5))+.35
    ax.plot(threshold,automation,color=TEAL,lw=2.4,marker="o",ms=3,label="auto-decision rate")
    ax.set_ylabel("auto-decision rate (%)",color=TEAL,fontsize=8); ax.set_xlabel("model confidence threshold",fontsize=8)
    ax.tick_params(axis="y",labelcolor=TEAL,labelsize=7); ax.tick_params(axis="x",labelsize=7); ax.set_ylim(0,100)
    ax2=ax.twinx(); ax2.plot(threshold,exception,color=RUST,lw=2.4,ls="--",marker="s",ms=3,label="exception rate")
    ax2.set_ylabel("material exception rate (%)",color=RUST,fontsize=8); ax2.tick_params(axis="y",labelcolor=RUST,labelsize=7); ax2.set_ylim(0,10)
    ax.axvline(.84,color=GOLD,lw=1.2,ls=":"); ax.text(.842,88,"example threshold",fontsize=7,color=GOLD,rotation=90,va="top")
    ax.grid(axis="y",color=LINE,lw=.5); ax.spines["top"].set_visible(False); ax2.spines["top"].set_visible(False)
    save(fig, 12)


def f13():
    fig, ax = setup(13, "Human approval policy matrix", "Required approval mode by action and commercial exposure", plot=True)
    fig.subplots_adjust(left=0.22, right=0.96, top=0.78, bottom=0.16)
    data=np.array([[0,0,0,1],[0,0,1,1],[0,1,1,2],[1,1,2,2],[1,2,2,3],[2,2,3,3]])
    from matplotlib.colors import ListedColormap
    cmap=ListedColormap([TEAL_LIGHT,BLUE_LIGHT,GOLD_LIGHT,RUST_LIGHT])
    ax.imshow(data,cmap=cmap,vmin=0,vmax=3,aspect="auto")
    rows=["create task","draft plan","schedule meeting","send email","service credit","discount / terms"]
    cols=["< $25k","$25k–100k","$100k–500k","> $500k"]
    labels=["auto","logged","single approval","dual approval"]
    ax.set_xticks(range(4),cols,fontsize=8); ax.set_yticks(range(6),rows,fontsize=8)
    for i in range(6):
        for j in range(4): ax.text(j,i,labels[data[i,j]],ha="center",va="center",fontsize=7,color=INK,fontweight="bold")
    ax.tick_params(length=0); [s.set_visible(False) for s in ax.spines.values()]
    save(fig, 13)


def f14():
    fig, ax = setup(14, "Maker-checker approval flow", "Separation of proposal, approval, credential issuance, and execution")
    lanes=[("Agent",78),("Account owner",58),("Deal desk",38),("Control services",18)]
    for name,y in lanes:
        ax.text(3,y,name,fontsize=8,color=INK,fontweight="bold",va="center")
        ax.plot([20,96],[y,y],color=LINE,lw=.8)
    events=[(24,78,"propose"),(38,58,"validate facts"),(52,38,"approve limits"),(67,18,"issue lease"),(81,78,"request action"),(92,18,"execute + verify")]
    colors=[TEAL,BLUE,GOLD,TEAL,TEAL,RUST]
    for (x,y,label),color in zip(events,colors):
        ax.add_patch(Circle((x,y),2.4,facecolor=color,edgecolor=WHITE,lw=1))
        ax.text(x,y+6,label,ha="center",fontsize=7,color=color,fontweight="bold")
    for a,b in zip(events[:-1],events[1:]): arrow(ax,(a[0]+2.5,a[1]),(b[0]-2.5,b[1]),color=MUTED,connectionstyle="arc3,rad=-.05")
    ax.text(59,4,"No actor can both propose and self-approve a high-impact commercial commitment.",ha="center",fontsize=8,color=MUTED)
    save(fig, 14)


def f15():
    fig, ax = setup(15, "Approval latency trade-off", "Modeled expected loss per escalation by review time", plot=True)
    minutes=np.linspace(1,180,60)
    rush=190*np.exp(-minutes/22)+12
    delay=8+0.0038*(minutes**2)
    total=rush+delay
    ax.plot(minutes,rush,color=RUST,lw=2,label="rushed-decision loss")
    ax.plot(minutes,delay,color=BLUE,lw=2,ls="--",label="delay / deal loss")
    ax.plot(minutes,total,color=INK,lw=2.7,label="combined expected loss")
    optimum=minutes[np.argmin(total)]; ax.axvline(optimum,color=GOLD,lw=1.2,ls=":")
    ax.text(optimum+4,min(total)+8,f"modeled minimum ≈ {optimum:.0f} min",fontsize=7,color=GOLD)
    ax.set_xlabel("approval turnaround (minutes)",fontsize=8); ax.set_ylabel("expected loss ($000)",fontsize=8)
    ax.legend(frameon=False,fontsize=7,ncol=3); ax.grid(color=LINE,lw=.5); ax.spines[["top","right"]].set_visible(False); ax.tick_params(labelsize=7)
    save(fig, 15)


def f16():
    fig, ax = setup(16, "Approval packet design", "The minimum decision surface for a $2.4M escalation")
    box(ax,4,14,57,68,"PROPOSED ACTION","12% renewal discount · 36-month term\nOne quote · expires in 20 minutes",color=SURFACE,edge=LINE,title_color=TEAL)
    items=[("Evidence delta","usage −23% · 2 P1 incidents"),("Conflicts","positive notes vs declining telemetry"),("Modeled range","$0–$288k concession exposure"),("Guardrails","margin ≥ 58% · no auto-renew change"),("Recovery","void quote · restore v18 · notify owner")]
    for i,(k,v) in enumerate(items):
        y=63-i*9
        ax.text(8,y,k,fontsize=7,color=MUTED,fontweight="bold")
        ax.text(26,y,v,fontsize=7.5,color=INK)
    box(ax,66,55,29,27,"DECISION","Approve · step up · deny",color="#EEF4F2",edge=TEAL_LIGHT,title_color=TEAL)
    box(ax,66,14,29,32,"APPROVAL","Account owner + deal desk\nReason code required\nSLA: 45 minutes",color="#FBF3E4",edge=GOLD_LIGHT,title_color=GOLD)
    save(fig, 16)


def f17():
    fig, ax = setup(17, "Authority envelope", "Transaction-level authority carried with the action")
    fields=[("Principal","account-owner-184"),("Actor","crm-agent-prod"),("Action","approve_discount"),("Resource","quote-771 / account-42"),("Purpose","renewal retention"),("Limits","≤12%; margin ≥58%"),("Time","20-minute lease"),("Tool","pricing.commit.v2"),("Evidence","bundle-9d3 / policy-44")]
    for i,(k,v) in enumerate(fields):
        col=i%3; row=i//3; x=3+col*32; y=61-row*23
        box(ax,x,y,29,18,k,wrap(v,26),color=SURFACE,edge=TEAL_LIGHT if i in [0,1,2,3] else LINE,title_color=TEAL if i in [0,1,2,3] else INK)
    ax.text(50,7,"The envelope is a design pattern, not a standard. Standards supply several of its fields.",ha="center",fontsize=8,color=MUTED)
    save(fig, 17)


def f18():
    fig, ax = setup(18, "Permission scope lattice", "Each layer removes authority before the tool can act")
    levels=[
        (7,72,86,15,"Standing CRM role","read/write across accounts · persistent"),
        (14,52,72,14,"Tool capability","pricing.commit only"),
        (22,33,56,13,"Resource scope","quote-771 · account-42"),
        (31,15,38,12,"Transaction lease","≤12% · 20 min · one use"),
    ]
    colors=[RUST_LIGHT,GOLD_LIGHT,BLUE_LIGHT,TEAL_LIGHT]
    for (x,y,w,h,t,b),c in zip(levels,colors):
        box(ax,x,y,w,h,t,b,color=c,edge=INK,title_color=INK,radius=.012)
    for y in [72,52,33]: arrow(ax,(50,y),(50,y-4),color=INK)
    ax.text(94,80,"broad",ha="right",fontsize=7,color=RUST); ax.text(69,9,"narrow",ha="center",fontsize=7,color=TEAL)
    save(fig, 18)


def f19():
    fig, ax = setup(19, "Permission lease lifecycle", "A short-lived, single-purpose credential for one transaction")
    stages=[("request",8,TEAL),("evaluate",25,BLUE),("approve",42,GOLD),("issue",59,TEAL),("use once",76,INK),("verify + revoke",92,RUST)]
    ax.plot([8,92],[48,48],color=LINE,lw=5,solid_capstyle="round")
    for i,(name,x,color) in enumerate(stages):
        ax.add_patch(Circle((x,48),4.2,facecolor=color,edgecolor=WHITE,lw=1.5))
        ax.text(x,61 if i%2==0 else 31,name,ha="center",fontsize=8,color=color,fontweight="bold")
        detail=["intent + evidence","policy decision","human reason","audience + TTL","tool-bound call","before/after proof"][i]
        ax.text(x,56 if i%2==0 else 39,wrap(detail,15),ha="center",fontsize=6.7,color=MUTED)
    ax.add_patch(FancyBboxPatch((58,6),36,10,boxstyle="round,pad=.02",facecolor="#EEF4F2",edgecolor=TEAL_LIGHT))
    ax.text(76,11,"expiry is a fallback; verified revocation is the target",ha="center",va="center",fontsize=7.2,color=TEAL,fontweight="bold")
    save(fig, 19)


def f20():
    fig, ax = setup(20, "TTL and scope exposure", "Modeled concession exposure ($000) for one credential", plot=True)
    fig.subplots_adjust(left=0.18, right=0.96, top=0.78, bottom=0.16)
    ttl=np.array([1,5,15,60,240]); scope=np.array([1,5,25,100])
    data=np.outer(scope**.72, (ttl/5+1)**.58)*18
    im=ax.imshow(data,cmap="YlOrBr",aspect="auto")
    ax.set_xticks(range(len(ttl)),[f"{x}m" for x in ttl],fontsize=8); ax.set_yticks(range(len(scope)),[f"{x} account"+("s" if x>1 else "") for x in scope],fontsize=8)
    ax.set_xlabel("credential lifetime",fontsize=8); ax.set_ylabel("resource scope",fontsize=8)
    for i in range(data.shape[0]):
        for j in range(data.shape[1]): ax.text(j,i,f"${data[i,j]:.0f}k",ha="center",va="center",fontsize=7,color=WHITE if data[i,j]>180 else INK,fontweight="bold")
    ax.tick_params(length=0); [s.set_visible(False) for s in ax.spines.values()]
    save(fig, 20)


def f21():
    fig, ax = setup(21, "Delegated token exchange", "Subject and actor remain distinct across the tool boundary")
    actors=[("Human principal",10),("CRM agent",31),("Authorization service",54),("Pricing tool",78),("Receipt store",94)]
    for name,x in actors:
        ax.add_patch(Circle((x,77),3.2,facecolor=TEAL if x<40 else GOLD if x<70 else INK,edgecolor=WHITE,lw=1))
        ax.text(x,68,wrap(name,15),ha="center",fontsize=7.5,color=INK,fontweight="bold")
        ax.plot([x,x],[64,12],color=LINE,lw=.8,ls="--")
    messages=[(10,31,57,"intent + subject token"),(31,54,46,"actor token + authorization_details"),(54,31,35,"leased token: sub + act + aud + exp"),(31,78,24,"commit quote with sender-bound token"),(78,94,14,"result + before/after hash")]
    for a,b,y,label in messages:
        arrow(ax,(a,y),(b,y),color=TEAL if b>a else GOLD,lw=1.2)
        ax.text((a+b)/2,y+3,wrap(label,28),ha="center",fontsize=6.5,color=INK)
    save(fig, 21)


def f22():
    fig, ax = setup(22, "Pre-action verification gates", "Every gate must pass before the write endpoint becomes reachable")
    gates=[("1","Evidence","fresh · sourced"),("2","Policy","action allowed"),("3","Approval","right approvers"),("4","Lease","scope + TTL"),("5","Preconditions","quote v18 · margin"),("6","Execute","one call")]
    for i,(n,t,b) in enumerate(gates):
        x=2+i*16.2
        color=TEAL if i<5 else INK
        box(ax,x,39,14,31,t,b,color=SURFACE,edge=color,title_color=color)
        ax.add_patch(Circle((x+7,77),3.3,facecolor=color,edgecolor=WHITE,lw=1))
        ax.text(x+7,77,n,ha="center",va="center",fontsize=8,color=WHITE,fontweight="bold")
        if i<5: arrow(ax,(x+14,54.5),(x+16.2,54.5),color=MUTED)
    ax.text(50,22,"Mismatch at any gate → deny or step up; never “best effort” a commercial write.",ha="center",fontsize=8,color=RUST,fontweight="bold")
    save(fig, 22)


def f23():
    fig, ax = setup(23, "Post-action verification loop", "The control objective is verified business state, not HTTP 200")
    nodes=[("Propose",50,80,TEAL),("Authorize",79,63,GOLD),("Execute",79,32,INK),("Observe",50,15,BLUE),("Compare",21,32,GOLD),("Receipt",21,63,TEAL)]
    for name,x,y,color in nodes:
        ax.add_patch(Circle((x,y),8,facecolor=SURFACE,edgecolor=color,lw=2))
        ax.text(x,y,name,ha="center",va="center",fontsize=8,color=color,fontweight="bold")
    for (a,b) in zip(nodes,nodes[1:]+nodes[:1]): arrow(ax,(a[1],a[2]),(b[1],b[2]),color=MUTED,lw=1.3,connectionstyle="arc3,rad=-.12")
    box(ax,39,39,22,21,"VERIFY","quote version\nprice · margin · term",color="#EEF4F2",edge=TEAL_LIGHT,title_color=TEAL)
    ax.text(50,5,"If observed state differs from intent, trigger containment and recovery.",ha="center",fontsize=8,color=RUST)
    save(fig, 23)


def f24():
    fig, ax = setup(24, "Action receipt schema", "Append-only record that can reconstruct one consequential decision")
    sections=[
        ("Intent",["request_id","principal","business purpose"]),
        ("Authority",["actor","approval","credential ID + expiry"]),
        ("Decision",["policy version","risk score","allow / step-up / deny"]),
        ("Execution",["tool + resource","request hash","response hash"]),
        ("Verification",["before state","after state","invariants"]),
        ("Recovery",["revoke pointer","compensation","incident ID"]),
    ]
    for i,(title,fields) in enumerate(sections):
        col=i%3; row=i//3; x=3+col*32; y=53-row*37
        box(ax,x,y,29,30,title,"\n".join(fields),color=SURFACE,edge=TEAL_LIGHT if row==0 else GOLD_LIGHT,title_color=TEAL if row==0 else GOLD)
    ax.text(50,7,"receipt_id · trace_id · account_id · immutable timestamp · schema version",ha="center",fontsize=8,color=MUTED,family="monospace")
    save(fig, 24)


def f25():
    fig, ax = setup(25, "End-to-end observability trace", "One synthetic trace across planning, control, execution, and verification", plot=True)
    fig.subplots_adjust(left=0.21, right=0.96, top=0.78, bottom=0.15)
    spans=[("ingest signals",0,55,TEAL),("assemble evidence",12,68,BLUE),("plan options",26,46,TEAL),("policy evaluate",39,24,GOLD),("human approval",48,780,GOLD),("issue lease",835,18,TEAL),("tool execute",858,42,INK),("verify state",905,58,BLUE),("write receipt",970,22,TEAL)]
    y=np.arange(len(spans))[::-1]
    for yi,(name,start,duration,color) in zip(y,spans):
        ax.barh(yi,duration,left=start,height=.55,color=color,edgecolor=INK,lw=.3)
        ax.text(start+duration+8,yi,f"{duration} ms",va="center",fontsize=6.8,color=MUTED)
    ax.set_yticks(y,[s[0] for s in spans],fontsize=7.5); ax.set_xlabel("elapsed time (ms)",fontsize=8); ax.set_xlim(0,1040)
    ax.grid(axis="x",color=LINE,lw=.5); ax.spines[["top","right","left"]].set_visible(False); ax.tick_params(axis="x",labelsize=7)
    ax.text(1015,8.7,"trace_id: 6fa2…9c1",ha="right",fontsize=7,color=INK,family="monospace")
    save(fig, 25)


def f26():
    fig, ax = setup(26, "Failure-mode risk matrix", "Illustrative likelihood × impact before production controls", plot=True)
    fig.subplots_adjust(left=0.18, right=0.96, top=0.78, bottom=0.16)
    grid=np.add.outer(np.arange(1,6),np.arange(1,6))
    from matplotlib.colors import LinearSegmentedColormap
    cmap=LinearSegmentedColormap.from_list("risk",[TEAL_LIGHT,GOLD_LIGHT,RUST_LIGHT])
    ax.imshow(grid,cmap=cmap,vmin=2,vmax=10,origin="lower")
    ax.set_xticks(range(5),["rare","unlikely","possible","likely","frequent"],fontsize=7)
    ax.set_yticks(range(5),["minor","moderate","material","major","severe"],fontsize=7)
    ax.set_xlabel("likelihood",fontsize=8); ax.set_ylabel("impact",fontsize=8)
    failures=[(3,4,"over-broad\ncredential"),(2,4,"wrong quote\nversion"),(4,3,"approval\nbypass"),(2,3,"stale\nevidence"),(1,4,"failed\nrollback"),(3,2,"duplicate\nexecution")]
    for x,y,label in failures:
        ax.scatter(x,y,s=150,facecolor=SURFACE,edgecolor=INK,lw=1.2)
        ax.text(x,y,label,ha="center",va="center",fontsize=6.5,color=INK,fontweight="bold")
    ax.tick_params(length=0); [s.set_visible(False) for s in ax.spines.values()]
    save(fig, 26)


def f27():
    fig, ax = setup(27, "Containment stack", "Illustrative reduction in reachable commercial exposure")
    stages=[("Standing CRM role",2400,RUST),("Tool allowlist",920,GOLD),("One account",410,BLUE),("Amount cap",288,GOLD),("20-minute TTL",102,TEAL),("One-use + verification",36,TEAL)]
    maxv=2400
    for i,(name,value,color) in enumerate(stages):
        y=78-i*13
        ax.text(3,y,name,va="center",fontsize=8,color=INK)
        ax.add_patch(FancyBboxPatch((30,y-4.2),60,8.4,boxstyle="round,pad=.01",facecolor="#ECE8DE",edgecolor="none"))
        ax.add_patch(FancyBboxPatch((30,y-4.2),60*value/maxv,8.4,boxstyle="round,pad=.01",facecolor=color,edgecolor="none"))
        ax.text(93,y,f"${value:,.0f}k",va="center",ha="right",fontsize=8,color=color,fontweight="bold",family="monospace")
        if i<len(stages)-1: ax.text(27,y-7,"↓",ha="center",fontsize=8,color=MUTED)
    ax.text(50,5,"Modeled reachable exposure; controls are intentionally independent and cumulative.",ha="center",fontsize=8,color=MUTED)
    save(fig, 27)


def f28():
    fig, ax = setup(28, "Recovery state machine", "Designed recovery path for a verified mismatch or control failure")
    states=[("Detected",10,58,BLUE),("Freeze",27,58,RUST),("Revoke",44,58,RUST),("Compensate",61,58,GOLD),("Reconcile",78,58,TEAL),("Close",94,58,INK)]
    for i,(name,x,y,color) in enumerate(states):
        ax.add_patch(Circle((x,y),6.2,facecolor=SURFACE,edgecolor=color,lw=2))
        ax.text(x,y,name,ha="center",va="center",fontsize=7.5,color=color,fontweight="bold")
        if i<len(states)-1: arrow(ax,(x+6.5,y),(states[i+1][1]-6.5,y),color=MUTED)
    annotations=[("state mismatch",10),("block writes",27),("kill lease",44),("restore quote",61),("ledger + CRM",78),("owner sign-off",94)]
    for text,x in annotations: ax.text(x,36,wrap(text,13),ha="center",fontsize=6.7,color=MUTED)
    arrow(ax,(78,66),(27,66),color=RUST,connectionstyle="arc3,rad=.22")
    ax.text(52.5,83,"reopen on reconciliation failure",ha="center",fontsize=7,color=RUST)
    save(fig, 28)


def f29():
    fig, ax = setup(29, "Operational reconciliation view", "Synthetic daily operating metrics for the CRM agent control plane")
    cards=[("1,842","proposals"),("37%","auto-safe"),("9.4%","stepped up"),("99.7%","receipt complete")]
    for i,(v,l) in enumerate(cards): box(ax,3+i*24,68,21,18,v,l,color=SURFACE,edge=LINE,title_color=TEAL if i!=2 else GOLD)
    ax.text(5,58,"Approval turnaround (minutes)",fontsize=8,color=INK,fontweight="bold")
    vals=[22,31,44,68]; labs=["p50","p75","p90","p95"]
    for i,(lab,v) in enumerate(zip(labs,vals)):
        y=49-i*8; ax.text(5,y,lab,fontsize=7,color=MUTED); ax.plot([16,50],[y,y],color=LINE,lw=5,solid_capstyle="round"); ax.plot([16,16+34*v/80],[y,y],color=BLUE,lw=5,solid_capstyle="round"); ax.text(53,y,str(v),fontsize=7,color=INK,va="center")
    ax.text(62,58,"Verification outcomes",fontsize=8,color=INK,fontweight="bold")
    outcomes=[("matched",94.8,TEAL),("reconciled",4.6,GOLD),("contained",.6,RUST)]
    for i,(lab,v,c) in enumerate(outcomes):
        y=48-i*11; ax.text(62,y,lab,fontsize=7.5,color=INK); ax.text(93,y,f"{v:.1f}%",ha="right",fontsize=8,color=c,fontweight="bold")
    ax.add_patch(FancyBboxPatch((61,12),33,8,boxstyle="round,pad=.01",facecolor=TEAL_LIGHT,edgecolor="none"))
    ax.add_patch(FancyBboxPatch((61,12),33*.052,8,boxstyle="round,pad=.01",facecolor=GOLD,edgecolor="none"))
    ax.add_patch(FancyBboxPatch((61,12),33*.006,8,boxstyle="round,pad=.01",facecolor=RUST,edgecolor="none"))
    save(fig, 29)


def f30():
    fig, ax = setup(30, "Production rollout roadmap", "Autonomy expands only after control evidence meets explicit gates")
    phases=[
        (3,"1 · Observe","shadow decisions\nno tool writes","evidence ≥95%\ntrace ≥99%",BLUE),
        (27,"2 · Recommend","human executes\nagent explains","override stable\nno critical gaps",TEAL),
        (51,"3 · Bounded act","low-impact writes\nleased permissions","receipt ≥99.5%\nrecovery tested",GOLD),
        (75,"4 · Scale","selected actions\ncontinuous evaluation","loss within tolerance\nquarterly review",INK),
    ]
    for x,title,scope,gate,color in phases:
        box(ax,x,34,21,46,title,scope,color=SURFACE,edge=color,title_color=color)
        ax.add_patch(FancyBboxPatch((x+2,15),17,12,boxstyle="round,pad=.02",facecolor="#EEF4F2",edgecolor=LINE))
        ax.text(x+10.5,21,"GATE\n"+gate,ha="center",va="center",fontsize=6.6,color=INK,fontweight="bold")
    for x in [24,48,72]: arrow(ax,(x,57),(x+3,57),color=MUTED)
    ax.text(50,7,"Promotion is reversible. A missed control target moves the action class back one phase.",ha="center",fontsize=8,color=RUST)
    save(fig, 30)


FUNCTIONS=[f01,f02,f03,f04,f05,f06,f07,f08,f09,f10,f11,f12,f13,f14,f15,f16,f17,f18,f19,f20,f21,f22,f23,f24,f25,f26,f27,f28,f29,f30]


def write_chart_map() -> None:
    MAP_PATH.parent.mkdir(parents=True, exist_ok=True)
    lines=[
        "# Figure map — A $2.4M Account Is Escalating. Should the AI Agent Act?",
        "",
        "All quantitative values are synthetic scenario data. Diagrams are production design patterns, not claims about a deployed system.",
        "",
        "Palette policy: two-root cap (teal and gold) with rust for high-risk exceptions, blue for evidence/observation, and neutral ink. Every distinction also uses position, label, shape, or line style.",
        "",
        "| Figure | Analytical question | Form | Supported takeaway |",
        "|---:|---|---|---|",
    ]
    for number,title,form,takeaway in FIGURE_META:
        lines.append(f"| {number} | {title} | {form} | {takeaway} |")
    lines += ["", "Renderer: reproducible Matplotlib PNG, 1600×900. Final QA surface: responsive GitHub Pages article and mobile viewport.", ""]
    MAP_PATH.write_text("\n".join(lines),encoding="utf-8")


def main() -> None:
    plt.rcParams.update({
        "font.family":"DejaVu Sans", "axes.labelcolor":INK, "text.color":INK,
        "axes.edgecolor":LINE, "xtick.color":MUTED, "ytick.color":MUTED,
    })
    for fn in FUNCTIONS:
        fn()
    write_chart_map()
    print(f"generated {len(FUNCTIONS)} figures in {OUT}")


if __name__ == "__main__":
    main()
