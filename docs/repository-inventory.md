# Repository inventory and categorization

Snapshot: 31 August 2026. This inventory covers the 456 tracked files in this repository. Generated working directories are listed separately because they are deliberately ignored by Git.

## 1. Root project and public-site metadata

| Files | Category | Suggested ownership |
| --- | --- | --- |
| `.gitignore`, `.nojekyll`, `README.md`, `requirements.txt` | Repository configuration and developer onboarding | Project maintainers |
| `index.html`, `favicon.ico`, `robots.txt`, `sitemap.xml`, `feed.json`, `feed.xml`, `rss.xml` | Public GitHub Pages entry point, discovery, and feeds | Static-site builder |

## 2. GitHub workflow definitions

All 11 files in `.github/workflows/` are automation definitions, not content or agent memory:

- `content-ci.yml`, `pages.yml`, `performance.yml`, `site-health.yml`
- `distribution-pack.yml`, `weekly-editorial.yml`, `metrics-report.yml`
- `medium-release.yml`, `medium-continuation.yml`
- `engagement-automation.yml`, `engagement-continuation.yml`

Suggested category: **repository automation**. These workflows may validate and prepare work, but must not receive browser credentials or publish social interactions.

## 3. Public static-site output

| Path pattern | Count | Category |
| --- | ---: | --- |
| `articles/<story-slug>/index.html` | 14 | Individual published-story pages |
| `series/index.html`, `series/<series-slug>/index.html` | 5 | Series navigation pages |
| `assets/styles.css`, `assets/site.js`, `assets/favicon.svg` | 3 | Shared static-site presentation assets |
| `assets/images/<story-slug>/figure-*.(png|webp|jpg)` | 224 | Story-specific figures |

The 14 article slugs are:

`a-2-4m-account-is-escalating`, `agentic-crm-reference-architecture`, `ai-agent-identity-is-not-enough`, `do-not-let-an-ai-agent-touch-production-until-it-passes-this-evaluation`, `enterprise-agent-control-tower`, `every-ai-agent-action-needs-a-receipt`, `human-approval-is-a-queueing-system`, `model-routing-is-capital-allocation`, `traditional-crm-agentic-ai`, `what-an-agent-actually-costs`, `your-ai-agent-needs-a-real-kill-switch`, `your-ai-agent-should-not-have-a-standing-role`, `your-ai-agents-memory-is-a-database-not-a-prompt`, and `your-multi-agent-system-is-a-distributed-system`.

Figure ownership is exact and complete by story folder:

| Image folder | Figures |
| --- | ---: |
| `a-2-4m-account-is-escalating` | 30 |
| `agentic-crm-reference-architecture` | 10 |
| `ai-agent-identity-is-not-enough` | 6 |
| `do-not-let-an-ai-agent-touch-production-until-it-passes-this-evaluation` | 18 |
| `enterprise-agent-control-tower` | 10 |
| `every-ai-agent-action-needs-a-receipt` | 18 |
| `human-approval-is-a-queueing-system` | 18 |
| `model-routing-is-capital-allocation` | 18 |
| `traditional-crm-agentic-ai` | 7 |
| `what-an-agent-actually-costs` | 10 |
| `your-ai-agent-needs-a-real-kill-switch` | 18 |
| `your-ai-agent-should-not-have-a-standing-role` | 25 |
| `your-ai-agents-memory-is-a-database-not-a-prompt` | 18 |
| `your-multi-agent-system-is-a-distributed-system` | 18 |

Suggested category: **deployable public artifact**. LinkedIn-agent working state must never be placed under `articles/`, `series/`, or `assets/`.

## 4. Editorial source and structured content

| Path | Count | Category |
| --- | ---: | --- |
| `stories/<story-slug>.md` | 9 | Canonical long-form story source |
| `stories/<story-slug>-figure-map.md` | 9 | Figure requirements and placement plans |
| `data/stories.json` | 1 | Story index and site manifest input |
| `data/<story-slug>.json` | 14 | Story metadata/content snapshots used by the builder |
| `editorial/seven-story-continuation.md` | 1 | Forward editorial planning |
| `editorial/phase-2/*.md` | 8 | Revision batch, distribution package, and approved phase-two copy |
| `editorial/phase-2/drafts/*.md` | 5 | Working editorial variants |

Suggested category: **editorial source of truth**. Agents may cite this material when drafting, but must not overwrite it without an explicit editorial request.

## 5. Deterministic scripts

All 30 files in `scripts/` are deterministic local tooling:

- Site lifecycle: `build_site.py`, `stage_pages.py`, `validate_site.py`, `check_lighthouse.py`
- Story and figure generation: `prepare_story.py`, `technical_figure_framework.py`, `generate_action_receipt_figures.py`, `generate_agent_evaluation_figures.py`, `generate_agent_kill_switch_figures.py`, `generate_approval_queue_figures.py`, `generate_crm_figures.py`, `generate_memory_figures.py`, `generate_model_routing_figures.py`, `generate_multi_agent_distributed_figures.py`, `generate_permission_lease_figures.py`
- Editorial and distribution preparation: `build_phase2_drafts.py`, `generate_distribution_pack.py`, `generate_weekly_editorial.py`, `prepare_medium_release.py`
- Measurement and review: `generate_metrics_report.py`, `generate_engagement_review.py`, `validate_engagement_automation.py`, `validate_agent_dry_run.py`, `validate_medium_bridge.py`
- Credential-free action evidence: `record_linkedin_execution.py`, `record_linkedin_message.py`, `record_medium_execution.py`, `render_linkedin_receipt.py`, `render_medium_receipt.py`
- Queue operations: `manage_engagement_queue.py`

Suggested category: **deterministic operator tooling**. New LinkedIn-agent helper scripts belong here only if they transform local, approved data and never access or export browser credentials.

## 6. Analytics and measurement

`analytics/` contains 17 tracked files:

- Current/operator artifacts: `engagement-dashboard.html`, `engagement-dashboard.artifact.json`, `engagement-baseline.json`, `snapshot.schema.json`
- Dated audits and execution summaries: `phase1-baseline-2026-08-27.json`, `medium-growth-audit-2026-08-28.json`, `medium-subscriber-email-state-2026-08-28.json`, `cross-platform-engagement-wave-2026-08-28.json`, `profile-conversion-execution-2026-08-28.json`, `linkedin-dm-audit-2026-08-29.json`, `linkedin-notification-audit-2026-08-29.json`, `linkedin-engagement-execution-2026-08-29-h1-h3.json`, `linkedin-engagement-execution-2026-08-29-p1-p5.json`, `linkedin-network-execution-2026-08-29-pavan-kumar-b.json`
- Periodic snapshots: `snapshots/2026-08-21.json`, `snapshots/2026-08-28.json`, `snapshots/2026-08-31.json`

Suggested category: **measurement evidence**. New two-hourly agent summaries may go under `analytics/linkedin/` only when they are aggregated, privacy-safe, and useful for trend analysis; drafts and personal context belong elsewhere.

## 7. Engagement control plane

`engagement/` contains seven policy and queue files plus the shared agent workspace:

- `strategy.json`, `queue.json`, `queue.schema.json`
- `linkedin-relationship-watchlist.json`
- `linkedin-opportunities-2026-08-27.json`, `medium-opportunities-2026-08-28.json`
- `README.md`

Suggested category: **shared engagement state**. This is the canonical location for scoring, approval state, candidate priority, duplicate prevention, and relationship timing. Future agents must read it before creating a draft and must not duplicate it in a private parallel queue.

The shared, cross-platform agent workspace is under `engagement/agents/`:

```text
engagement/agents/
  README.md          # five shared research and review roles
  policy.md          # no-new-schedule, approval, privacy, and evidence boundaries
  evaluations/       # deterministic role and guardrail dry-run matrix
```

These logical roles run only as hooks inside the existing LinkedIn and Medium schedules. They have no browser identity, independent schedule, or authority to act publicly.

## 8. LinkedIn evidence and agent workspace

| Path | Count | Category |
| --- | ---: | --- |
| `linkedin/execution.schema.json`, `linkedin/message-execution.schema.json` | 2 | Receipt contracts |
| `linkedin/executions/*.json` | 49 | Verified, approved public comment/reply receipts |
| `linkedin/message-executions/*.json` | 14 | Verified, approved DM receipts |
| `linkedin/executions/README.md`, `linkedin/message-executions/README.md` | 2 | Receipt guidance |

Suggested category: **immutable LinkedIn receipts**. Do not place agent prompts, candidate research, browser information, cookies, or drafts here.

The future non-API agent workspace belongs at `linkedin/agents/`:

```text
linkedin/agents/
  README.md          # agent roles and orchestration contract
  roles.md           # role-level input, decision, and outcome contracts
  policy.md          # approval, privacy, anti-spam, and quality limits
  prompts/           # task-specific drafting instructions
  runbooks/          # two-hourly research and morning approval process
  drafts/            # unapproved, local draft packets; gitignored
  evaluations/       # deterministic review criteria
```

## 9. Medium publishing control plane and agent workspace

| Path | Count | Category |
| --- | ---: | --- |
| `medium/README.md`, `medium/SIGNED_IN_BRIDGE.md` | 2 | Operating and signed-in bridge documentation |
| `medium/publications.json`, `medium/publications.schema.json`, `medium/release.schema.json`, `medium/execution.schema.json` | 4 | Publication registry and evidence contracts |
| `medium/releases/*.json` | 8 | Prepared release settings |
| `medium/executions/*.json` | 36 | Verified signed-in Medium actions |
| `medium/executions/README.md` | 1 | Receipt guidance |

Suggested category: **Medium control and evidence plane**. It shares the approval-gated approach with LinkedIn, but must remain independently auditable.

The non-API Medium agent workspace is under `medium/agents/`:

```text
medium/agents/
  README.md          # Medium roles and state ownership
  roles.md           # role-level input, decision, and outcome contracts
  policy.md          # AI disclosure, anti-spam, approval, and privacy limits
  prompts/           # story-research and audit/conversation instructions
  runbooks/          # 11 PM–7 AM IST overnight cycle
  evaluations/       # quality gates for briefs, audits, and response candidates
```

These agents may prepare stories and recommendations. They must not publish, schedule, send subscriber email, submit, clap, follow, highlight, or respond without exact user approval.

## 10. Generated local workspaces

The following folders exist locally but are ignored by Git and must remain regenerable:

`_site/`, `distribution-packs/`, `editorial-brief/`, `engagement-review/`, `metrics-report/`, `medium-continuation-report/`, `medium-release-bundle/`, and `medium-release-bundles/`.

Suggested category: **ephemeral generated output**. Do not treat these folders as canonical agent state.

## Guardrails for the LinkedIn and Medium agent builds

1. Keep public site, story sources, analytics, engagement state, and verified receipts separate.
2. Keep drafts local and unapproved; never commit credentials, cookies, browser state, or private message URLs.
3. Read `engagement/strategy.json` and `engagement/queue.json` before any research packet is prepared. LinkedIn also requires the relationship watchlist; Medium also requires story/release, publication, execution, and metrics evidence.
4. Put only verified user-approved actions in their platform's immutable receipt folders.
5. Use Codex recurring automation and the signed-in Chrome session; do not add an OpenAI API key or an API-backed daemon.
