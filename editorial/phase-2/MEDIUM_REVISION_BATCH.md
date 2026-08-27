# Phase 2 — exact Medium scheduled-draft revision batch

Prepared and locally validated on 2026-08-27. This batch describes the exact content replacement that is ready for action-time approval in the signed-in Medium session.

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
| Human Approval Is a Queueing System | [`stories/human-approval-is-a-queueing-system.md`](../../stories/human-approval-is-a-queueing-system.md) | `58cd5ad41239fb9630c464006b640b45dfe9d1ee14b187e56ce675d3f97c78ee` | 14 min | 10 | 2026-08-27 19:30 |
| Your Multi-Agent System Is a Distributed System | [`stories/your-multi-agent-system-is-a-distributed-system.md`](../../stories/your-multi-agent-system-is-a-distributed-system.md) | `6ed54f7cdca06f74aa3b07a86d136ac86f2500959b984491e6835f84ea63eb66` | 15 min | 10 | 2026-08-31 14:00 |
| Model Routing Is Capital Allocation | [`stories/model-routing-is-capital-allocation.md`](../../stories/model-routing-is-capital-allocation.md) | `bc329c14212ad4bb6d6b8cd3b4a77163af651f0be8b57b7ac83a045224e1241a` | 12 min | 9 | 2026-09-03 14:00 |
| Your AI Agent Needs a Real Kill Switch | [`stories/your-ai-agent-needs-a-real-kill-switch.md`](../../stories/your-ai-agent-needs-a-real-kill-switch.md) | `68d677711ae1c4441760f51b2d66efab5ef29c4650a6d9606f7808701e47c9bd` | 15 min | 9 | 2026-09-07 14:00 |
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

## Validation evidence

- `python3 scripts/build_site.py` — passed for 14 stories.
- `python3 scripts/validate_site.py` — passed for 14 stories, four series, and three feeds.
- `python3 scripts/validate_medium_bridge.py` — passed for one snapshot and 18 execution receipts.
- Desktop and 375 px mobile visual checks — passed with no document-level horizontal overflow.
- All selected technical figures — local 2400×1600 PNGs with alt text and AI-assisted/synthetic captions.
