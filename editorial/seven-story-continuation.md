# Seven-story continuation — production-grade agent systems

Status: active editorial and engineering program  
Audience: technical leaders, platform engineers, security architects, product owners, risk leaders, and enterprise operators  
Delivery surface: the repository's existing GitHub Pages article system  
Canonical policy: GitHub Pages is the original; any later Medium import must preserve that canonical URL  

## Quality contract

Every story must satisfy all of the following before publication:

- 6,000–8,000 words of substantive narrative, excluding captions and code.
- A technical summary that states the decision-useful result before the methods.
- Concrete business scenario, control boundary, data model, formulas, implementation code, failure analysis, operating model, migration plan, and limitations.
- At least 18 bespoke figures, for a program total of at least 126 figures.
- A compact 3:2 deep-dive visual system at 2400×1600 with a dominant technical canvas, figure-specific analysis, explicit assumptions, and no generic decorative rail.
- A chart map that records the analytical question, selected form, fields, source or assumptions, supported claim, and final asset path.
- Primary-source references near material technical claims. Standards, specifications, official documentation, and original research papers take priority.
- Honest quantitative framing: observed, benchmark, illustrative, and simulated evidence must never be mixed. Synthetic models must declare units, formulas, parameters, seeds, and limitations.
- Every image needs descriptive alt text and a caption that identifies AI-assisted design and whether the content is synthetic or a reference architecture.
- Generated prose must be disclosed within the first two paragraphs. The author must review factual claims and add any personal experience before a later Medium publication action.
- GitHub Pages build, site validation, Medium release validation, image QA, responsive visual QA, and live-URL verification must pass.

## Story 08 — Your AI Agent's Memory Is a Database, Not a Prompt

Subtitle: A production blueprint for provenance, temporal validity, trust zones, poisoning resistance, retention, and deletion.

Decision: whether an enterprise should permit retrieved or learned memory to influence consequential agent actions.

Thesis: memory is governed data with provenance, validity, purpose, access, retention, and revocation—not undifferentiated text appended to a context window.

Business scenario: a revenue agent combines CRM records, email, support tickets, prior model summaries, and user corrections while preparing a renewal intervention. One poisoned note or stale discount term can redirect a high-value decision.

Core technical spine:

1. Memory threat model and business failure surface.
2. Six-plane architecture: ingestion, provenance, trust, retrieval, policy, and deletion.
3. Bitemporal memory record and source-of-truth hierarchy.
4. Trust scoring, freshness decay, corroboration, and uncertainty.
5. Poisoning quarantine, retrieval-time policy, and decision-time evidence binding.
6. Retention, legal hold, consent, correction, and cryptographic erasure patterns.
7. Memory SLOs, evaluation design, operational ownership, and rollout.

Figure program (18): memory-vs-prompt comparison; end-to-end memory control plane; source trust-zone map; provenance graph; memory-envelope schema; bitemporal timeline; ingestion validation pipeline; poisoning attack graph; quarantine state machine; freshness-decay curves; trust/corroboration formula; retrieval decision tree; policy-filtered vector search; conflict-resolution matrix; deletion propagation sequence; retention heatmap; memory SLO scorecard; phased migration roadmap.

Primary evidence set:

- W3C PROV-DM and PROV-O for entities, activities, agents, derivation, attribution, and invalidation.
- NIST AI RMF and the Generative AI Profile for lifecycle risk, data governance, measurement, and monitoring.
- OWASP prompt-injection guidance for direct and indirect instruction attacks.
- Official database and access-control documentation where implementation semantics are referenced.

## Story 09 — Every AI Agent Action Needs a Receipt

Subtitle: How signed action receipts turn opaque tool use into auditable, replay-safe, recoverable business transactions.

Decision: what durable evidence an organization must require before an agent action is considered complete.

Thesis: a trace explains execution; a receipt proves the exact intent, evidence, authority, request, effect, verification, and recovery state of a business action.

Business scenario: an agent applies a pricing exception, triggers billing, and sends a customer notice. A timeout occurs after the CRM mutation but before the orchestrator sees the response.

Core technical spine:

1. Trace, log, event, and receipt semantics.
2. Receipt control plane and append-only lineage.
3. Canonicalization, digests, signatures, timestamping, and key rotation.
4. Idempotency, conditional mutation, ambiguity, and reconciliation.
5. Cross-service correlation without storing sensitive payloads in trace context.
6. Evidence retention, selective disclosure, dispute handling, and audit economics.
7. Receipt SLOs, schema evolution, verification, and rollout.

Figure program (18): observability-vs-proof comparison; receipt architecture; business-action lineage graph; receipt-envelope schema; canonicalization pipeline; digest/Merkle chain; signature and verification sequence; trace-to-receipt mapping; idempotency state machine; timeout ambiguity timeline; conditional-write protocol; reconciliation decision tree; selective-disclosure map; tamper-evidence matrix; receipt storage cost model; dispute-resolution timeline; receipt SLO scorecard; adoption roadmap.

Primary evidence set:

- W3C Trace Context and OpenTelemetry data models for interoperable correlation.
- CloudEvents for a common event envelope.
- RFC 8785 for canonical JSON, RFC 7515 for JSON Web Signatures, and RFC 3161 for trusted timestamp semantics.
- W3C PROV for lineage and derivation.

## Story 10 — Human Approval Is a Queueing System

Subtitle: How to price review capacity, escalation risk, response time, fatigue, and value of information.

Decision: which agent actions require review, which reviewer should receive them, and how much review capacity the business should fund.

Thesis: human-in-the-loop is not a boolean safety feature; it is a capacity-constrained decision service whose delay, error, and fatigue can be modeled and operated.

Business scenario: 12,000 daily agent proposals span low-risk record cleanup, contract changes, refunds, pricing exceptions, and account termination. A uniform approval rule creates a backlog and trains reviewers to approve mechanically.

Core technical spine:

1. Approval as a risk-priced service, not a modal dialog.
2. Action-level risk, expected loss, reversibility, novelty, and evidence quality.
3. Queueing model, service classes, abandonment, and deadline breach.
4. Reviewer eligibility, separation of duties, and conflict controls.
5. Approval packet design and minimum decision information.
6. Threshold optimization, shadow review, calibration, and automation promotion.
7. Workforce model, SLOs, governance, and rollout.

Figure program (18): naive-vs-risk-based approval; approval service architecture; action-risk decomposition; expected-loss formula; service-class matrix; M/M/c sensitivity surface; arrival/service timeline; backlog growth scenarios; reviewer-skill routing; separation-of-duties graph; approval packet anatomy; evidence-quality score; value-of-information curve; fatigue/error relationship; threshold frontier; shadow-review confusion matrix; approval SLO scorecard; operating roadmap.

Primary evidence set:

- NIST AI RMF Core and Playbook for human oversight, roles, accountability, risk tolerance, and documented evaluation.
- NIST SP 800-53 AC-5 and AC-6 for separation of duties and least privilege.
- Declared queueing and decision-theory derivations; all operating volumes and performance values remain synthetic.

## Story 11 — Your Multi-Agent System Is a Distributed System

Subtitle: Why delegation, retries, races, partial failure, leases, and sagas matter more than conversational fluency.

Decision: how to coordinate multiple specialized agents without duplicate, conflicting, or partially committed business effects.

Thesis: multi-agent reliability comes from distributed-systems invariants—stable identity, ownership, ordering, idempotency, fencing, durable state, and compensation—not from agents politely exchanging messages.

Business scenario: sales, pricing, contracting, billing, fulfillment, and communication agents cooperate on a renewal. Two agents race on the same quote while a downstream call succeeds after its caller times out.

Core technical spine:

1. Coordination failure model and invariant catalog.
2. Orchestrated versus choreographed topology.
3. Durable workflow state, ownership leases, fencing, and leader election.
4. At-least-once delivery, idempotency, conditional writes, and deduplication.
5. Sagas, compensation, irreversible effects, and human intervention.
6. Causal ordering, stale messages, split brain, and reconciliation.
7. Multi-agent SLOs, chaos testing, and migration.

Figure program (18): conversation-vs-distributed-system comparison; multi-agent topology; invariant map; message envelope; orchestration/choreography decision matrix; ownership lease timeline; fencing-token sequence; replicated-state-machine view; delivery-semantics comparison; idempotency ledger; concurrent-update race; causal-ordering graph; saga state machine; compensation graph; split-brain failure tree; chaos-test matrix; coordination SLO scorecard; rollout roadmap.

Primary evidence set:

- Raft paper for replicated logs, leader election, and safety concepts.
- Kubernetes Lease API for production coordination semantics.
- RFC 9110 for idempotency and retry constraints; the current IETF Idempotency-Key work only with its draft status made explicit.
- Garcia-Molina and Salem's original Sagas paper for long-lived transactions and compensation.

## Story 12 — Model Routing Is Capital Allocation

Subtitle: A risk-adjusted method for allocating quality, latency, token, verification, and failure budgets across agent workflows.

Decision: which model and reasoning path should handle each step of a business workflow under quality, risk, latency, and budget constraints.

Thesis: production routing is a portfolio decision over expected business utility and tail loss, not a prompt classifier that sends “hard” requests to a larger model.

Business scenario: one million monthly agent tasks range from extraction and classification to pricing analysis and customer-facing negotiation. Token price alone understates retries, tool calls, verification, and error cost.

Core technical spine:

1. Workflow cost ledger and hidden token inflation.
2. Quality, latency, reliability, privacy, and business-loss constraints.
3. Constrained optimization and risk-adjusted utility.
4. Router features, calibration, uncertainty, and out-of-distribution detection.
5. Cascades, parallelism, escalation, fresh-context retry, and verification.
6. Offline policy evaluation, counterfactual replay, and guardrail budgets.
7. Routing SLOs, FinOps ownership, and rollout.

Figure program (18): static-vs-economic routing; routing control plane; workflow cost ledger; utility formula; model capability matrix; Pareto frontier; risk-adjusted efficient frontier; route decision tree; feature and policy pipeline; calibration curve; OOD routing map; cascade sequence; retry-inflation waterfall; verification allocation; budget shadow-price curve; counterfactual evaluation design; routing SLO scorecard; rollout roadmap.

Primary evidence set:

- RouteLLM, Hybrid LLM, FrugalGPT, and RouterBench primary research for cost-quality routing approaches and their limitations.
- MLCommons inference metrics for latency, throughput, TTFT, TPOT, and agentic end-to-end duration.
- NIST AI RMF Map 3 for documented expected benefits, monetary and non-monetary costs, benchmarks, and risk tolerance.

## Story 13 — Your AI Agent Needs a Real Kill Switch

Subtitle: A production architecture for revocation, fencing, network containment, draining, reconciliation, and recovery.

Decision: how an enterprise can reliably stop an agent's authority and effects during compromise or unsafe behavior.

Thesis: a dashboard toggle is not a kill switch; containment must revoke authority, fence stale workers, stop egress, drain in-flight work, reconcile ambiguous effects, and prove recovery.

Business scenario: a compromised revenue-operations agent begins issuing anomalous changes across CRM, CPQ, email, and data-export tools while some workers are disconnected from the control plane.

Core technical spine:

1. Kill-switch threat model and stop-time objective.
2. Multi-layer containment architecture.
3. Token and lease revocation, continuous security events, and propagation.
4. Fencing epochs, workload quarantine, network deny, and tool disablement.
5. In-flight drain, ambiguous effects, reconciliation, and compensation.
6. Recovery authorization, staged re-entry, evidence preservation, and drills.
7. Containment SLOs, ownership, and rollout.

Figure program (18): UI-toggle-vs-containment comparison; kill-switch architecture; authority revocation graph; security-event propagation sequence; revocation latency budget; fencing-epoch timeline; stale-worker rejection; default-deny egress map; tool kill matrix; drain state machine; in-flight action inventory; ambiguous-effect decision tree; containment blast-radius model; recovery authorization chain; drill scenario timeline; control coverage matrix; containment SLO scorecard; rollout roadmap.

Primary evidence set:

- RFC 7009 for OAuth token revocation, RFC 8417 for Security Event Tokens, and OpenID Shared Signals/CAEP for continuous access attenuation.
- Kubernetes NetworkPolicy and Lease documentation for default-deny egress and coordination semantics.
- NIST SP 800-61 Rev. 3 for incident-response preparation, detection, containment, recovery, and improvement.

## Story 14 — Do Not Let an AI Agent Touch Production Until It Passes This Evaluation

Subtitle: A deployment gate for scenario coverage, tool safety, shadow traffic, canaries, SLOs, red teams, and rollback.

Decision: what evidence is sufficient to promote an agent from development to bounded production authority.

Thesis: benchmark accuracy is not production readiness; an agent must demonstrate system-level behavior across tasks, tools, policies, failures, recovery, and operating conditions similar to deployment.

Business scenario: a collections agent performs well on curated conversations but fails when accounts have conflicting records, stale promises, unavailable tools, policy changes, or adversarial attachments.

Core technical spine:

1. Evaluation claim model and deployment contract.
2. Scenario taxonomy, coverage, and evidence quality.
3. Component, workflow, policy, safety, and business-outcome metrics.
4. Tool simulation, fault injection, adversarial testing, and metamorphic checks.
5. Shadow traffic, counterfactual replay, canary authority, and promotion gates.
6. Statistical confidence, rare-event bounds, drift, and continuous evaluation.
7. Evaluation governance, independent review, SLOs, and rollback.

Figure program (18): benchmark-vs-production-readiness comparison; evaluation architecture; claim-evidence graph; scenario taxonomy; coverage matrix; test-case schema; metric hierarchy; failure-injection map; tool-simulator architecture; adversarial test pipeline; shadow-mode sequence; canary authority ladder; confidence-interval chart; rare-event upper-bound curve; drift detection timeline; promotion decision tree; evaluation SLO scorecard; continuous-evaluation roadmap.

Primary evidence set:

- NIST AI RMF Core, Generative AI Profile, AI Resource Center, and TEVV guidance for documented, repeatable, deployment-relevant evaluation and monitoring.
- NIST's August 2026 TEVV-Athlon initial public draft, explicitly labeled as a draft, for a current customizable evaluation framework.
- MLCommons agentic and inference benchmark definitions for end-to-end duration and serving metrics where relevant.

## Cross-story structure map

The technical-report contract maps to each story as follows:

| Required role | Reader-facing implementation |
|---|---|
| Title | Specific decision or failure-mode title |
| Technical summary | Opening thesis, business consequence, and production result |
| Key findings with visual evidence | Core visual path of 8–10 figures embedded beside interpretation |
| Scope, data, and definitions | Explicit definitions, synthetic/observed boundary, units, and scenario |
| Methodology | Architecture, formulas, algorithms, schemas, code, and assumptions |
| Limitations and robustness | Failure modes, sensitivity, non-goals, counterexamples, and uncertainty |
| Recommended next steps | Phased production migration with gates and owners |
| Further questions | Open engineering and governance questions that could change the design |

## Publication sequence

The sequence is intentional: memory determines what the agent may believe; receipts determine what can be proven; approval determines which actions need people; distributed coordination determines how multiple actors commit; routing determines how compute and risk budgets are allocated; containment determines how authority stops; evaluation determines whether production authority should begin or expand.
