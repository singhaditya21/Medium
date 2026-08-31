# Two-hourly LinkedIn research cycle

## Purpose

Keep a high-quality approval queue ready without continuously polling LinkedIn or creating public activity without the user's permission.

## Cycle sequence

1. Pull and validate the repository.
2. Read the current queue, watchlist, latest receipts, `engagement/strategy.json`, and only the runbook/policy sections required for the observed signal.
3. Apply the **idle-first gate**. A new substantive inbound item, a due measurement checkpoint, an explicit user research request, or an approved action needing verification is required before deeper research. If no trigger exists—or the approval queue is at capacity—do not open new external sources or draft external communication.
4. On a valid trigger, review the relevant notifications, comments, replies, or DMs. Separate inbound conversations from passive reactions, generic job alerts, and noise.
5. Inspect up to five relevant source-specific posts or profiles only when the trigger needs discovery. Check prior interaction before creating any candidate.
6. Score valid candidates with the repository's relevance, discussion-quality, unique-contribution, and recency formula.
7. Draft up to one original post concept, five comments/replies, and five DMs only after a qualified signal. Retain DM and post wording only in the approval brief unless separately requested for editorial review.
8. Add only compliant comment/reply candidates to `engagement/queue.json` through `scripts/manage_engagement_queue.py`. Do not add low-score, duplicated, stale, or capacity-exceeding candidates.
9. Produce a concise approval packet when there are qualifying actions: target, evidence, exact text, intended tag, score, and relationship context.
10. If there is no material action, return a quiet status that says no action is recommended and names the next checkpoint. Do not manufacture an engagement batch.

## Review cadence

- The scheduler invokes this cycle every two hours.
- A rolling day may contain up to 50 researched comment opportunities and 50 DM prospects; each cycle remains narrow to protect relevance and avoid repetitive browsing.
- The morning approval packet should rank the highest-value items rather than presenting every research lead as an action request.

## Approval and execution

After the user approves exact items, execute only that approved subset in the signed-in LinkedIn UI. Verify the rendered public action or sent message, record the appropriate receipt, commit and push the resulting repository state, then report only stable public result URLs.
