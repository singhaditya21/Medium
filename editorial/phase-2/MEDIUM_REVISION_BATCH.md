# Phase 2 — executed Medium scheduled-draft revision batch

Approved, executed, and freshly verified on 2026-08-27. This batch records the exact Phase 2 content now saved in the five scheduled Medium stories.

## Mutation boundary

- Replace the existing body of each listed scheduled Medium story with the matching canonical `stories/*.md` body.
- Preserve the current title and subtitle.
- Preserve the existing schedule, topics, publication/submission state, subscriber-email setting, paywall setting, canonical URL, and featured-image setting.
- Keep the AI-writing and visualization disclosure as body paragraph two.
- Do not publish immediately, send subscriber email, add a paywall, change a publication, or post any response.
- After each save, verify word count, disclosure, figures, schedule, and scheduled status from fresh Medium state.

## Exact revisions

| Story | Exact source | SHA-256 | GitHub Pages read time | Figures | Authoritative schedule (IST) |
|---|---|---|---:|---:|---:|
| Human Approval Is a Queueing System | [`stories/human-approval-is-a-queueing-system.md`](../../stories/human-approval-is-a-queueing-system.md) | `b7660d3abfce8c209ca711083a4ffc5bec107aa83d601b75455fdb2b2f74d352` | 14 min | 11 | 2026-08-27 19:30 |
| Your Multi-Agent System Is a Distributed System | [`stories/your-multi-agent-system-is-a-distributed-system.md`](../../stories/your-multi-agent-system-is-a-distributed-system.md) | `9375f51146298d7f318f49fbe72fb7711d8cb5a8d6b80373d46ba95995fce83f` | 15 min | 11 | 2026-08-31 14:00 |
| Model Routing Is Capital Allocation | [`stories/model-routing-is-capital-allocation.md`](../../stories/model-routing-is-capital-allocation.md) | `428dce0f960bffe96abb173fdbd4a49af64cf417c531170a6aaa9adf2fe45b2b` | 12 min | 10 | 2026-09-03 14:00 |
| Your AI Agent Needs a Real Kill Switch | [`stories/your-ai-agent-needs-a-real-kill-switch.md`](../../stories/your-ai-agent-needs-a-real-kill-switch.md) | `c1d506c6c94ed83be425bbf1c9b38f60b6bc876d850544b6c21ed9632480af01` | 15 min | 10 | 2026-09-07 14:00 |
| Do Not Let an AI Agent Touch Production Until It Passes This Evaluation | [`stories/do-not-let-an-ai-agent-touch-production-until-it-passes-this-evaluation.md`](../../stories/do-not-let-an-ai-agent-touch-production-until-it-passes-this-evaluation.md) | `3b7373b663cc346aaf63d18b5ca355c04ee095b54eaaabd32f97fa139f241b2a` | 24 min | 18 | 2026-09-10 14:00 |

## Current signed-in Medium baseline

| Story | Current Medium size | Current outbox display |
|---|---:|---:|
| Human Approval Is a Queueing System | 6,214 words / 26 min | Aug 27, 2:00 PM |
| Your Multi-Agent System Is a Distributed System | 6,261 words / 26 min | Aug 31, 8:30 AM |
| Model Routing Is Capital Allocation | 6,686 words / 27 min | Sep 3, 8:30 AM |
| Your AI Agent Needs a Real Kill Switch | 6,688 words / 27 min | Sep 7, 8:30 AM |
| Do Not Let an AI Agent Touch Production Until It Passes This Evaluation | 6,609 words / 27 min | Sep 10, 8:30 AM |

Medium's outbox is displaying UTC-like clock values. The schedule-review pages and execution receipts explicitly record the authoritative GMT+5:30 times above; the revision must not change them.

## Verified Medium result

| Story | Saved Medium body | Figures / captions / native alt text | Scheduled (IST) |
|---|---:|---:|---:|
| Human Approval Is a Queueing System | 3,095 words / 13 min | 11 / 11 / 11 | 2026-08-27 19:30 |
| Your Multi-Agent System Is a Distributed System | 3,258 words / 14 min | 11 / 11 / 11 | 2026-08-31 14:00 |
| Model Routing Is Capital Allocation | 2,728 words / 12 min | 10 / 10 / 10 | 2026-09-03 14:00 |
| Your AI Agent Needs a Real Kill Switch | 3,247 words / 14 min | 10 / 10 / 10 | 2026-09-07 14:00 |
| Do Not Let an AI Agent Touch Production Until It Passes This Evaluation | 5,301 words / 22 min | 18 / 18 / 18 | 2026-09-10 14:00 |

Medium strips HTML table markup during import, so each compact decision table is represented as a Medium-native structured list with every source cell preserved. The original `figure-01` featured image remains selected for all five stories. Titles, subtitles, topics, publication state, canonical URLs, paywall settings, and subscriber-email settings were unchanged.

## Validation evidence

- `python3 scripts/build_site.py` — passed for 14 stories.
- `python3 scripts/validate_site.py` — passed for 14 stories, four series, and three feeds.
- `python3 scripts/validate_medium_bridge.py` — passed for one snapshot and 23 execution receipts, including five signed-in draft-revision receipts.
- Desktop and 375 px mobile visual checks — passed with no document-level horizontal overflow.
- All selected technical figures — local 2400×1600 PNGs with alt text and AI-assisted/synthetic captions.
