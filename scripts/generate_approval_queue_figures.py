#!/usr/bin/env python3
"""Generate 18 reproducible figures for the human-approval queueing story."""

from __future__ import annotations

import math
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.colors import LinearSegmentedColormap
from matplotlib.patches import Circle, FancyBboxPatch, Polygon, Rectangle

from technical_figure_framework import (
    BLUE, BLUE_LIGHT, GOLD, GOLD_LIGHT, INK, LINE, MUTED, PAPER, PURPLE,
    PURPLE_LIGHT, RUST, RUST_LIGHT, SURFACE, TEAL, TEAL_LIGHT, FigureSpec,
    FigureSystem, arrow, box,
)


ROOT = Path(__file__).resolve().parents[1]
SLUG = "human-approval-is-a-queueing-system"
OUT = ROOT / "assets" / "images" / SLUG
MAP_PATH = ROOT / "stories" / f"{SLUG}-figure-map.md"


def S(n,t,f,k,d,i,c,a="Reference architecture; no observed production data.",core=True):
    return FigureSpec(n,t,f,k,d,tuple(i),tuple(c),a,core)


SPECS=[
S(1,"Human approval is not a checkbox","Comparison","Uniform approval routes create delay and habituation; risk-priced service classes spend review where it changes outcomes.","OPERATING MODEL",["A binary human-in-the-loop setting hides capacity, competence, and deadline.","Low-risk volume can crowd out rare, high-loss decisions.","Review value is the avoided decision loss minus delay, labor, and fatigue cost."],[("NAIVE","all actions → one queue"),("DESIGN","risk × service class"),("OUTPUT","decision + receipt")]),
S(2,"Approval decision-service architecture","Architecture","A governed approval service separates risk scoring, eligibility, routing, review, execution, and calibration.","CONTROL PLANE",["The agent submits a typed proposal and evidence packet—not a free-form request.","Policy selects service class and eligible reviewer pool before queue entry.","Outcomes feed calibration without letting reviewers rewrite the original proposal."],[("INPUT","proposal + evidence"),("ROUTE","risk + eligibility"),("EXIT","approve · deny · expire")]),
S(3,"Action-level risk decomposition","Risk model","Approval need depends on impact, likelihood, reversibility, novelty, evidence, propagation, and control strength.","RISK",["Account value alone does not determine approval need.","Irreversibility and downstream propagation amplify small direct mutations.","Evidence weakness and novelty increase uncertainty, not just mean loss."],[("FACTORS","7 explicit terms"),("OUTPUT","risk band"),("POLICY","categorical floors")]),
S(4,"Expected-loss decision boundary","Formula","Review is economically rational when expected avoided loss exceeds review, delay, and residual-error cost.","DECISION THEORY",["The model compares decisions—not an abstract confidence score.","Reviewer effectiveness is action- and evidence-specific.","Tail constraints can require review even when average economics do not."],[("NO REVIEW","p_agent × L"),("REVIEW","C_review + C_delay + p_review × L"),("CHOOSE","lower constrained loss")],"Synthetic example: p_agent=.018, p_review=.004, loss=$42k, review=$18, delay=$65; review saves an illustrative $505 per action."),
S(5,"Four approval service classes","Service matrix","Risk, deadline, skills, evidence, and fallback rules define distinct queues rather than one undifferentiated backlog.","SERVICE DESIGN",["Emergency containment and commercial approval have different objectives.","Each class declares maximum wait, reviewer pool, and expiry behavior.","Work never silently downgrades to a less qualified queue."],[("CLASSES","S0 through S3"),("DEADLINE","30 s → 8 h"),("FALLBACK","deny · expire · escalate")]),
S(6,"Erlang-C wait sensitivity","Queue heatmap","When offered load approaches reviewer capacity, expected wait rises nonlinearly and service objectives collapse.","QUEUEING",["Small utilization changes near saturation create large delay changes.","Average staffing is insufficient when arrival bursts and skill partitions matter.","The model is diagnostic; real arrivals and service times must be tested."],[("MODEL","M/M/c Erlang C"),("SERVICE","6 min mean"),("OUTPUT","E[wait] minutes")],"Synthetic M/M/c model: mean service 6 minutes, 3–10 reviewers, arrivals 12–92 per hour; unstable cells are marked.",core=True),
S(7,"Arrival, service, and deadline anatomy","Timeline","Approval latency includes queue, assignment, open, decision, and execution handoff—not only reviewer handling time.","LATENCY",["Queue wait and reviewer response are separately controllable.","An expired proposal must not remain approvable after business state changes.","The receipt records every timestamp and revalidation event."],[("ARRIVE","T0 proposal"),("DECIDE","T4 signed choice"),("EXPIRE","bounded deadline")]),
S(8,"Backlog growth under three staffing scenarios","Scenario curves","A queue with arrival rate above effective service rate accumulates risk continuously even if daily averages look close.","CAPACITY",["Nominal headcount overstates capacity after breaks, training, and skill constraints.","Backlog is segmented by deadline and risk, not only count.","Admission control protects critical classes when demand spikes."],[("ARRIVAL","1,200 / hour burst"),("SCENARIOS","under · matched · surge"),("HORIZON","8 synthetic hours")],"Synthetic fluid model: arrivals 1,200/hour; effective capacities 900, 1,200, and 1,500/hour; initial backlog 250."),
S(9,"Reviewer-skill routing graph","Bipartite graph","Eligibility, jurisdiction, product, value limit, and conflicts constrain routing before workload balancing.","ROUTING",["The fastest reviewer may be ineligible for the action.","Skill pools create fragmented capacity and hidden bottlenecks.","Routing must preserve separation of duties and workload fairness."],[("LEFT","action classes"),("RIGHT","reviewer pools"),("EDGE","eligible + available")]),
S(10,"Separation-of-duties enforcement graph","Control graph","The proposer, evidence curator, approver, lease issuer, executor, and verifier need explicit forbidden-role combinations.","GOVERNANCE",["A human click does not create independence if the same person controls proposal and evidence.","Conflict rules apply to humans, workloads, groups, and delegated identities.","Break-glass decisions require stronger logging and after-action review."],[("ROLES","6 responsibilities"),("DENY","4 toxic combinations"),("PROVE","identity chain")]),
S(11,"Approval packet anatomy","Structured packet","A reviewer needs the exact delta, evidence, uncertainty, policy reason, alternatives, expiry, and recovery—not an agent summary alone.","DECISION UX",["Critical information is visible without opening ten systems.","The interface distinguishes observed facts, model inference, and policy result.","Approve signs the packet digest and cannot authorize a later mutation."],[("CENTER","exact business delta"),("CONTEXT","evidence + conflicts"),("CHOICE","approve · deny · edit")]),
S(12,"Evidence-quality score decomposition","Formula","Evidence quality combines required-source coverage, freshness, corroboration, conflict, provenance, and model uncertainty.","EVIDENCE",["The score routes review depth; it does not declare truth.","Missing required sources remain categorical blockers.","Conflict appears as a separate penalty and reviewer cue."],[("SUPPORT","coverage + freshness"),("PENALTY","conflict + uncertainty"),("OUTPUT","quality band")],"Synthetic factors: required-source .90, freshness .82, corroboration .70, provenance 1.0, conflict .25, uncertainty .18."),
S(13,"Value of additional information","Value curve","Review depth should stop when expected decision improvement falls below the next evidence step's time and cost.","VALUE OF INFO",["The first independent source often has the highest marginal value.","More evidence can delay an expiring opportunity.","High-impact uncertainty justifies deeper review than low-risk cleanup."],[("X","review minutes"),("Y","expected net value"),("STOP","marginal VOI ≤ cost")],"Synthetic saturating benefit and linear review/delay cost for three action-risk classes; not observed reviewer performance."),
S(14,"Fatigue and approval error","Scenario curves","Long uninterrupted review streaks can raise synthetic miss probability while decision time appears to improve.","HUMAN FACTORS",["Faster decisions are not automatically more efficient.","Mechanical approvals can hide behind low queue latency.","Rotation, breaks, sampling, and packet quality need controlled evaluation."],[("X","consecutive decisions"),("Y","miss probability"),("SIGNAL","time falls as risk rises")],"Synthetic fatigue curves only: miss probability and median handling time by consecutive decision number; no human-subject claim."),
S(15,"Automation threshold frontier","Efficient frontier","The optimal threshold balances review spend, delay, residual loss, and hard risk constraints by action class.","OPTIMIZATION",["One global confidence threshold is rarely optimal.","Review capacity has a shadow price that changes during demand spikes.","Policy floors override an economically efficient but unsafe point."],[("X","review rate"),("Y","total cost index"),("FRONTIER","risk-constrained minimum")],"Synthetic 50,000-action simulation with declared risk-score distributions and illustrative cost terms."),
S(16,"Shadow-review calibration matrix","Confusion matrix","Shadow review measures where automated decisions and qualified reviewers disagree before authority expands.","CALIBRATION",["Agreement alone is insufficient when both actors share bad evidence.","False-autonomy cells receive risk-weighted investigation.","Reviewer disagreement is adjudicated rather than treated as ground truth automatically."],[("N","10,000 synthetic cases"),("ROWS","automated decision"),("COLS","adjudicated outcome")],"Synthetic 10,000-case matrix: safe automate 7,820; correct escalate 1,410; false escalation 560; false autonomy 210."),
S(17,"Approval-service operating objectives","SLO scorecard","Queue health, eligibility, decision quality, expiry, fatigue, and appeal outcomes need separate objectives and owners.","OPERATIONS",["Meeting mean response time can hide critical-class breaches.","Reviewer overrides and appeals are calibration inputs, not blame metrics.","A false-autonomy breach can freeze promotion even if throughput is high."],[("WINDOW","synthetic 30 days"),("STATUS","6 pass · 2 breach"),("ACTION","re-route + contain")],"Synthetic 30-day window with deliberate critical-wait and false-autonomy breaches."),
S(18,"Migration to risk-priced approval","Maturity roadmap","Teams should instrument current review work before changing thresholds, staffing, or autonomy.","MIGRATION",["Inventory every approval surface and hidden reviewer queue.","Shadow routing reveals demand and skill bottlenecks safely.","Automation expands only after calibrated outcomes and rollback drills."],[("PHASES","0 through 5"),("GATE","risk + capacity"),("ROLLBACK","action class")]),
]

SYSTEM=FigureSystem(SLUG,OUT,MAP_PATH,"Human Approval Is a Queueing System",SPECS)


def f01():
    fig,ax=SYSTEM.setup(1,"Same action volume; different use of scarce human judgment")
    rows=[("ROUTING","everything"),("PRIORITY","arrival order"),("PACKET","agent summary"),("REVIEWER","any available"),("EXPIRY","unclear"),("LEARNING","approval rate")]
    for x,title,c,fill,vals in [(4,"CHECKBOX REVIEW",RUST,RUST_LIGHT,["one queue","FIFO","free text","broad pool","stale work persists","vanity metric"]),(52,"DECISION SERVICE",TEAL,TEAL_LIGHT,["risk class","deadline + loss","bound evidence","eligible pool","fail-closed","calibration"] )]:
        box(ax,x,74,42,10,title,"human-in-the-loop",edge=c,fill=fill,title_color=c,fs=8.5)
        for i,((r,_),v) in enumerate(zip(rows,vals)):
            y=64-i*9
            box(ax,x,y,42,7,r,edge=LINE,fill=SURFACE,fs=6.7); ax.text(x+39,y+3.5,v,ha="right",va="center",color=c,fontsize=6.7,fontweight="bold")
    ax.text(49,39,"≠",ha="center",va="center",color=GOLD,fontsize=30,fontweight="bold")
    SYSTEM.save(fig,1)


def f02():
    fig,ax=SYSTEM.setup(2,"Risk, eligibility, service class, review, and learning remain independent")
    top=[("PROPOSAL","typed delta",BLUE),("RISK ENGINE","loss + novelty",PURPLE),("POLICY","review class",GOLD),("QUEUE ROUTER","deadline + skills",TEAL),("REVIEW UI","signed choice",BLUE)]
    for i,(t,b,c) in enumerate(top):
        x=2+i*19.2; box(ax,x,61,17,18,t,b,edge=c,fill=SURFACE,title_color=c,fs=6.8)
        if i<4: arrow(ax,(x+17,70),(x+19.2,70),color=c)
    lower=[(12,"IDENTITY + ELIGIBILITY","role · limits · conflicts",GOLD),(38,"OUTCOME LEDGER","approve · deny · expire",TEAL),(64,"CALIBRATION","adjudication · drift",PURPLE)]
    for x,t,b,c in lower:
        box(ax,x,22,24,16,t,b,edge=c,fill=SURFACE,title_color=c,fs=6.8)
    arrow(ax,(50,61),(50,38),color=TEAL); arrow(ax,(24,38),(74,61),color=GOLD); arrow(ax,(62,30),(88,61),color=PURPLE)
    box(ax,25,5,50,9,"EXECUTION BOUNDARY","approved packet digest → permission lease → receipt",edge=TEAL,fill=TEAL_LIGHT,title_color=TEAL,fs=7)
    arrow(ax,(88,61),(50,14),color=TEAL)
    SYSTEM.save(fig,2)


def f03():
    fig,ax=SYSTEM.setup(3,"Seven factors determine review depth and service class")
    factors=[("IMPACT","reachable value",RUST,.85),("LIKELIHOOD","model / tool error",PURPLE,.48),("REVERSIBILITY","recovery gap",RUST,.70),("NOVELTY","OOD distance",GOLD,.55),("EVIDENCE","missing / conflict",BLUE,.35),("PROPAGATION","downstream fanout",RUST,.65),("CONTROLS","lease + verify",TEAL,.72)]
    for i,(t,b,c,v) in enumerate(factors):
        x=2+i*13.6
        box(ax,x,53,12,22,t,b,edge=c,fill=SURFACE,title_color=c,fs=5.8)
        ax.add_patch(Rectangle((x+1.5,56),9*v,2.5,facecolor=c,edgecolor="none")); ax.add_patch(Rectangle((x+1.5+9*v,56),9*(1-v),2.5,facecolor=LINE,edgecolor="none"))
        if i<6: ax.text(x+12.8,64,"×" if i<6 else "",color=MUTED,fontsize=12,fontweight="bold")
    box(ax,18,20,64,15,"ACTION-RISK BAND","categorical floors + quantitative features + uncertainty → S0 / S1 / S2 / S3",edge=GOLD,fill=GOLD_LIGHT,title_color=GOLD,fs=7.7)
    arrow(ax,(49,53),(50,35),color=GOLD)
    ax.text(50,7,"NO SINGLE CONFIDENCE SCORE MAY OVERRIDE AN IRREVERSIBILITY OR SOURCE REQUIREMENT",ha="center",color=RUST,fontsize=6.5,fontweight="bold")
    SYSTEM.save(fig,3)


def f04():
    fig,ax=SYSTEM.setup(4,"Compare constrained expected loss with and without qualified review")
    box(ax,4,55,40,25,"NO REVIEW", "EL₀ = pₐ × L\n.018 × $42,000 = $756",edge=RUST,fill=RUST_LIGHT,title_color=RUST,fs=8)
    box(ax,55,55,40,25,"QUALIFIED REVIEW", "EL_review = C_review + C_delay + p_review × L\n$18 + $65 + .004 × $42,000 = $251",edge=TEAL,fill=TEAL_LIGHT,title_color=TEAL,fs=8)
    box(ax,20,24,60,17,"ILLUSTRATIVE VALUE OF REVIEW","$756 − $251 = $505 avoided expected cost per action",edge=BLUE,fill=BLUE_LIGHT,title_color=BLUE,fs=8)
    ax.text(50,10,"POLICY FLOOR: REVIEW REMAINS REQUIRED IF TAIL LOSS OR DUTY CONSTRAINT IS BREACHED",ha="center",color=GOLD,fontsize=6.4,fontweight="bold")
    SYSTEM.save(fig,4)


def f05():
    fig,ax=SYSTEM.setup(5,"Each class declares queue objective, reviewer pool, and terminal fallback")
    classes=[("S0","NO REVIEW","low impact · reversible","auto + sampled","—",BLUE_LIGHT,BLUE),("S1","ASYNC REVIEW","moderate · non-urgent","domain reviewer","8 h",TEAL_LIGHT,TEAL),("S2","PRIORITY REVIEW","high impact / deadline","senior + limit","15 min",GOLD_LIGHT,GOLD),("S3","INCIDENT REVIEW","containment / irreversible","incident commander","30 s",RUST_LIGHT,RUST)]
    for i,(n,t,b,p,d,fill,c) in enumerate(classes):
        x=2+i*23.5
        box(ax,x,58,21,22,f"{n}  {t}",b,edge=c,fill=fill,title_color=c,fs=6.8)
        box(ax,x,38,21,14,"POOL",p,edge=c,fill=SURFACE,title_color=c,fs=6.2)
        box(ax,x,20,21,14,"WAIT TARGET",d,edge=c,fill=SURFACE,title_color=c,fs=6.2)
        ax.text(x+10.5,11,["execute","expire","deny + escalate","contain + command"][i],ha="center",color=c,fontsize=6.3,fontweight="bold")
    SYSTEM.save(fig,5)


def erlang_c_wait(lam_per_hr, service_min, servers):
    mu=60/service_min; a=lam_per_hr/mu; rho=a/servers
    if rho>=1: return np.inf
    denom=sum(a**k/math.factorial(k) for k in range(servers))+(a**servers/math.factorial(servers))/(1-rho)
    p_wait=((a**servers/math.factorial(servers))/(1-rho))/denom
    return p_wait/(servers*mu-lam_per_hr)*60


def f06():
    fig,ax=SYSTEM.setup(6,"Mean queue wait explodes as offered load approaches effective capacity",plot=True)
    arrivals=np.arange(12,93,10); servers=np.arange(3,11)
    data=np.array([[erlang_c_wait(l,6,int(c)) for l in arrivals] for c in servers])
    clipped=np.where(np.isfinite(data),np.minimum(data,60),60)
    cmap=LinearSegmentedColormap.from_list("wait",[TEAL_LIGHT,BLUE_LIGHT,GOLD_LIGHT,RUST_LIGHT,RUST])
    ax.imshow(clipped,cmap=cmap,vmin=0,vmax=60,aspect="auto")
    for i,c in enumerate(servers):
        for j,l in enumerate(arrivals):
            txt="UNSTABLE" if not np.isfinite(data[i,j]) else f"{data[i,j]:.1f}m"
            ax.text(j,i,txt,ha="center",va="center",fontsize=5.4,color=INK,fontweight="bold")
    ax.set_xticks(range(len(arrivals)),arrivals,fontsize=6); ax.set_yticks(range(len(servers)),servers,fontsize=6); ax.set_xlabel("ARRIVALS / HOUR",fontsize=7,color=MUTED); ax.set_ylabel("QUALIFIED REVIEWERS",fontsize=7,color=MUTED); ax.tick_params(length=0,colors=MUTED)
    SYSTEM.save(fig,6)


def f07():
    fig,ax=SYSTEM.setup(7,"The approval clock contains six observable intervals and a hard expiry")
    points=[(5,"T0","ARRIVE",BLUE),(20,"T1","CLASSIFY",PURPLE),(36,"T2","ASSIGN",GOLD),(52,"T3","OPEN",TEAL),(70,"T4","DECIDE",BLUE),(86,"T5","HANDOFF",TEAL)]
    ax.plot([5,91],[48,48],color=INK,lw=1.2)
    for x,t,l,c in points:
        ax.add_patch(Circle((x,48),2.2,facecolor=c,edgecolor=c)); ax.text(x,56,t,color=c,ha="center",fontsize=7,fontweight="bold"); ax.text(x,39,l,color=INK,ha="center",fontsize=6,fontweight="bold")
    spans=[(5,20,"INTAKE",BLUE),(20,36,"ROUTING",PURPLE),(36,52,"QUEUE",RUST),(52,70,"HANDLE",GOLD),(70,86,"EXECUTE",TEAL)]
    for s,e,t,c in spans:
        ax.annotate("",xy=(e,27),xytext=(s,27),arrowprops=dict(arrowstyle="<->",color=c,lw=1.3)); ax.text((s+e)/2,22,t,color=c,ha="center",fontsize=6.3,fontweight="bold")
    ax.axvline(78,ymin=.25,ymax=.8,color=RUST,lw=1.4,ls="--"); ax.text(78,69,"EXPIRY / REVALIDATE",rotation=90,color=RUST,fontsize=6.3,fontweight="bold",ha="center")
    SYSTEM.save(fig,7)


def f08():
    fig,ax=SYSTEM.setup(8,"Fluid backlog model under under-capacity, matched, and surge staffing",plot=True)
    t=np.linspace(0,8,161); initial=250; arrival=1200
    for cap,name,c in [(900,"UNDER-CAPACITY · 900/h",RUST),(1200,"MATCHED · 1,200/h",GOLD),(1500,"SURGE · 1,500/h",TEAL)]:
        q=np.maximum(0,initial+(arrival-cap)*t)
        ax.plot(t,q,label=name,color=c,lw=2.2)
    ax.axhline(1000,color=RUST,lw=.8,ls="--"); ax.text(7.9,1040,"CRITICAL BACKLOG",ha="right",color=RUST,fontsize=6.5,fontweight="bold")
    ax.set_xlim(0,8); ax.set_ylim(0,2800); ax.set_xlabel("HOURS FROM BURST START",fontsize=7,color=MUTED); ax.set_ylabel("OPEN APPROVALS",fontsize=7,color=MUTED); ax.grid(color=LINE,lw=.5); ax.tick_params(colors=MUTED,labelsize=6); ax.legend(frameon=False,fontsize=6.2)
    SYSTEM.save(fig,8)


def f09():
    fig,ax=SYSTEM.setup(9,"Eligibility edges reveal fragmented capacity and hidden bottlenecks")
    actions=[("PRICING >10%",6,72,RUST),("REFUND >$5K",6,52,GOLD),("ACCOUNT CLOSE",6,32,PURPLE),("DATA EXPORT",6,12,BLUE)]
    pools=[("SR PRICING",76,72,RUST),("FINANCE L2",76,52,GOLD),("RISK OFFICER",76,32,PURPLE),("PRIVACY",76,12,BLUE)]
    for t,x,y,c in actions+pools: box(ax,x,y,18,10,t,"eligible node",edge=c,fill=SURFACE,title_color=c,fs=6.4)
    edges=[(82,77),(82,57),(62,57),(62,37),(42,37),(42,17),(22,17)]
    pairs=[((24,77),(76,77),RUST),((24,57),(76,57),GOLD),((24,57),(76,37),GOLD),((24,37),(76,37),PURPLE),((24,17),(76,17),BLUE),((24,77),(76,37),RUST)]
    for s,e,c in pairs: arrow(ax,s,e,color=c,lw=.9,style="-")
    box(ax,34,2,32,8,"ROUTER","eligibility ∧ limit ∧ jurisdiction ∧ availability",edge=TEAL,fill=TEAL_LIGHT,title_color=TEAL,fs=6.2)
    SYSTEM.save(fig,9)


def f10():
    fig,ax=SYSTEM.setup(10,"Forbidden role combinations prevent self-approval and self-verification")
    roles=[("PROPOSER",10,68,BLUE),("EVIDENCE CURATOR",38,74,PURPLE),("APPROVER",72,68,GOLD),("LEASE ISSUER",82,34,TEAL),("EXECUTOR",50,16,RUST),("VERIFIER",18,34,TEAL)]
    for t,x,y,c in roles:
        ax.add_patch(Circle((x,y),7,facecolor=SURFACE,edgecolor=c,linewidth=1.3)); ax.text(x,y,SYSTEM.wrap(t,14),ha="center",va="center",color=c,fontsize=6.3,fontweight="bold")
    allowed=[((17,68),(65,68),BLUE),((72,61),(78,41),GOLD),((75,34),(57,19),TEAL),((43,18),(25,31),TEAL)]
    for s,e,c in allowed: arrow(ax,s,e,color=c,lw=1.1)
    forbidden=[((10,61),(18,41),"NO SELF-VERIFY"),((17,68),(43,20),"NO SELF-EXECUTE"),((45,74),(67,70),"NO CURATE+APPROVE"),((75,63),(55,21),"NO APPROVE+EXECUTE")]
    for s,e,t in forbidden:
        arrow(ax,s,e,color=RUST,lw=1.1,style="-["); ax.text((s[0]+e[0])/2,(s[1]+e[1])/2,t,color=RUST,fontsize=5.3,fontweight="bold",ha="center")
    SYSTEM.save(fig,10)


def f11():
    fig,ax=SYSTEM.setup(11,"The reviewer signs an exact, expiring decision packet")
    box(ax,30,36,40,28,"EXACT DELTA","quote:771 · discount 0% → 8% · expected v20",edge=BLUE,fill=BLUE_LIGHT,title_color=BLUE,fs=8)
    panels=[(3,65,"EVIDENCE","3 sources · 1 conflict",TEAL),(3,30,"UNCERTAINTY","OOD .18 · score .87",PURPLE),(76,65,"POLICY","S2 · senior pricing",GOLD),(76,30,"RECOVERY","revert quote · notify",RUST)]
    for x,y,t,b,c in panels: box(ax,x,y,20,17,t,b,edge=c,fill=SURFACE,title_color=c,fs=6.5); arrow(ax,(x+20 if x<30 else x,y+8.5),(30 if x<30 else 70,y+8.5),color=c,lw=.8)
    choices=[(24,"DENY",RUST),(43,"EDIT",GOLD),(62,"APPROVE",TEAL)]
    for x,t,c in choices: box(ax,x,10,15,10,t,"sign packet hash",edge=c,fill={RUST:RUST_LIGHT,GOLD:GOLD_LIGHT,TEAL:TEAL_LIGHT}[c],title_color=c,fs=6.5)
    SYSTEM.save(fig,11)


def f12():
    fig,ax=SYSTEM.setup(12,"Support factors and explicit penalties produce a review-routing signal")
    factors=[("REQUIRED SOURCE",.90,.30,BLUE),("FRESHNESS",.82,.20,TEAL),("CORROBORATION",.70,.20,GOLD),("PROVENANCE",1.0,.15,PURPLE)]
    weighted=0
    for i,(t,v,w,c) in enumerate(factors):
        x=3+i*22.5; box(ax,x,57,19,20,t,f"{v:.2f} × {w:.2f}",edge=c,fill=SURFACE,title_color=c,fs=6.3); cont=v*w; weighted+=cont; ax.text(x+9.5,61,f"{cont:.3f}",ha="center",color=INK,fontsize=8,fontweight="bold")
    penalty=.25*.20+.18*.15
    box(ax,12,26,33,15,"WEIGHTED SUPPORT",f"Σ = {weighted:.3f}",edge=TEAL,fill=TEAL_LIGHT,title_color=TEAL,fs=7.5)
    box(ax,55,26,33,15,"PENALTIES",f"conflict + uncertainty = {penalty:.3f}",edge=RUST,fill=RUST_LIGHT,title_color=RUST,fs=7.5)
    result=weighted-penalty
    box(ax,31,5,38,10,"EVIDENCE QUALITY",f"E = {result:.3f} → DEEP REVIEW",edge=GOLD,fill=GOLD_LIGHT,title_color=GOLD,fs=7.3)
    SYSTEM.save(fig,12)


def f13():
    fig,ax=SYSTEM.setup(13,"Stop review when marginal decision benefit falls below labor and delay cost",plot=True)
    mins=np.linspace(0,30,120)
    for scale,name,c in [(80,"LOW RISK",BLUE),(260,"MEDIUM RISK",GOLD),(800,"HIGH RISK",RUST)]:
        benefit=scale*(1-np.exp(-mins/8)); cost=6*mins+0.12*mins**2; net=benefit-cost
        ax.plot(mins,net,label=name,color=c,lw=2.2)
        idx=np.argmax(net); ax.scatter([mins[idx]],[net[idx]],color=c,s=28,zorder=3); ax.text(mins[idx],net[idx]+18,f"stop {mins[idx]:.0f}m",color=c,fontsize=6,ha="center",fontweight="bold")
    ax.axhline(0,color=INK,lw=.7); ax.set_xlabel("REVIEW MINUTES",fontsize=7,color=MUTED); ax.set_ylabel("SYNTHETIC EXPECTED NET VALUE ($)",fontsize=7,color=MUTED); ax.grid(color=LINE,lw=.5); ax.tick_params(colors=MUTED,labelsize=6); ax.legend(frameon=False,fontsize=6.3)
    SYSTEM.save(fig,13)


def f14():
    fig,ax=SYSTEM.setup(14,"Synthetic miss probability rises as uninterrupted review streak lengthens",plot=True)
    n=np.arange(1,101); miss=.012+.000012*n**1.75; handle=155-35*(1-np.exp(-n/25))
    ax.plot(n,miss*100,color=RUST,lw=2.2,label="MISS PROBABILITY (%)")
    ax.set_xlabel("CONSECUTIVE DECISIONS WITHOUT ROTATION / BREAK",fontsize=7,color=MUTED); ax.set_ylabel("SYNTHETIC MISS PROBABILITY (%)",fontsize=7,color=RUST); ax.tick_params(colors=MUTED,labelsize=6); ax.grid(color=LINE,lw=.5)
    ax2=ax.twinx(); ax2.plot(n,handle,color=BLUE,lw=2,ls="--",label="MEDIAN HANDLE TIME"); ax2.tick_params(colors=BLUE,labelsize=6,direction="in",pad=-28)
    ax.text(98,1.35,"BLUE AXIS: HANDLE TIME (SECONDS)",ha="right",color=BLUE,fontsize=6.2,fontweight="bold")
    ax.axvspan(60,100,color=RUST_LIGHT,alpha=.5); ax.text(80,max(miss*100)*.9,"FATIGUE WATCH",ha="center",color=RUST,fontsize=7,fontweight="bold")
    lines=ax.get_lines()+ax2.get_lines(); ax.legend(lines,[l.get_label() for l in lines],frameon=False,fontsize=6.2,loc="upper center")
    SYSTEM.save(fig,14)


def f15():
    fig,ax=SYSTEM.setup(15,"Risk-constrained threshold minimizes total review, delay, and residual-loss cost",plot=True)
    rng=np.random.default_rng(10); n=50000; scores=rng.beta(2.1,6.2,n); loss=200+48000*scores**2.4
    thresholds=np.linspace(.05,.95,80); review_rate=[]; total=[]; residual=[]
    for th in thresholds:
        review=scores>=th; rr=review.mean(); review_cost=rr*24; delay=rr*18; residual_cost=np.mean(loss*(~review)*(.012+.11*scores)); review_rate.append(rr); total.append(review_cost+delay+residual_cost); residual.append(residual_cost)
    review_rate=np.array(review_rate)*100; total=np.array(total); residual=np.array(residual)
    ax.plot(review_rate,total,color=BLUE,lw=2.2,label="TOTAL COST INDEX"); ax.plot(review_rate,residual,color=RUST,lw=1.8,ls="--",label="RESIDUAL LOSS")
    feasible=residual<35; idx=np.argmin(np.where(feasible,total,np.inf)); ax.scatter([review_rate[idx]],[total[idx]],color=TEAL,s=45,zorder=3); ax.text(review_rate[idx],total[idx]+3,"risk-constrained minimum",ha="center",color=TEAL,fontsize=6.2,fontweight="bold")
    ax.set_xlabel("ACTIONS SENT TO REVIEW (%)",fontsize=7,color=MUTED); ax.set_ylabel("SYNTHETIC COST / ACTION ($)",fontsize=7,color=MUTED); ax.grid(color=LINE,lw=.5); ax.tick_params(colors=MUTED,labelsize=6); ax.legend(frameon=False,fontsize=6.2)
    SYSTEM.save(fig,15)


def f16():
    fig,ax=SYSTEM.setup(16,"Risk-weighted disagreement reveals false-autonomy cases",plot=True)
    data=np.array([[7820,210],[560,1410]])
    cmap=LinearSegmentedColormap.from_list("cm",[TEAL_LIGHT,BLUE_LIGHT,GOLD_LIGHT,RUST_LIGHT])
    ax.imshow([[0,3],[2,1]],cmap=cmap,aspect="auto")
    labels=[["SAFE AUTOMATE","FALSE AUTONOMY"],["FALSE ESCALATION","CORRECT ESCALATE"]]
    for i in range(2):
        for j in range(2): ax.text(j,i,f"{labels[i][j]}\n{data[i,j]:,}\n{data[i,j]/100:.1f}%",ha="center",va="center",fontsize=8,color=INK,fontweight="bold")
    ax.set_xticks([0,1],["ADJUDICATED SAFE","ADJUDICATED REVIEW"],fontsize=6.3); ax.set_yticks([0,1],["AUTO DECISION","REVIEW DECISION"],fontsize=6.3); ax.set_xlabel("ADJUDICATED OUTCOME",fontsize=7,color=MUTED); ax.set_ylabel("SYSTEM ROUTE",fontsize=7,color=MUTED); ax.tick_params(length=0,colors=MUTED)
    SYSTEM.save(fig,16)


def f17():
    fig,ax=SYSTEM.setup(17,"Every service objective has a class, owner, and escalation")
    rows=[("S2 P95 WAIT","≤15m","22m","OPS","BREACH"),("S3 P99 WAIT","≤30s","27s","INCIDENT","PASS"),("ELIGIBLE ROUTING","100%","100%","IAM","PASS"),("EXPIRED APPROVAL","0","0","PLATFORM","PASS"),("FALSE AUTONOMY","≤0.20%","0.24%","RISK","BREACH"),("APPEAL OVERTURN","≤4%","3.2%","QUALITY","PASS"),("PACKET COVERAGE","≥99.5%","99.7%","PRODUCT","PASS"),("FATIGUE ROTATION","≥98%","98.6%","OPS","PASS")]
    for h,x in [("OBJECTIVE",3),("TARGET",46),("ACTUAL",61),("OWNER",76),("STATE",90)]: ax.text(x,81,h,color=BLUE,fontsize=6.4,fontweight="bold")
    for i,row in enumerate(rows):
        y=70-i*8.2;c=TEAL if row[4]=="PASS" else RUST; ax.add_patch(Rectangle((2,y-3),95,7,facecolor=SURFACE if i%2==0 else PAPER,edgecolor=LINE,lw=.4))
        for txt,x in zip(row,[3,46,61,76,90]): ax.text(x,y,txt,color=c if x==90 else INK,fontsize=6.2,fontweight="bold" if x in [3,90] else "normal",va="center")
        ax.add_patch(Circle((87,y),1.5,facecolor=c,edgecolor=c))
    SYSTEM.save(fig,17)


def f18():
    fig,ax=SYSTEM.setup(18,"Approval maturity increases only after demand, capacity, and quality are measured")
    phases=[("0","INVENTORY","hidden queues","map owners",BLUE),("1","INSTRUMENT","timestamps + outcomes","baseline",PURPLE),("2","CLASSIFY","risk + service class","policy review",GOLD),("3","ROUTE","skills + deadlines","queue SLO",TEAL),("4","CALIBRATE","shadow + adjudicate","false autonomy",TEAL),("5","EXPAND","bounded autonomy","independent review",BLUE)]
    for i,(n,t,b,g,c) in enumerate(phases):
        x=2+i*15.7;y=17+i*9;box(ax,x,y,14,23,f"{n}  {t}",b,edge=c,fill=SURFACE,title_color=c,fs=6.5);ax.text(x+7,y+4,SYSTEM.wrap("GATE: "+g,18),ha="center",va="center",color=GOLD,fontsize=5.8,fontweight="bold")
        if i<5:arrow(ax,(x+14,y+11),(x+15.7,y+20),color=c)
    ax.plot([2,95],[10,10],color=RUST,lw=1.2);ax.text(48.5,5,"BREACH → NARROW ACTION CLASS · ADD CAPACITY · RECALIBRATE BEFORE PROMOTION",ha="center",color=RUST,fontsize=6.5,fontweight="bold")
    SYSTEM.save(fig,18)


def main():SYSTEM.render([f01,f02,f03,f04,f05,f06,f07,f08,f09,f10,f11,f12,f13,f14,f15,f16,f17,f18])
if __name__=="__main__":main()
