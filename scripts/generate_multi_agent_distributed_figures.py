#!/usr/bin/env python3
"""Generate 18 deep-dive figures for the multi-agent distributed-systems story."""

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

ROOT=Path(__file__).resolve().parents[1]
SLUG="your-multi-agent-system-is-a-distributed-system"
OUT=ROOT/"assets"/"images"/SLUG
MAP_PATH=ROOT/"stories"/f"{SLUG}-figure-map.md"

def S(n,t,f,k,d,i,c,a="Reference architecture; no observed production data.",core=True):return FigureSpec(n,t,f,k,d,tuple(i),tuple(c),a,core)

SPECS=[
S(1,"Multi-agent fluency is not coordination","Comparison","Polite message exchange does not provide ownership, order, atomicity, idempotency, or recoverable business effects.","SYSTEM MODEL",["Natural-language delegation leaves invariants implicit.","Retries and timeouts create duplicate or ambiguous work.","Durable workflow state and domain controls—not conversational tone—provide reliability."],[("CHAT","intent exchange"),("SYSTEM","state + invariants"),("OUTPUT","verified workflow")]),
S(2,"Multi-agent renewal topology","Architecture","Specialized agents coordinate through a durable workflow and domain APIs rather than granting peers direct shared-state mutation.","TOPOLOGY",["The orchestrator owns workflow state, not every domain decision.","Domain services enforce idempotency, versions, and authority independently.","Events, receipts, and reconciliation make partial effects visible."],[("AGENTS","6 specialists"),("CONTROL","durable workflow"),("DOMAINS","systems of record")]),
S(3,"Coordination invariant map","Invariant map","Every consequential workflow needs explicit ownership, uniqueness, ordering, state, authority, effect, and recovery invariants.","INVARIANTS",["An invariant is testable under faults; a prompt instruction is not.","Different domains own different truth and atomicity boundaries.","The receipt joins proof without pretending the whole workflow is one transaction."],[("COUNT","8 invariants"),("SCOPE","workflow + domain"),("TEST","fault injection")]),
S(4,"Versioned agent-message envelope","Structured schema","A message needs stable workflow, action, step, attempt, causal parent, schema, expiry, authority, and payload digests.","MESSAGE CONTRACT",["Message identity differs from business action identity.","Attempt number helps operations but never becomes the idempotency key.","Consumers reject unknown schema, expired authority, and stale fencing epochs."],[("KEY","message_id"),("BUSINESS","action_id + step"),("ORDER","causal_parent + epoch")]),
S(5,"Orchestration versus choreography","Decision matrix","Use choreography for decoupled facts and orchestration for constrained multi-step business invariants; combine them deliberately.","TOPOLOGY CHOICE",["Central control improves visibility but can become a bottleneck.","Choreography reduces coupling but hides global progress and compensation.","Hybrid designs publish domain facts while a durable workflow owns completion."],[("ROWS","7 decision factors"),("OPTIONS","orchestrate · choreograph"),("DEFAULT","hybrid by invariant")],"Ordinal architectural comparison; not measured performance."),
S(6,"Ownership lease and failover timeline","Lease timeline","A durable lease limits ownership in time, but takeover is safe only when stale owners are fenced from writes.","OWNERSHIP",["Heartbeat renewal is an availability mechanism—not proof of exclusive effect.","A new owner increments the fencing epoch.","The old worker may continue running and must be rejected downstream."],[("LEASE","owner + expiry"),("TAKEOVER","epoch 42 → 43"),("GUARD","domain rejects stale")]),
S(7,"Fencing-token enforcement sequence","Sequence","Every protected write carries a monotonically increasing epoch so a paused former owner cannot commit after takeover.","FENCING",["Lease expiry alone does not stop a partitioned worker.","The domain stores the highest accepted epoch with workflow state.","Retries in the current epoch still require action-level idempotency."],[("TOKEN","monotonic epoch"),("CHECK","epoch ≥ stored"),("RESULT","accept or stale-owner reject")]),
S(8,"Durable workflow as a replicated state machine","State machine","Workflow commands become committed state transitions before side-effect workers act, allowing restart and deterministic replay.","DURABILITY",["Consensus belongs in the state store, not agent conversation.","Committed command order and application state are distinct.","External effects still require idempotency and reconciliation."],[("LOG","ordered commands"),("APPLY","deterministic state"),("EFFECT","outbox + worker")]),
S(9,"Delivery semantics versus business guarantees","Comparison matrix","At-most-once, at-least-once, and ordered delivery each leave application responsibilities; none alone creates exactly-once business outcome.","DELIVERY",["At-most-once can lose work.","At-least-once duplicates delivery and demands idempotency.","Ordered streams do not order effects across partitions or external systems."],[("ROWS","4 semantics"),("COLS","loss · duplicate · order"),("NEED","domain invariant")]),
S(10,"Idempotency ledger for every effect","Structured ledger","A stable business action ID and proposal digest turn redelivery into a recorded result rather than a second effect.","IDEMPOTENCY",["Reserve before effect and store result atomically where possible.","Same key with different intent is a conflict.","Ambiguous outcomes remain non-reusable until reconciled."],[("KEY","workflow + action"),("BIND","proposal digest"),("STATE","reserved → terminal")]),
S(11,"Concurrent quote update race","Timeline","Optimistic concurrency prevents pricing and contracting agents from overwriting each other's decisions on stale state.","CONCURRENCY",["Both agents can be authorized yet one proposal is stale.","Field-level merge is policy, not a generic last-write-wins rule.","The losing action re-reads, re-evaluates, and obtains new authority."],[("READ","both see v20"),("WIN","pricing commits v21"),("LOSE","contract If-Match v20 → 409")]),
S(12,"Causal ordering across agent events","Causal graph","Causal parents and resource versions prevent a late message from reversing a later business decision.","ORDERING",["Wall-clock timestamps are insufficient under skew and delay.","Causal metadata identifies what a command depended on.","Concurrent events need a domain merge or conflict rule."],[("MODEL","happens-before"),("CONCURRENT","no causal edge"),("RESOLVE","domain policy")]),
S(13,"Renewal saga state machine","Saga","Long-lived workflows commit local transactions and use explicit compensations when later steps fail.","SAGA",["A saga is not global atomicity.","Every forward step and compensation has its own receipt.","Irreversible customer effects may require human remediation rather than reversal."],[("FORWARD","6 local transactions"),("FAILURE","billing reject"),("RECOVERY","compensate in policy order")]),
S(14,"Compensation dependency graph","Recovery graph","Compensations run by dependency and business risk—not blindly in reverse message order.","COMPENSATION",["Reverting a quote may depend on cancelling billing first.","A sent message receives correction, not erasure.","Compensation failure creates a durable intervention task."],[("ROOT","failed invariant"),("PLAN","dependency DAG"),("EXIT","recovered or escalated")]),
S(15,"Split-brain failure tree","Failure tree","Duplicate owners emerge from partition, delayed lease observation, clock assumptions, or state-store failover; fencing contains their writes.","SPLIT BRAIN",["Health checks cannot prove global uniqueness.","Clock-based expiry without bounded assumptions can overlap ownership.","Default-deny domains and fencing reduce effect even when execution continues."],[("TOP","two active owners"),("CAUSES","4 branches"),("BREAK","epoch + idempotency")]),
S(16,"Coordination chaos-test matrix","Test matrix","Fault injection must cover messages, workers, stores, clocks, domains, and compensations while asserting business invariants.","CHAOS",["A green model response is irrelevant if the domain effect duplicates.","Each scenario declares injection point and authoritative oracle.","Tests continue through recovery, not only initial failure detection."],[("ROWS","8 fault scenarios"),("COLS","7 assertions"),("RESULT","pass · breach")],"Reference test matrix with intentionally mixed pass/breach cells; no production test results."),
S(17,"Multi-agent coordination objectives","SLO scorecard","Duplicate effects, stale-owner rejects, ambiguity age, saga recovery, and invariant breaches need independent objectives.","OPERATIONS",["Agent task success rate can hide partial business failure.","Rejection by fencing is evidence the control worked—not merely an error.","Unresolved sagas are risk backlog with owners and deadlines."],[("WINDOW","synthetic 30 days"),("STATUS","6 pass · 2 breach"),("ACTION","contain + reconcile")],"Synthetic 30-day window with deliberate ambiguity-age and compensation breaches."),
S(18,"Migration to durable multi-agent coordination","Maturity roadmap","Teams should stabilize one-agent business effects before adding specialized agents and distributed ownership.","MIGRATION",["Inventory shared state and hidden retry paths.","Introduce stable action IDs, versions, and durable workflow state first.","Add agents only when domain invariants and recovery are proven under faults."],[("PHASES","0 through 5"),("GATE","invariant evidence"),("ROLLBACK","workflow slice")]),
]
SYSTEM=FigureSystem(SLUG,OUT,MAP_PATH,"Your Multi-Agent System Is a Distributed System",SPECS)

def f01():
    fig,ax=SYSTEM.setup(1,"Same agents; different reliability contract")
    dims=["OWNER","STATE","ORDER","RETRY","EFFECT","FAILURE","RECOVERY"]
    for x,t,c,fill,vals in [(3,"AGENT CONVERSATION",RUST,RUST_LIGHT,["whoever responds","chat history","arrival time","ask again","assumed","exception text","try another agent"]),(52,"DISTRIBUTED WORKFLOW",TEAL,TEAL_LIGHT,["leased + fenced","durable machine","causal + version","idempotent","verified","explicit state","saga + reconcile"] )]:
        box(ax,x,74,43,10,t,"coordination contract",edge=c,fill=fill,title_color=c,fs=8)
        for i,(d,v) in enumerate(zip(dims,vals)):
            y=65-i*8;box(ax,x,y,43,6,d,edge=LINE,fill=SURFACE,fs=6.2);ax.text(x+40.5,y+3,v,ha="right",va="center",color=c,fontsize=6.1,fontweight="bold")
    ax.text(49,39,"≠",ha="center",color=GOLD,fontsize=28,fontweight="bold")
    SYSTEM.save(fig,1)

def f02():
    fig,ax=SYSTEM.setup(2,"Six specialists act through one durable workflow and domain-owned controls")
    agents=[("SALES",2,76,BLUE),("PRICING",2,61,GOLD),("CONTRACT",2,46,PURPLE),("BILLING",2,31,TEAL),("FULFILL",2,16,BLUE),("COMMS",2,1,RUST)]
    for t,x,y,c in agents:box(ax,x,y,14,10,t,"specialist agent",edge=c,fill=SURFACE,title_color=c,fs=6.2)
    box(ax,24,33,29,30,"DURABLE WORKFLOW","state · owner · epoch · steps\noutbox · receipts · recovery",edge=PURPLE,fill=PURPLE_LIGHT,title_color=PURPLE,fs=8)
    domains=[("CRM",64,68,BLUE),("CPQ",82,68,GOLD),("CONTRACT",64,42,PURPLE),("BILLING",82,42,TEAL),("FULFILL",64,16,BLUE),("MESSAGING",82,16,RUST)]
    for t,x,y,c in domains:box(ax,x,y,14,11,t,"system of record",edge=c,fill=SURFACE,title_color=c,fs=6.2)
    for _,x,y,c in agents:arrow(ax,(16,y+5),(24,48),color=c,lw=.6)
    for _,x,y,c in domains:arrow(ax,(53,48),(x,y+5),color=c,lw=.7)
    SYSTEM.save(fig,2)

def f03():
    fig,ax=SYSTEM.setup(3,"Eight testable invariants replace informal coordination assumptions")
    items=[("OWNERSHIP","≤1 accepted epoch",BLUE),("UNIQUENESS","≤1 effect / action",TEAL),("ORDER","precondition holds",PURPLE),("DURABILITY","committed state survives",BLUE),("AUTHORITY","current bounded lease",GOLD),("EFFECT","postcondition observed",TEAL),("LINEAGE","receipt resolves",PURPLE),("RECOVERY","no orphan saga",RUST)]
    for i,(t,b,c) in enumerate(items):
        x=3+(i%4)*24;y=54-(i//4)*32;box(ax,x,y,21,24,t,b,edge=c,fill=SURFACE,title_color=c,fs=6.8);ax.text(x+10.5,y+5,"ASSERT UNDER FAULT",ha="center",color=RUST,fontsize=5.4,fontweight="bold")
    SYSTEM.save(fig,3)

def f04():
    fig,ax=SYSTEM.setup(4,"Identity, business intent, causality, authority, and expiry travel together")
    groups=[("IDENTITY",BLUE,[("message_id","msg_92"),("workflow_id","wf_42"),("action_id","A7")]),("STEP",TEAL,[("step","price.apply"),("attempt","2"),("schema","v3")]),("ORDER",PURPLE,[("parent","msg_88"),("epoch","43"),("resource_v","20")]),("AUTHORITY",GOLD,[("lease","l_71"),("expires","10:42:30"),("actor","pricing-agent")]),("PAYLOAD",BLUE,[("proposal","sha256…"),("evidence","sha256…"),("content","vault:91")]),("DELIVERY",RUST,[("created","10:42:01"),("not_after","10:42:20"),("dedupe","A7")])]
    for i,(t,c,fields) in enumerate(groups):
        x=3+(i%3)*31;y=52-(i//3)*38;box(ax,x,y,28,30,t,edge=c,fill=SURFACE,title_color=c,fs=7)
        for j,(k,v) in enumerate(fields):ax.text(x+2,y+18-j*6,k,color=MUTED,fontsize=5.8,fontweight="bold");ax.text(x+26,y+18-j*6,v,color=INK,fontsize=5.8,ha="right",family="monospace")
    SYSTEM.save(fig,4)

def f05():
    fig,ax=SYSTEM.setup(5,"Choose topology from invariants, coupling, visibility, and recovery",plot=True)
    fig.subplots_adjust(left=.115,right=.745,top=.82,bottom=.11)
    rows=["GLOBAL INVARIANT","DOMAIN AUTONOMY","END-TO-END VISIBILITY","CHANGE COUPLING","EVENT FANOUT","COMPENSATION","HOT-PATH LATENCY"]
    cols=["ORCHESTRATION","CHOREOGRAPHY","HYBRID"]
    data=np.array([[4,1,4],[2,4,4],[4,1,4],[1,4,3],[2,4,4],[4,1,4],[2,4,3]])
    cmap=LinearSegmentedColormap.from_list("choice",[RUST_LIGHT,GOLD_LIGHT,BLUE_LIGHT,TEAL_LIGHT,TEAL])
    ax.imshow(data,cmap=cmap,vmin=0,vmax=4,aspect="auto")
    labels={1:"WEAK",2:"LIMITED",3:"STRONG",4:"PRIMARY"}
    for i in range(len(rows)):
        for j in range(3):ax.text(j,i,labels[data[i,j]],ha="center",va="center",fontsize=6.5,color=INK,fontweight="bold")
    ax.set_xticks(range(3),cols,fontsize=6.5);ax.set_yticks(range(len(rows)),rows,fontsize=5.8);ax.tick_params(length=0,colors=MUTED)
    SYSTEM.save(fig,5)

def f06():
    fig,ax=SYSTEM.setup(6,"A partitioned worker survives lease expiry; epoch takeover fences its effects")
    ax.plot([5,94],[55,55],color=INK,lw=1)
    events=[(8,"T0","worker A owns\nepoch 42",BLUE),(28,"T1","partition",RUST),(48,"T2","lease expires",GOLD),(65,"T3","worker B takes\nepoch 43",TEAL),(86,"T4","A resumes stale",RUST)]
    for x,t,b,c in events:
        ax.add_patch(Circle((x,55),2.2,facecolor=c,edgecolor=c));ax.text(x,67,t,ha="center",color=c,fontsize=7,fontweight="bold");ax.text(x,44,b,ha="center",color=INK,fontsize=6)
    ax.add_patch(Rectangle((8,73),40,7,facecolor=BLUE_LIGHT,edgecolor=BLUE));ax.text(28,76.5,"LEASE A · EPOCH 42",ha="center",va="center",color=BLUE,fontsize=6.5,fontweight="bold")
    ax.add_patch(Rectangle((65,73),29,7,facecolor=TEAL_LIGHT,edgecolor=TEAL));ax.text(79.5,76.5,"LEASE B · EPOCH 43",ha="center",va="center",color=TEAL,fontsize=6.5,fontweight="bold")
    box(ax,66,15,28,12,"DOMAIN FENCE","reject A(epoch 42) < stored 43",edge=RUST,fill=RUST_LIGHT,title_color=RUST,fs=6.7)
    SYSTEM.save(fig,6)

def f07():
    fig,ax=SYSTEM.setup(7,"The resource domain—not the lease client—enforces ownership epoch")
    actors=[("STATE STORE",8,BLUE),("WORKER A",30,RUST),("WORKER B",52,TEAL),("DOMAIN API",76,GOLD),("LEDGER",93,PURPLE)]
    for t,x,c in actors:ax.text(x,82,t,ha="center",color=c,fontsize=6,fontweight="bold");ax.plot([x,x],[12,78],color=LINE,lw=.8,ls="--")
    msgs=[(8,30,70,"lease epoch 42",BLUE),(8,52,61,"takeover epoch 43",TEAL),(52,76,52,"write A7 · e43",TEAL),(76,93,44,"store max_epoch=43",GOLD),(30,76,34,"late write A6 · e42",RUST),(76,30,25,"REJECT STALE_OWNER",RUST),(52,76,16,"retry A7 · e43",TEAL)]
    for s,e,y,t,c in msgs:arrow(ax,(s,y),(e,y),color=c);ax.text((s+e)/2,y+2,t,ha="center",color=c,fontsize=5.4,fontweight="bold")
    SYSTEM.save(fig,7)

def f08():
    fig,ax=SYSTEM.setup(8,"Committed commands drive deterministic state; effects leave through an outbox")
    nodes=[(3,"CLIENT COMMAND","advance wf42",BLUE),(23,"CONSENSUS LOG","term · index · command",PURPLE),(44,"COMMITTED INDEX","majority durable",GOLD),(64,"STATE MACHINE","deterministic apply",TEAL),(84,"OUTBOX","effect intent",RUST)]
    for x,t,b,c in nodes:
        box(ax,x,57,15,17,t,b,edge=c,fill=SURFACE,title_color=c,fs=6.2)
        if x<84:arrow(ax,(x+15,65.5),(x+20,65.5),color=c)
    replicas=[("R1",26,26),("R2",45,26),("R3",64,26)]
    for t,x,y in replicas:box(ax,x,y,14,12,t,"same committed prefix",edge=PURPLE,fill=PURPLE_LIGHT,title_color=PURPLE,fs=6.2);arrow(ax,(50,57),(x+7,y+12),color=PURPLE,lw=.7)
    box(ax,32,5,36,9,"EFFECT WORKER","idempotency + authority + precondition + receipt",edge=TEAL,fill=TEAL_LIGHT,title_color=TEAL,fs=6.5);arrow(ax,(91.5,57),(68,14),color=RUST)
    SYSTEM.save(fig,8)

def f09():
    fig,ax=SYSTEM.setup(9,"Transport semantics leave different application obligations",plot=True)
    fig.subplots_adjust(left=.115,right=.745,top=.82,bottom=.14)
    rows=["AT-MOST-ONCE","AT-LEAST-ONCE","PARTITION ORDERED","TRANSACTIONAL OUTBOX"]
    cols=["MAY LOSE","MAY DUPLICATE","LOCAL ORDER","CROSS-DOMAIN ORDER","NEEDS IDEMPOTENCY","NEEDS RECONCILE"]
    data=np.array([[4,0,1,0,2,4],[1,4,1,0,4,4],[1,4,4,1,4,4],[1,4,4,1,4,3]])
    cmap=LinearSegmentedColormap.from_list("delivery",[TEAL_LIGHT,BLUE_LIGHT,GOLD_LIGHT,RUST_LIGHT,RUST])
    ax.imshow(data,cmap=cmap,vmin=0,vmax=4,aspect="auto")
    for i in range(4):
        for j in range(6):ax.text(j,i,["NO","LOW","SOME","HIGH","YES"][data[i,j]],ha="center",va="center",fontsize=6,color=INK,fontweight="bold")
    ax.set_xticks(range(6),cols,fontsize=5.4,rotation=25,ha="right");ax.set_yticks(range(4),rows,fontsize=6);ax.tick_params(length=0,colors=MUTED)
    SYSTEM.save(fig,9)

def f10():
    fig,ax=SYSTEM.setup(10,"One ledger record binds intent, reservation, attempts, effect, and terminal result")
    stages=[("ABSENT","no action A7",BLUE),("RESERVED","digest P7 · epoch43",PURPLE),("EXECUTING","attempts 1..n",GOLD),("AMBIGUOUS","effect unknown",RUST),("VERIFIED","effect v21",TEAL)]
    for i,(t,b,c) in enumerate(stages):
        x=2+i*19.2;y=55-(i%2)*8;box(ax,x,y,17,19,t,b,edge=c,fill=SURFACE,title_color=c,fs=6.6)
        if i<4:arrow(ax,(x+17,y+9.5),(x+19.2,y+17 if (i+1)%2 else y+2),color=c)
    fields=[("KEY","tenant · workflow · action"),("BIND","proposal_sha256"),("GUARD","max_epoch · resource_v"),("RESULT","status · response · receipt")]
    for i,(k,v) in enumerate(fields):box(ax,8+i*22,17,20,12,k,v,edge=TEAL,fill=TEAL_LIGHT,title_color=TEAL,fs=6.2)
    SYSTEM.save(fig,10)

def f11():
    fig,ax=SYSTEM.setup(11,"Two authorized agents read v20; only one conditional write may commit")
    ax.plot([6,94],[47,47],color=INK,lw=1)
    events=[(8,"T0","pricing reads v20",BLUE),(28,"T1","contract reads v20",PURPLE),(50,"T2","pricing writes 8%",TEAL),(70,"T3","CRM commits v21",TEAL),(90,"T4","contract write v20",RUST)]
    for x,t,b,c in events:ax.add_patch(Circle((x,47),2.2,facecolor=c,edgecolor=c));ax.text(x,59,t,ha="center",color=c,fontsize=7,fontweight="bold");ax.text(x,36,b,ha="center",color=INK,fontsize=5.8)
    box(ax,10,71,35,9,"PROPOSAL P","discount 0 → 8 · If-Match v20",edge=BLUE,fill=BLUE_LIGHT,title_color=BLUE,fs=6.4)
    box(ax,55,71,35,9,"PROPOSAL C","term edit · If-Match v20",edge=PURPLE,fill=PURPLE_LIGHT,title_color=PURPLE,fs=6.4)
    box(ax,65,11,29,11,"CONFLICT","409 · re-read v21 · re-evaluate",edge=RUST,fill=RUST_LIGHT,title_color=RUST,fs=6.4)
    SYSTEM.save(fig,11)

def f12():
    fig,ax=SYSTEM.setup(12,"Causal parents distinguish ordered dependencies from concurrent work")
    nodes=[("A CRM READ",8,66,BLUE),("B PRICE PROPOSE",32,66,GOLD),("C CONTRACT READ",8,24,PURPLE),("D TERM PROPOSE",32,24,PURPLE),("E PRICE COMMIT",60,66,TEAL),("F MESSAGE",83,45,RUST),("G TERM CONFLICT",60,24,RUST)]
    for t,x,y,c in nodes:box(ax,x,y,16,10,t,"version / parent",edge=c,fill=SURFACE,title_color=c,fs=5.9)
    for s,e,c in [((24,71),(32,71),BLUE),((48,71),(60,71),GOLD),((24,29),(32,29),PURPLE),((48,29),(60,29),PURPLE),((76,71),(83,50),TEAL),((76,29),(83,45),RUST)]:arrow(ax,s,e,color=c)
    ax.text(45,47,"B ∥ D\nCONCURRENT",ha="center",color=GOLD,fontsize=7,fontweight="bold");ax.plot([40,50],[50,50],color=GOLD,lw=1,ls="--")
    SYSTEM.save(fig,12)

def f13():
    fig,ax=SYSTEM.setup(13,"Six local transactions and policy-defined compensations form the renewal saga")
    forward=[("RESERVE QUOTE",BLUE),("APPLY PRICE",GOLD),("SIGN TERM",PURPLE),("ADJUST BILL",TEAL),("FULFILL",BLUE),("NOTIFY",RUST)]
    for i,(t,c) in enumerate(forward):
        x=2+i*15.7;box(ax,x,59,14,16,f"T{i+1}",t,edge=c,fill=SURFACE,title_color=c,fs=6.2)
        if i<5:arrow(ax,(x+14,67),(x+15.7,67),color=c)
    ax.text(58,50,"BILLING REJECTS",color=RUST,fontsize=7,fontweight="bold",ha="center");arrow(ax,(58,59),(58,40),color=RUST)
    comps=[("C3 RELEASE TERM",PURPLE),("C2 REVERT PRICE",GOLD),("C1 RELEASE QUOTE",BLUE)]
    for i,(t,c) in enumerate(comps):
        x=50-i*20;box(ax,x,20,18,12,t,"verified compensation",edge=c,fill={PURPLE:PURPLE_LIGHT,GOLD:GOLD_LIGHT,BLUE:BLUE_LIGHT}[c],title_color=c,fs=5.8)
        if i<2:arrow(ax,(x,26),(x-2,26),color=c)
    box(ax,70,18,24,15,"HUMAN REMEDIATION","if external commitment cannot reverse",edge=RUST,fill=RUST_LIGHT,title_color=RUST,fs=6.2)
    SYSTEM.save(fig,13)

def f14():
    fig,ax=SYSTEM.setup(14,"Recovery order follows dependencies and customer impact")
    root=(47,72);ax.add_patch(Circle(root,7,facecolor=RUST_LIGHT,edgecolor=RUST,linewidth=1.3));ax.text(*root,"FAILED\nINVARIANT",ha="center",va="center",color=RUST,fontsize=7,fontweight="bold")
    nodes=[("CANCEL BILLING",10,46,TEAL),("REVERT QUOTE",38,46,GOLD),("RELEASE CONTRACT",66,46,PURPLE),("CORRECT MESSAGE",80,18,RUST),("VERIFY ACCOUNT",38,16,BLUE)]
    for t,x,y,c in nodes:box(ax,x,y,18,11,t,"receipt + postcondition",edge=c,fill=SURFACE,title_color=c,fs=5.8)
    for s,e,c in [((47,65),(19,57),TEAL),((47,65),(47,57),GOLD),((47,65),(75,57),PURPLE),((19,46),(47,27),TEAL),((47,46),(47,27),GOLD),((75,46),(89,29),PURPLE),((89,18),(56,21),RUST)]:arrow(ax,s,e,color=c,lw=.9)
    SYSTEM.save(fig,14)

def f15():
    fig,ax=SYSTEM.setup(15,"Two active owners arise through independent control-plane failures")
    top=(50,75);ax.add_patch(Polygon([[42,75],[50,83],[58,75],[50,67]],closed=True,facecolor=RUST_LIGHT,edgecolor=RUST,linewidth=1.3));ax.text(*top,"TWO ACTIVE\nOWNERS",ha="center",va="center",color=RUST,fontsize=7,fontweight="bold")
    causes=[("NETWORK PARTITION",5,44),("LEASE STORE FAILOVER",28,44),("CLOCK ASSUMPTION",52,44),("DELAYED REVOCATION",75,44)]
    for t,x,y in causes:box(ax,x,y,19,12,t,"control divergence",edge=RUST,fill=SURFACE,title_color=RUST,fs=5.9);arrow(ax,(x+9.5,y+12),(50,67),color=RUST,lw=.8)
    controls=[("MONOTONIC EPOCH",12,16,BLUE),("DOMAIN FENCE",39,16,TEAL),("ACTION IDEMPOTENCY",66,16,GOLD)]
    for t,x,y,c in controls:box(ax,x,y,22,11,t,"effect containment",edge=c,fill={BLUE:BLUE_LIGHT,TEAL:TEAL_LIGHT,GOLD:GOLD_LIGHT}[c],title_color=c,fs=6);arrow(ax,(50,67),(x+11,y+11),color=c,lw=.7)
    SYSTEM.save(fig,15)

def f16():
    fig,ax=SYSTEM.setup(16,"Inject faults across layers and assert business invariants through recovery",plot=True)
    fig.subplots_adjust(left=.115,right=.745,top=.82,bottom=.13)
    rows=["DROP AFTER COMMIT","DUPLICATE DELIVERY","PAUSE OLD OWNER","CLOCK SKEW","STATE-STORE FAILOVER","STALE EVENT","COMPENSATION FAIL","DOMAIN TIMEOUT"]
    cols=["ONE OWNER","ONE EFFECT","VERSION","AUTHORITY","RECEIPT","RECOVERY","NO ORPHAN"]
    data=np.array([[1,1,1,1,1,1,1],[1,1,1,1,1,1,1],[1,1,1,1,1,1,1],[0,1,1,1,1,1,1],[1,1,1,1,1,1,1],[1,1,1,1,1,1,1],[1,1,1,1,1,0,0],[1,1,1,1,0,0,1]])
    cmap=LinearSegmentedColormap.from_list("chaos",[RUST_LIGHT,TEAL_LIGHT])
    ax.imshow(data,cmap=cmap,vmin=0,vmax=1,aspect="auto")
    for i in range(8):
        for j in range(7):ax.text(j,i,"PASS" if data[i,j] else "BREACH",ha="center",va="center",fontsize=5.5,color=TEAL if data[i,j] else RUST,fontweight="bold")
    ax.set_xticks(range(7),cols,fontsize=5.4,rotation=25,ha="right");ax.set_yticks(range(8),rows,fontsize=5.6);ax.tick_params(length=0,colors=MUTED)
    SYSTEM.save(fig,16)

def f17():
    fig,ax=SYSTEM.setup(17,"Coordination objectives measure business effects, not conversational success")
    rows=[("DUPLICATE EFFECT","0","0","DOMAIN","PASS"),("STALE-OWNER ACCEPT","0","0","PLATFORM","PASS"),("P99 AMBIGUITY AGE","≤10m","24m","SRE","BREACH"),("SAGA RECOVERY","≥99.5%","99.7%","WORKFLOW","PASS"),("COMPENSATION BREACH","0","1","DOMAIN","BREACH"),("ORPHAN SAGA","0","0","OPS","PASS"),("CAUSAL REJECT","100%","100%","EVENTS","PASS"),("RECEIPT COVERAGE","100%","100%","AUDIT","PASS")]
    for h,x in [("OBJECTIVE",3),("TARGET",46),("ACTUAL",61),("OWNER",76),("STATE",90)]:ax.text(x,81,h,color=BLUE,fontsize=6.4,fontweight="bold")
    for i,row in enumerate(rows):
        y=70-i*8.2;c=TEAL if row[4]=="PASS" else RUST;ax.add_patch(Rectangle((2,y-3),95,7,facecolor=SURFACE if i%2==0 else PAPER,edgecolor=LINE,lw=.4))
        for txt,x in zip(row,[3,46,61,76,90]):ax.text(x,y,txt,color=c if x==90 else INK,fontsize=6.2,fontweight="bold" if x in [3,90] else "normal",va="center")
        ax.add_patch(Circle((87,y),1.5,facecolor=c,edgecolor=c))
    SYSTEM.save(fig,17)

def f18():
    fig,ax=SYSTEM.setup(18,"Coordination maturity increases only after domain effects survive fault injection")
    phases=[("0","INVENTORY","shared state","map invariants",BLUE),("1","IDENTIFY","workflow + action IDs","dedupe",PURPLE),("2","DURABLE","state + outbox","replay",GOLD),("3","FENCE","lease + epochs","stale reject",TEAL),("4","RECOVER","sagas + reconcile","chaos SLO",TEAL),("5","SPECIALIZE","add agents","independent review",BLUE)]
    for i,(n,t,b,g,c) in enumerate(phases):
        x=2+i*15.7;y=17+i*9;box(ax,x,y,14,23,f"{n}  {t}",b,edge=c,fill=SURFACE,title_color=c,fs=6.3);ax.text(x+7,y+4,SYSTEM.wrap("GATE: "+g,18),ha="center",va="center",color=GOLD,fontsize=5.7,fontweight="bold")
        if i<5:arrow(ax,(x+14,y+11),(x+15.7,y+20),color=c)
    ax.plot([2,95],[10,10],color=RUST,lw=1.2);ax.text(48.5,5,"INVARIANT BREACH → FENCE WORKFLOW · STOP NEW EFFECTS · RECONCILE DOMAIN STATE",ha="center",color=RUST,fontsize=6.4,fontweight="bold")
    SYSTEM.save(fig,18)

def main():SYSTEM.render([f01,f02,f03,f04,f05,f06,f07,f08,f09,f10,f11,f12,f13,f14,f15,f16,f17,f18])
if __name__=="__main__":main()
