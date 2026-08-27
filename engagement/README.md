# Cross-platform engagement operating system

This directory is the source of truth for the Medium + LinkedIn engagement loop. GitHub Actions performs the repeatable work: it validates policy, ranks a bounded queue, packages exact drafts, derives 48-hour/7-day/28-day measurement checkpoints, refreshes one weekly GitHub issue, and resumes reporting from execution receipts.

## State machine

```text
discovered -> proposed -> ready_for_confirmation
                              |
                              +-> exact user confirmation in signed-in Chrome
                                      -> posted -> visible verification -> receipt
                              |
                              +-> skipped
```

`ready_for_confirmation` is not permission to post. The exact target, exact text, and any intended mention must be shown immediately before each public action. Medium and LinkedIn results are recorded only after the public result is visible.

## Candidate requirements

Every item in `queue.json` contains:

- one platform and one action;
- the exact public target URL, author, and title;
- source-specific evidence and a reason to engage;
- the complete proposed response;
- a priority score from 0 to 1;
- at most one relevant LinkedIn mention;
- an explicit state.

Up to five active candidates per platform are allowed in a review batch. Posted and skipped entries remain as an audit trail and do not consume the active limit.

Larger researched campaigns are stored as dated opportunity backlogs. Only one wave of five moves into `queue.json` at a time; later waves must have their source and exact target revalidated before promotion. This prevents stale, duplicate, or high-volume interactions while preserving the research and draft work.

The score is:

```text
S = 0.35(relevance) + 0.25(discussion quality)
  + 0.20(unique contribution) + 0.20(recency)
```

Only candidates at or above 0.70 are eligible to move to `ready_for_confirmation`.

## Automated cadence

`engagement-automation.yml` runs twice each weekday and can also be dispatched manually. It updates one weekly review issue instead of creating notification spam. The package contains the current publishing calendar, due measurement windows, queue status, and exact next steps.

`engagement-continuation.yml` validates new LinkedIn receipts. Medium receipts continue through `medium-continuation.yml`. Both paths preserve the same confirmation, verification, and no-credential rules.

## Commands

Generate the operating packet locally:

```bash
python scripts/generate_engagement_review.py --output-dir engagement-review
```

Add or promote a reviewed candidate:

```bash
python scripts/manage_engagement_queue.py add \
  --platform linkedin \
  --action comment \
  --direction outbound \
  --target-url PUBLIC_POST_URL \
  --title "POST_TITLE" \
  --author "AUTHOR" \
  --reason "WHY_THIS_CONVERSATION_MATTERS" \
  --evidence "SOURCE_SPECIFIC_DETAIL" \
  --draft-response "EXACT_PROPOSED_COMMENT" \
  --priority-score 0.82

python scripts/manage_engagement_queue.py ready --candidate-id CANDIDATE_ID
```

After one approved LinkedIn action is visibly verified, record it:

```bash
python scripts/record_linkedin_execution.py comment-posted \
  --candidate-id CANDIDATE_ID \
  --target-url PUBLIC_POST_URL \
  --public-url PUBLIC_COMMENT_URL \
  --issue-number ISSUE_NUMBER \
  --confirmation-scope "Post this exact comment on this exact LinkedIn post" \
  --verification "The public comment is visible with the expected text"
```

## Non-negotiable boundary

GitHub-hosted runners cannot use the Chrome profile on the author's Mac. They do not sign in, export cookies, replay sessions, scrape private feeds, comment, respond, react, follow, repost, or manufacture traffic. This is also required by current Medium and LinkedIn automation rules. The repository automates every safe surrounding step; the public account action remains individually approved and user-initiated.
