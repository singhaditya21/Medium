# Two-hourly LinkedIn research cycle

## Purpose

Keep a high-quality approval queue ready without continuously polling LinkedIn or creating public activity without the user's permission.

## Cycle sequence

1. Pull and validate the repository.
2. Read `linkedin/agents/policy.md`, `engagement/strategy.json`, the current queue, the relationship watchlist, and the latest receipt history.
3. Review current LinkedIn notifications, comments, replies, and DMs. Separate inbound conversations from passive reactions, generic job alerts, and noise.
4. Inspect up to five relevant source-specific posts or profiles. Check prior interaction before creating any candidate.
5. Score valid candidates with the repository's relevance, discussion-quality, unique-contribution, and recency formula.
6. Draft up to one original post concept, five comments/replies, and five DMs. Retain DM and post wording only in the approval brief unless separately requested for editorial review.
7. Add only compliant comment/reply candidates to `engagement/queue.json` through `scripts/manage_engagement_queue.py`. Do not add low-score, duplicated, or stale candidates.
8. Produce a concise approval packet when there are qualifying actions: target, evidence, exact text, intended tag, score, and relationship context.
9. If there is no material action, retain only validated preparation changes, commit and push them, and return a quiet status.

## Review cadence

- The scheduler invokes this cycle every two hours.
- A rolling day may contain up to 50 researched comment opportunities and 50 DM prospects; each cycle remains narrow to protect relevance and avoid repetitive browsing.
- The morning approval packet should rank the highest-value items rather than presenting every research lead as an action request.

## Approval and execution

After the user approves exact items, execute only that approved subset in the signed-in LinkedIn UI. Verify the rendered public action or sent message, record the appropriate receipt, commit and push the resulting repository state, then report only stable public result URLs.
