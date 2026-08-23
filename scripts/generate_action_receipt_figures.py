#!/usr/bin/env python3
"""Generate the 18 deep-dive figures for the signed action-receipt story."""

from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.colors import LinearSegmentedColormap
from matplotlib.patches import Circle, FancyBboxPatch, Polygon, Rectangle

from technical_figure_framework import (
    BLUE, BLUE_LIGHT, GOLD, GOLD_LIGHT, GREEN, GREEN_LIGHT, INK, LINE, MUTED,
    PAPER, PURPLE, PURPLE_LIGHT, RUST, RUST_LIGHT, SURFACE, TEAL, TEAL_LIGHT,
    FigureSpec, FigureSystem, arrow, box,
)


ROOT = Path(__file__).resolve().parents[1]
SLUG = "every-ai-agent-action-needs-a-receipt"
OUT = ROOT / "assets" / "images" / SLUG
MAP_PATH = ROOT / "stories" / f"{SLUG}-figure-map.md"


def spec(n, title, form, takeaway, domain, insights, contract, assumption="Reference architecture; no observed production data.", core=True):
    return FigureSpec(n, title, form, takeaway, domain, tuple(insights), tuple(contract), assumption, core)


SPECS = [
    spec(1,"Observability is not proof","Comparison","Traces explain runtime behavior; a receipt proves one exact business action and its terminal state.","SEMANTICS",["Logs and spans may be sampled, mutable, or operationally scoped.","Events announce facts but do not automatically bind intent, authority, and verification.","A receipt joins evidence, authorization, effect, and recovery in one durable contract."],[("TRACE","execution path"),("EVENT","state notification"),("RECEIPT","business proof")]),
    spec(2,"Signed action-receipt control plane","Architecture","The receipt service seals intent before execution and completes proof only after effect verification.","CONTROL PLANE",["Prepare and complete are separate durable transitions.","The executor cannot claim success; a verifier observes target state independently.","Signatures and append-only storage make later alteration evident."],[("PREPARE","intent + evidence"),("EXECUTE","idempotent mutation"),("COMPLETE","verify + seal")]),
    spec(3,"Business-action lineage graph","Lineage graph","One receipt connects request, evidence, policy, approval, authority, calls, outcome, verification, and recovery.","PROVENANCE",["Execution artifacts remain linked to the business decision that caused them.","A timeout creates an ambiguity node instead of a fictional failure.","Recovery produces a new linked event; it never rewrites the original outcome."],[("ROOT","business intent"),("EFFECT","target mutation"),("PROOF","terminal receipt")]),
    spec(4,"Receipt-envelope contract","Structured schema","A versioned receipt binds exact intent, authority, request, effect, verification, signatures, and retention.","DATA CONTRACT",["Sensitive payloads are referenced by digest and governed location.","Status is a state-machine value, not an arbitrary string.","Schema and cryptographic profile versions support independent verification."],[("KEY","receipt_id + version"),("BIND","digests + IDs"),("SEAL","JWS + timestamp")]),
    spec(5,"Canonicalization before signing","Stage pipeline","Signing raw application JSON is unsafe; deterministic canonical bytes must be produced and verified identically.","CRYPTOGRAPHY",["Schema validation precedes canonicalization.","Excluded volatile fields are defined by profile—not ad hoc code.","The verifier reconstructs canonical bytes rather than trusting a stored digest."],[("INPUT","typed receipt"),("PROFILE","JCS / v1"),("OUTPUT","canonical bytes")]),
    spec(6,"Digest chain and batch anchoring","Merkle structure","Per-receipt hashes plus batch roots make deletion, insertion, or mutation detectable without signing every storage page.","TAMPER EVIDENCE",["Each leaf commits to canonical receipt bytes.","Merkle proofs permit selective inclusion without exposing sibling receipts.","An external timestamp anchors the batch root to an independent time claim."],[("LEAF","SHA-256(receipt)"),("ROOT","Merkle batch"),("ANCHOR","trusted timestamp")]),
    spec(7,"Receipt signing and verification sequence","Sequence","A verifier must validate schema, canonicalization, signature, key status, timestamp, lineage, and observed effect.","VERIFICATION",["Signature validity alone does not prove the action occurred.","Key validity is evaluated at signing time and verification time under policy.","Observed target state closes the proof chain."],[("SIGNER","receipt service"),("KEY","versioned KMS key"),("VERIFIER","independent path")]),
    spec(8,"Trace context mapped into a receipt","Field mapping","Trace IDs correlate runtime data; receipt IDs and digests carry durable business semantics outside trace headers.","CORRELATION",["Trace Context propagates request correlation, not sensitive evidence.","Sampling may remove spans; the receipt remains mandatory for consequential actions.","Receipt links point to telemetry stores without embedding payloads in trace state."],[("TRACE","traceparent"),("LOG","trace_id + span_id"),("RECEIPT","business_action_id")]),
    spec(9,"Idempotency and ambiguity state machine","State machine","A stable action ID prevents duplicate business effects and makes ambiguous outcomes a durable reconciliation state.","RELIABILITY",["Reservation occurs before the target call.","Retries return the recorded terminal result or continue reconciliation.","Ambiguous never transitions directly back to executable."],[("KEY","business_action_id"),("LOCK","atomic reservation"),("TERMINAL","verified / recovered")]),
    spec(10,"Timeout after effect: the ambiguity window","Timeline","A caller timeout cannot distinguish no effect from a committed effect; only target-state reconciliation can.","FAILURE MODEL",["Network failure after commit creates the dangerous uncertainty interval.","Blind retry can duplicate a non-idempotent mutation.","The receipt records known facts and unanswered questions separately."],[("T0","request reserved"),("T2","target commits"),("T3","caller times out")]),
    spec(11,"Conditional mutation and receipt protocol","Sequence","Preconditions, idempotency, and verification prevent a valid action from overwriting newer business state.","EXECUTION",["The proposal binds the version observed during decision.","The target atomically checks version and idempotency key.","A conflict produces no effect and a terminal rejected receipt."],[("PRECONDITION","If-Match v20"),("IDEMPOTENCY","action A7"),("OUTCOME","commit or conflict")]),
    spec(12,"Ambiguous-outcome reconciliation tree","Decision tree","Recovery starts with authoritative state observation, then returns prior success, retries safely, compensates, or escalates.","RECOVERY",["Reconciliation asks whether the intended effect exists—not whether a request log exists.","A replacement action needs new authority when the original is terminal.","Irreversible or mixed effects route to human incident handling."],[("OBSERVE","target + ledger"),("DECIDE","four outcomes"),("PROVE","recovery receipt")]),
    spec(13,"Selective disclosure and evidence compartments","Disclosure map","Auditors can verify the receipt core and Merkle proof without receiving customer payloads or broad operational telemetry.","PRIVACY",["Core identifiers and digests are separated from sensitive evidence.","Role-specific disclosure packages minimize data movement.","Redaction never changes the signed commitment to the original content."],[("CORE","minimal signed fields"),("PROOF","Merkle path"),("PAYLOAD","policy-gated")]),
    spec(14,"Failure-mode versus evidence-control matrix","Control matrix","No single signature, log, or idempotency key proves every property of a business action.","CONTROL COVERAGE",["Cryptography covers integrity and origin—not business correctness.","Idempotency covers duplication—not stale or unauthorized intent.","Independent verification covers effect but needs lineage to explain why."],[("ROWS","8 failure modes"),("COLS","8 controls"),("SCALE","none → primary")],"Ordinal reference matrix; coverage levels are architectural judgments, not measured effectiveness."),
    spec(15,"Receipt storage and verification cost model","Cost model","Payload separation and batch anchoring control audit cost without sacrificing mandatory proof for high-risk actions.","ECONOMICS",["Index and signed core dominate hot-path storage; evidence payloads can tier by policy.","Batch verification amortizes cryptographic and timestamp cost.","Retention class, action risk, and dispute horizon drive total cost."],[("VOLUME","10M actions / month"),("MODEL","synthetic bytes + USD"),("OUTPUT","monthly cost")],"Synthetic model: 10M actions/month, 3.2KB core, 8KB index/replication overhead, 42KB payload average; illustrative storage rates."),
    spec(16,"Dispute reconstruction timeline","Audit timeline","A receipt reduces dispute resolution from log archaeology to deterministic verification and targeted evidence disclosure.","AUDIT",["The receipt identifies exact source systems and versions.","Verification can proceed even when sampled trace spans are missing.","Exceptions and recovery remain visible as linked artifacts."],[("QUESTION","who changed quote?"),("PATH","7 verification steps"),("RESULT","supported finding")]),
    spec(17,"Action-receipt operating objectives","SLO scorecard","Coverage, seal latency, verification, ambiguity, reconciliation, and key health require separate objectives and owners.","OPERATIONS",["A high receipt count is meaningless if effects are not independently verified.","Ambiguity age is a business-risk backlog metric.","Key or timestamp failures must stop proof claims, not silently downgrade them."],[("WINDOW","synthetic 30 days"),("STATUS","6 pass · 2 breach"),("ACTION","freeze + reconcile")],"Synthetic 30-day window with two deliberate breaches to demonstrate escalation behavior."),
    spec(18,"Adoption roadmap for action receipts","Maturity roadmap","Teams should start with one consequential action and prove end-to-end lineage before expanding receipt coverage.","MIGRATION",["Inventory current claims of success and their evidence gaps.","Shadow receipts expose missing IDs and ambiguous effects without changing execution.","Cryptographic sealing follows schema and verification stability—not the reverse."],[("PHASES","0 through 5"),("GATE","evidence quality"),("ROLLBACK","action class")]),
]

SYSTEM = FigureSystem(SLUG, OUT, MAP_PATH, "Every AI Agent Action Needs a Receipt", SPECS)


def f01():
    fig, ax = SYSTEM.setup(1,"Four artifacts answer different questions")
    cols=[("TRACE","How did code run?",BLUE,["request path","span timing","sampling","operational"]),("LOG","What was recorded?",PURPLE,["service event","free/typed body","retention varies","mutable sink"]),("EVENT","What was announced?",GOLD,["state change","subscriber fanout","delivery semantics","not proof alone"]),("RECEIPT","What action is proven?",TEAL,["exact intent","authority + effect","verification","terminal state"])]
    for i,(t,q,c,items) in enumerate(cols):
        x=2+i*23.5
        box(ax,x,68,20,14,t,q,edge=c,fill=[BLUE_LIGHT,PURPLE_LIGHT,GOLD_LIGHT,TEAL_LIGHT][i],title_color=c,fs=8)
        for j,item in enumerate(items):
            box(ax,x,55-j*11,20,8,item.upper(),edge=LINE,fill=SURFACE,fs=6.4)
    ax.text(49,6,"CORRELATE ALL FOUR · DO NOT SUBSTITUTE ONE FOR ANOTHER",ha="center",color=RUST,fontsize=7.5,fontweight="bold")
    SYSTEM.save(fig,1)


def f02():
    fig, ax = SYSTEM.setup(2,"Prepare, execute, verify, seal, and retain are independent control responsibilities")
    nodes=[(3,64,"PROPOSAL","intent + evidence",BLUE),(22,64,"POLICY + APPROVAL","decision digest",GOLD),(43,64,"RECEIPT PREPARE","reserve action ID",PURPLE),(64,64,"EXECUTOR","conditional call",TEAL),(83,64,"TARGET API","business state",BLUE),
           (22,25,"KEY SERVICE","signing profile",GOLD),(43,25,"RECEIPT STORE","append-only core",PURPLE),(64,25,"VERIFIER","observe effect",TEAL),(83,25,"RECOVERY","reconcile / compensate",RUST)]
    for x,y,t,b,c in nodes: box(ax,x,y,15,14,t,b,edge=c,fill=SURFACE,title_color=c,fs=6.8)
    for s,e,c in [((18,71),(22,71),BLUE),((37,71),(43,71),GOLD),((58,71),(64,71),PURPLE),((79,71),(83,71),TEAL),((90,64),(71,39),BLUE),((64,32),(58,32),TEAL),((43,32),(37,32),PURPLE),((50,64),(29,39),GOLD),((71,25),(83,32),RUST)]: arrow(ax,s,e,color=c)
    box(ax,16,5,68,9,"TERMINAL RECEIPT","verified success · failed before effect · rejected · recovered · unresolved ambiguity",edge=TEAL,fill=TEAL_LIGHT,title_color=TEAL,fs=7.5)
    arrow(ax,(50,25),(50,14),color=TEAL)
    SYSTEM.save(fig,2)


def f03():
    fig, ax = SYSTEM.setup(3,"The receipt is the durable join across decision and execution evidence")
    center=(48,42)
    ax.add_patch(Circle(center,9,facecolor=TEAL_LIGHT,edgecolor=TEAL,linewidth=1.6)); ax.text(*center,"RECEIPT\nr_883",ha="center",va="center",color=TEAL,fontsize=8,fontweight="bold")
    nodes=[(5,70,"INTENT","proposal p7",BLUE),(28,70,"EVIDENCE","pack e4",BLUE),(58,70,"POLICY","decision d2",GOLD),(81,70,"APPROVAL","approval a9",GOLD),
           (5,12,"AUTHORITY","lease l3",PURPLE),(28,12,"REQUEST","call c1",TEAL),(58,12,"EFFECT","quote v21",TEAL),(81,12,"RECOVERY","event x2",RUST)]
    for x,y,t,b,c in nodes:
        box(ax,x,y,14,10,t,b,edge=c,fill=SURFACE,title_color=c,fs=6.5)
        arrow(ax,(x+7,y+10 if y<42 else y),(48,42),color=c,lw=.9)
    ax.text(48,28,"verified by state hash",ha="center",color=TEAL,fontsize=6.5,fontweight="bold")
    SYSTEM.save(fig,3)


def f04():
    fig, ax = SYSTEM.setup(4,"Eight compartments separate business proof from governed payloads")
    groups=[("IDENTITY",BLUE,[("receipt_id","r_883"),("schema","v1.2"),("action_id","A7")]),("INTENT",TEAL,[("type","discount.apply"),("resource","quote:771"),("proposal","sha256…")]),
            ("AUTHORITY",GOLD,[("policy","p/41"),("approval","a9"),("lease","l3")]),("REQUEST",PURPLE,[("idempotency","A7"),("trace_id","4bf9…"),("request","sha256…")]),
            ("EFFECT",TEAL,[("before","v20"),("after","v21"),("observed","8%")]),("RECOVERY",RUST,[("state","verified"),("pointer","none"),("terminal","true")]),
            ("CRYPTO",BLUE,[("profile","JCS/JWS"),("kid","kms:17"),("timestamp","tst_4")]),("LIFECYCLE",GOLD,[("retention","7y"),("legal_hold","false"),("payload_ref","vault:…")])]
    for i,(t,c,fields) in enumerate(groups):
        x=2+(i%4)*23.5; y=49-(i//4)*37
        box(ax,x,y,21,31,t,edge=c,fill=SURFACE,title_color=c,fs=7)
        for j,(k,v) in enumerate(fields):
            yy=y+18-j*6
            ax.text(x+1.5,yy,k,color=MUTED,fontsize=5.8,fontweight="bold"); ax.text(x+19.5,yy,v,color=INK,fontsize=5.8,ha="right",family="monospace")
    SYSTEM.save(fig,4)


def f05():
    fig, ax = SYSTEM.setup(5,"Deterministic bytes—not application object order—become the signature input")
    stages=[("1 SCHEMA","reject unknown",BLUE),("2 NORMALIZE","types + Unicode",PURPLE),("3 PROJECT","signed fields",GOLD),("4 CANONICALIZE","RFC 8785 JCS",TEAL),("5 HASH","SHA-256",BLUE),("6 SIGN","JWS profile",TEAL)]
    for i,(t,b,c) in enumerate(stages):
        x=2+i*15.7; y=51+(i%2)*9
        box(ax,x,y,14,20,t,b,edge=c,fill=SURFACE,title_color=c,fs=6.5)
        if i<5: arrow(ax,(x+14,y+10),(x+15.7,y+19 if (i+1)%2 else y+1),color=c)
    box(ax,18,16,64,17,"SIGNED INPUT PROFILE","UTF-8 · I-JSON constraints · deterministic property sorting · no duplicate names · profile v1",edge=PURPLE,fill=PURPLE_LIGHT,title_color=PURPLE,fs=7.5)
    box(ax,31,3,38,8,"OUTPUT","digest + protected header + signature",edge=TEAL,fill=TEAL_LIGHT,title_color=TEAL,fs=7)
    SYSTEM.save(fig,5)


def f06():
    fig, ax = SYSTEM.setup(6,"Four receipt leaves form one independently timestamped batch root")
    leaves=[("H(r1)",8),("H(r2)",29),("H(r3)",57),("H(r4)",78)]
    for t,x in leaves: box(ax,x,16,14,9,t,"canonical bytes",edge=BLUE,fill=BLUE_LIGHT,title_color=BLUE,fs=6.5)
    mids=[("H(1∥2)",19),("H(3∥4)",68)]
    for t,x in mids: box(ax,x,42,16,10,t,"ordered pair",edge=PURPLE,fill=PURPLE_LIGHT,title_color=PURPLE,fs=6.5)
    for x1,x2 in [(15,27),(36,27),(64,76),(85,76)]: arrow(ax,(x1,25),(x2,42),color=PURPLE,lw=1)
    box(ax,42,66,18,11,"MERKLE ROOT","batch 2026-08-23",edge=TEAL,fill=TEAL_LIGHT,title_color=TEAL,fs=7)
    arrow(ax,(27,52),(48,66),color=TEAL); arrow(ax,(76,52),(54,66),color=TEAL)
    box(ax,68,67,25,10,"TIMESTAMP TOKEN","RFC 3161 profile",edge=GOLD,fill=GOLD_LIGHT,title_color=GOLD,fs=6.5); arrow(ax,(60,71.5),(68,72),color=GOLD)
    ax.text(50,5,"INCLUSION PROOF FOR r2 = sibling H(r1) + sibling H(3∥4) + anchored root",ha="center",color=INK,fontsize=6.5,fontweight="bold")
    SYSTEM.save(fig,6)


def f07():
    fig, ax = SYSTEM.setup(7,"Independent verification closes both the cryptographic and business-effect chains")
    actors=[("RECEIPT SVC",7,BLUE),("KMS",28,GOLD),("APPEND STORE",49,PURPLE),("TARGET API",70,TEAL),("VERIFIER",91,BLUE)]
    for name,x,c in actors:
        ax.text(x,82,name,ha="center",color=c,fontsize=6.2,fontweight="bold"); ax.plot([x,x],[10,78],color=LINE,lw=.8,ls="--")
    msgs=[(7,28,71,"1 sign digest",BLUE),(28,7,63,"2 JWS + kid",GOLD),(7,49,54,"3 append sealed core",PURPLE),(91,49,44,"4 fetch receipt",BLUE),(91,28,35,"5 key + status",GOLD),(91,70,26,"6 observe effect",TEAL),(91,91,17,"7 verify lineage + state",TEAL)]
    for s,e,y,t,c in msgs:
        arrow(ax,(s,y),(e,y),color=c); ax.text((s+e)/2,y+2,t,ha="center",color=INK,fontsize=5.6,fontweight="bold")
    SYSTEM.save(fig,7)


def f08():
    fig, ax = SYSTEM.setup(8,"Correlation IDs cross the observability surface without carrying business payloads")
    rows=[("W3C TRACE CONTEXT",BLUE,["trace-id","parent-id","flags","vendor state"]),("OTEL LOG RECORD",PURPLE,["timestamp","trace_id","span_id","severity/body"]),("CLOUD EVENT",GOLD,["id","source","type","subject"]),("ACTION RECEIPT",TEAL,["receipt_id","action_id","intent/effect digests","terminal proof"])]
    for i,(title,c,items) in enumerate(rows):
        y=70-i*18
        box(ax,2,y,20,12,title,"artifact",edge=c,fill=SURFACE,title_color=c,fs=6.3)
        for j,item in enumerate(items): box(ax,26+j*17.5,y,15,12,item.upper(),edge=c,fill=[BLUE_LIGHT,PURPLE_LIGHT,GOLD_LIGHT,TEAL_LIGHT][i],title_color=INK,fs=5.7)
    ax.text(49,5,"LINK BY IDENTIFIERS · KEEP SENSITIVE EVIDENCE OUT OF PROPAGATION HEADERS",ha="center",color=RUST,fontsize=6.8,fontweight="bold")
    SYSTEM.save(fig,8)


def f09():
    fig, ax = SYSTEM.setup(9,"An action identifier becomes terminal after execution begins")
    states=[(4,62,"PROPOSED",BLUE),(28,62,"RESERVED",PURPLE),(52,62,"EXECUTING",GOLD),(76,62,"EFFECT OBSERVED",TEAL),(16,20,"FAILED BEFORE EFFECT",RUST),(46,20,"AMBIGUOUS",RUST),(76,20,"VERIFIED / RECOVERED",TEAL)]
    for x,y,t,c in states: box(ax,x,y,20,12,t,"durable state",edge=c,fill={BLUE:BLUE_LIGHT,PURPLE:PURPLE_LIGHT,GOLD:GOLD_LIGHT,RUST:RUST_LIGHT,TEAL:TEAL_LIGHT}[c],title_color=c,fs=6.7)
    for s,e,c in [((24,68),(28,68),BLUE),((48,68),(52,68),PURPLE),((72,68),(76,68),GOLD),((86,62),(86,32),TEAL),((62,62),(56,32),RUST),((52,62),(26,32),RUST),((66,26),(76,26),TEAL)]: arrow(ax,s,e,color=c)
    ax.text(50,6,"NO TRANSITION FROM AMBIGUOUS OR TERMINAL BACK TO EXECUTABLE",ha="center",color=RUST,fontsize=7,fontweight="bold")
    SYSTEM.save(fig,9)


def f10():
    fig, ax = SYSTEM.setup(10,"The dangerous interval begins after target commit and before caller knowledge")
    actors=[("ORCHESTRATOR",7,BLUE),("NETWORK",31,PURPLE),("TARGET",55,TEAL),("RECEIPT",79,GOLD)]
    for name,x,c in actors:
        ax.text(x,82,name,ha="center",color=c,fontsize=6.5,fontweight="bold"); ax.plot([x,x],[16,78],color=LINE,lw=.8,ls="--")
    events=[(7,31,69,"T0 send A7",BLUE),(31,55,60,"T1 deliver",PURPLE),(55,55,50,"T2 COMMIT v21",TEAL),(55,31,40,"response",TEAL),(31,31,31,"T3 DROP / TIMEOUT",RUST),(7,79,22,"T4 mark ambiguous",RUST)]
    for s,e,y,t,c in events:
        arrow(ax,(s,y),(e,y),color=c); ax.text((s+e)/2,y+2,t,ha="center",color=c,fontsize=5.8,fontweight="bold")
    ax.add_patch(Rectangle((7,27),72,28,facecolor=RUST_LIGHT,edgecolor="none",alpha=.35)); ax.text(43,14,"UNCERTAINTY: EFFECT EXISTS, CALLER DOES NOT KNOW",ha="center",color=RUST,fontsize=7,fontweight="bold")
    SYSTEM.save(fig,10)


def f11():
    fig, ax = SYSTEM.setup(11,"Version and idempotency checks are atomic with the business mutation")
    steps=[("1 READ","quote v20",BLUE),("2 PROPOSE","8% + v20",PURPLE),("3 RESERVE","action A7",GOLD),("4 MUTATE","If-Match v20",TEAL),("5 VERIFY","quote v21 = 8%",TEAL)]
    for i,(t,b,c) in enumerate(steps):
        x=2+i*19.1; y=55-(i%2)*8
        box(ax,x,y,17,20,t,b,edge=c,fill=SURFACE,title_color=c,fs=7)
        if i<4: arrow(ax,(x+17,y+10),(x+19.1,y+18 if (i+1)%2 else y+2),color=c)
    box(ax,17,18,29,12,"CONFLICT PATH","current version ≠ v20 → 409 · no effect",edge=RUST,fill=RUST_LIGHT,title_color=RUST,fs=7)
    box(ax,54,18,29,12,"RETRY PATH","action A7 exists → return recorded result",edge=TEAL,fill=TEAL_LIGHT,title_color=TEAL,fs=7)
    arrow(ax,(68,47),(68,30),color=TEAL); arrow(ax,(58,55),(31,30),color=RUST)
    SYSTEM.save(fig,11)


def f12():
    fig, ax = SYSTEM.setup(12,"Observe target state first; then choose one bounded recovery path")
    qs=[("EFFECT PRESENT?",BLUE),("MATCH INTENT?",TEAL),("SAFE RETRY?",GOLD),("COMPENSABLE?",PURPLE)]
    for i,(t,c) in enumerate(qs):
        x=4+i*23
        ax.add_patch(Polygon([[x,60],[x+10,70],[x+20,60],[x+10,50]],closed=True,facecolor=SURFACE,edgecolor=c,linewidth=1.2)); ax.text(x+10,60,SYSTEM.wrap(t,14),ha="center",va="center",color=c,fontsize=6.5,fontweight="bold")
        if i<3: arrow(ax,(x+20,60),(x+23,60),color=c)
    outcomes=[(3,"RETURN PRIOR SUCCESS",TEAL),(27,"RETRY WITH BOUND AUTHORITY",GOLD),(51,"COMPENSATE + VERIFY",PURPLE),(75,"HUMAN INCIDENT",RUST)]
    for x,t,c in outcomes:
        box(ax,x,18,20,12,t,"terminal receipt",edge=c,fill={TEAL:TEAL_LIGHT,GOLD:GOLD_LIGHT,PURPLE:PURPLE_LIGHT,RUST:RUST_LIGHT}[c],title_color=c,fs=6.3)
        arrow(ax,(x+10,50),(x+10,30),color=c,lw=.8)
    SYSTEM.save(fig,12)


def f13():
    fig, ax = SYSTEM.setup(13,"One signed commitment supports role-specific evidence packages")
    box(ax,37,64,27,16,"SIGNED RECEIPT CORE","IDs · digests · times · state · JWS",edge=TEAL,fill=TEAL_LIGHT,title_color=TEAL,fs=7.5)
    packs=[(3,29,"OPERATIONS","trace links · latency",BLUE),(27,16,"AUDIT","policy · approval · proof",GOLD),(54,16,"CUSTOMER DISPUTE","exact affected fields",PURPLE),(78,29,"SECURITY","key · integrity · lineage",RUST)]
    for x,y,t,b,c in packs:
        box(ax,x,y,19,15,t,b,edge=c,fill=SURFACE,title_color=c,fs=6.5); arrow(ax,(50.5,64),(x+9.5,y+15),color=c,lw=.9)
    ax.text(50,6,"PAYLOAD VAULT REMAINS POLICY-GATED · DIGEST COMMITMENT DOES NOT CHANGE",ha="center",color=INK,fontsize=6.5,fontweight="bold")
    SYSTEM.save(fig,13)


def f14():
    fig, ax = SYSTEM.setup(14,"Ordinal coverage shows why proof requires a control composition",plot=True)
    # Long failure-mode labels are part of the analytical payload. Reserve
    # additional left margin so the final article render never clips them.
    fig.subplots_adjust(left=.105, right=.745, top=.82, bottom=.13)
    rows=["ALTERED RECEIPT","FAKE ORIGIN","DUPLICATE EFFECT","STALE INTENT","UNAUTHORIZED","AMBIGUOUS","WRONG EFFECT","MISSING LINEAGE"]
    cols=["SCHEMA","DIGEST","JWS","TIMESTAMP","IDEMPOTENCY","PRECONDITION","VERIFY","PROVENANCE"]
    data=np.array([[1,3,4,2,0,0,1,1],[0,1,4,2,0,0,1,2],[0,1,1,0,4,1,3,1],[1,1,1,1,0,4,2,2],[1,1,2,1,0,3,2,4],[0,1,1,1,3,1,4,3],[1,1,1,1,1,2,4,2],[1,2,2,1,1,1,2,4]])
    cmap=LinearSegmentedColormap.from_list("coverage",[SURFACE,RUST_LIGHT,GOLD_LIGHT,BLUE_LIGHT,TEAL])
    ax.imshow(data,cmap=cmap,vmin=0,vmax=4,aspect="auto")
    for i in range(len(rows)):
        for j in range(len(cols)): ax.text(j,i,["—","S","M","STR","PRI"][data[i,j]],ha="center",va="center",fontsize=5.7,color=INK,fontweight="bold")
    ax.set_xticks(range(len(cols)),cols,fontsize=5.3,rotation=30,ha="right"); ax.set_yticks(range(len(rows)),rows,fontsize=5.7); ax.tick_params(length=0,colors=MUTED)
    SYSTEM.save(fig,14)


def f15():
    fig, ax = SYSTEM.setup(15,"Synthetic monthly storage separates hot proof from tiered payload",plot=True)
    components=["SIGNED CORE","INDEX + REPLICATION","HOT PAYLOAD","COLD PAYLOAD","ANCHOR + VERIFY"]
    gb=np.array([32,80,126,294,2.5])
    rates=np.array([.12,.12,.12,.023,1.0])
    cost=gb*rates
    colors=[BLUE,PURPLE,GOLD,TEAL,RUST]
    bars=ax.barh(components,cost,color=colors,height=.58)
    for bar,g,c in zip(bars,gb,cost): ax.text(bar.get_width()+.15,bar.get_y()+bar.get_height()/2,f"{g:.0f} GB · ${c:,.1f}",va="center",fontsize=6.8,color=INK,fontweight="bold")
    ax.set_xlabel("SYNTHETIC MONTHLY STORAGE / SERVICE COST (USD)",fontsize=7,color=MUTED); ax.grid(axis="x",color=LINE,lw=.5); ax.tick_params(colors=MUTED,labelsize=6.2); ax.set_xlim(0,max(cost)*1.25)
    ax.text(max(cost)*1.22,4.3,"10M actions\n42KB avg payload",ha="right",color=RUST,fontsize=7,fontweight="bold")
    SYSTEM.save(fig,15)


def f16():
    fig, ax = SYSTEM.setup(16,"A deterministic proof path replaces broad log archaeology")
    steps=[("QUESTION","Who changed quote 771?",BLUE),("LOCATE","action ID A7",PURPLE),("VERIFY","JWS + timestamp",GOLD),("REPLAY","policy + evidence",BLUE),("OBSERVE","quote v20 → v21",TEAL),("EXPLAIN","approval + agent",GOLD),("FINDING","supported / exception",TEAL)]
    for i,(t,b,c) in enumerate(steps):
        x=2+i*13.4; y=20+i*8
        box(ax,x,y,12,22,t,b,edge=c,fill=SURFACE,title_color=c,fs=6.2)
        if i<6: arrow(ax,(x+12,y+11),(x+13.4,y+19),color=c)
    ax.plot([2,94],[12,12],color=RUST,lw=1); ax.text(48,7,"SAMPLED SPANS MAY BE MISSING; MANDATORY RECEIPT PROOF REMAINS",ha="center",color=RUST,fontsize=6.7,fontweight="bold")
    SYSTEM.save(fig,16)


def f17():
    fig, ax = SYSTEM.setup(17,"Targets pair proof quality with operational risk")
    rows=[("RECEIPT COVERAGE","100%","100%","PLATFORM","PASS"),("P95 SEAL LATENCY","≤45 ms","38 ms","SECURITY","PASS"),("EFFECT VERIFICATION","≥99.99%","99.995%","DOMAIN","PASS"),("AMBIGUITY RATE","≤0.05%","0.04%","SRE","PASS"),("P99 AMBIGUITY AGE","≤15 min","31 min","SRE","BREACH"),("SIGNATURE VERIFY","100%","100%","SECURITY","PASS"),("KEY STATUS UNKNOWN","0","0","SECURITY","PASS"),("ORPHAN LINEAGE","0","3","DATA","BREACH")]
    headers=[("OBJECTIVE",3),("TARGET",46),("ACTUAL",61),("OWNER",76),("STATE",90)]
    for h,x in headers: ax.text(x,81,h,color=BLUE,fontsize=6.4,fontweight="bold")
    for i,row in enumerate(rows):
        y=70-i*8.2; c=TEAL if row[4]=="PASS" else RUST
        ax.add_patch(Rectangle((2,y-3),95,7,facecolor=SURFACE if i%2==0 else PAPER,edgecolor=LINE,lw=.4))
        for txt,x in zip(row,[3,46,61,76,90]): ax.text(x,y,txt,color=c if x==90 else INK,fontsize=6.2,fontweight="bold" if x in [3,90] else "normal",va="center")
        ax.add_patch(Circle((87,y),1.5,facecolor=c,edgecolor=c))
    SYSTEM.save(fig,17)


def f18():
    fig, ax = SYSTEM.setup(18,"Proof maturity rises only when verification and recovery are demonstrated")
    phases=[("0","INVENTORY","success claims","map action IDs",BLUE),("1","SCHEMA","typed envelope","contract tests",PURPLE),("2","SHADOW","build receipts","coverage ≥99.9%",GOLD),("3","VERIFY","observe effects","ambiguity SLO",TEAL),("4","SEAL","sign + anchor","key drills",TEAL),("5","EXPAND","cross-domain proof","independent audit",BLUE)]
    for i,(n,t,b,g,c) in enumerate(phases):
        x=2+i*15.7; y=17+i*9
        box(ax,x,y,14,23,f"{n}  {t}",b,edge=c,fill=SURFACE,title_color=c,fs=6.7); ax.text(x+7,y+4,SYSTEM.wrap("GATE: "+g,18),ha="center",va="center",color=GOLD,fontsize=5.8,fontweight="bold")
        if i<5: arrow(ax,(x+14,y+11),(x+15.7,y+20),color=c)
    ax.plot([2,95],[10,10],color=RUST,lw=1.2); ax.text(48.5,5,"BREACH → STOP PROOF CLAIMS · PRESERVE EVIDENCE · RECONCILE ACTION CLASS",ha="center",color=RUST,fontsize=6.6,fontweight="bold")
    SYSTEM.save(fig,18)


def main():
    SYSTEM.render([f01,f02,f03,f04,f05,f06,f07,f08,f09,f10,f11,f12,f13,f14,f15,f16,f17,f18])


if __name__ == "__main__":
    main()
