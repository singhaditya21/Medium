# Phase 2 package — Model Routing Is Capital Allocation

Canonical source: [story Markdown](../../stories/model-routing-is-capital-allocation.md)
Current Medium length: 6,686 words / 27 min
Target: 2,800–3,400 words / 11–14 min

## Feed preview

**Title:** Model Routing Is Capital Allocation

**Subtitle:** Stop sending “easy” work to a cheap model. Allocate model, context and verification budgets against business value and failure loss.

## Decision-oriented opening

A production router sends “easy” tasks to a cheap model and “hard” tasks to a large one. That rule looks efficient until a short, syntactically simple request changes a $2.4 million quote while a long, technically complex request only drafts an internal summary. Difficulty is not exposure. Token price is not completed-workflow cost. Average quality is not the loss distribution.

This story was written with AI writing and visualization assistance. All routes, costs, budgets, loss estimates, performance values and charts are synthetic reference scenarios.

Model routing is a capital-allocation problem. Each action competes for a portfolio of model capacity, context, tools, retries, latency and verification. The router must first remove routes that violate policy or cannot satisfy the action’s assurance floor. It should then maximize expected business value net of workflow cost, delay and tail loss—not merely choose the lowest-priced model above a generic score. The output is a governed route bundle with evidence, limits and an accountable decision record.

## First interior figure

Place `figure-02.png`, **Risk-aware routing control plane**, immediately after the opening. Move `figure-01.png` to the start of the deep dive or omit it from the Medium cut.

## What this changes in production

- Route an action cohort, not an isolated prompt.
- Filter policy-ineligible routes before economic optimization.
- Price the completed workflow, including tools, retries, verification, delay and recovery.
- Calibrate route suitability by cohort and abstain outside evaluated support.
- Allocate verification where its marginal expected-loss reduction is highest.

## Compact decision table

| Routing signal | Wrong shortcut | Production treatment | Output |
|---|---|---|---|
| Action impact | “Prompt looks easy” | Apply assurance and policy floor | Eligible route set |
| Workflow cost | Token price | Include tools, retries, latency and recovery | Expected total cost |
| Quality | Global benchmark | Use calibrated cohort evidence | Suitability distribution |
| Budget pressure | Cheapest model | Use marginal value and hard limits | Governed route bundle |

## Recommended Medium structure

1. Decision-oriented opening and `figure-02`.
2. **What this changes in production** summary and decision table.
3. Collapse scope and decision-unit definitions into a short action-route contract.
4. Keep completed-workflow accounting and risk-adjusted utility; retain `figure-03` and `figure-04`.
5. Combine capability matrix, Pareto frontier and business-loss frontier; retain `figure-05` and either `figure-06` or `figure-07`.
6. Combine policy filtering, feature versioning, calibration and OOD abstention into one governed-router section; retain `figure-08`, `figure-10` and `figure-11`.
7. Combine cascades, retry inflation and verification allocation; retain `figure-13` and `figure-14`.
8. Move shadow-price mathematics, counterfactual evaluation, SLOs, operating model and business case under **Technical deep dive**.
9. End with the migration plan, checklist and series CTA.

Cut repeated contrasts between “cheap versus large” and “capital allocation.” Establish the thesis once, then use the cost ledger and constrained-utility equation as the evidence.

## Technical deep dive

Mark the section with: **Technical deep dive: constrained utility, calibration and counterfactual routing.** Preserve one objective function, the hard policy constraints, the distinction between chosen-route and candidate-route evidence, and the warning about selection bias in replay evaluation.

## Implementation checklist

- Define the action cohort and business postcondition before selecting a model.
- Maintain a versioned portfolio of model, context, tool, retry and verification bundles.
- Record workflow-level cost and outcome, not only token usage.
- Apply policy, privacy, residency and assurance floors before scoring utility.
- Calibrate suitability by cohort and expose uncertainty.
- Add an abstain or conservative route for unsupported requests.
- Log candidate routes for defensible counterfactual evaluation.
- Set separate quality, latency, budget, loss and policy objectives.

## Related stories and CTA

- [What an Agent Actually Costs](https://singhaditya21.github.io/Medium/articles/what-an-agent-actually-costs/)
- [Human Approval Is a Queueing System](https://singhaditya21.github.io/Medium/articles/human-approval-is-a-queueing-system/)
- [Do Not Let an AI Agent Touch Production Until It Passes This Evaluation](https://singhaditya21.github.io/Medium/articles/do-not-let-an-ai-agent-touch-production-until-it-passes-this-evaluation/)

*Part of the Production AI Control Plane series—practical architectures for agent identity, authorization, governance, observability and recovery.*

*Follow Aditya Singh for production-grade enterprise AI architecture, governance and economics.*

## Feed-cover direction

A portfolio dial allocates a fixed budget across four bold blocks: `MODEL`, `CONTEXT`, `TOOLS`, `VERIFY`. A red tail-loss marker forces the allocation away from the cheapest route. No vendor names, price table or dense frontier chart on the cover.
