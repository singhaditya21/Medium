# Phase 2 package — Do Not Let an AI Agent Touch Production Until It Passes This Evaluation

Canonical source: [story Markdown](../../stories/do-not-let-an-ai-agent-touch-production-until-it-passes-this-evaluation.md)
Current Medium length: 6,609 words / 27 min
Target: 5,000–5,700 words / 20–25 min flagship

## Feed preview

**Title:** Do Not Let an AI Agent Touch Production Until It Passes This Evaluation

**Subtitle:** A deployment gate for full-system scenarios, tool failures, policy boundaries, shadow evidence, bounded canaries and rollback proof.

## Decision-oriented opening

A collections agent scores 94% on a curated conversation set. In a realistic rehearsal, the ledger and CRM disagree, a promise-to-pay is stale, policy changes mid-conversation, the payment API times out after accepting a request and an attachment tries to redirect the workflow. The agent retries with a new idempotency key, offers an out-of-policy term and closes the case before the system of record confirms the plan. None of those failures existed in the benchmark.

This story was written with AI writing and visualization assistance. All datasets, thresholds, sample sizes, results, coverage ratings and canary stages are synthetic reference scenarios.

Benchmark accuracy is evidence, not production authority. The evaluation unit is the complete deployable bundle—model, prompts, retrieval, memory, tools, identity, policy, retries, verifiers, runtime and rollback—inside a declared authority envelope. A release should pass only when versioned evidence supports the exact actions, populations, tools, value limits and failure conditions the agent will encounter, and when the control plane can enforce that bounded contract.

## First interior figure

Place `figure-02.png`, **Production evaluation architecture**, immediately after the opening. Keep `figure-01.png` as the visual transition into the technical deep dive.

## What this changes in production

- Replace a universal “production ready” label with a scoped deployment contract.
- Bind evaluation evidence to the exact artifact, environment and tool contracts.
- Evaluate stateful trajectories and business effects, not only final responses.
- Expand authority through shadow and multidimensional canaries.
- Expire, narrow or revoke authority when the validated envelope changes.

## Compact decision table

| Evidence state | Release decision | Authority | Required next step |
|---|---|---|---|
| Missing critical scenario or rollback proof | Block | None | Add executable evidence |
| Core claims pass, representative shadow incomplete | Shadow only | No external effects | Collect cohort evidence |
| Shadow passes, rare-event uncertainty remains | Bounded canary | Narrow actions and value | Monitor and accumulate exposure |
| Claims, controls and operations remain current | Promote within contract | Explicit envelope only | Continuous evaluation |
| Material artifact, policy or population change | Expire or narrow | Reduced/revoked | Re-evaluate affected claims |

## Recommended Medium structure

This remains the flagship. Preserve more technical depth than the other four stories, but make the main argument navigable.

1. Decision-oriented opening and `figure-02`.
2. **What this changes in production** summary and decision table.
3. Keep the deployment contract and a shortened YAML example.
4. Keep the evidence plane and data-governance section, but compress repeated lineage guidance.
5. Keep the assurance graph and claim record; retain `figure-03`.
6. Combine scenario taxonomy, coverage and executable test contracts; retain `figure-04`, `figure-05` and `figure-06`.
7. Combine metric hierarchy, trajectory diagnosis, fault injection and stateful tool simulation; retain `figure-07`, `figure-08` and `figure-09`.
8. Combine adversarial regression, shadow mode and canary expansion; retain `figure-10`, `figure-11` and `figure-12`.
9. Combine confidence bounds, zero-failure limits and evidence expiry; retain `figure-13`, `figure-14` and `figure-15`.
10. Keep machine-enforced promotion and SLOs; retain `figure-16` and `figure-17`.
11. End with authority rollout, failure modes, production-readiness checklist and series CTA.

Remove duplicated warnings that aggregate pass rate is insufficient. Establish that rule through the assurance graph and coverage matrix, then apply it consistently.

## Technical deep dive

Mark the section with: **Technical deep dive: executable evidence, uncertainty and authority gates.** Preserve the full test-contract schema, metric hierarchy, stateful simulator requirements, Wilson interval example, zero-failure upper-bound assumptions and signed promotion attestation. Keep the distinction between a model judge, a policy oracle, domain state and adjudicated business outcome.

## Implementation checklist

- Define a policy-enforceable deployment contract and prohibited actions.
- Hash the full artifact, policies, evaluators, tool contracts and environment.
- Build a claim graph with owners, thresholds, evidence, limitations and expiry.
- Create stateful scenarios with world state, faults, invariants and postconditions.
- Simulate permissions, versions, idempotency, async jobs and partial commits.
- Separate component, workflow, policy, reliability, human and business metrics.
- Report cohort denominators, uncertainty and label provenance.
- Run adversarial tests in isolation and convert failures into regressions.
- Use shadow mode before external-effect authority.
- Expand canaries by population, action, value, tool, volume, duration and reversibility.
- Make promotion, rollback and evidence expiry machine-enforced.
- Continuously monitor drift against the validated envelope.

## Related stories and CTA

- [Your Multi-Agent System Is a Distributed System](https://singhaditya21.github.io/Medium/articles/your-multi-agent-system-is-a-distributed-system/)
- [Your AI Agent Needs a Real Kill Switch](https://singhaditya21.github.io/Medium/articles/your-ai-agent-needs-a-real-kill-switch/)
- [Every AI Agent Action Needs a Receipt](https://singhaditya21.github.io/Medium/articles/every-ai-agent-action-needs-a-receipt/)

*Part of the Production AI Control Plane series—practical architectures for agent identity, authorization, governance, observability and recovery.*

*Follow Aditya Singh for production-grade enterprise AI architecture, governance and economics.*

## Feed-cover direction

A bold deployment gate separates a benchmark scorecard from a production system. The scorecard says `94%`; the gate requires four large proofs: `SCENARIOS`, `TOOLS`, `CANARY`, `ROLLBACK`. Avoid a dense coverage matrix on the cover.
