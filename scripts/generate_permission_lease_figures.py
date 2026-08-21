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
    (3, "Just-in-time lease control plane", "Architecture diagram", "Independent evidence, policy, approval, issuance, enforcement, verification, and recovery services bound authority."),
    (4, "Authority narrowing path", "Stage progression", "Each control step removes unused resources, actions, values, time, and repetitions."),
    (5, "Permission lease envelope", "Structured schema", "A useful lease binds principal, actor, action, resource, limits, evidence, audience, proof key, time, and use count."),
    (6, "Lease lifecycle", "State machine", "A lease moves through requested, evaluated, approved, issued, consumed, verified, and terminal states."),
    (7, "Lease issuance sequence", "Sequence diagram", "The executor receives authority only after current policy and approval checks succeed."),
    (8, "Policy decision boundary", "PEP/PDP diagram", "The policy enforcement point asks an external decision service and enforces returned obligations."),
    (9, "Rich authorization mapping", "Field map", "Business intent is translated into structured authorization details instead of a coarse scope string."),
    (10, "Exposure model", "Formula decomposition", "Modeled exposure depends on reachable value, scope, duration, uses, propagation, and control effectiveness."),
    (11, "TTL and scope exposure", "Heatmap", "Modeled exposure grows nonlinearly when credential lifetime and resource breadth expand together."),
    (12, "Compromise opportunity by TTL", "Multi-series line", "Shorter leases reduce the probability that a compromise window overlaps valid authority."),
    (13, "Replay containment by token mode", "Grouped bar", "Audience binding, sender constraint, and one-use consumption reduce replay reach."),
    (14, "Blast-radius distribution", "Distribution", "Leased authority compresses the loss tail in a synthetic compromise simulation."),
    (15, "Audience and resource binding", "Reachability graph", "A lease valid for one resource server should fail at adjacent APIs."),
    (16, "Lease policy decision tree", "Decision tree", "High-risk actions require evidence, eligible approval, bounded values, and live preconditions."),
    (17, "Approval-to-lease binding", "Cryptographic binding diagram", "Digests prevent an approved proposal from being silently changed before issuance or execution."),
    (18, "Executor validation gates", "Stage bars", "Execution stops unless signature, time, audience, proof, use count, policy, and preconditions all agree."),
    (19, "Concurrent-state race", "Timeline", "Optimistic concurrency prevents a valid lease from overwriting a newer human change."),
    (20, "Idempotent execution protocol", "Sequence diagram", "One action identifier makes retries safe and duplicate effects observable."),
    (21, "Action receipt chain", "Structured lineage", "The receipt joins intent, evidence, approval, lease, request, outcome, verification, and recovery."),
    (22, "Failure-mode control matrix", "Heatmap", "No single control covers theft, replay, stale context, over-scope, duplication, and downstream divergence."),
    (23, "End-to-end latency budget", "Stacked bar", "A lease path can remain operationally fast when control services have explicit budgets."),
    (24, "Lease control-plane SLOs", "Operational scorecard", "Security and reliability require measurable issuance, denial, expiry, replay, verification, and recovery signals."),
    (25, "Permission-lease rollout", "Maturity roadmap", "Teams should remove standing privilege action class by action class behind promotion gates."),
]


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
    box(ax, 3, 42, 17, 22, "COMPROMISED AGENT", "prompt injection\nor runtime breach", color=RUST_LIGHT, edge=RUST, title_color=RUST)
    box(ax, 28, 42, 18, 22, "STANDING TOKEN", "crm.enterprise.write\n8-hour lifetime", edge=RUST, title_color=RUST)
    arrow(ax, (20, 53), (28, 53), color=RUST)
    targets = [(58, 69, "QUOTES", "price · term"), (78, 69, "CONTACTS", "email · phone"), (58, 30, "CASES", "status · credit"), (78, 30, "EXPORT", "accounts · notes")]
    for x, y, title, body in targets:
        box(ax, x, y, 17, 17, title, body, edge=RUST_LIGHT, title_color=RUST)
        arrow(ax, (46, 53), (x, y + 8), color=RUST, connectionstyle="arc3,rad=.08")
    ax.text(50, 8, "One secret crosses four resource families because the role was designed for a user session, not one agent action.", ha="center", fontsize=8, color=INK)
    save(fig, 2)


def f03():
    fig, ax = setup(3, "Just-in-time lease control plane", "Control plane issues bounded authority; data plane enforces and verifies it")
    layers = [(4, 63, 92, 20, "DECISION PLANE", BLUE_LIGHT, BLUE), (4, 35, 92, 20, "AUTHORITY PLANE", GOLD_LIGHT, GOLD), (4, 7, 92, 20, "EXECUTION PLANE", TEAL_LIGHT, TEAL)]
    for x, y, w, h, title, fill, edge in layers:
        ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=.01", facecolor=fill, edgecolor=edge, alpha=.32, linewidth=1.1))
        ax.text(x + 2, y + h - 3, title, color=edge, fontsize=7.5, fontweight="bold", va="top")
    boxes = [(9, 66, "Evidence", "digest + freshness", BLUE), (32, 66, "Policy", "allow + obligations", BLUE), (55, 66, "Approval", "eligible principal", BLUE), (76, 66, "Risk", "action-level", BLUE),
             (17, 38, "Lease issuer", "sign + TTL + jti", GOLD), (43, 38, "Proof key", "DPoP / mTLS", GOLD), (69, 38, "Consumption", "one-use ledger", GOLD),
             (10, 10, "PEP", "validate + gate", TEAL), (34, 10, "CRM API", "expected version", TEAL), (58, 10, "Verifier", "read postcondition", TEAL), (79, 10, "Recovery", "freeze + compensate", TEAL)]
    for x, y, title, body, color in boxes:
        box(ax, x, y, 17, 12, title, body, color=SURFACE, edge=color, title_color=color)
    for a, b in [((26,72),(32,72)),((49,72),(55,72)),((72,72),(76,72)),((84,66),(77,50)),((34,44),(43,44)),((60,44),(69,44)),((77,38),(18,22)),((27,16),(34,16)),((51,16),(58,16)),((75,16),(79,16))]:
        arrow(ax, a, b, color=MUTED, lw=1)
    save(fig, 3)


def f04():
    fig, ax = setup(4, "Authority narrowing path", "Illustrative reachable authority after each independent restriction", plot=True)
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
    fig, ax = setup(6, "Lease lifecycle", "Terminal states prevent authority from silently returning to active")
    nodes = [(7,55,"REQUESTED",BLUE),(25,55,"EVALUATED",BLUE),(43,55,"APPROVED",GOLD),(61,55,"ISSUED",GOLD),(79,55,"CONSUMED",TEAL),(79,21,"VERIFIED",TEAL),(52,21,"REVOKED",RUST),(25,21,"EXPIRED",MUTED)]
    for x,y,name,color in nodes: box(ax,x,y,15,13,name,"",edge=color,title_color=color)
    for start,end in [((22,61),(25,61)),((40,61),(43,61)),((58,61),(61,61)),((76,61),(79,61)),((86,55),(86,34)),((79,27),(67,27)),((61,55),(59,34)),((61,55),(40,34))]: arrow(ax,start,end,color=MUTED,lw=1.1)
    ax.text(50,7,"deny / cancel / context change can terminate the lease before execution",ha="center",fontsize=8,color=RUST)
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
        box(ax,x,34,17,26,symbol,wrap(name,18),edge=TEAL_LIGHT if i<3 else GOLD_LIGHT,title_color=TEAL if i<3 else GOLD)
        ax.text(x+8.5,39,value,ha="center",fontsize=8,color=INK,fontweight="bold")
    ax.text(50,17,"Illustrative bound: $2.4M × .05 × 1 × 1.2 × .30 = $43.2k",ha="center",fontsize=10,color=RUST,fontweight="bold",fontfamily="monospace")
    ax.text(50,8,"The formula is a routing model, not an actuarial claim; calibrate every term with your own loss data.",ha="center",fontsize=7.5,color=MUTED)
    save(fig, 10)


def f11():
    fig, ax = setup(11, "TTL and scope exposure", "Modeled reachable loss ($000) for one stolen credential", plot=True)
    fig.subplots_adjust(left=.18,right=.96,top=.78,bottom=.16)
    ttls=np.array([30,60,90,300,900,3600])
    scopes=np.array([1,5,25,100])
    exposure=np.outer(np.sqrt(scopes), 18*(ttls/30)**.55)
    cmap=LinearSegmentedColormap.from_list("exp",["#EAF4F1",GOLD_LIGHT,RUST])
    ax.imshow(exposure,cmap=cmap,aspect="auto",vmin=0,vmax=exposure.max())
    ax.set_xticks(range(len(ttls)),["30s","60s","90s","5m","15m","60m"],fontsize=8)
    ax.set_yticks(range(len(scopes)),["1 record","5 records","25 records","100 records"],fontsize=8)
    for i in range(len(scopes)):
        for j in range(len(ttls)):
            ax.text(j,i,f"${exposure[i,j]:.0f}k",ha="center",va="center",fontsize=7,color=WHITE if exposure[i,j]>.58*exposure.max() else INK,fontweight="bold")
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
    fig, ax = setup(18, "Executor validation gates", "Illustrative cumulative pass rate across 100,000 attempted executions", plot=True)
    gates=["signature","time","audience","proof key","one-use jti","policy","precondition","execute"]
    pass_rate=[100,99.8,99.1,98.6,97.9,96.8,94.7,94.7]
    y=np.arange(len(gates))
    colors=[TEAL]*5+[GOLD,GOLD,TEAL]
    ax.barh(y,pass_rate,color=colors,edgecolor=INK,lw=.35)
    ax.set_yticks(y,gates,fontsize=8); ax.invert_yaxis(); ax.set_xlim(90,100.5)
    for yi,v in zip(y,pass_rate): ax.text(v+.1,yi,f"{v:.1f}%",va="center",fontsize=7,color=INK,fontweight="bold")
    ax.set_xlabel("cumulative pass rate (%) · focused scale",fontsize=8); ax.grid(axis="x",color=LINE,lw=.5); ax.spines[["top","right","left"]].set_visible(False); ax.tick_params(axis="x",labelsize=7)
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
        ax.text(x,77,name,ha="center",fontsize=8,fontweight="bold",color=INK); ax.plot([x,x],[13,72],color=LINE,lw=1,ls="--")
    events=[(10,34,66,"action_id=A7",BLUE),(34,59,57,"reserve A7",GOLD),(59,34,48,"new",GOLD),(34,86,39,"conditional mutate",TEAL),(86,34,30,"201 + state hash",TEAL),(34,59,21,"commit result",GOLD),(10,34,13,"retry A7 → cached receipt",BLUE)]
    for a,b,y,label,color in events:
        arrow(ax,(a,y),(b,y),color=color,lw=1.1); ax.text((a+b)/2,y+2,label,ha="center",fontsize=6.5,color=color)
    save(fig, 20)


def f21():
    fig, ax = setup(21, "Action receipt chain", "Append-only lineage for one permission lease and one business mutation")
    items=[("intent","action + delta",BLUE),("evidence","bundle digest",BLUE),("decision","policy + reason",GOLD),("approval","principal + limits",GOLD),("lease","claims + proof",TEAL),("request","API + idempotency",TEAL),("outcome","state + hash",TEAL),("recovery","pointer + status",RUST)]
    for i,(title,body,color) in enumerate(items):
        col,row=i%4,i//4; x=3+col*24; y=52-row*34
        box(ax,x,y,21,25,title.upper(),body,edge=color,title_color=color)
        if col<3: arrow(ax,(x+21,y+12),(x+24,y+12),color=MUTED,lw=1)
    ax.text(50,7,"receipt_id · trace_id · lease_jti · immutable timestamp · schema version",ha="center",fontsize=7.5,color=INK,fontfamily="monospace")
    save(fig, 21)


def f22():
    fig, ax = setup(22, "Failure-mode control matrix", "Relative control coverage: 0 = none, 3 = primary", plot=True)
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
    save(fig, 22)


def f23():
    fig, ax = setup(23, "End-to-end latency budget", "Synthetic p95 service budget for an approved execution path", plot=True)
    components=[("normalize",12,BLUE),("policy",28,GOLD),("approval lookup",18,GOLD),("token exchange",42,TEAL),("DPoP sign",6,TEAL),("CRM write",110,INK),("verification",75,BLUE),("receipt",16,TEAL)]
    left=0
    for name,value,color in components:
        ax.barh([0],[value],left=left,height=.48,color=color,edgecolor=PAPER,lw=1,label=name)
        if value>15: ax.text(left+value/2,0,f"{value}ms",ha="center",va="center",fontsize=6.5,color=WHITE if color in [TEAL,BLUE,INK] else INK,fontweight="bold")
        left+=value
    ax.axvline(350,color=RUST,ls="--",lw=1.2); ax.text(352,.31,"350ms control-path SLO",fontsize=7,color=RUST)
    ax.set_xlim(0,400); ax.set_yticks([]); ax.set_xlabel("elapsed milliseconds",fontsize=8); ax.legend(frameon=False,fontsize=6.2,ncol=4,loc="upper center")
    ax.spines[["top","right","left"]].set_visible(False); ax.tick_params(axis="x",labelsize=7); ax.grid(axis="x",color=LINE,lw=.5)
    save(fig, 23)


def f24():
    fig, ax = setup(24, "Lease control-plane SLOs", "Synthetic 30-day operations scorecard")
    cards=[("99.97%","issuance availability",TEAL),("42 ms","p95 token exchange",TEAL),("0.18%","policy denials",GOLD),("0.07%","expired before use",GOLD),("14","replay attempts blocked",RUST),("0.11%","verification mismatch",RUST)]
    for i,(value,label,color) in enumerate(cards):
        col,row=i%3,i//3; x,y=4+col*32,53-row*34
        box(ax,x,y,28,27,value,wrap(label,22),edge=color,title_color=color)
    ax.text(50,8,"Track both availability and prevented actions; a control plane can fail open, fail closed, or fail slowly.",ha="center",fontsize=8,color=INK)
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
        "| Figure | Analytical question | Form | Supported takeaway |",
        "|---:|---|---|---|",
    ]
    for number,title,form,takeaway in FIGURE_META:
        lines.append(f"| {number} | {title} | {form} | {takeaway} |")
    lines += ["", "Renderer: reproducible Matplotlib PNG, 1600×900. Final QA surface: responsive GitHub Pages article and Medium import page.", ""]
    MAP_PATH.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    plt.rcParams.update({"font.family":"DejaVu Sans","axes.labelcolor":INK,"text.color":INK,"axes.edgecolor":LINE,"xtick.color":MUTED,"ytick.color":MUTED})
    for fn in FUNCTIONS: fn()
    write_chart_map()
    print(f"generated {len(FUNCTIONS)} figures in {OUT}")


if __name__ == "__main__":
    main()
