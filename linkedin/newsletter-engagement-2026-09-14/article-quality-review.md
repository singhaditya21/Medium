# Article-quality review — 14 September 2026

Status: recommendations only. No article body, title, cover or existing edition schedule was changed. This is a focused review of four editions, not a catalog-wide certification.

## Priority and scope

| Priority | Article | Specific improvement | Reader deliverable |
| --- | --- | --- | --- |
| 1 | Every AI Agent Needs a Passport | Qualify the claim that a last-moment permission recheck closes the check/use race | An enforcement-boundary diagram and a concurrent revocation test |
| 1 | How to Build an Agentic CRM: A Reference Architecture | Make the existing idempotency-key design's actual retry contract explicit | A lost-response execution trace and a runnable acceptance test |
| 2 | 99.5% Accurate—and Still Wrong 500 Times | Define conditional denominators and sensitivity, not just point estimates | A small risk table and an adjudicated sampling plan |
| 2 | The 3-Minute Decision That Took 3 Weeks to Ship | Separate modeled handling workload, elapsed waiting and realized business value | A controlled fast-lane decision memo |

## 1. Passport: define what the gateway can actually guarantee

[Reviewed edition](https://www.linkedin.com/pulse/every-ai-agent-needs-passport-aditya-singh-qrvrc/)

The current flow says a policy/revocation recheck immediately before mutation closes the time-of-check/time-of-use gap. A separate read immediately before a write can still race. The revision should state which conditions the resource server enforces atomically with the mutation and which depend on a separately managed freshness bound.

Proposed additions:

- Distinguish identity, permission, business approval and effect uniqueness. A signed assertion does not itself enforce any of the latter three.
- Specify the transaction/version predicate at the system that owns the business record. Do not suggest that putting two calls in a gateway creates atomicity across services.
- State what happens if policy/revocation freshness cannot be established; describe a bounded-staleness contract explicitly when instantaneous revocation cannot be guaranteed.
- Test concurrent revocation, expired authority, a wrong-tenant request and two workers attempting to consume the same approval.
- Distinguish replay protection for a DPoP proof from one-use authorization of a business action. A short lifetime is not a durable consumption record.

These are engineering recommendations, not claims that one RFC mandates this architecture. PostgreSQL illustrates why separate reads can observe changing state and how a conditional update can re-evaluate its predicate; that does not solve external-service atomicity. [PostgreSQL transaction isolation](https://www.postgresql.org/docs/current/transaction-iso.html). DPoP's own replay discussion describes stateful proof-identifier checks and distributed-state limits. [RFC 9449 §11.1](https://www.rfc-editor.org/rfc/rfc9449.html#section-11.1).

## 2. Agentic CRM: turn architecture components into an executable contract

The local source is `data/agentic-crm-reference-architecture.json`, corresponding to the published Ledger edition. It already includes idempotency keys, a gateway, an outbox and postcondition verification; the proposed improvement is precision and demonstration, not claiming those controls are absent.

Its timeout passages currently prescribe bounded retries. A bound limits attempts but does not by itself establish that a write is safe to repeat. A timeout may mean the write committed and its response was lost. [AWS Builders' Library: safe retries](https://aws.amazon.com/builders-library/making-retries-safe-with-idempotent-APIs/).

Proposed additions:

1. Carry the existing 4:47 p.m. escalation through a single numbered trace: duplicate event, first committed write, lost response, second worker, outcome lookup, changed record version, final receipt.
2. Define the idempotency scope: principal, tenant, operation and business intent; durable retention; same-key/different-payload rejection; and how the recorded result is recovered. Identical request parameters do not always imply the same intent.
3. Show the enforcement and business-effect atomic boundary. If the downstream domain lacks the needed contract, route unknown outcomes to reconciliation or human resolution instead of implying an automatic retry is safe.
4. Distinguish compensable partial failure from irreversible external harm. Compensation is a new business action, not guaranteed restoration of history.
5. Add a small reproducible harness with a command, expected outputs and negative tests. Label it a reference implementation with explicit exclusions, not a certified production system.

Retain the useful existing ten figures. Redesign only figures that cannot answer a specific question; show data flow separately from control decisions, the mutation boundary and the unknown-outcome branch.

## 3. Accuracy: make the assumptions inspectable

[Reviewed edition](https://www.linkedin.com/pulse/995-accurateand-still-wrong-500-times-aditya-singh-get5c/)

The illustrative calculation `100,000 × 0.005 × 0.05 × 0.20 = 5` is arithmetically sound. Define it as attempts × error probability × high-impact share **among errors** × miss probability **within the reviewed high-impact-error set**. The conditional populations matter; unrelated dashboard percentages cannot simply be multiplied.

With 25 expected high-impact errors in that modeled workload:

| Assumed review recall on that subset | Expected escapes |
| --- | ---: |
| 50% | 12.5 |
| 80% | 5 |
| 95% | 1.25 |

These are scenario expectations, not observed incident counts or statistical confidence intervals. The improved edition should expose input sources, uncertainty and an adjudicated sample design covering both reviewed and unreviewed actions. Avoid presenting sampled accuracy as the entire deployment's known error rate. Include severity and recovery cost without converting all outcomes into one unsupported average loss.

## 4. Three-minute decision: connect the arithmetic to a management choice

[Reviewed edition](https://www.linkedin.com/pulse/3-minute-decision-took-3-weeks-ship-aditya-singh-kmejc/)

The assumed 400 records/day, 4% misrouting and 20 minutes/repair imply 5.33 handling hours/day, 26.7 hours across five working days and 80 hours across fifteen. They do not prove those hours become cash savings, nor that the delay itself caused every misrouting.

Improve the decision memo by separating queue waiting, exception handling, released staff capacity, avoided expenditure and revenue/customer effects. Give a controlled fast lane for a reversible rule with a named owner, approved version, staged test and recovery route. Track waiting alongside bad changes and recovery time. Include the counterexample: a faster deployment of a bad rule can increase damage.

Sensitivity at 2%, 4% and 6% misrouting is 40, 80 and 120 modeled handling hours over fifteen working days. Label it sensitivity, not a forecast. End with a one-page policy-change acceptance checklist that a manager can actually use.

## Shared editorial acceptance gates

- One distinct reader decision and one new worked example per article. Link earlier deep dives instead of repeating the same identity/approval/receipt sections.
- Separate observed results, sourced facts, assumptions, forecasts and author proposals. Every important number needs its denominator and time window.
- Two reading layers: an accessible opening and decision summary, followed by technical detail. Ledger should supply an implementable contract; RRR should explain ownership and the operating trade-off.
- Code must either run with documented prerequisites/tests or be clearly labeled pseudocode. Include the failure path, not only the happy path.
- Use consistent white backgrounds and black/blue diagram text in future approved redesigns. Test mobile legibility; add animation only when a changing state is the subject. Figure count is not a quality target.
- Stop publication for a false central claim, failed runnable example, misleading diagram or substantive duplicate. Do not manufacture experience or metrics to pass a stylistic check.

Recommended next revision batch: Passport and Agentic CRM correctness first, then the accuracy and waiting-cost decision aids. Prepare exact revised bodies and affected figures for approval before replacing any published edition.

## Measurement limits

Existing views, email opens and comments do not establish reading completion. The new Ledger article's early audience is too small for a causal retention diagnosis. Evaluate technical correctness independently of popularity, then compare like-aged seven-day and 28-day engagement windows after approved revisions. Do not attribute all subsequent growth to a comment, new post or rewrite.

## Follow-up: revised drafts completed

After the user approved preparing the changes, the [four-article review package](../article-quality-revisions-2026-09-14/index.html) was completed with exact revised bodies, three corrected diagrams and a reproducible local companion. Sixteen protocol tests and eight arithmetic tests pass, as do the two runnable article examples and package checks. The accuracy revision clarifies that the five-escape example requires 80% **end-to-end timely interception among all high-impact errors**, not recall only within the reviewed subset. See the [change log](../article-quality-revisions-2026-09-14/README.md) and [validation record](../article-quality-revisions-2026-09-14/validation.json).

These remain **review drafts**. No published LinkedIn or Medium article, original GitHub Pages body, cover, title, URL, schedule or publishing setting was changed by this follow-up. Exact live replacement remains a separate approval step.
