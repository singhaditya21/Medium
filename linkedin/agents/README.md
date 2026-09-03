# LinkedIn agent workspace

This folder defines a non-API, approval-gated LinkedIn operating system. It runs through the existing Codex heartbeat and the user's signed-in Chrome session; it is not an autonomous browser bot and does not store any session data.

## Agent roles

1. **Signal triage** reads notifications and identifies meaningful inbound activity.
2. **Relationship context** checks the watchlist, prior receipts, and unanswered threads.
3. **Relationship allocator** ranks follow-ups by relationship stage, reciprocity, relevance, and a contact-frequency cap.
4. **Network adjacency mapper** finds credible bridges among RevOps, enterprise-AI, CRM, governance, and adjacent practitioner communities.
5. **Opportunity research** finds source-specific post and profile opportunities.
6. **Conversation-quality verifier** rejects generic, duplicative, weakly evidenced, or engagement-bait comments before they reach an approval brief.
7. **Comment and reply drafting** prepares compact, evidence-based responses.
8. **DM drafting** prepares individual messages only when there is a real relationship reason.
9. **Post-format strategist** selects the most suitable native format, hook structure, visual need, and timing hypothesis for a post idea.
10. **Post drafting** prepares original LinkedIn-native posts from the editorial catalog and performance context.
11. **Reputation-risk editor** checks claims, tags, tone, confidentiality, and avoidable controversy before an action is presented.
12. **Performance analysis** interprets post, profile, and series metrics.
13. **Approval and receipts** presents exact actions, enforces confirmation, verifies execution, and records credential-free evidence.

The roles are logical stages within the five scheduled LinkedIn Codex runs. They are not thirteen independent accounts, browser sessions, or autonomous actors. See [`roles.md`](roles.md) for the input, decision, and outcome contract for every role.

## Schedule

LinkedIn runs only at **10 PM, 12 AM, 2 AM, 4 AM, and 6 AM IST**. Shared cross-platform roles run within the appropriate LinkedIn cycle; they never add a schedule or take public actions.

## State ownership

- `engagement/strategy.json` is the operating policy and cadence contract.
- `engagement/queue.json` is the only persistent comment/reply approval queue.
- `engagement/linkedin-relationship-watchlist.json` is the relationship timing source of truth.
- `linkedin/executions/`, `linkedin/message-executions/`, and `linkedin/schedule-executions/` are immutable execution evidence.
- Unapproved DM text and post drafts are presented in the approval brief. They are not committed unless the user explicitly asks to retain a draft.

Read [`policy.md`](policy.md) before every cycle and follow [`runbooks/two-hourly-cycle.md`](runbooks/two-hourly-cycle.md).
