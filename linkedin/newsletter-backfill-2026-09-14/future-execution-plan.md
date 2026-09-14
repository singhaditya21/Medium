# Future plan — preparation completed, publication approval pending

14 September 2026. No platform publication, scheduling or engagement action was executed in this continuation. Existing schedules and automations are unchanged.

## Next release batch

N05, N06 and N07 now have complete source-reconciled local previews, exact launch introductions, existing covers and inline figures, explicit engineering notes, and an [approval packet](approval-N05-N07.md). Proposed Mondays at 14:00 IST: October 12, 19 and 26. These are separate full articles attached to **The Operating AI Ledger**, not three new newsletters or standalone feed posts.

The combined batch preserves 66 figures and 24 code/protocol/formula blocks. Live source text is compared with the local body after documented typography normalization. JSON and Python snippets receive syntax checks, not production certification. Medium's split code fragments are rejoined. Disclosures, source references and related-story navigation remain. Native LinkedIn image, code and setting validation still happens after exact approval and before scheduling.

## Calendar findings — do not silently move anything

The live composer badge shows 14 scheduled objects. Paging to the end exposes 11 ordinary feed posts, September 16–October 9; the article manager independently shows 3 scheduled newsletter editions. They must not be reported as 14 newsletter editions.

| ID | Exact target opening | Current time, IST | Proposed timing-only change, IST |
| --- | --- | --- | --- |
| T1 | A 97% approval rate can coexist with a broken approval system. | September 21, 2026, 14:00 | September 22, 2026, 08:45 |
| T2 | A memory system can achieve 104 ms p95 retrieval and still be unsafe. | October 5, 2026, 14:00 | October 6, 2026, 08:45 |

T1 collides exactly with N02 and T2 with N04. Proposed moves affect only those ordinary feed posts' time; preserve their complete text, mentions, links, video, audience and comments. The newsletter dates stay fixed. These moves require separate exact approval and a final native recheck. The proposed Tuesday slots have no collision in the observed inventory; this is not an optimal-time or reach claim. N03 has a feed post earlier that day at 08:45, not an exact collision. N05–N07 have no observed collision, but the inventory must be refreshed at execution.

## Standing Role and the remaining backfills

Medium still shows Standing Role scheduled in the current audit. N14 remains held until its public release is visible. Do not create a duplicate Medium draft or infer publication from the date alone. N08–N13 remain in the existing backfill queue and need the same source/duplicate/technical gates. N09 needs a full comparison against The Coordination Tax before approval.

## Twenty-story pipeline — one weekly edition, no second lane

The existing [20-story package](../../editorial/wave-20-2026-09-12/preview.html) passes its structural validator: 20 story drafts, 20 launch-post drafts, 44 existing figures, 8 new SVG/PNG pairs, 67 local links and 2 syntax-checked code blocks in the eight new drafts. That is **not** a claim that all 20 received deep technical or native-platform review in this turn.

The previous Thursday/Friday calendar was an unexecuted two-editions-per-week proposal. It is held, not the active plan. Maintain one weekly newsletter edition. Finish the next three backfills, then review evidence before choosing whether to interleave new pieces with remaining backfills. Show the revised exact calendar before scheduling; do not reserve a second weekly lane or automatically displace an approved edition.

| Priority | IDs | Focus | Required next output |
| --- | --- | --- | --- |
| 1 | M01–M05 | Transaction boundary, ambiguous success, retry decisions, independent verifier, compiled policy | Distinct failure traces, concrete contracts, concurrency/negative tests and exact review editions |
| 2 | M06–M10 | Observability, safe degradation, fencing, incident owner, change budget | Owned state transitions, failure recovery and denominator-based operating measures |
| 3 | M11–M15 | Context/data boundary, RevOps ledger, tool versioning, shadow data, authorization-aware cache | Data-purpose and isolation model, invalidation tests and bounded source claims |
| 4 | M16–M20 | Fair queues, merge undo graph, irreversible email, contact-policy ledger, incremental value | Counterexamples, measurable assumptions, irreversible-action limits and measurement design |

M01–M12 already have GitHub Pages sources. “LinkedIn first” means before Medium, not first public appearance anywhere. M13–M20 are local drafts. Their GitHub Pages and final media need their own preparation and verification; do not claim those pages exist yet.

## First two technical briefs

### M01 — Your AI Agent Needs a Transaction Boundary

Source read in full: [existing article JSON](../../data/your-ai-agent-needs-a-transaction-boundary.json).

Distinct promise: move from N07's evidence envelope to the concrete last-write protocol. Show two concurrent workers, one stable intent, a unique tenant/action reservation, version-precondition failure and a response lost after commit. A transaction capability is not a substitute for an atomic domain idempotency primitive.

Required additions before an exact publication request:

- A step-by-step two-worker race trace with exactly one committed mutation and a stored prior result.
- A minimal runnable harness with fake domain storage: same key/same intent, same key/different intent, concurrent first claim, stale version, lost response after commit, and crash before receipt closure.
- Explicit separation of stable business intent from a renewed credential. A renewed lease must be a linked authorization attempt, not an accidental new business action or digest conflict.
- Failure-specific commentary replacing repeated cross-catalog boilerplate. Keep the existing figures unless a separately shown redesign is approved.
- Use duplicate effects per attempted business action, unresolved exposure by age, and p99 reconciliation time. Label every modeled number as synthetic; no guaranteed exactly-once network claim.

### M02 — The Hardest Agent Failure Is an Ambiguous Success

Source read in full: [existing article JSON](../../data/the-hardest-agent-failure-is-an-ambiguous-success.json).

Distinct promise: define how a multi-system outcome is resolved, rather than retell the single API timeout story. Use CRM version, billing-ledger count and approved-message evidence with separate lag budgets and authoritative owners.

Required additions before an exact publication request:

- A worked trace distinguishing accepted, committed, propagated, partial, duplicate, delayed and unknown states; include a stale negative read that must not authorize retry.
- A versioned assertion contract with owner, source, maximum evidence age, consistency requirement, expected value and deadline for each assertion.
- Repair the current VOI sketch's units: entropy reduction cannot be subtracted directly from currency costs. Express all terms in expected monetary decision loss, or supply and justify an explicit conversion. Mandatory authoritative assertions remain hard gates.
- Test false closure, replica lag, contradictory sources, eventual settlement after deadline and compensation failure. Report false-closure count and reopen rate separately from speed.
- Shorten shared generic review/checklist material and spend that space on the outcome-resolution example and its limits.

These are concrete editorial specifications, not claims that new harnesses or revised stories have already been built.

## Cross-platform release and measurement

For a future new piece: approve exact LinkedIn edition → visibly verify public release and series identity → prepare Medium mirror with its real source link → approve exact Medium body/settings/time → verify publication. Keep subscriber email enabled where the native Medium control permits, but never promise inbox delivery. Preserve existing Medium/GitHub canonical values; do not silently claim LinkedIn as original for previously public GitHub work.

Use the [checkpoint plan](newsletter-checkpoints.json) for 48-hour, 7-day and 28-day review. N01's recording time is an observation proxy, not an exact publication timestamp; N02–N04 checkpoints are provisional until release is observed. Keep series subscribers, edition views/reading metrics, announcement impressions/interactions and Medium presentations/views/reads separate. Unknown values remain null. This file is a review plan, **not a registered scheduler**; no new automation has been created or existing research cadence changed.

At review, capture the actual collection timestamp and label late cumulative snapshots honestly. Compare like-aged editions. Choose changes based on the observed bottleneck; do not rewrite on a tiny sample or sum article views and feed impressions as unique readers.

The [both-newsletter engagement activation](../newsletter-engagement-2026-09-14/plan.md) adds a same-day native readership baseline and a separate exact-approval batch for reader discussion, an RRR resurfacing post and proposed RRR metadata. It does not approve N05–N07, move T1/T2, create an additional weekly edition lane or change any automation.

## Targeted technical sources checked in this continuation

- [PostgreSQL row-level locks](https://www.postgresql.org/docs/current/explicit-locking.html#LOCKING-ROWS): locks apply to retrieved rows; the missing-key reservation gap is a design inference from that behavior.
- [PostgreSQL INSERT / ON CONFLICT](https://www.postgresql.org/docs/current/sql-insert.html): database support for atomic conflict handling; the application's effect protocol still needs explicit implementation.
- [RFC 9449, DPoP](https://www.rfc-editor.org/rfc/rfc9449.html): token presentation includes a separate DPoP proof; a short TTL is not one-use enforcement.
- [RFC 8785, JCS](https://www.rfc-editor.org/rfc/rfc8785.html): deterministic canonicalization does not prove the underlying business fact.

This was targeted source checking, complete N05–N07 body reconciliation, two related-article body comparisons and package structural QA—not a complete rerun of every simulation, standards citation or production control.
