# AI Agents Need an Exception Budget

New technical newsletter review package, prepared 14 September 2026 for The Operating AI Ledger.

## Publication status

**LinkedIn draft deleted at the user's confirmed request on 15 September 2026.** LinkedIn displayed “Your draft was deleted.” The title was absent from Drafts immediately afterward and after revisiting the article manager. It was never published or scheduled. The complete local/GitHub manuscript, 12 figures and calculation package remain preserved in this directory.

The deletion instruction supersedes the earlier September 24 scheduling approval. **Do not recreate, publish or schedule this edition without a new explicit instruction.** All other newsletter editions and schedules remain unchanged. See `deletion-receipt-2026-09-15.json` and `progress-2026-09-15.md`.

The requested “Technical companion and editorial method” section has been removed from the manuscript, generated reading preview and native draft. All other manuscript content remains unchanged. LinkedIn's text transfer uses labeled paragraphs for the three tables; every source table cell was checked. All existing live bodies, media, mentions, settings and schedules remain unchanged. This directory is outside the public GitHub Pages staging inputs.

See `../newsletter-inventory-2026-09-15.md` for the current live-verified inventory. The September 14 inventory is historical; its Exception Budget scheduling proposal is cancelled. No private editor URL or browser state is retained.

Open `index.html` for the complete reading preview. Its architecture figures open full-size. The contact sheet is an index; inspect the full-resolution files for technical detail.

## Deliverables

- `newsletter.md`: complete original manuscript; answer-first, grouped arguments and an executive scaling decision.
- `index.html`: responsive reading edition with source citations, tables, code, all exhibits and accessible captions.
- `figures/`: **10 architecture plates + 2 statistical exhibits**, each in editable SVG and **3840 × 2720 PNG**.
- `contact-sheet.png`: overview of all 12 exhibits.
- `analytics.py`, `test_analytics.py`, `calculations.json`: reproducible calculations and 22 unit tests.
- `draw_figures.py`, `build.mjs`: deterministic figure and reading-preview build.
- `figures.json`, `manifest.json`: figure inventory, file sizes and hashes.
- `validate_package.py`, `validation.json`: structural validation and scoped review evidence.

## Exhibit inventory

| # | Architecture / statistical question |
|---|---|
| 1 | End-to-end exception-budget control plane, including feedback to admission |
| 2 | Durable action lifecycle, unknown outcomes and settlement |
| 3 | Event/action/attempt/incident data lineage and metric denominators |
| 4 | Atomic capacity reservation under concurrent execution |
| 5 | Leased authority, revocation and independent recovery identity |
| 6 | Domain transaction and lost-response sequence |
| 7 | Independent postcondition verification and protected receipts |
| 8 | Skill-aware human recovery, staffing and corrective approval |
| 9 | Capability-scoped backpressure and controlled reentry |
| 10 | Replay, failure injection, canary and release-assurance architecture |
| 11 | Recovery-demand sensitivity, Wilson uncertainty and planning cap |
| 12 | Mean and p95 queueing delays near saturation |

## Evidence classification and mathematical limits

There are **no observed customer workload data** in this package. Operating volumes, staffing, recovery effort and economics are hypothetical assumptions. Resulting numbers are calculated scenarios, not invented observations. No production savings, engagement improvement or safety rate is claimed.

The daily fluid model has constant input and service capacity, starts with zero backlog in the displayed scenario and ignores within-day randomness. Wilson intervals assume a fixed, fully observed cohort of independent comparable Bernoulli trials. The interval is about exception probability, not daily overload probability or a guarantee of safe actions. The chosen 75% capacity allocation is illustrative, not a benchmark. The displayed planning caps round down to whole actions.

The queue plot is an ideal stationary M/M/4 model: Poisson arrivals, independent exponential service, FIFO, unlimited waiting room, no abandonment and continuously available servers. It excludes shifts, holidays, priority, heterogeneous skills and correlated incidents. Its p95 is a **model-derived service-clock waiting percentile**, not measured calendar-time latency. No finite stationary answer is given at utilization ≥ 1.

The financial example estimates released labor capacity only, using a hypothetical comparable baseline. It is not a cash-savings calculation and excludes several cost categories. The article describes those exclusions.

## Architecture limits

The diagrams are original reference designs, not vendor-certified deployment architectures. They distinguish permission, capacity, local atomic mutation, downstream effects and independent verification. Authority breaches bypass budget tolerance. Unknown outcomes remain owned and encumbered. Compensation requires separate current authority.

The SQL is explicitly transactional pseudocode. The JSON is an illustrative receipt schema with nonfunctional example values. No production service is implemented by this package. The 22 tests concern arithmetic and mathematical boundary cases only; they do not validate the architecture in production or replace integration/security testing.

## Sources and their roles

- [NIST proportion intervals](https://www.itl.nist.gov/div898/handbook/prc/section2/prc241.htm): Wilson calculation method.
- [Gunther, Erlang Redux](https://arxiv.org/html/2008.06823v1): multi-server Erlang-C queue relationship. This package's numerical values are independently calculated from its own assumptions.
- [Google SRE error-budget policy](https://sre.google/workbook/error-budget-policy/): related reliability governance mechanism; article distinguishes it from human recovery capacity.
- [AWS safe retries](https://aws.amazon.com/builders-library/making-retries-safe-with-idempotent-APIs/): caller intent, ambiguous outcomes and supported idempotency contracts.
- [AWS transactional outbox](https://docs.aws.amazon.com/prescriptive-guidance/latest/cloud-design-patterns/transactional-outbox.html): local dual-write solution and duplicate-delivery caveat.
- [PostgreSQL transaction isolation](https://www.postgresql.org/docs/18/transaction-iso.html): transaction and concurrency semantics; SQL remains pseudocode.
- [RFC 9449](https://www.rfc-editor.org/rfc/rfc9449.html#section-11): sender-constrained token security considerations, not business approval.
- [CloudEvents v1.0.2](https://github.com/cloudevents/spec/blob/v1.0.2/cloudevents/spec.md): source/event identity, distinct from action identity.
- [McKinsey interview with Barbara Minto](https://www.mckinsey.com/alumni/news-and-events/global-news/alumni-news/barbara-minto-mece-i-invented-it-so-i-get-to-say-how-to-pronounce-it): answer-first editorial structure. No McKinsey authorship or endorsement is implied.

## Rebuild

Run from this directory:

```bash
python3 analytics.py
python3 -m unittest -v test_analytics.py
python3 draw_figures.py
node build.mjs
python3 validate_package.py
```

`build.mjs` uses the installed desktop runtime's `marked` and `sharp` packages. `CODEX_NODE_MODULES` can point to another existing module directory. No API key, model API, browser export, detector service or external posting tool is used.

## Review approach

The visualization skill guided numeric labeling, uncertainty and model-scope checks. The LinkedIn editorial skills guided clarity and unsupported-claim review, subject to the repository's integration contract. Their upstream detector-evasion and invented-experience suggestions were not used. No personal experience or customer result was invented.

The review includes inspection of rendered full-size figures and the contact sheet, correction of arrow/label overlaps, validation of asset references/dimensions and a browser preview check. See `validation.json` for completed checks and their limits.
