"""Editable, deterministic architecture plates and analytic charts. No external APIs."""
from pathlib import Path
from html import escape
import json
import math
import textwrap
from analytics import results

HERE=Path(__file__).parent
OUT=HERE/'figures'
OUT.mkdir(exist_ok=True)
BLUE='#1457c5'; INK='#101828'; PALE='#bfd2ef'; LIGHT='#edf4ff'
W=1920; H=1360
MANIFEST=[]


class Plate:
    def __init__(self,num,title,subtitle,kind='REFERENCE ARCHITECTURE'):
        self.num=num;self.title=title;self.parts=[];self.nodes={}
        self.parts.append(f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img"><title>{escape(title)}</title><desc>{escape(subtitle)}</desc><defs><marker id="arrow" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" orient="auto-start-reverse"><path d="M 0 0 L 10 5 L 0 10 z" fill="{BLUE}"/></marker><pattern id="hatch" width="12" height="12" patternUnits="userSpaceOnUse"><path d="M0 12L12 0" stroke="{PALE}" stroke-width="2"/></pattern></defs>')
        self.rect(0,0,W,H,fill='white',stroke='none')
        self.txt(64,46,'THE OPERATING AI LEDGER  /  ENGINEERING SERIES',18,BLUE,700)
        self.txt(1856,46,f'EXHIBIT {num:02d}  /  {kind}',17,BLUE,700,anchor='end')
        self.txt(64,104,title,43,INK,700)
        self.txt(64,151,subtitle,23,INK)
        self.line([(64,181),(1856,181)],color=PALE,arrow=False)
    def txt(self,x,y,t,size=22,color=INK,weight=400,anchor='start'):
        self.parts.append(f'<text x="{x}" y="{y}" font-family="Arial, Helvetica, sans-serif" font-size="{size}" fill="{color}" font-weight="{weight}" text-anchor="{anchor}">{escape(str(t))}</text>')
    def rect(self,x,y,w,h,fill='white',stroke=PALE,dashed=False,r=10):
        dash='stroke-dasharray="8 6"' if dashed else ''
        self.parts.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{r}" fill="{fill}" stroke="{stroke}" stroke-width="2" {dash}/>')
    def line(self,points,dashed=False,arrow=True,color=BLUE,width=2.5):
        pts=' '.join(f'{x},{y}' for x,y in points)
        dash='stroke-dasharray="10 7"' if dashed else ''
        mark='marker-end="url(#arrow)"' if arrow else ''
        self.parts.append(f'<polyline points="{pts}" fill="none" stroke="{color}" stroke-width="{width}" {dash} {mark}/>')
    def block(self,x,y,w,text,size=22,line=29,color=INK):
        lines=[]
        for para in text.split('|'):
            lines += textwrap.wrap(para, max(8,int(w/(size*.56))),break_long_words=False,break_on_hyphens=False) or ['']
        for i,s in enumerate(lines): self.txt(x,y+i*line,s,size,color)
        return len(lines)*line
    def card(self,key,x,y,w,h,title,body,tag=None):
        self.nodes[key]=(x,y,w,h)
        self.rect(x,y,w,h,stroke=BLUE)
        self.rect(x,y,6,h,fill=BLUE,stroke='none',r=0)
        head=self.block(x+22,y+34,w-44,title,24,29,BLUE)
        used=self.block(x+22,y+head+56,w-44,body,21,27)
        if tag: self.txt(x+22,y+h-18,tag,16,BLUE,700)
        if head+used+58 > h-(16 if tag else 0):
            raise ValueError(f'Card overflow {self.num}:{key}: {title}')
    def connect(self,a,b,dashed=False):
        x,y,w,h=self.nodes[a];X,Y,V,J=self.nodes[b]
        if y==Y:
            if any(nx>min(x,X) and nx<max(x,X) and ny==y for nx,ny,nw,nh in self.nodes.values()):
                # Skip a column through the gutter, never through an intervening component.
                points=[(x+w/2,y+h),(x+w/2,y+h+18),(X+V/2,y+h+18),(X+V/2,Y+J)]
            else:
                points=[(x+w,y+h/2),(X,Y+J/2)] if x<X else [(x,y+h/2),(X+V,Y+J/2)]
        elif x==X: points=[(x+w/2,y+h),(X+V/2,Y)] if y<Y else [(x+w/2,y),(X+V/2,Y+J)]
        else:
            gy=Y-70 if y<Y else y-70
            points=[(x+w/2,y+h if y<Y else y),(x+w/2,gy),(X+V/2,gy),(X+V/2,Y if y<Y else Y+J)]
        self.line(points,dashed)
    def sidebar(self,sections):
        self.rect(1440,213,416,877,stroke=PALE)
        self.txt(1466,251,'IMPLEMENTATION CONTRACT',20,BLUE,700)
        for i,(title,body) in enumerate(sections):
            y=294+i*254
            self.txt(1466,y,title,23,BLUE,700)
            used=self.block(1466,y+40,354,body,21,29)
            if used>203:raise ValueError(f'Sidebar overflow {self.num}: {title}')
            if i<2:self.line([(1466,y+220),(1830,y+220)],color=PALE,arrow=False)
    def footer(self,invariant,metrics,legend=None):
        self.rect(64,1122,1792,125,stroke=BLUE)
        self.txt(87,1156,'SYSTEM INVARIANT' if self.num<11 else 'MODEL AND EVIDENCE LIMITS',18,BLUE,700)
        self.block(87,1191,1718,invariant,24,30)
        self.txt(64,1290,metrics,21,INK)
        self.txt(64,1328,legend or 'Author-proposed design • White = component / boundary • Solid arrow = execution or evidence • Dashed = policy / control',17,BLUE)
        self.txt(1856,1328,f'{self.num:02d}',18,BLUE,700,anchor='end')
    def save(self,slug,caption):
        self.parts.append('</svg>')
        filename=f'{self.num:02d}-{slug}'
        (OUT/(filename+'.svg')).write_text('\n'.join(self.parts))
        MANIFEST.append({'number':self.num,'title':self.title,'file':filename,'caption':caption,'width':W,'height':H,'nodes':len(self.nodes)})


def grid(num,title,subtitle,lanes,cards,edges,side,invariant,metrics,slug,caption):
    p=Plate(num,title,subtitle)
    xs=[64,516,968];ys=[265,565,865]
    for i,(title,body,tag) in enumerate(cards):
        p.card(str(i),xs[i%3],ys[i//3],392,220,title,body,tag)
    for edge in edges:p.connect(*edge)
    if num==1:
        p.line([(1360,975),(1405,975),(1405,504),(35,504),(35,675),(64,675)],dashed=True)
    # Draw section labels after paths with a white backing to keep text legible.
    for row,head in enumerate(lanes):
        p.rect(60,ys[row]-49,len(head)*11.6+14,30,stroke='none',r=0)
        p.txt(64,ys[row]-28,head,19,BLUE,700)
    p.sidebar(side);p.footer(invariant,metrics);p.save(slug,caption)


def architectures():
    grid(1,'Make recovery capacity part of the execution path',
        'One business intent crosses separate authority, capacity, mutation and verification boundaries.',
        ['01  /  INTAKE AND PRECONDITIONS','02  /  ADMISSION AND DOMAIN EXECUTION','03  /  OUTCOME AND FEEDBACK'],[
        ('Evidence gateway','Authenticate source|Pin evidence version|Reject stale input','OWNER: SOURCE ADAPTER'),
        ('Typed intent builder','Stable action_id|Exact target + payload|Expected state version','UNTRUSTED MODEL OUTPUT'),
        ('Policy decision','Classify action risk|Require exact approval|Issue scoped grant','HARD DENIAL WINS'),
        ('Capacity allocator','Resolve pool + epoch|Reserve forecast work|Reject stale budget','ATOMIC RESERVATION'),
        ('Tool gateway','Validate grant + permit|Fence stale capability|Restrict outbound path','NO DIRECT AGENT WRITE'),
        ('Domain transaction','Check current version|Write + outcome + outbox|Bind intent digest','LOCAL COMMIT BOUNDARY'),
        ('Independent verifier','Read trusted history|Test exact postcondition|Unknown → recovery queue','TRANSPORT ACK ≠ PROOF'),
        ('Recovery workbench','Assign accountable owner|Resolve partial effects|Authorize compensation','TRACK ACTUAL LABOR'),
        ('Budget controller','Reconcile mature cohorts|Forecast by risk cell|Reduce affected writes','VERSIONED FEEDBACK')],
        [('0','1'),('1','2'),('2','3',True),('3','4'),('4','5'),('5','6'),('6','7'),('7','8')],
        [('Two independent gates','A policy grant permits an exact action. A capacity permit admits its expected recovery load. Neither substitutes for the other.'),
         ('Feedback route','Controller publishes a new budget epoch to the allocator. Gateway checks capability freshness before dispatch; in-flight effects still need reconciliation.'),
         ('Isolation key','tenant × operation × region × risk tier. Allocate shared human capacity once; do not give each cell a copy of the full pool.')],
        'A spare recovery slot never authorizes a prohibited action. Every dispatched write must remain attributable to one business intent.',
        'OBSERVE  /  admitted intents • verified outcomes • unresolved age • reserved / actual recovery minutes',
        'control-plane','The exception-budget control plane adds a capacity gate to the write path while keeping authorization independent.')

    p=Plate(2,'Unknown is a durable state, not a retry instruction',
        'Business-action state and recovery accounting must survive process crashes and lost acknowledgements.')
    states=[('p',64,260,'PROPOSED','Canonical intent frozen|No side effect allowed|No reservation yet'),
            ('a',516,260,'ADMITTED','Authority + capacity pass|Reservation is durable|Dispatch is fenced'),
            ('d',968,260,'DISPATCHED','Request sent to domain|Attempt_id recorded|Outcome may be unknown'),
            ('c',64,670,'CONTROLLED NO-EFFECT','Non-execution proven|Cancellation fenced|Release unused reserve'),
            ('v',516,670,'VERIFIED EFFECT','Postcondition established|Finalize outcome receipt|Retain history'),
            ('u',968,670,'UNRESOLVED','Lost response / mismatch|Keep owner + reservation|Resolve original action_id')]
    for k,x,y,t,b in states:p.card(k,x,y,392,224,t,b)
    p.connect('p','a');p.connect('a','d');p.connect('d','u');p.connect('u','v');p.connect('a','c',True)
    p.txt(65,548,'CANCEL ONLY WITH A DISPATCH FENCE',19,BLUE,700)
    p.txt(970,548,'TIMEOUT / INCOMPLETE EVIDENCE',19,BLUE,700)
    p.txt(529,961,'RESOLVE ORIGINAL ID; DO NOT CREATE A NEW INTENT',20,BLUE,700)
    p.block(64,1015,1296,'Admission denial remains a pre-dispatch outcome. An unresolved action can close as verified effect or proven no-effect after reconciliation.',23,30)
    p.sidebar([('Three identifiers','action_id = one business intent; attempt_id = one execution attempt; incident_id = one investigation grouping. Counts are not interchangeable.'),
               ('Accounting ledger','Keep unknown reserves encumbered. Settlement records actual work and releases unused allocation. Closing a case never erases spent hours.'),
               ('Expiry semantics','An expired permission blocks a new write. An expired process lease does not prove an earlier write failed. Transfer ownership; reconcile before releasing capacity.')])
    p.footer('Do not turn a timeout into a second business action. Terminal classification requires trusted evidence and a fenced dispatch boundary.',
             'OBSERVE  /  unknown_count • oldest_unknown_age • duplicate attempts / action • definitive settlement coverage')
    p.save('action-state-machine','A lost response enters a durable unresolved state. Cancellation, retry and settlement each require a distinct proof.')

    grid(3,'Build the metric denominator before the dashboard',
        'Event identity, business intent, attempts and incidents have different grains and reconciliation rules.',
        ['01  /  SOURCES AND INGRESS','02  /  CANONICAL FACTS AND EVIDENCE','03  /  COHORTS AND DECISION PRODUCTS'],[
        ('Source envelope','source + event_id|Schema + occurred_at|Ingest timestamp','DUPLICATE EVENT CHECK'),
        ('Execution stream','action_id + attempt_id|Intent digest + version|Dispatch + outcome','ONE INTENT, MANY ATTEMPTS'),
        ('Human work log','incident_id + action links|Effort minutes + skill|Owner + disposition','NO PRIVATE MESSAGE CONTENT'),
        ('Action fact','One row / business action|Admission cohort time|Current + prior status','KEEP NONCOMPLETION'),
        ('Evidence journal','Protected object reference|Observation provenance|Postcondition verdict','APPEND-ONLY HISTORY'),
        ('Incident effort fact','One work entry / interval|No duplicate labor charge|Affected action bridge','SEPARATE LABOR GRAIN'),
        ('Mature cohort view','Fixed outcome window τ|Include all due actions|Flag late observations','DO NOT DROP TIMEOUTS'),
        ('Semantic metrics','Verified / admitted|Unknown by severity|Effort / 1,000 intents','VERSIONED DEFINITIONS'),
        ('Admission forecast','Risk-cell p and effort|Freshness + uncertainty|Pool-level reconciliation','CONTROL INPUT, NOT TRUTH')],
        [('0','3'),('1','4'),('2','5'),('3','6'),('4','7'),('5','8'),('6','7'),('7','8')],
        [('Join contract','Join action facts to incident links with explicit aggregation. A many-to-many bridge must not multiply action counts or billed recovery minutes.'),
         ('Time contract','Freeze the action cohort at admission. Evaluate by a stated outcome deadline. Store event and ingest time so late data can revise a versioned metric.'),
         ('Privacy contract','Public metrics use aggregate counts. Keep identities and evidence behind access controls. High-cardinality action IDs belong in traces or facts, not metric labels.')],
        'Distinct action counts reconcile across outcomes. Deduplicating an incident may reduce labor; it must not hide affected business actions.',
        'OBSERVE  /  unmatched action IDs • late-event share • unknown outcomes • labor reconciliation difference',
        'metric-lineage','A metric architecture keeps the business-action denominator separate from attempts, source events and deduplicated investigations.')

    grid(4,'Reserve capacity atomically, before granting dispatch',
        'A planning forecast becomes enforceable only when concurrent workers cannot spend the same headroom.',
        ['01  /  NON-NEGOTIABLE ELIGIBILITY','02  /  CAPACITY ACCOUNTING','03  /  RUNTIME CONTROL'],[
        ('Policy eligibility','Exact action approval|Current target + version|Risk tier permitted','DENY BEFORE CAPACITY'),
        ('Forecast snapshot','p_upper × effort estimate|Existing unresolved work|Finite staffing calendar','VERSION + VALID_UNTIL'),
        ('Pool allocation','Usable reviewer minutes|Reserve for uncertainty|Partition quotas sum ≤ pool','SKILL-CONSTRAINED'),
        ('Atomic budget row','Lock / compare-and-swap|Check epoch + headroom|Insert unique reservation','ONE TRANSACTION'),
        ('Dispatch permit','action_id + intent digest|Pool + budget epoch|Reserved work units','REPLAY RETURNS SAME ID'),
        ('Capability gateway','Check current hold state|Reject expired snapshot|No bypass egress','RECHECK AT DISPATCH'),
        ('Actual work charge','Record investigated effort|Replace forecast estimate|Retain period spend','NO DOUBLE-RELEASE'),
        ('Unresolved liability','Keep unknown encumbered|Increase estimate if needed|Transfer recovery owner','NO TTL AUTO-REFUND'),
        ('Controller update','Recompute headroom|Block affected admission|Reopen only through gates','HYSTERESIS + OWNER')],
        [('0','3',True),('1','3',True),('2','3',True),('3','4'),('4','5'),('5','8'),('6','8'),('7','8')],
        [('Admission inequality','actual_spend + unresolved_remaining + new_forecast ≤ usable_capacity. Use one period and non-overlapping accounting buckets.'),
         ('Distributed workers','A read-then-increment cache is insufficient. Use atomic conditional updates or disjoint, fenced sub-allocations whose sum is bounded.'),
         ('Model limit','Expected minutes are a planning weight, not a guarantee. Separate hard caps on in-flight actions, age and severity; actual work can exceed reserve.')],
        'Reservation IDs are unique per action and budget period. Cross-region failover must not resurrect a spent or invalidated permit.',
        'OBSERVE  /  forecast error • reservation contention • stale-epoch rejects • outstanding recovery liability',
        'atomic-admission','Atomic reservations prevent concurrent overspend; they cannot eliminate forecast error or authorize unsafe work.')

    grid(5,'Keep authority shorter-lived than the workflow',
        'Bind permission to an exact intent; isolate long-lived recovery responsibility from short-lived write authority.',
        ['01  /  IDENTITY AND DECISION','02  /  CONSTRAINED EXECUTION','03  /  REVOCATION AND RECOVERY'],[
        ('Workload identity','Attested runtime identity|Tenant binding + audience|No shared standing secret','IDENTITY ≠ PERMISSION'),
        ('Approval record','Exact target + diff|Approver identity + time|Evidence version','ONLY WHEN POLICY REQUIRES'),
        ('Grant issuer','Actor + subject|Action digest + expiry|Capability epoch','SIGNED APPLICATION CONTRACT'),
        ('Isolated agent','Receives scoped grant|No direct CRM credential|No self-approved extension','UNTRUSTED PLANNER'),
        ('Policy gateway','Verify issuer + audience|Validate digest + expiry|Check current revocation','SINGLE EGRESS PATH'),
        ('Domain enforcer','Validate local permission|Check current precondition|Consume approval once','COMMIT-TIME CHECK'),
        ('Revocation service','Advance capability epoch|Bound cache staleness|Fail closed on stale state','NO INSTANT-GLOBAL CLAIM'),
        ('Recovery identity','Separate accountable owner|Read/reconcile permission|New grant for correction','OLD LEASE NOT EXTENDED'),
        ('Audit journal','Link grant + action + result|Record denials + overrides|Retain authorized history','ACCESS-CONTROLLED')],
        [('0','1',True),('1','2',True),('2','3',True),('3','4'),('4','5'),('6','4',True),('7','8'),('5','8')],
        [('Example fields','grant_id; actor; tenant; operation; target; intent_hash; audience; expires_at; policy_version; capability_epoch. Field names are proposed, not a standard.'),
         ('Revocation bound','Effective stop latency depends on propagation, cache TTL, clock behavior and in-flight dispatch. Measure it at the domain boundary.'),
         ('Proof boundary','Sender-constrained tokens protect token use. They do not by themselves create one-use business approval or idempotent CRM mutations.')],
        'Neither an available exception budget nor an unexpired identity credential confers a standing right to change CRM state.',
        'OBSERVE  /  grant lifetime • revocation-to-enforcement latency • denied stale grants • direct-egress violations',
        'leased-authority','Leased authority and recovery ownership have different lifecycles. A compensation needs its own current authorization.')

    p=Plate(6,'Commit the action once; reconcile the missing response',
        'Sequence for one internal CRM mutation. Downstream email remains a separate, independently authorized action.')
    xs=[94,407,720,1033,1346]
    names=['Agent runtime','Policy gateway','CRM command API','Local database','Verifier / owner']
    for x,name in zip(xs,names):
        p.rect(x,215,275,69,stroke=BLUE);p.txt(x+137,256,name,21,BLUE,700,'middle')
        p.line([(x+137,284),(x+137,1070)],dashed=True,arrow=False,color=PALE)
    def msg(a,b,y,label):
        p.line([(xs[a]+137,y),(xs[b]+137,y)])
        p.txt(min(xs[a],xs[b])+148,y-13,label,19,BLUE)
    msg(0,1,355,'01  same action_id + digest')
    msg(1,2,440,'02  validate grant + permit')
    p.rect(1000,495,340,300,fill='white',stroke=BLUE,dashed=True)
    p.txt(1020,528,'LOCAL ATOMIC TRANSACTION',18,BLUE,700)
    p.block(1020,563,297,'Resolve idempotency key|Reject changed payload|Check new-write authority|Check current version|Apply one state delta|Store outcome + outbox|Consume local approval',20,29)
    msg(2,3,475,'03  command')
    msg(3,2,840,'04  committed result')
    p.line([(xs[2]+137,887),(xs[0]+137,887)],dashed=True,arrow=False)
    p.txt(329,875,'05  RESPONSE LOST: caller remains UNRESOLVED',20,BLUE,700)
    msg(0,2,958,'06  authenticated result lookup by original action_id')
    msg(3,4,1025,'07  trusted outcome / change history')
    p.rect(1660,214,197,875,stroke=PALE)
    p.block(1680,253,158,'BOUNDARY|The outbox relay may deliver more than once.|Each consumer deduplicates its own supported effects.|A refund or message is a new domain action.|No cross-system exactly-once claim.',20,30)
    p.footer('When the CRM response is lost, resolve the original intent. Use a same-key retry only under a supported domain idempotency contract.',
             'OBSERVE  /  intent-key conflicts • duplicate delivery • commit-to-verification lag • unresolved action age',
             'Sequence notation • Solid arrow = request / evidence • Dashed response = lost delivery • Dashed vertical = participant lifeline')
    p.save('domain-transaction','The sequence identifies the local atomic boundary, lost-response branch and separate downstream-effect contracts.')

    grid(7,'Verification needs evidence independent of the agent',
        'Compare the authorized change with trusted, versioned domain history before classifying completion.',
        ['01  /  INPUTS WITH DIFFERENT TRUST LEVELS','02  /  DETERMINISTIC CHECKS','03  /  DISPOSITION AND RECEIPT'],[
        ('Approved intent','Target + allowed fields|Expected pre-version|Expected postcondition','TRUSTED APPROVAL STORE'),
        ('Domain observation','Versioned change record|Original action correlation|Authoritative source','PROTECTED HISTORY'),
        ('Agent narrative','Claimed result + trace|Useful for diagnosis|Never sufficient proof','UNTRUSTED ASSERTION'),
        ('Identity match','Same tenant + target|Same intent/action ID|No cross-case evidence','REJECT MISBINDING'),
        ('Delta validator','Allowed fields changed|Expected version relation|No forbidden side effect','DETERMINISTIC RULES'),
        ('Evidence sufficiency','Handle delayed history|Detect conflicting versions|Bound observation window','UNKNOWN IS VALID OUTPUT'),
        ('Verified completion','Postcondition proven|Record verification time|Close forecast liability','RETAIN ACTUAL SPEND'),
        ('Unresolved / mismatch','Owner + risk + age|Preserve prior outcome|Start reconciliation','DO NOT ASSERT FAILURE'),
        ('Protected receipt','Intent + grant + evidence|Verifier version + verdict|Later revisions linked','AUDITABLE, NOT PUBLIC PII')],
        [('0','3'),('1','4'),('2','5',True),('3','4'),('4','5'),('5','6'),('5','7'),('6','8'),('7','8')],
        [('State can move again','A later legitimate update can overwrite the current value. Verify the historical transition and causality; a current-state read alone may be insufficient.'),
         ('Receipt contract','action_id; target_version; expected_delta_hash; observation_ref; verifier_version; verdict; observed_at. Redact public exports.'),
         ('No circular proof','The model that chose the action cannot certify it merely by repeating the plan. A model-based evaluator can supplement, but not replace, domain evidence.')],
        'A transport-level success code is insufficient unless its authenticated domain result establishes the required business postcondition.',
        'OBSERVE  /  evidence coverage • verification lag • mismatch rate • overturned verdicts • unresolved tail',
        'independent-verification','Verification links an approved postcondition to authoritative evidence without using the agent narrative as its own proof.')

    grid(8,'Design human recovery as a finite service system',
        'Assign work by risk, skill and deadlines; measure actual handling effort separately from elapsed waiting.',
        ['01  /  EXCEPTION INTAKE','02  /  SERVICE AND APPROVAL','03  /  RESOLUTION AND LEARNING'],[
        ('Exception router','Action + severity + age|Unknown effect retained|Attach protected evidence','NO GENERIC ALERT DUMP'),
        ('Incident grouping','Group common root cause|Keep all affected actions|Avoid duplicate labor logs','DEDUPE ≠ HIDE IMPACT'),
        ('Skill-aware queues','Routing vs refund vs IAM|Deadline + priority class|Accountable owner','NO UNLIMITED POOL'),
        ('Staffing calendar','Available service hours|Shifts + breaks + absence|Reserved emergency work','REAL CAPACITY INPUT'),
        ('Investigation desk','Resolve original outcome|Record handling minutes|Escalate unsafe ambiguity','READ BEFORE REISSUE'),
        ('Correction approval','Exact corrective delta|Current state version|Separate short-lived grant','NO AUTOMATIC ROLLBACK'),
        ('Recovery executor','Same enforcement gates|Independent verification|Stop on changed context','CORRECTION MAY FAIL'),
        ('Case settlement','Outcome + owner + effort|Partial effects retained|Reopen if evidence changes','REMAIN AUDITABLE'),
        ('Forecast update','Effort by incident type|Arrival bursts + clustering|Staffing bottleneck','BACKPRESSURE INPUT')],
        [('0','1'),('1','2'),('2','4'),('3','4',True),('4','5'),('5','6'),('6','7'),('7','8')],
        [('Worked daily capacity','4 reviewers × 4 available hours = 16 reviewer-hours/day. At 12 minutes per case, the fluid capacity is 80 cases/day.'),
         ('Two different clocks','Handling time measures labor. Calendar waiting includes nights, shifts, priority and missing skills. The stationary queue exhibit excludes those calendar effects.'),
         ('Customer-facing risk','A sent email cannot be unsent. A correction is a new action with its own possible harm, evidence and approval requirement.')],
        'Every unresolved action has an accountable recovery owner. No new autonomy is admitted on the assumption of unlimited human cleanup.',
        'OBSERVE  /  staffed hours • cases by skill • p95 calendar age • handling minutes • customer correction count',
        'human-recovery','The recovery architecture exposes staffing, skill constraints and the separate authorization of corrective actions.')

    p=Plate(9,'Throttle the affected capability, preserve recovery',
        'Use explicit state transitions and independent safety stops; a quiet metric interval alone cannot clear an incident.')
    p.card('n',64,285,555,235,'NORMAL','Policy gates pass; budgets current|Admit within assigned pool quota|Continue verification and telemetry','PER-CELL: TENANT × OPERATION × REGION')
    p.card('c',810,285,555,235,'CONSTRAINED','Headroom or queue-age threshold hit|Reduce new affected writes|Keep evidence and recovery paths','THRESHOLDS ARE OWNER-DEFINED')
    p.card('r',64,795,555,255,'RECOVERY','Reconcile pending effects|Verify corrective actions|Demonstrate bounded backlog and age','OWNER-APPROVED REENTRY')
    p.card('h',810,795,555,255,'HOLD','Block new affected writes|Fence stale dispatch permits|Keep unresolved obligations owned','HARD POLICY BREACH: IMMEDIATE STOP')
    p.connect('n','c',True);p.connect('c','h',True);p.connect('h','r',True);p.connect('r','n',True)
    p.txt(638,383,'REDUCE',18,BLUE,700);p.txt(638,884,'RECONCILE',18,BLUE,700)
    p.block(1124,625,247,'FRESHNESS FAILURE /|HARD CAP / SEVERITY',18,26,BLUE)
    p.block(64,625,231,'EXIT GATES +|AUTHORIZED REENTRY',18,26,BLUE)
    p.sidebar([('Separate triggers','Hard authority breach stops the relevant capability regardless of capacity. Budget pressure reduces admission. Missing critical telemetry can force HOLD.'),
               ('Hysteresis','Use distinct entry and exit thresholds, minimum evidence windows and an owner decision. Choose values from the actual service objective, not a generic percentage.'),
               ('Cell isolation','A routing incident need not stop safe evidence reads. Shared identity compromise can require a wider stop. The incident owner selects the containment scope.')])
    p.footer('Stopping new dispatch does not undo committed effects. Recovery and truthful outcome tracking remain active during HOLD.',
             'OBSERVE  /  state-change reason • containment latency • time in HOLD • unresolved age at reentry')
    p.save('backpressure-state-control','Capability-scoped backpressure has explicit hold, recovery and reentry behavior, with hard safety stops outside the capacity budget.')

    grid(10,'Prove the failure paths before increasing autonomy',
        'Release evidence must test authority, concurrency, unknown outcomes and recovery under constrained capacity.',
        ['01  /  PRE-PRODUCTION EVIDENCE','02  /  FAILURE INJECTION AND SHADOW','03  /  RELEASE DECISION'],[
        ('Point-in-time replay','Historical inputs only|Stable intent cohort|No future-state leakage','NO PRODUCTION WRITES'),
        ('Policy negative tests','Expired / wrong audience|Wrong tenant / target|Tampered approval digest','ALL MUST DENY'),
        ('Concurrency tests','Competing reservations|Duplicate action IDs|Stale epochs at failover','ASSERT CONSERVATION'),
        ('Unknown-outcome drill','Commit then drop response|Delay change evidence|Restart runtime / verifier','NO BLIND NEW INTENT'),
        ('Recovery exercise','Absent reviewer / wrong skill|One correlated incident|Failed compensation','TEST THE SERVICE CALENDAR'),
        ('Shadow evaluator','Proposed actions only|Compare current baseline|Measure evidence gaps','SIDE EFFECTS BLOCKED'),
        ('Bounded canary','Approved tenant + operation|Explicit volume and stop cap|Comparable mature cohorts','WATCH SEVERITY TAILS'),
        ('Release scorecard','Completion + labor + age|Per-risk-cell results|Uncertainty + missing data','NO AVERAGE-ONLY PASS'),
        ('Accountable decision','Scale / hold / reduce|Named owner + evidence|Recovery plan still funded','PUBLISH VERSIONED GATES')],
        [('0','3'),('1','4',True),('2','5',True),('3','6'),('4','7'),('5','8'),('6','7'),('7','8')],
        [('Required invariants','No policy-denied mutation. No duplicated supported domain effect. Unknowns survive restart. Reservations reconcile across workers and recovery ownership transfers.'),
         ('Coverage limit','A passing test suite shows the tested cases passed. It cannot establish zero production risk or validate an untested integration.'),
         ('Stop conditions','Unexpected side effect, evidence loss, stale permit acceptance or capacity-accounting drift blocks expansion. Preserve the failing trace and scope the repair.')],
        'A canary may expand only when its business outcomes and recovery obligations reconcile under the same stated cohort definition.',
        'OBSERVE  /  negative-test failures • duplicate effects • unknowns after restart • risk-cell completion • recovery effort',
        'release-assurance','Failure injection and bounded canaries test the real enforcement boundary and recovery burden before raising admission limits.')


def charts():
    d=results()
    p=Plate(11,'A 1% exception rate can exceed the recovery budget',
            'Hypothetical CRM workload: 10,000 actions/day; 12 minutes/case; 16 reviewer-hours/day.', 'ANALYTIC SCENARIO')
    p.txt(74,243,'A  /  DAILY RECOVERY DEMAND',24,BLUE,700)
    x0=380;scale=21
    for i,s in enumerate(d['scenarios']):
        y=331+i*166
        p.txt(74,y+14,f"{s['p']*100:.1f}% exceptions",23,INK,700)
        p.rect(x0,y-22,s['demand_hours']*scale,66,fill=LIGHT,stroke=BLUE,r=0)
        p.txt(x0+s['demand_hours']*scale+15,y+20,f"{s['demand_hours']:.0f} h / {s['cases']:.0f} cases",23,BLUE,700)
    for value in range(0,41,8):
        x=x0+value*scale;p.line([(x,288),(x,735)],color=PALE,arrow=False,width=1)
        p.txt(x,777,str(value),20,INK,anchor='middle')
    p.txt(783,818,'Reviewer-hours per day (zero baseline)',21,INK,anchor='middle')
    for val,label,y in [(12,'12 h planning allocation',859),(16,'16 h physical service capacity',906)]:
        x=x0+val*scale;p.line([(x,291),(x,735)],dashed=True)
        p.line([(420,y-12),(525,y-12)],dashed=True,arrow=False)
        p.txt(542,y-4,label,22,BLUE,700)
    p.rect(1415,215,441,842,stroke=BLUE)
    p.txt(1443,257,'B  /  STATISTICAL PLANNING',22,BLUE,700)
    p.block(1443,307,373,'Hypothetical mature cohort: 100 exceptions / 10,000 actions.|Wilson 95% interval for p:',23,31)
    p.txt(1443,468,'0.823% – 1.215%',35,BLUE,700)
    p.block(1443,531,373,'12 h usable / (p × 12 min)|Point p = 1%:',22,30)
    p.txt(1443,644,'6,000 actions/day',32,INK,700)
    p.block(1443,699,373,'Using the upper endpoint:',22,30)
    p.txt(1443,756,'4,939 actions/day',32,BLUE,700)
    p.block(1443,822,373,'Rounded down. A conservative planning choice, not a probability of safe operation or an SLA guarantee.',22,31)
    p.block(74,984,1237,'At 1%: 100 cases arrive against fluid capacity of 80. Starting empty, unresolved backlog grows by 20/day, reaching 100 after five working days.',25,34)
    p.footer('These are derived scenarios, not observed customer results. The interval assumes independent trials and a complete, fixed follow-up window.',
             'METHOD  /  D = N × p × m / 60 • capacity = reviewer count × available hours • cap = floor(60 × H × u / (p × m))',
             'Analytic exhibit • All numbers derive from declared hypothetical assumptions • No customer measurement or safety guarantee')
    p.save('capacity-and-uncertainty','Scenario demand exceeds daily service capacity at 1%. Wilson uncertainty lowers the illustrative planning cap from 6,000 to 4,939 actions/day.')

    p=Plate(12,'Queueing delay accelerates before full utilization',
            'Ideal M/M/4 benchmark: four continuously available reviewers; mean service time 12 minutes.', 'QUEUEING MODEL')
    x0=160;y0=908;cw=1135;ch=608
    def xy(rho,wait):return x0+(rho-.5)/.48*cw,y0-wait/460*ch
    for v in range(0,451,90):
        y=y0-v/460*ch;p.line([(x0,y),(x0+cw,y)],color=PALE,arrow=False,width=1)
        p.txt(x0-23,y+7,str(v),21,INK,anchor='end')
    for r in [.5,.6,.7,.8,.9,.98]:
        x,y=xy(r,0);p.txt(x,y+41,f'{r*100:.0f}%',22,INK,anchor='middle')
    p.txt(74,255,'WAIT IN QUEUE (MINUTES)',21,BLUE,700)
    p.txt(724,991,'Utilization ρ = arrivals / total service capacity',24,INK,anchor='middle')
    for metric,dash in [('mean_wait_min',False),('p95_wait_min',True)]:
        points=[xy(q['rho'],q[metric]) for q in d['queue_curve']]
        p.line(points,dashed=dash,arrow=False,width=4)
    p.line([(170,1060),(257,1060)],arrow=False,width=4);p.txt(276,1067,'Mean wait',23)
    p.line([(533,1060),(620,1060)],dashed=True,arrow=False,width=4);p.txt(640,1067,'95th percentile wait',23)
    p.rect(1410,215,447,875,stroke=BLUE)
    p.txt(1437,256,'SELECTED MODEL OUTPUTS',22,BLUE,700)
    p.txt(1437,310,'Load',21,BLUE,700);p.txt(1570,310,'Mean',21,BLUE,700);p.txt(1726,310,'p95',21,BLUE,700)
    for i,q in enumerate(d['queue_rows']):
        y=374+69*i
        p.txt(1437,y,f"{q['rho']*100:.0f}%",25,INK,700)
        p.txt(1570,y,f"{q['mean_wait_min']:.1f}m",25)
        p.txt(1726,y,f"{q['p95_wait_min']:.1f}m",25,BLUE,700)
    p.block(1437,758,385,'At ρ ≥ 1, this model has no finite stationary waiting-time distribution.|The plot ends at 98%. No curve is extrapolated through instability.',22,31)
    p.footer('Poisson arrivals, independent exponential service, FIFO and no abandonment. These are service-clock waits; real shifts and skills require a richer model.',
             'METHOD  /  Erlang C • E[Wq] = C / (cμ − λ) • P(Wq > t) = C exp[−(cμ − λ)t] • not measured operating latency',
             'Analytic exhibit • All numbers derive from declared hypothetical assumptions • No customer measurement or safety guarantee')
    p.save('queueing-tail','Waiting time grows nonlinearly as utilization approaches one. The model is a continuous-service benchmark, not a forecast of calendar waiting time.')


if __name__=='__main__':
    architectures();charts()
    (HERE/'figures.json').write_text(json.dumps(MANIFEST,indent=2)+'\n')
    print(f'Built {len(MANIFEST)} editable SVG exhibits')
