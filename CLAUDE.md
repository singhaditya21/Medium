# CLAUDE.md

Guidance for Claude Code when working in this repository.

## What this is

A static publishing and distribution system for Aditya Singh's enterprise-AI essays
(agent architecture, identity, governance, economics, CRM). It builds a GitHub Pages
site from captured story data and runs a human-approved Medium + LinkedIn engagement
loop. It is a content pipeline, not an application.

- Live site: <https://singhaditya21.github.io/Medium/>
- Canonical publication: <https://medium.com/@singhaditya21_89007>

## The one rule that governs everything

**Automation prepares. The user acts. Receipts record.**

Claude and GitHub Actions may research, rank, draft, validate, package, and report.
Neither may perform a public account action. Never post, comment, reply, message,
react, like, follow, connect, repost, publish, schedule, or submit to a publication.
Never sign in, export cookies, replay a session, or scrape a signed-in page.

Every public interaction is performed by the user in their own signed-in browser after
approving the exact target and the exact text, and is then recorded as a
credential-free receipt that a continuation workflow validates.

`ready_for_confirmation` is a queue state, not permission to post. Approval of one item
never approves another.

## Build and validate

```bash
python3 -m venv .venv && source .venv/bin/activate && pip install -r requirements.txt
python scripts/build_site.py      # regenerate articles, index, series, feeds, sitemap, robots
python scripts/validate_site.py   # story metadata + local link checks
python scripts/stage_pages.py     # clean _site/ containing public files only
python3 -m http.server 8000       # preview at http://localhost:8000
```

Run all three after any content change. `content-ci.yml` runs the same sequence.

## Source of truth

| Path | Role |
| --- | --- |
| `data/*.json` | **Source of truth** for stories (26 + `stories.json`) |
| `articles/`, `index.html`, `feed.*`, `rss.xml`, `sitemap.xml` | Generated and committed — edit `data/` and rebuild, never by hand |
| `_site/` | Staged deploy output — gitignored, never edit or commit |
| `assets/images/` | Locally archived figures; the builder downloads missing ones |
| `scripts/` | Builder, validators, figure generators, queue and receipt CLIs |
| `engagement/queue.json` | Combined Medium + LinkedIn candidate queue |
| `linkedin/executions/`, `linkedin/*-executions/` | Verified receipts (append-only audit trail) |
| `analytics/engagement-dashboard.artifact.json` | Canonical all-story scorecard |

`analytics/engagement-dashboard.html` is a historical August snapshot only. Do not cite
it as current evidence.

Generated working directories are gitignored: `distribution-packs/`, `editorial-brief/`,
`metrics-report/`, `medium-release-bundle*/`, `medium-continuation-report/`,
`engagement-review/`, `engagement-continuation-report/`, `lighthouse-reports/`.

## Engagement loop

```text
discovered -> proposed -> ready_for_confirmation
                              |
                              +-> exact user confirmation in signed-in browser
                              |      -> posted -> visible verification -> receipt
                              +-> skipped
```

Scoring, with a 0.70 minimum to reach `ready_for_confirmation`:

```text
S = 0.35(relevance) + 0.25(discussion quality)
  + 0.20(unique contribution) + 0.20(recency)
```

Limits, all enforced by `engagement/queue.schema.json` and
`scripts/validate_engagement_automation.py`:

- At most **5 active candidates per platform** per batch. `posted` and `skipped` entries
  stay as audit trail and do not consume the limit.
- At most **1 relevant mention** per candidate. Never tag for reach.
- Research ceiling per cycle: 5 source-specific posts or profiles. Rolling 24 hours:
  50 comment opportunities, 50 DM prospects — a research target, never a sending target.
- Read `engagement/linkedin-relationship-watchlist.json` before drafting a follow-up.
  Do not duplicate a thread or nudge one awaiting an inbound reply.

Larger researched campaigns live in dated opportunity backlogs
(`engagement/*-opportunities-YYYY-MM-DD.json`). Promote one wave of five at a time and
revalidate source and exact target before promotion.

**Idle-first gate.** Deeper research requires a trigger: a new substantive inbound item,
a due measurement checkpoint, an explicit user research request, or an approved action
awaiting verification. With no trigger, or a full queue, return a quiet status naming the
next checkpoint. Never manufacture a batch.

### Quality bar for drafts

A comment adds an operational implication, metric, implementation trade-off, or
constructive challenge — it never restates the source. A DM gives the genuine reason for
outreach, with no template, pitch, or unexplained link. Every proposal names the exact
target, exact text, intended mentions, evidence, and why now.

### Queue and receipt commands

```bash
python scripts/manage_engagement_queue.py add \
  --platform linkedin --action comment --direction outbound \
  --target-url PUBLIC_POST_URL --title "TITLE" --author "AUTHOR" \
  --reason "WHY_THIS_CONVERSATION_MATTERS" --evidence "SOURCE_SPECIFIC_DETAIL" \
  --draft-response "EXACT_PROPOSED_TEXT" --priority-score 0.82

python scripts/manage_engagement_queue.py ready --candidate-id CANDIDATE_ID
python scripts/manage_engagement_queue.py skip  --candidate-id CANDIDATE_ID
python scripts/manage_engagement_queue.py list

# only after the user posted it and the public result is visible
python scripts/record_linkedin_execution.py reply-posted \
  --candidate-id CANDIDATE_ID --target-url PUBLIC_POST_URL \
  --public-url PUBLIC_RESULT_URL --issue-number ISSUE_NUMBER \
  --confirmation-scope "EXACT_SCOPE_THE_USER_APPROVED" \
  --verification "WHAT_WAS_VISIBLY_CONFIRMED"
```

Receipt actions: `comment-posted`, `reply-posted`, `author-comment-posted`.
Medium equivalents are `scripts/record_medium_execution.py` and
`scripts/prepare_medium_release.py`.

Candidate ids follow `YYYY-MM-DD-<platform>-<action>-<person>-<topic-slug>`.

## Receipts

A receipt is written only after the public result is visibly verified. It records the
operation id, action, confirmation scope and time, target and public URLs,
`publishedTextSha256`, verification sentence, `secretsStored: false`, and
`githubActionsPerformedLinkedInAction: false`.

Never put private conversation text, private LinkedIn URLs, browser state, cookies, or
credentials in Git. Only the allowed receipt fields.

## Medium releases

`medium/` holds the approval-gated bridge. GitHub prepares the exact import bundle and
validates against the reviewed publication registry, rejecting duplicates. The signed-in
Medium UI performs the private draft import after a direct request. Final Publish or
Schedule always requires confirmation of topics, publication, subscriber email, paywall,
canonical URL, and timing. See `medium/SIGNED_IN_BRIDGE.md`.

## Workflows

`content-ci.yml` (build/validate/stage/packs) · `pages.yml` (deploy `_site/` on push to
`main`) · `site-health.yml` (Wednesdays) · `performance.yml` (Lighthouse, post-deploy and
Fridays) · `distribution-pack.yml` · `weekly-editorial.yml` (one Monday issue) ·
`metrics-report.yml` (monthly) · `medium-release.yml` · `medium-continuation.yml` ·
`engagement-automation.yml` (twice each weekday, refreshes one weekly control issue) ·
`engagement-continuation.yml`.

Workflows update a single control issue rather than creating notification spam. Pin
action dependencies to full commit SHAs.

## Conventions

- Commit subjects are short, imperative, and name the artifact:
  `Prepare LinkedIn notification replies for Sep 5`, `Record verified LinkedIn growth cycle`.
- Prepare and record are **separate commits**. Never record an action that has not happened.
- Timestamps are UTC ISO-8601 (`2026-09-05T08:01:44Z`); operation ids are `YYYYMMDDHHMMSS`.
- Analytics stay off unless both `SITE_ANALYTICS_SCRIPT_URL` and
  `SITE_ANALYTICS_WEBSITE_ID` repository variables are set. Never store Medium or
  LinkedIn cookies or credentials in them.
- Article text and original diagrams are © Aditya Singh; keep canonical Medium links on
  every article page.
