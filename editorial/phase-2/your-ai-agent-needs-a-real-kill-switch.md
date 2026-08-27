# Phase 2 package — Your AI Agent Needs a Real Kill Switch

Canonical source: [story Markdown](../../stories/your-ai-agent-needs-a-real-kill-switch.md)
Current Medium length: 6,688 words / 27 min
Target: 2,800–3,400 words / 11–14 min

## Feed preview

**Title:** Your AI Agent Needs a Real Kill Switch

**Subtitle:** A dashboard toggle cannot stop cached authority, stale workers or queued effects. Production containment needs fencing, proof and recovery.

## Decision-oriented opening

At 09:19, security clicks **Disable agent**. The dashboard turns green. One worker stops polling, but another is partitioned from the control plane, a third still has a cached vendor session and asynchronous jobs are already waiting on external queues. A price change commits at 09:21. Two emails leave at 09:23. The response team still cannot classify what was rejected, accepted, committed, duplicated or left ambiguous.

This story was written with AI writing and visualization assistance. The incident, action counts, latency budgets, exposure curves and control ratings are synthetic reference scenarios.

An agent’s authority is distributed across tokens, sessions, workload leases, delegated children, network paths, tool-side jobs and in-flight operations. A central flag records intent; it does not remove those capabilities. A real kill switch is a containment protocol: advance a monotonic epoch, revoke the authority graph, fence stale workers at effect boundaries, remove reachability, classify in-flight work, reconcile uncertain effects and require fresh authorization for recovery. It must also produce independent proof that every material boundary complied.

## First interior figure

Place `figure-02.png`, **Multi-layer kill-switch architecture**, immediately after the opening. Keep `figure-01.png` as an optional comparison at the start of the deep dive.

## What this changes in production

- Define containment scope independently of process identity.
- Propagate a signed containment epoch to every material enforcement point.
- Reject stale authority at tool and data effect boundaries, even when a worker is disconnected.
- Inventory actions by effect state, not only by running process.
- Treat recovery as a new, evidence-bound authorization event.

## Compact decision table

| In-flight state | Safe containment action | Retry allowed? | Required evidence |
|---|---|---|---|
| Proposed or authorized | Revoke and discard | Only with new authority | Revocation receipt |
| Dispatched, not accepted | Cancel or fence | After terminal proof | Queue/tool acknowledgement |
| Accepted, outcome unknown | Reconcile authoritative state | No blind retry | Effect query and action ID |
| Committed | Verify, compensate or freeze | Not as a duplicate action | Domain receipt and recovery decision |

## Recommended Medium structure

1. Decision-oriented opening and `figure-02`.
2. **What this changes in production** summary and decision table.
3. Combine the falsifiable stop claim and threat model into one containment contract.
4. Combine containment layers, authority-graph revocation and security-event propagation; retain `figure-03` and `figure-04`.
5. Combine stop-time budget, fencing and stale-worker rejection; retain `figure-05` and `figure-07`.
6. Combine network deny and tool-specific kill contracts; retain `figure-08` or `figure-09`.
7. Combine in-flight inventory and ambiguity handling; retain `figure-10` and `figure-12`.
8. Keep recovery authorization as the closing architecture section; retain `figure-14`.
9. Move blast-radius equations, drill design, coverage grading, SLOs and business case under **Technical deep dive**.
10. End with the rollout checklist and series CTA.

Remove repeated statements that token revocation is insufficient. Demonstrate it once with the authority graph, then move directly to enforceable epochs and effect-state reconciliation.

## Technical deep dive

Mark the section with: **Technical deep dive: stop-time budgets, fencing and ambiguous effects.** Preserve the `STO` and effect-reconciliation objectives, the epoch check, one timeout-after-accept decision tree and the synthetic blast-radius model with its assumptions.

## Implementation checklist

- Inventory principals, sessions, grants, leases, child agents, queues, tools and network paths.
- Define containment scopes and a signed monotonic epoch contract.
- Enforce epoch freshness at every protected effect boundary.
- Issue short-lived, audience-bound authority and deny stale grants.
- Add default-deny egress containment and tool-specific cancel/freeze controls.
- Maintain an in-flight action ledger with authoritative state.
- Reconcile ambiguous effects before retrying.
- Require fresh credentials, a higher epoch, shadow mode and bounded canary for recovery.
- Drill partitioned workers, cached sessions, queued work and partial commits.

## Related stories and CTA

- [Your AI Agent Should Not Have a Standing Role](https://singhaditya21.github.io/Medium/articles/your-ai-agent-should-not-have-a-standing-role/)
- [Your Multi-Agent System Is a Distributed System](https://singhaditya21.github.io/Medium/articles/your-multi-agent-system-is-a-distributed-system/)
- [Every AI Agent Action Needs a Receipt](https://singhaditya21.github.io/Medium/articles/every-ai-agent-action-needs-a-receipt/)

*Part of the Production AI Control Plane series—practical architectures for agent identity, authorization, governance, observability and recovery.*

*Follow Aditya Singh for production-grade enterprise AI architecture, governance and economics.*

## Feed-cover direction

A large red `STOP` command fans out to seven enforcement boundaries. Six show verified locks; one stale worker is visibly rejected at an effect gateway. Use only the labels `COMMAND`, `EPOCH`, `PROOF`.
