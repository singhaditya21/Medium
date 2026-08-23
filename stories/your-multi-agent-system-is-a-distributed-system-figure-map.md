# Figure map — Your Multi-Agent System Is a Distributed System

All quantitative values are synthetic. Diagrams are reference architectures, not claims about a deployed system.

Renderer: reproducible Matplotlib PNG at 2400×1600. Each figure includes a technical analysis rail, control contract, assumptions, semantic legend, and evidence label.

| Figure | Tier | Analytical question / form | Supported takeaway | Inputs / assumptions |
|---:|---|---|---|---|
| 1 | Core | Multi-agent fluency is not coordination · Comparison | Polite message exchange does not provide ownership, order, atomicity, idempotency, or recoverable business effects. | Reference architecture; no observed production data. |
| 2 | Core | Multi-agent renewal topology · Architecture | Specialized agents coordinate through a durable workflow and domain APIs rather than granting peers direct shared-state mutation. | Reference architecture; no observed production data. |
| 3 | Core | Coordination invariant map · Invariant map | Every consequential workflow needs explicit ownership, uniqueness, ordering, state, authority, effect, and recovery invariants. | Reference architecture; no observed production data. |
| 4 | Core | Versioned agent-message envelope · Structured schema | A message needs stable workflow, action, step, attempt, causal parent, schema, expiry, authority, and payload digests. | Reference architecture; no observed production data. |
| 5 | Core | Orchestration versus choreography · Decision matrix | Use choreography for decoupled facts and orchestration for constrained multi-step business invariants; combine them deliberately. | Ordinal architectural comparison; not measured performance. |
| 6 | Core | Ownership lease and failover timeline · Lease timeline | A durable lease limits ownership in time, but takeover is safe only when stale owners are fenced from writes. | Reference architecture; no observed production data. |
| 7 | Core | Fencing-token enforcement sequence · Sequence | Every protected write carries a monotonically increasing epoch so a paused former owner cannot commit after takeover. | Reference architecture; no observed production data. |
| 8 | Core | Durable workflow as a replicated state machine · State machine | Workflow commands become committed state transitions before side-effect workers act, allowing restart and deterministic replay. | Reference architecture; no observed production data. |
| 9 | Core | Delivery semantics versus business guarantees · Comparison matrix | At-most-once, at-least-once, and ordered delivery each leave application responsibilities; none alone creates exactly-once business outcome. | Reference architecture; no observed production data. |
| 10 | Core | Idempotency ledger for every effect · Structured ledger | A stable business action ID and proposal digest turn redelivery into a recorded result rather than a second effect. | Reference architecture; no observed production data. |
| 11 | Core | Concurrent quote update race · Timeline | Optimistic concurrency prevents pricing and contracting agents from overwriting each other's decisions on stale state. | Reference architecture; no observed production data. |
| 12 | Core | Causal ordering across agent events · Causal graph | Causal parents and resource versions prevent a late message from reversing a later business decision. | Reference architecture; no observed production data. |
| 13 | Core | Renewal saga state machine · Saga | Long-lived workflows commit local transactions and use explicit compensations when later steps fail. | Reference architecture; no observed production data. |
| 14 | Core | Compensation dependency graph · Recovery graph | Compensations run by dependency and business risk—not blindly in reverse message order. | Reference architecture; no observed production data. |
| 15 | Core | Split-brain failure tree · Failure tree | Duplicate owners emerge from partition, delayed lease observation, clock assumptions, or state-store failover; fencing contains their writes. | Reference architecture; no observed production data. |
| 16 | Core | Coordination chaos-test matrix · Test matrix | Fault injection must cover messages, workers, stores, clocks, domains, and compensations while asserting business invariants. | Reference test matrix with intentionally mixed pass/breach cells; no production test results. |
| 17 | Core | Multi-agent coordination objectives · SLO scorecard | Duplicate effects, stale-owner rejects, ambiguity age, saga recovery, and invariant breaches need independent objectives. | Synthetic 30-day window with deliberate ambiguity-age and compensation breaches. |
| 18 | Core | Migration to durable multi-agent coordination · Maturity roadmap | Teams should stabilize one-agent business effects before adding specialized agents and distributed ownership. | Reference architecture; no observed production data. |

Palette: blue/teal for trusted or verified paths, gold for decisions, rust for risk/failure, and purple for transformation or policy context. Shape, position, and labels duplicate every color encoding.
