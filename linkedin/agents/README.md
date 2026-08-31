# LinkedIn agent workspace

This folder defines a non-API, approval-gated LinkedIn operating system. It runs through the existing Codex heartbeat and the user's signed-in Chrome session; it is not an autonomous browser bot and does not store any session data.

## Agent roles

1. **Signal triage** reads notifications and identifies meaningful inbound activity.
2. **Relationship context** checks the watchlist, prior receipts, and unanswered threads.
3. **Opportunity research** finds source-specific post and profile opportunities.
4. **Comment and reply drafting** prepares compact, evidence-based responses.
5. **DM drafting** prepares individual messages only when there is a real relationship reason.
6. **Post drafting** prepares original LinkedIn-native posts from the editorial catalog and performance context.
7. **Performance analysis** interprets post, profile, and series metrics.
8. **Approval and receipts** presents exact actions, enforces confirmation, verifies execution, and records credential-free evidence.

The roles are logical stages within one two-hourly Codex run. They are not eight independent accounts, browser sessions, or autonomous actors.

## State ownership

- `engagement/strategy.json` is the operating policy and cadence contract.
- `engagement/queue.json` is the only persistent comment/reply approval queue.
- `engagement/linkedin-relationship-watchlist.json` is the relationship timing source of truth.
- `linkedin/executions/` and `linkedin/message-executions/` are immutable execution evidence.
- Unapproved DM text and post drafts are presented in the approval brief. They are not committed unless the user explicitly asks to retain a draft.

Read [`policy.md`](policy.md) before every cycle and follow [`runbooks/two-hourly-cycle.md`](runbooks/two-hourly-cycle.md).
