#!/usr/bin/env python3
"""Generate reproducible figures for the just-in-time permission lease story."""

from __future__ import annotations

import math
import textwrap
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.colors import LinearSegmentedColormap, ListedColormap
from matplotlib.patches import Circle, FancyArrowPatch, FancyBboxPatch, Rectangle


ROOT = Path(__file__).resolve().parents[1]
SLUG = "your-ai-agent-should-not-have-a-standing-role"
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
WHITE = "#FFFFFF"


FIGURE_META = [
    (1, "Permission model comparison", "Scorecard", "A standing role preserves broad authority between decisions; a lease exists only for one bounded action."),
    (2, "Standing-role attack graph", "Architecture diagram", "One reusable credential creates multiple reachable resources and mutation paths."),
    (3, "Just-in-time lease control plane", "Architecture diagram", "Decision inputs authorize issuance; the protected API consumes, enforces, verifies, and recovers."),
    (4, "Authority narrowing path", "Stage progression", "Each control step removes unused resources, actions, values, time, and repetitions."),
    (5, "Permission lease envelope", "Structured schema", "A useful lease binds principal, actor, action, resource, limits, evidence, audience, proof key, time, and use count."),
    (6, "Lease lifecycle", "State machine", "Reservation, effect observation, ambiguity, verification, and recovery are explicit durable states."),
    (7, "Lease issuance sequence", "Sequence diagram", "The executor receives authority only after current policy and approval checks succeed."),
    (8, "Policy decision boundary", "PEP/PDP diagram", "The policy enforcement point asks an external decision service and enforces returned obligations."),
    (9, "Rich authorization mapping", "Field map", "Business intent is translated into structured authorization details instead of a coarse scope string."),
    (10, "Exposure model", "Formula decomposition", "Modeled exposure depends on reachable value, scope, duration, uses, propagation, and control effectiveness."),
    (11, "TTL and scope exposure", "Heatmap", "A declared sensitivity index rises when credential lifetime and resource breadth expand together."),
    (12, "Compromise opportunity by TTL", "Multi-series line", "Shorter leases reduce the probability that a compromise window overlaps valid authority."),
    (13, "Replay containment by token mode", "Grouped bar", "Audience binding, sender constraint, and one-use consumption reduce replay reach."),
    (14, "Blast-radius distribution", "Distribution", "Leased authority compresses the loss tail in a synthetic compromise simulation."),
    (15, "Audience and resource binding", "Reachability graph", "A lease valid for one resource server should fail at adjacent APIs."),
    (16, "Lease policy decision tree", "Decision tree", "High-risk actions require evidence, eligible approval, bounded values, and live preconditions."),
    (17, "Approval-to-lease binding", "Cryptographic binding diagram", "Digests prevent an approved proposal from being silently changed before issuance or execution."),
    (18, "Executor validation gates", "Stage progression", "Cryptographic, sender, authority, freshness, consumption, and effect gates are independently mandatory."),
    (19, "Concurrent-state race", "Timeline", "Optimistic concurrency prevents a valid lease from overwriting a newer human change."),
    (20, "Idempotent execution protocol", "Sequence diagram", "One action identifier makes retries safe and duplicate effects observable."),
    (21, "Action receipt chain", "Structured lineage", "The receipt joins intent, evidence, approval, lease, request, outcome, verification, and recovery."),
    (22, "Failure-mode control matrix", "Heatmap", "No single control covers theft, replay, stale context, over-scope, duplication, and downstream divergence."),
    (23, "End-to-end latency budget", "Stage bars with cumulative line", "Direct stage budgets reveal where the control-path objective is spent."),
    (24, "Lease control-plane objectives", "Target-versus-actual scorecard", "Every operating objective needs a target, actual result, and visible pass or breach state."),
    (25, "Permission-lease rollout", "Maturity roadmap", "Teams should remove standing privilege action class by action class behind promotion gates."),
]

CORE_FIGURES = {1, 3, 5, 6, 7, 11, 15, 18, 20, 21, 22, 23, 25}
FIGURE_ASSUMPTIONS = {
    4: "Synthetic reachable-surface stages: 100, 52, 31, 12, 5.5, 1.6, 0.35 percent.",
    10: "Illustrative V=USD 2.4M, S=.05, U=1, P=1.2, C=.70; output USD 43.2k.",
    11: "Index = sqrt(records) × (TTL/30s)^.55, normalized to 100 at 100 records and 60 minutes.",
    12: "Poisson opportunity rates per second: 1/7200, 1/1800, 1/450.",
    13: "Fixed scenario indexes; bearer baseline = 100. Values are not observed calls.",
    14: "Seed 21; 20,000 lognormal draws per model; parameters are declared in the story.",
    18: "Reference gate contract only; no pass-rate or production-volume claim.",
    23: "Synthetic p95 stage budgets in ms: 12, 28, 18, 42, 6, 110, 75, 16; total 307.",
    24: "Synthetic 30-day targets and actuals; one deliberate verification-mismatch breach.",
}


def wrap(value: str, width: int = 22) -> str:
    return "\n".join(textwrap.wrap(value, width=width))


def setup(number: int, title: str, subtitle: str, plot: bool = False):
    fig, ax = plt.subplots(figsize=(10, 5.625), dpi=160)
    fig.patch.set_facecolor(PAPER)
    ax.set_facecolor(PAPER)
    fig.subplots_adjust(left=0.08, right=0.96, top=0.78, bottom=0.13)
    fig.text(0.08, 0.935, f"FIGURE {number:02d}", color=TEAL, fontsize=8, fontweight="bold")
    fig.text(0.08, 0.87, title, color=INK, fontsize=20, fontweight="bold")
    fig.text(0.08, 0.82, subtitle, color=MUTED, fontsize=9)
    fig.text(0.96, 0.035, "Illustrative reference design · synthetic values · not production data", ha="right", color=MUTED, fontsize=6.8)
    if not plot:
        ax.set_xlim(0, 100)
        ax.set_ylim(0, 100)
        ax.axis("off")
    return fig, ax


def save(fig, number: int) -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    fig.savefig(OUT / f"figure-{number:02d}.png", facecolor=PAPER, dpi=160)
    plt.close(fig)


def box(ax, x, y, w, h, title, body="", color=SURFACE, edge=LINE, title_color=INK, lw=1.1):
    patch = FancyBboxPatch((x, y), w, h, boxstyle="round,pad=.015,rounding_size=.02", facecolor=color, edgecolor=edge, linewidth=lw)
    ax.add_patch(patch)
    ax.text(x + w * .06, y + h * .66, title, color=title_color, fontsize=9.2, fontweight="bold", va="center")
    if body:
        ax.text(x + w * .06, y + h * .30, body, color=MUTED, fontsize=7, va="center", linespacing=1.35)
    return patch


def arrow(ax, start, end, color=MUTED, lw=1.35, style="-|>", connectionstyle="arc3"):
    ax.add_patch(FancyArrowPatch(start, end, arrowstyle=style, mutation_scale=11, color=color, linewidth=lw, connectionstyle=connectionstyle))


def f01():
    fig, ax = setup(1, "Permission model comparison", "Same agent and action; different authority persistence")
    columns = [(4, "STANDING ROLE", RUST, ["valid for 8 hours", "all enterprise accounts", "quote + contact + export", "unbounded repetitions"]),
               (52, "PERMISSION LEASE", TEAL, ["valid for 90 seconds", "one account + quote", "one approved field delta", "one consumable use"])]
    for x, title, color, rows in columns:
        box(ax, x, 14, 44, 69, title, "", color=SURFACE, edge=color, title_color=color, lw=1.5)
        for i, row in enumerate(rows):
            y = 50 - i * 11
            ax.add_patch(Circle((x + 6, y), 2.2, facecolor=color if x > 50 else RUST_LIGHT, edgecolor=color, lw=1))
            ax.text(x + 11, y, row, va="center", fontsize=8, color=INK)
    ax.text(50, 5, "Authority should be created by the decision—not inherited from the runtime.", ha="center", fontsize=8, color=INK, fontweight="bold")
    save(fig, 1)


def f02():
    fig, ax = setup(2, "Standing-role attack graph", "Reachable mutations after one reusable credential is exposed")
    box(ax, 3, 42, 21, 22, "COMPROMISED AGENT", "prompt injection\nor runtime breach", color=RUST_LIGHT, edge=RUST, title_color=RUST)
    box(ax, 31, 42, 19, 22, "STANDING TOKEN", "crm.enterprise.write\n8-hour lifetime", edge=RUST, title_color=RUST)
    arrow(ax, (24, 53), (31, 53), color=RUST)
    targets = [(61, 69, "QUOTES", "price · term"), (80, 69, "CONTACTS", "email · phone"), (61, 30, "CASES", "status · credit"), (80, 30, "EXPORT", "accounts · notes")]
    for x, y, title, body in targets:
        box(ax, x, y, 16, 17, title, body, edge=RUST_LIGHT, title_color=RUST)
        arrow(ax, (50, 53), (x, y + 8), color=RUST, connectionstyle="arc3,rad=.08")
    ax.text(50, 8, "One secret crosses four resource families because the role was designed for a user session, not one agent action.", ha="center", fontsize=8, color=INK)
    save(fig, 2)


def f03():
    fig, ax = setup(3, "Just-in-time lease control plane", "Control plane issues bounded authority; data plane enforces and verifies it")
    layers = [(4, 63, 92, 20, "DECISION PLANE", BLUE_LIGHT, BLUE), (4, 35, 92, 20, "AUTHORITY PLANE", GOLD_LIGHT, GOLD), (4, 7, 92, 20, "EXECUTION PLANE", TEAL_LIGHT, TEAL)]
    for x, y, w, h, title, fill, edge in layers:
        ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=.01", facecolor=fill, edgecolor=edge, alpha=.32, linewidth=1.1))
        ax.text(x + 2, y + h - 3, title, color=edge, fontsize=7.5, fontweight="bold", va="top")
    boxes = [(8, 64, "Evidence", "digest + freshness", BLUE), (30, 64, "Policy", "allow + obligations", BLUE), (52, 64, "Risk", "action-level", BLUE), (74, 64, "Approval", "eligible principal", BLUE),
             (13, 36, "Consumption", "atomic one-use ledger", GOLD), (41, 36, "Bound lease", "aud + cnf + TTL + jti", GOLD), (69, 36, "Lease issuer", "sign governed claims", GOLD),
             (13, 8, "PEP", "validate + reserve", TEAL), (36, 8, "CRM API", "conditional mutation", TEAL), (59, 8, "Verifier", "read postcondition", TEAL), (80, 8, "Recovery", "freeze + compensate", TEAL)]
    for x, y, title, body, color in boxes:
        box(ax, x, y, 17, 12, title, body, color=SURFACE, edge=color, title_color=color)
    for a, b in [((25,70),(30,70)),((47,70),(52,70)),((69,70),(74,70)),((82,64),(78,48)),((69,42),(58,42)),((41,42),(30,42)),((49,36),(21,20)),((30,14),(36,14)),((53,14),(59,14)),((76,14),(80,14))]:
        arrow(ax, a, b, color=MUTED, lw=1)
    arrow(ax, (21, 20), (21, 36), color=MUTED, lw=1, style="<->")
    save(fig, 3)


def f04():
    fig, ax = setup(4, "Authority narrowing path", "Illustrative reachable authority after each independent restriction", plot=True)
    fig.subplots_adjust(left=.20, right=.96, top=.78, bottom=.15)
    stages = ["employee role", "agent action class", "one resource server", "one account", "one quote", "field + value bound", "90s + one use"]
    reachable = np.array([100, 52, 31, 12, 5.5, 1.6, .35])
    y = np.arange(len(stages))
    ax.barh(y, reachable, color=[RUST, GOLD, GOLD, BLUE, BLUE, TEAL, TEAL], edgecolor=INK, lw=.4)
    ax.set_yticks(y, stages, fontsize=8); ax.invert_yaxis(); ax.set_xlim(0, 105)
    for yi, value in zip(y, reachable): ax.text(value + 1.5, yi, f"{value:g}%", va="center", fontsize=8, color=INK, fontweight="bold")
    ax.set_xlabel("reachable mutation surface (% of standing role)", fontsize=8)
    ax.grid(axis="x", color=LINE, lw=.6); ax.spines[["top","right","left"]].set_visible(False); ax.tick_params(axis="x", labelsize=7, colors=MUTED)
    save(fig, 4)


def f05():
    fig, ax = setup(5, "Permission lease envelope", "Minimal transaction-bound authority object")
    fields = [("iss / aud", "trusted issuer · CRM API"), ("sub / act", "human principal · agent workload"), ("authorization_details", "action · resource · field delta"), ("constraints", "value cap · expected version"),
              ("evidence / approval", "digests bind the decision"), ("iat / nbf / exp", "90-second validity window"), ("cnf", "sender proof-key thumbprint"), ("jti / uses", "unique ID · one consumption")]
    for i, (name, value) in enumerate(fields):
        col, row = i % 2, i // 2
        x, y = 4 + col * 48, 67 - row * 16
        box(ax, x, y, 44, 13, name, value, edge=TEAL_LIGHT if col else GOLD_LIGHT, title_color=TEAL if col else GOLD)
    ax.text(50, 7, "A coarse role name is not enough information to authorize a consequential mutation.", ha="center", fontsize=8, color=INK, fontweight="bold")
    save(fig, 5)


def f06():
    fig, ax = setup(6, "Lease lifecycle", "Durable states separate no effect, observed effect, ambiguity, verification, and recovery")

    def state(x, y, w, label, color):
        ax.add_patch(FancyBboxPatch((x, y), w, 11, boxstyle="round,pad=.015", facecolor=SURFACE, edgecolor=color, linewidth=1.15))
        ax.text(x + w / 2, y + 5.5, label, ha="center", va="center", fontsize=6.2, color=color, fontweight="bold", linespacing=1.0)

    top = [
        (2, "REQUESTED", BLUE), (16, "EVALUATED", BLUE), (30, "APPROVED", GOLD),
        (44, "ISSUED", GOLD), (58, "RESERVED", TEAL), (72, "EFFECT\nOBSERVED", TEAL),
        (86, "VERIFIED", TEAL),
    ]
    for x, label, color in top:
        state(x, 57, 12, label, color)
    for x in [14, 28, 42, 56, 70, 84]:
        arrow(ax, (x, 62.5), (x + 2, 62.5), color=MUTED, lw=1)

    state(31, 28, 13, "EXPIRED", MUTED)
    state(45, 28, 13, "REVOKED", RUST)
    state(59, 28, 18, "FAILED BEFORE\nEFFECT", RUST)
    state(79, 28, 15, "AMBIGUOUS", GOLD)
    state(79, 9, 15, "RECOVERED", TEAL)
    arrow(ax, (50, 57), (37.5, 39), color=MUTED, lw=1)
    arrow(ax, (50, 57), (51.5, 39), color=MUTED, lw=1)
    arrow(ax, (64, 57), (68, 39), color=MUTED, lw=1)
    arrow(ax, (64, 57), (86.5, 39), color=MUTED, lw=1)
    arrow(ax, (86.5, 28), (86.5, 20), color=MUTED, lw=1)
    ax.text(3, 10, "No terminal state returns authority to active.", fontsize=7.2, color=RUST, fontweight="bold")
    save(fig, 6)


def f07():
    fig, ax = setup(7, "Lease issuance sequence", "One approved CRM mutation with separate subject and actor")
    actors = [(8,"Human"),(27,"Agent"),(46,"PDP"),(65,"Issuer"),(84,"CRM PEP")]
    for x,name in actors:
        ax.text(x,77,name,ha="center",fontsize=8,fontweight="bold",color=INK)
        ax.plot([x,x],[13,72],color=LINE,lw=1,ls="--")
    events = [(27,46,67,"evaluate action",BLUE),(46,27,58,"allow + obligations",BLUE),(27,8,49,"request approval",GOLD),(8,65,40,"approved digest",GOLD),(27,65,31,"exchange + proof key",TEAL),(65,27,22,"90s one-use lease",TEAL),(27,84,13,"execute + DPoP",INK)]
    for a,b,y,label,color in events:
        arrow(ax,(a,y),(b,y),color=color,lw=1.2)
        ax.text((a+b)/2,y+2,label,ha="center",fontsize=6.8,color=color)
    save(fig, 7)


def f08():
    fig, ax = setup(8, "Policy decision boundary", "Externalized authorization with obligations returned to the enforcement point")
    box(ax,4,40,19,25,"AGENT", "proposed action\n+ evidence digest",edge=BLUE,title_color=BLUE)
    box(ax,31,40,20,25,"PEP", "normalize request\nenforce response",edge=TEAL,title_color=TEAL)
    box(ax,60,40,20,25,"PDP", "policy + context\nallow / deny",edge=GOLD,title_color=GOLD)
    box(ax,84,40,12,25,"PIP", "roles\nlimits",edge=LINE,title_color=INK)
    arrow(ax,(23,52),(31,52),color=BLUE); arrow(ax,(51,57),(60,57),color=GOLD); arrow(ax,(84,52),(80,52),color=MUTED)
    arrow(ax,(60,46),(51,46),color=TEAL)
    ax.text(55,60,"subject · action · resource · context",ha="center",fontsize=6.8,color=GOLD)
    ax.text(55,42,"decision · reason · obligations",ha="center",fontsize=6.8,color=TEAL)
    box(ax,31,11,49,17,"OBLIGATIONS", "max_discount=8% · ttl≤90s · uses=1 · verify=quote.v19",color="#EEF4F2",edge=TEAL,title_color=TEAL)
    arrow(ax,(41,40),(52,28),color=TEAL)
    save(fig, 8)


def f09():
    fig, ax = setup(9, "Rich authorization mapping", "From business delta to structured authorization details")
    left=[("action","quote.discount.apply"),("resource","quote/771"),("field","discount_pct"),("from → to","0 → 8"),("purpose","renewal-retention")]
    right=[("type","crm_quote_change"),("locations",'["/accounts/42/quotes/771"]'),("actions",'["discount.apply"]'),("limits",'{"discount_pct":{"lte":8}}'),("expected_version","19")]
    box(ax,3,13,37,68,"BUSINESS INTENT","",edge=BLUE,title_color=BLUE)
    box(ax,60,13,37,68,"AUTHORIZATION_DETAILS","",edge=TEAL,title_color=TEAL)
    for i,((lk,lv),(rk,rv)) in enumerate(zip(left,right)):
        y=65-i*11
        ax.text(7,y,lk,fontsize=7,color=MUTED); ax.text(18,y,lv,fontsize=7.5,color=INK,fontfamily="monospace")
        ax.text(64,y,rk,fontsize=7,color=MUTED); ax.text(76,y,rv,fontsize=7,color=INK,fontfamily="monospace")
        arrow(ax,(40,y),(60,y),color=GOLD,lw=1)
    save(fig, 9)


def f10():
    fig, ax = setup(10, "Exposure model", "A deliberately conservative upper-bound model for one credential")
    ax.text(50,75,"B = V × S × U × P × (1 − C)",ha="center",fontsize=20,color=INK,fontweight="bold",fontfamily="monospace")
    terms=[("V","reachable value","$2.4M"),("S","normalized scope","0.05"),("U","permitted uses","1"),("P","propagation multiplier","1.2"),("C","effective containment","0.70")]
    for i,(symbol,name,value) in enumerate(terms):
        x=4+i*19
        box(ax,x,34,17,26,symbol,"",edge=TEAL_LIGHT if i<3 else GOLD_LIGHT,title_color=TEAL if i<3 else GOLD)
        ax.text(x+1.2,44,wrap(name,18),ha="left",va="center",fontsize=6.7,color=MUTED,linespacing=1.15)
        ax.text(x+8.5,37.5,value,ha="center",fontsize=8.2,color=INK,fontweight="bold")
    ax.text(50,17,"Illustrative bound: USD 2.4M × .05 × 1 × 1.2 × .30 = USD 43.2k",ha="center",fontsize=9.2,color=RUST,fontweight="bold",fontfamily="monospace")
    ax.text(50,8,"The formula is a routing model, not an actuarial claim; calibrate every term with your own loss data.",ha="center",fontsize=7.5,color=MUTED)
    save(fig, 10)


def f11():
    fig, ax = setup(11, "TTL and scope exposure", "Declared sensitivity index; 60m × 100 records is normalized to 100", plot=True)
    fig.subplots_adjust(left=.18,right=.96,top=.78,bottom=.16)
    ttls=np.array([30,60,90,300,900,3600])
    scopes=np.array([1,5,25,100])
    raw=np.outer(np.sqrt(scopes), (ttls/30)**.55)
    exposure=100*raw/raw.max()
    cmap=LinearSegmentedColormap.from_list("exp",["#EAF4F1",GOLD_LIGHT,RUST])
    ax.imshow(exposure,cmap=cmap,aspect="auto",vmin=0,vmax=exposure.max())
    ax.set_xticks(range(len(ttls)),["30s","60s","90s","5m","15m","60m"],fontsize=8)
    ax.set_yticks(range(len(scopes)),["1 record","5 records","25 records","100 records"],fontsize=8)
    for i in range(len(scopes)):
        for j in range(len(ttls)):
            ax.text(j,i,f"{exposure[i,j]:.1f}",ha="center",va="center",fontsize=7,color=WHITE if exposure[i,j]>.58*exposure.max() else INK,fontweight="bold")
    ax.set_xlabel("credential lifetime",fontsize=8); ax.set_ylabel("resource scope",fontsize=8); ax.tick_params(length=0)
    [s.set_visible(False) for s in ax.spines.values()]
    save(fig, 11)


def f12():
    fig, ax = setup(12, "Compromise opportunity by TTL", "Probability that an attacker window overlaps valid authority; Poisson arrival model", plot=True)
    ttl=np.linspace(1,3600,120)
    rates=[("low pressure",1/7200,TEAL,"-"),("elevated",1/1800,GOLD,"--"),("active compromise",1/450,RUST,"-")]
    for name,lam,color,ls in rates:
        p=1-np.exp(-lam*ttl)
        ax.plot(ttl/60,100*p,label=name,color=color,lw=2.2,ls=ls)
    for marker,label in [(1.5,"90s lease"),(15,"15m token"),(60,"60m role token")]:
        ax.axvline(marker,color=LINE,lw=1); ax.text(marker+1,75,label,rotation=90,fontsize=6.8,color=MUTED,va="top")
    ax.set_xlim(0,60); ax.set_ylim(0,100); ax.set_xlabel("validity window (minutes)",fontsize=8); ax.set_ylabel("overlap probability (%)",fontsize=8)
    ax.legend(frameon=False,fontsize=7,loc="upper left"); ax.grid(color=LINE,lw=.5); ax.spines[["top","right"]].set_visible(False); ax.tick_params(labelsize=7)
    save(fig, 12)


def f13():
    fig, ax = setup(13, "Replay containment by token mode", "Synthetic reachable API calls after one token is copied", plot=True)
    modes=["bearer + broad aud","audience bound","DPoP bound","DPoP + one-use lease"]
    same=[100,72,8,1]; adjacent=[100,4,1,0]; other_actor=[100,72,0,0]
    x=np.arange(len(modes)); w=.22
    ax.bar(x-w,same,w,label="same API",color=RUST,edgecolor=INK,lw=.4)
    ax.bar(x,adjacent,w,label="adjacent API",color=GOLD,edgecolor=INK,lw=.4)
    ax.bar(x+w,other_actor,w,label="different actor",color=TEAL,edgecolor=INK,lw=.4)
    ax.set_xticks(x,modes,fontsize=7); ax.set_ylabel("reachable calls (index; bearer = 100)",fontsize=8); ax.set_ylim(0,110)
    ax.legend(frameon=False,fontsize=7,ncol=3,loc="upper right"); ax.grid(axis="y",color=LINE,lw=.5); ax.spines[["top","right"]].set_visible(False); ax.tick_params(axis="y",labelsize=7)
    save(fig, 13)


def f14():
    rng=np.random.default_rng(21)
    fig, ax = setup(14, "Blast-radius distribution", "20,000 synthetic credential compromises per permission model; loss in $000", plot=True)
    standing=np.clip(rng.lognormal(5.05,.82,20000),0,1800)
    scoped=np.clip(rng.lognormal(4.15,.62,20000),0,1800)
    leased=np.clip(rng.lognormal(3.15,.48,20000),0,1800)
    bins=np.linspace(0,900,60)
    for data,color,label in [(standing,RUST,"standing role"),(scoped,GOLD,"scoped long-lived token"),(leased,TEAL,"one-use lease")]:
        ax.hist(data,bins=bins,density=True,histtype="step",lw=2,label=label,color=color)
        p95=np.percentile(data,95); ax.axvline(p95,color=color,ls="--",lw=1); ax.text(p95+8,.0065,f"p95 ${p95:.0f}k",rotation=90,va="bottom",fontsize=6.8,color=color)
    ax.set_xlim(0,900); ax.set_xlabel("modeled loss per compromise ($000)",fontsize=8); ax.set_ylabel("density",fontsize=8)
    ax.legend(frameon=False,fontsize=7,ncol=3,loc="upper right"); ax.grid(axis="y",color=LINE,lw=.5); ax.spines[["top","right"]].set_visible(False); ax.tick_params(labelsize=7)
    save(fig, 14)


def f15():
    fig, ax = setup(15, "Audience and resource binding", "Expected decision when the same lease is presented to different APIs")
    box(ax,4,40,18,25,"LEASE", "aud=crm-api\nresource=quote/771",edge=TEAL,title_color=TEAL)
    targets=[(38,66,"CRM API","ALLOW",TEAL),(68,66,"BILLING API","DENY aud",RUST),(38,20,"EXPORT API","DENY aud",RUST),(68,20,"CRM quote/992","DENY resource",RUST)]
    for x,y,title,result,color in targets:
        box(ax,x,y,24,18,title,result,edge=color,title_color=color)
        arrow(ax,(22,52),(x,y+9),color=color,connectionstyle="arc3,rad=.08")
    save(fig, 15)


def f16():
    fig, ax = setup(16, "Lease policy decision tree", "Policy outcome for one consequential mutation")
    nodes=[
        (7,69,25,10,"ACTION ALLOWED?",GOLD),(7,54,25,10,"EVIDENCE FRESH?",BLUE),
        (7,39,25,10,"APPROVAL VALID?",GOLD),(7,24,25,10,"WITHIN LIMITS?",GOLD),
        (7,9,25,10,"ISSUE LEASE",TEAL),(58,69,25,10,"DENY",RUST),
        (58,54,25,10,"RE-EVALUATE",RUST),(58,39,25,10,"DENY",RUST),(58,24,25,10,"DENY",RUST),
    ]
    for x,y,w,h,title,color in nodes: box(ax,x,y,w,h,title,"",edge=color,title_color=color)
    edges=[
        ((19.5,69),(19.5,64),"yes"),((32,74),(58,74),"no"),
        ((19.5,54),(19.5,49),"yes"),((32,59),(58,59),"no"),
        ((19.5,39),(19.5,34),"yes"),((32,44),(58,44),"no"),
        ((19.5,24),(19.5,19),"yes"),((32,29),(58,29),"no"),
    ]
    for a,b,label in edges:
        arrow(ax,a,b,color=MUTED,lw=1)
        if a[0] == b[0]:
            ax.text(a[0] + 2, (a[1] + b[1]) / 2, label, fontsize=6.5, color=MUTED, va="center")
        else:
            ax.text((a[0] + b[0]) / 2, a[1] + 1.5, label, fontsize=6.5, color=MUTED, ha="center")
    save(fig, 16)


def f17():
    fig, ax = setup(17, "Approval-to-lease binding", "Digest chain rejects any post-approval mutation")
    items=[(3,"PROPOSAL","canonical JSON\nsha256 = P",BLUE),(27,"EVIDENCE","bundle manifest\nsha256 = E",BLUE),(51,"APPROVAL","sign(P || E || policy)",GOLD),(75,"LEASE","claims include\nP + E + approval",TEAL)]
    for x,title,body,color in items:
        box(ax,x,43,20,27,title,body,edge=color,title_color=color)
    for x in [23,47,71]: arrow(ax,(x,56),(x+4,56),color=MUTED)
    ax.text(50,25,"executor recomputes P and E",ha="center",fontsize=9,color=INK,fontweight="bold")
    ax.plot([20,80],[18,18],color=LINE,lw=7,solid_capstyle="round")
    ax.plot([20,67],[18,18],color=TEAL,lw=7,solid_capstyle="round")
    ax.text(20,10,"mismatch → reject",ha="center",fontsize=7,color=RUST); ax.text(80,10,"match → continue",ha="center",fontsize=7,color=TEAL)
    save(fig, 17)


def f18():
    fig, ax = setup(18, "Executor validation gates", "Every gate is mandatory; no synthetic pass-rate claim")
    gates=[
        ("CRYPTO","algorithm · issuer\ntime window",BLUE),
        ("SENDER","DPoP htm · htu\niat · jti · ath",BLUE),
        ("AUTHORITY","audience · type\nresource · delta",GOLD),
        ("FRESHNESS","policy · approval\ndigests · version",GOLD),
        ("ONE USE","atomic reserve\nidempotency state",TEAL),
        ("EFFECT","conditional write\nverify · receipt",TEAL),
    ]
    for i,(title,body,color) in enumerate(gates):
        x=2+i*16
        box(ax,x,38,14,32,title,body,edge=color,title_color=color)
        if i < len(gates)-1:
            arrow(ax,(x+14,54),(x+16,54),color=MUTED,lw=1)
    ax.text(50,25,"any failure before effect → reject and persist terminal state",ha="center",fontsize=7.5,color=RUST,fontweight="bold")
    ax.text(50,15,"uncertain effect → mark ambiguous → reconcile → verify or recover",ha="center",fontsize=7.5,color=GOLD,fontweight="bold")
    save(fig, 18)


def f19():
    fig, ax = setup(19, "Concurrent-state race", "Expected-version enforcement protects newer human work")
    lanes=[(79,"HUMAN"),(58,"AGENT"),(37,"CRM"),(16,"VERIFIER")]
    for y,name in lanes:
        ax.text(3,y,name,fontsize=7.5,fontweight="bold",color=INK,va="center")
        ax.plot([14,96],[y,y],color=LINE,lw=1)
    events=[(24,58,"read quote v19",BLUE),(39,79,"human edits → v20",GOLD),(56,58,"lease expects v19",TEAL),(71,37,"conditional write",RUST),(83,37,"409 version conflict",RUST),(91,16,"no mutation to verify",TEAL)]
    for x,y,label,color in events:
        ax.scatter([x],[y],s=80,facecolor=SURFACE,edgecolor=color,lw=1.5,zorder=3)
        ax.text(x,y+5,label,ha="center",fontsize=6.5,color=color,fontweight="bold")
    for (x1,y1,_,_),(x2,y2,_,_) in zip(events,events[1:]): arrow(ax,(x1+2,y1),(x2-2,y2),color=MUTED,lw=1,connectionstyle="arc3,rad=.08")
    save(fig, 19)


def f20():
    fig, ax = setup(20, "Idempotent execution protocol", "A retry returns the recorded result instead of repeating the business effect")
    actors=[(10,"Agent"),(34,"PEP"),(59,"Idempotency store"),(86,"CRM")]
    for x,name in actors:
        ax.text(x,77,name,ha="center",fontsize=8,fontweight="bold",color=INK); ax.plot([x,x],[8,72],color=LINE,lw=1,ls="--")
    events=[(10,34,67,"action_id=A7",BLUE),(34,59,59,"reserve A7",GOLD),(59,34,51,"new",GOLD),(34,86,43,"conditional mutate",TEAL),(86,34,35,"201 + state hash",TEAL),(34,59,27,"commit result",GOLD),(10,34,18,"retry A7",BLUE),(34,10,10,"cached receipt; no new effect",TEAL)]
    for a,b,y,label,color in events:
        arrow(ax,(a,y),(b,y),color=color,lw=1.1); ax.text((a+b)/2,y+2,label,ha="center",fontsize=6.5,color=color)
    save(fig, 20)


def f21():
    fig, ax = setup(21, "Action receipt chain", "Append-only lineage for one permission lease and one business mutation")
    items=[("intent","action + delta",BLUE),("evidence","bundle digest",BLUE),("decision","policy + reason",GOLD),("approval","principal + limits",GOLD),("lease","claims + proof",TEAL),("request","API + idempotency",TEAL),("outcome","state + hash",TEAL),("recovery","pointer + status",RUST)]
    for i,(title,body,color) in enumerate(items[:4]):
        x=3+i*24
        box(ax,x,52,21,25,title.upper(),body,edge=color,title_color=color)
        if i<3: arrow(ax,(x+21,64),(x+24,64),color=MUTED,lw=1)
    second=list(reversed(items[4:]))
    for i,(title,body,color) in enumerate(second):
        x=3+i*24
        box(ax,x,18,21,25,title.upper(),body,edge=color,title_color=color)
        if i<3: arrow(ax,(x+24,30),(x+21,30),color=MUTED,lw=1)
    arrow(ax,(96,64),(96,43),color=MUTED,lw=1)
    ax.text(50,7,"receipt_id · trace_id · lease_jti · immutable timestamp · schema version",ha="center",fontsize=7.5,color=INK,fontfamily="monospace")
    save(fig, 21)


def f22():
    fig, ax = setup(22, "Failure-mode control matrix", "Declared ordinal coverage: 0 none · 1 support · 2 strong · 3 primary", plot=True)
    fig.subplots_adjust(left=.22,right=.96,top=.78,bottom=.18)
    rows=["token theft","replay","over-broad scope","stale approval","concurrent edit","duplicate retry","wrong downstream state"]
    cols=["TTL","audience","DPoP","one use","policy","version","verify"]
    data=np.array([[2,1,3,1,1,0,0],[1,1,3,3,0,0,0],[1,3,0,1,3,0,0],[2,0,0,1,3,2,1],[0,0,0,0,1,3,2],[0,0,1,3,0,1,2],[0,1,0,0,1,1,3]])
    cmap=ListedColormap(["#F0EEE6",BLUE_LIGHT,GOLD_LIGHT,TEAL_LIGHT])
    ax.imshow(data,cmap=cmap,vmin=0,vmax=3,aspect="auto")
    ax.set_xticks(range(len(cols)),cols,fontsize=7); ax.set_yticks(range(len(rows)),rows,fontsize=7.5)
    labels=["—","support","strong","primary"]
    for i in range(data.shape[0]):
        for j in range(data.shape[1]): ax.text(j,i,labels[data[i,j]],ha="center",va="center",fontsize=6.2,color=INK,fontweight="bold")
    ax.tick_params(length=0); [s.set_visible(False) for s in ax.spines.values()]
    fig.text(.22,.10,"0  none     1  support     2  strong     3  primary",fontsize=7,color=MUTED)
    save(fig, 22)


def f23():
    fig, ax = setup(23, "End-to-end latency budget", "Synthetic p95 stage contributions and cumulative path", plot=True)
    components=[("normalize",12,BLUE),("policy",28,GOLD),("approval lookup",18,GOLD),("token exchange",42,TEAL),("DPoP sign",6,TEAL),("CRM write",110,INK),("verification",75,BLUE),("receipt",16,TEAL)]
    names=[name.replace(" ","\n") for name,_,_ in components]
    values=np.array([value for _,value,_ in components])
    colors=[color for _,_,color in components]
    x=np.arange(len(components))
    cumulative=np.cumsum(values)
    ax.bar(x,values,color=colors,edgecolor=INK,lw=.35,width=.68)
    for xi,value in zip(x,values):
        ax.text(xi,value+7,f"{value}ms",ha="center",fontsize=6.5,color=INK,fontweight="bold")
    ax.plot(x,cumulative,color=RUST,lw=2,marker="o",ms=4,label="cumulative path")
    for xi,total in zip(x,cumulative):
        if xi in {3,5}:
            ax.text(xi,total+8,f"cumulative {total}ms",ha="center",fontsize=6.2,color=RUST)
    ax.axhline(350,color=MUTED,ls="--",lw=1.2)
    ax.text(7.45,353,"350ms objective",ha="right",va="bottom",fontsize=7,color=MUTED)
    ax.set_xticks(x,names,fontsize=6.8); ax.set_ylim(0,380); ax.set_ylabel("milliseconds",fontsize=8)
    ax.text(7,313,"cumulative 307ms",ha="right",va="bottom",fontsize=7,color=RUST,fontweight="bold")
    ax.spines[["top","right"]].set_visible(False); ax.tick_params(axis="y",labelsize=7); ax.grid(axis="y",color=LINE,lw=.5)
    save(fig, 23)


def f24():
    fig, ax = setup(24, "Lease control-plane objectives", "Synthetic 30-day target versus actual scorecard")
    cards=[
        ("issuance availability","≥99.95%","99.97%","PASS",TEAL),
        ("p95 token exchange","≤50 ms","42 ms","PASS",TEAL),
        ("policy decision errors","≤0.10%","0.02%","PASS",TEAL),
        ("expired before use","≤0.10%","0.07%","PASS",TEAL),
        ("replays blocked","100%","14 / 14","PASS",TEAL),
        ("verification mismatch","≤0.05%","0.11%","BREACH",RUST),
    ]
    for i,(label,target,actual,status,color) in enumerate(cards):
        col,row=i%3,i//3; x,y=4+col*32,53-row*34
        ax.add_patch(FancyBboxPatch((x,y),28,27,boxstyle="round,pad=.015",facecolor=SURFACE,edgecolor=color,linewidth=1.15))
        ax.text(x+1.7,y+20.5,label,fontsize=6.8,color=MUTED,fontweight="bold")
        ax.text(x+1.7,y+13.5,actual,fontsize=10,color=color,fontweight="bold")
        ax.text(x+1.7,y+6.2,f"target {target}",fontsize=6.5,color=MUTED)
        ax.text(x+26.3,y+13.5,status,ha="right",fontsize=6.5,color=color,fontweight="bold")
    ax.text(50,8,"A metric is not an objective until target, actual, window, and breach handling are explicit.",ha="center",fontsize=8,color=INK)
    save(fig, 24)


def f25():
    fig, ax = setup(25, "Permission-lease rollout", "Remove standing privilege one action class at a time")
    phases=[(2,"1 · OBSERVE","inventory tokens\nmap actions","100% token census",BLUE),(22,"2 · SHADOW","evaluate policy\nissue no lease","decision parity ≥99%",BLUE),(42,"3 · INTERNAL","tasks + notes\none-use leases","verification ≥99.9%",GOLD),(62,"4 · APPROVED","commercial deltas\nhuman bound","recovery drill passes",GOLD),(82,"5 · BOUNDED","selected autonomy\ndynamic limits","error budget healthy",TEAL)]
    for x,title,scope,gate,color in phases:
        box(ax,x,35,16,44,title,scope,edge=color,title_color=color)
        ax.add_patch(FancyBboxPatch((x+1,16),14,12,boxstyle="round,pad=.01",facecolor="#EEF4F2",edgecolor=LINE))
        ax.text(x+8,22,"GATE\n"+gate,ha="center",va="center",fontsize=6,color=INK,fontweight="bold")
    for x in [18,38,58,78]: arrow(ax,(x,57),(x+4,57),color=MUTED,lw=1)
    ax.text(50,7,"Promotion is reversible; a missed SLO returns the action class to the previous phase.",ha="center",fontsize=8,color=RUST)
    save(fig, 25)


FUNCTIONS=[f01,f02,f03,f04,f05,f06,f07,f08,f09,f10,f11,f12,f13,f14,f15,f16,f17,f18,f19,f20,f21,f22,f23,f24,f25]


def write_chart_map() -> None:
    MAP_PATH.parent.mkdir(parents=True, exist_ok=True)
    lines=[
        "# Figure map — Your AI Agent Should Not Have a Standing Role",
        "",
        "All quantitative values are synthetic threat-model data. Diagrams are reference designs, not claims about a deployed system.",
        "",
        "Palette policy: hard two-root cap per chart, using teal/blue for bounded authority and observation, gold for decision controls, rust for risk, and neutral ink. Every distinction also uses labels, position, line style, or shape.",
        "",
        "| Figure | Tier | Analytical question | Form | Supported takeaway | Inputs / assumptions |",
        "|---:|---|---|---|---|---|",
    ]
    for number,title,form,takeaway in FIGURE_META:
        tier = "Core" if number in CORE_FIGURES else "Supplemental"
        assumptions = FIGURE_ASSUMPTIONS.get(number, "Reference design; no observed production data.")
        lines.append(f"| {number} | {tier} | {title} | {form} | {takeaway} | {assumptions} |")
    lines += ["", "Renderer: reproducible Matplotlib PNG, 1600×900. Final QA surface: responsive GitHub Pages article and Medium import page.", ""]
    MAP_PATH.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    plt.rcParams.update({"font.family":"DejaVu Sans","axes.labelcolor":INK,"text.color":INK,"axes.edgecolor":LINE,"xtick.color":MUTED,"ytick.color":MUTED})
    for fn in FUNCTIONS: fn()
    write_chart_map()
    print(f"generated {len(FUNCTIONS)} figures in {OUT}")


if __name__ == "__main__":
    main()
