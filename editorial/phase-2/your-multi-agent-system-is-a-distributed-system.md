# Phase 2 package — Your Multi-Agent System Is a Distributed System

Canonical source: [story Markdown](../../stories/your-multi-agent-system-is-a-distributed-system.md)
Current Medium length: 6,261 words / 26 min
Target: 2,800–3,400 words / 11–14 min

## Feed preview

**Title:** Your Multi-Agent System Is a Distributed System

**Subtitle:** Fluent delegation is not coordination. Production agents need durable ownership, idempotent effects, fencing, causal state and recovery.

## Decision-oriented opening

Six AI agents coordinate a strategic renewal. Pricing commits an 8% discount and advances the account to version 21. Contract, still reading version 20, submits an incompatible term. Billing commits a schedule change, but its response times out. The workflow retries while a second worker takes over after a lease expires. Every model produced fluent output. The business now has overlapping owners, incompatible truths and an ambiguous charge.

This story was written with AI writing and visualization assistance. The company, traffic, failure rates and economics are synthetic; the diagrams are reference architectures.

Once independent agents can observe and mutate shared business state, the architecture is a distributed system. The control question is no longer “Can the agents collaborate?” It is whether one durable workflow owns the intent, stale owners are fenced, each semantic action creates at most one business effect, concurrent writes respect versions and every ambiguous outcome enters reconciliation instead of blind retry. Conversation quality cannot provide those guarantees. Domain services, workflow state and effect receipts must.

## First interior figure

Place `figure-02.png`, **Multi-agent renewal topology**, immediately after the opening. Keep `figure-01.png` only as a later visual summary or omit it from the Medium cut.

## What this changes in production

- Give one durable workflow—not a chat transcript—ownership of the business intent.
- Separate stable action identity from retry attempt identity.
- Require conditional writes, idempotency and fencing at the domain boundary.
- Treat timeouts after dispatch as ambiguous until authoritative state is reconciled.
- Model cross-domain recovery as a saga with explicit human-remediation states.

## Compact decision table

| Coordination problem | Required mechanism | Enforcement point | Failure outcome |
|---|---|---|---|
| Worker takeover | Lease plus monotonic epoch | Workflow store and domain gateway | Reject stale owner |
| Duplicate delivery | Stable action ID and idempotency ledger | Authoritative domain | Return recorded result |
| Concurrent mutation | Expected resource version | System of record | Reject and re-evaluate |
| Cross-domain partial completion | Saga and compensation graph | Durable workflow | Reconcile, compensate or escalate |

## Recommended Medium structure

1. Decision-oriented opening and `figure-02`.
2. **What this changes in production** summary and decision table.
3. Collapse the definitions section to six terms: workflow, action, attempt, effect, receipt and epoch.
4. Combine invariants and the message envelope; retain `figure-03` and a shortened message schema from `figure-04`.
5. Combine leases, fencing and split brain into one ownership section; retain `figure-06` and `figure-07`.
6. Combine transport semantics, idempotency, lost updates and causal order into one effect-integrity section; retain `figure-09`, `figure-10` and `figure-11`.
7. Keep saga and ambiguity recovery as the final core section; retain `figure-13` or `figure-14`.
8. Move replicated-state detail, chaos-test matrix, SLO scorecard, economics and ownership model under **Technical deep dive**.
9. End with a compact migration checklist and series CTA.

Remove repeated explanations that “exactly once” is not a transport feature. State the principle once, then prove it with the action/attempt/effect example.

## Technical deep dive

Mark the section with: **Technical deep dive: fencing, idempotency and saga recovery.** Preserve the ownership-epoch pseudocode, conditional-write contract, idempotency ledger fields and one ambiguous-effect reconciliation path. Link the longer canonical version for replicated workflow state and chaos-test coverage.

## Implementation checklist

- Define workflow, step, action, attempt, effect and receipt identifiers.
- Persist workflow transitions before dispatching external effects.
- Put resource version, authority digest, expiry and ownership epoch on every effect request.
- Enforce fencing and idempotency in each authoritative domain.
- Use a transactional outbox or equivalent durable handoff.
- Reconcile timeout-after-dispatch before retrying.
- Declare compensations, dependencies and human-remediation states.
- Test duplicate delivery, lease expiry, partition, stale write and partial compensation.

## Related stories and CTA

- [Every AI Agent Action Needs a Receipt](https://singhaditya21.github.io/Medium/articles/every-ai-agent-action-needs-a-receipt/)
- [Your AI Agent Needs a Real Kill Switch](https://singhaditya21.github.io/Medium/articles/your-ai-agent-needs-a-real-kill-switch/)
- [Do Not Let an AI Agent Touch Production Until It Passes This Evaluation](https://singhaditya21.github.io/Medium/articles/do-not-let-an-ai-agent-touch-production-until-it-passes-this-evaluation/)

*Part of the Production AI Control Plane series—practical architectures for agent identity, authorization, governance, observability and recovery.*

*Follow Aditya Singh for production-grade enterprise AI architecture, governance and economics.*

## Feed-cover direction

Show two workers racing toward one business record. The stale worker carries epoch `41`; the accepted worker carries epoch `42`. A large gateway rejects `41`. Keep the cover to three labels: `OWNER 42`, `STALE 41`, `REJECTED`.
