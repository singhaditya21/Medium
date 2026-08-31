# Medium agent workspace

This folder defines the non-API, approval-gated Medium research system. It uses Codex heartbeat runs and the user's signed-in Chrome session only when a read-only audit or user-approved action requires the Medium UI. It is not a publishing bot, engagement bot, or autonomous author.

## Agent roles

1. **Catalog and gap analysis** maps the published catalog, audience promise, and content-pillar gaps.
2. **Scheduled-story and release audit** inspects every scheduled story and its release settings before it publishes.
3. **Source and story opportunity research** identifies differentiated technical story opportunities and primary evidence.
4. **Story architecture and visual planning** prepares the thesis, reader, outline, artifacts, figures, code, and series placement.
5. **Editorial, claims, and policy review** tests factual support, clarity, originality, image attribution, AI disclosure, and paywall/distribution eligibility.
6. **Performance and retention audit** diagnoses presentations, views, reads, read ratio, traffic, and audience conversion at 48-hour, 7-day, and 28-day checkpoints.
7. **Read-through engineering** evaluates the first screen, opening payoff, heading rhythm, figure placement, and internal navigation when evidence supports a retention intervention.
8. **Distribution and publication fit** checks story settings, preview rendering, topics, canonical links, subscriber-email intent, internal navigation, and selective publication fit.
9. **Conversation research and response drafting** identifies a small number of source-specific stories where an original technical response would add value.
10. **Growth experiment planning** proposes measured, reversible improvements to discovery, clickthrough, retention, and reader relationship.
11. **Approval, receipts, and reporting** presents exact choices in chat, enforces confirmation, verifies approved actions, and records credential-free evidence.

The roles are logical stages in the overnight Medium runs. They are not independent accounts, browser sessions, or permission to take public actions. See [`roles.md`](roles.md) for the input, decision, and outcome contract for every role.

## Overnight cadence

The Medium lane runs only at **11 PM, 1 AM, 3 AM, 5 AM, and 7 AM IST**. It shares the scheduler with LinkedIn, but its inputs, analysis, outputs, and approval requirements remain separate.

Each completed run reports in chat. When recommendations are ready, the report includes evidence, score, exact target, exact proposed text or settings, expected effect, and the exact approval needed. An empty or low-quality batch is reported as such; quantity never overrides judgment.

Every run also reports every scheduled story: title, scheduled date/time in IST, remaining time, publication destination, public/unlisted state, topics, canonical URL, featured-image/preview check, subscriber-email setting, paywall setting, and any release-risk alert. It may inspect these settings but never changes them without approval.

## State ownership

- `engagement/strategy.json` defines policy, scoring, schedule, limits, and approval boundaries.
- `engagement/queue.json` remains the canonical response-candidate queue and duplicate-prevention source.
- `stories/` and `data/stories.json` are the editorial catalog; research may cite them but must not overwrite them without a separate editorial request.
- `medium/releases/`, `medium/executions/`, and `medium/publications.json` are the release, verified-action, and publication records.
- `analytics/` contains accountable metrics and historical audit evidence.
- Unapproved full drafts and response wording are presented in chat, not retained in Git, unless the user explicitly asks to save an editorial draft.

Read [policy.md](policy.md) before every run and follow [runbooks/overnight-cycle.md](runbooks/overnight-cycle.md).
