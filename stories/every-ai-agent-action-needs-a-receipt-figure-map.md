# Figure map — Every AI Agent Action Needs a Receipt

All quantitative values are synthetic. Diagrams are reference architectures, not claims about a deployed system.

Renderer: reproducible Matplotlib PNG at 2400×1600. Each figure includes a technical analysis rail, control contract, assumptions, semantic legend, and evidence label.

| Figure | Tier | Analytical question / form | Supported takeaway | Inputs / assumptions |
|---:|---|---|---|---|
| 1 | Core | Observability is not proof · Comparison | Traces explain runtime behavior; a receipt proves one exact business action and its terminal state. | Reference architecture; no observed production data. |
| 2 | Core | Signed action-receipt control plane · Architecture | The receipt service seals intent before execution and completes proof only after effect verification. | Reference architecture; no observed production data. |
| 3 | Core | Business-action lineage graph · Lineage graph | One receipt connects request, evidence, policy, approval, authority, calls, outcome, verification, and recovery. | Reference architecture; no observed production data. |
| 4 | Core | Receipt-envelope contract · Structured schema | A versioned receipt binds exact intent, authority, request, effect, verification, signatures, and retention. | Reference architecture; no observed production data. |
| 5 | Core | Canonicalization before signing · Stage pipeline | Signing raw application JSON is unsafe; deterministic canonical bytes must be produced and verified identically. | Reference architecture; no observed production data. |
| 6 | Core | Digest chain and batch anchoring · Merkle structure | Per-receipt hashes plus batch roots make deletion, insertion, or mutation detectable without signing every storage page. | Reference architecture; no observed production data. |
| 7 | Core | Receipt signing and verification sequence · Sequence | A verifier must validate schema, canonicalization, signature, key status, timestamp, lineage, and observed effect. | Reference architecture; no observed production data. |
| 8 | Core | Trace context mapped into a receipt · Field mapping | Trace IDs correlate runtime data; receipt IDs and digests carry durable business semantics outside trace headers. | Reference architecture; no observed production data. |
| 9 | Core | Idempotency and ambiguity state machine · State machine | A stable action ID prevents duplicate business effects and makes ambiguous outcomes a durable reconciliation state. | Reference architecture; no observed production data. |
| 10 | Core | Timeout after effect: the ambiguity window · Timeline | A caller timeout cannot distinguish no effect from a committed effect; only target-state reconciliation can. | Reference architecture; no observed production data. |
| 11 | Core | Conditional mutation and receipt protocol · Sequence | Preconditions, idempotency, and verification prevent a valid action from overwriting newer business state. | Reference architecture; no observed production data. |
| 12 | Core | Ambiguous-outcome reconciliation tree · Decision tree | Recovery starts with authoritative state observation, then returns prior success, retries safely, compensates, or escalates. | Reference architecture; no observed production data. |
| 13 | Core | Selective disclosure and evidence compartments · Disclosure map | Auditors can verify the receipt core and Merkle proof without receiving customer payloads or broad operational telemetry. | Reference architecture; no observed production data. |
| 14 | Core | Failure-mode versus evidence-control matrix · Control matrix | No single signature, log, or idempotency key proves every property of a business action. | Ordinal reference matrix; coverage levels are architectural judgments, not measured effectiveness. |
| 15 | Core | Receipt storage and verification cost model · Cost model | Payload separation and batch anchoring control audit cost without sacrificing mandatory proof for high-risk actions. | Synthetic model: 10M actions/month, 3.2KB core, 8KB index/replication overhead, 42KB payload average; illustrative storage rates. |
| 16 | Core | Dispute reconstruction timeline · Audit timeline | A receipt reduces dispute resolution from log archaeology to deterministic verification and targeted evidence disclosure. | Reference architecture; no observed production data. |
| 17 | Core | Action-receipt operating objectives · SLO scorecard | Coverage, seal latency, verification, ambiguity, reconciliation, and key health require separate objectives and owners. | Synthetic 30-day window with two deliberate breaches to demonstrate escalation behavior. |
| 18 | Core | Adoption roadmap for action receipts · Maturity roadmap | Teams should start with one consequential action and prove end-to-end lineage before expanding receipt coverage. | Reference architecture; no observed production data. |

Palette: blue/teal for trusted or verified paths, gold for decisions, rust for risk/failure, and purple for transformation or policy context. Shape, position, and labels duplicate every color encoding.
