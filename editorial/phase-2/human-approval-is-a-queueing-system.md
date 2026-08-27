# Phase 2 package — Human Approval Is a Queueing System

Canonical source: [story Markdown](../../stories/human-approval-is-a-queueing-system.md)
Current Medium length: 6,214 words / 26 min
Target: 2,600–3,200 words / 10–13 min

## Feed preview

**Title:** Human Approval Is a Queueing System

**Subtitle:** Why one approval inbox creates hidden risk—and how to route agent decisions by impact, deadline, evidence and reviewer authority.

## Decision-oriented opening

An enterprise AI agent produces 12,000 proposals a day: record cleanup, refunds, pricing exceptions, data exports, customer messages and account termination. Governance sends every proposal to one approval inbox. By 11:00, 1,900 items are waiting. Reviewers learn that most are harmless, inspect less evidence and approve faster. A routine cleanup now sits ahead of an expiring containment decision. The dashboard still reports a 97% approval rate.

This story was written with AI writing and visualization assistance. All organizations, volumes, probabilities, losses, thresholds, reviewer behavior and service levels are synthetic reference scenarios.

The design error is treating “human in the loop” as a checkbox. Approval is a capacity-constrained decision service: work arrives unevenly, reviewers have different authority, evidence changes decision value and delay can create loss. The production question is not whether a human clicked. It is whether an eligible reviewer received the right evidence and made the decision before its safe operating window closed.

## First interior figure

Place `figure-02.png`, **Approval decision-service architecture**, immediately after the opening. Move the current comparison panel (`figure-01.png`) into the “why one queue fails” section or omit it from the Medium cut.

## What this changes in production

- Replace the global approval inbox with explicit service classes and terminal behavior.
- Route only to reviewers who satisfy role, jurisdiction, value-limit and separation-of-duties constraints.
- Bind every decision to an immutable proposal and evidence digest.
- Manage queue age as unresolved risk, not merely backlog volume.
- Use adjudicated outcomes to recalibrate automation and review thresholds.

## Compact decision table

| Action condition | Route | Deadline behavior | Required proof |
|---|---|---|---|
| Low impact, reversible, strong evidence | Execute under bounded authority | Verify asynchronously | Action receipt and sampled review |
| Moderate impact, non-urgent | Domain review queue | Expire and repropose | Eligible reviewer and evidence packet |
| High impact or time-sensitive | Priority review | Fail safe on missed deadline | Senior limit, exact delta, recovery plan |
| Irreversible or fast-propagating | Incident command | Contain first | Dual control and incident receipt |

## Recommended Medium structure

1. Decision-oriented opening and `figure-02`.
2. **What this changes in production** summary.
3. Collapse “Scope, scenario, and evidence boundary” into a short assumptions box.
4. Combine action-level risk, expected-loss analysis and service classes into one decision section; retain `figure-03`, `figure-04` and `figure-05`.
5. Keep the Erlang-C saturation cliff and one operational queue chart (`figure-06` plus either `figure-07` or `figure-08`).
6. Combine eligibility routing, separation of duties and approval packet into one control section; retain `figure-09` and `figure-11`.
7. Move detailed value-of-information, fatigue, threshold optimization, workforce portfolio and shadow calibration under **Technical deep dive**. Keep at most three figures there.
8. End with the migration sequence, production checklist and series CTA.

Cut repetition around the definitions of action-level risk, reviewer eligibility and evidence quality. Preserve equations only when the next paragraph interprets the operating decision they change.

## Technical deep dive

Mark the section with: **Technical deep dive: queue stability, expected loss and calibration.** It should retain the Erlang-C assumptions, expected-loss expression, one value-of-information example and the warning that synthetic fatigue scenarios are not human-subject findings.

## Implementation checklist

- Define immutable proposal, packet, decision and outcome schemas.
- Instrument arrival, assignment, open, decision, expiry, execution and adjudication timestamps.
- Create S0–S3 service classes with explicit expiry behavior.
- Enforce reviewer eligibility and forbidden role combinations at decision time.
- Bind approval to proposal and evidence digests.
- Alert on deadline risk, not only queue depth.
- Shadow-test new routing rules before changing autonomy.
- Measure false autonomy, false escalation, reviewer disagreement and appeals separately.

## Related stories and CTA

- [Every AI Agent Action Needs a Receipt](https://singhaditya21.github.io/Medium/articles/every-ai-agent-action-needs-a-receipt/)
- [Your AI Agent Needs a Real Kill Switch](https://singhaditya21.github.io/Medium/articles/your-ai-agent-needs-a-real-kill-switch/)
- [Do Not Let an AI Agent Touch Production Until It Passes This Evaluation](https://singhaditya21.github.io/Medium/articles/do-not-let-an-ai-agent-touch-production-until-it-passes-this-evaluation/)

*Part of the Production AI Control Plane series—practical architectures for agent identity, authorization, governance, observability and recovery.*

*Follow Aditya Singh for production-grade enterprise AI architecture, governance and economics.*

## Feed-cover direction

A clean split image: one overflowing FIFO inbox on the left and four risk-priced lanes on the right. Use large labels only—`FIFO`, `S0`, `S1`, `S2`, `S3`—with one red expiring action bypassing low-risk work. No equations or legends on the cover.
