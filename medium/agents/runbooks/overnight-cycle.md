# Overnight Medium research cycle

## Purpose

Maintain an evidence-backed Medium editorial and growth pipeline while keeping public authorship and engagement under the user's control.

## Every run

1. Pull and validate the repository.
2. Read `engagement/strategy.json`, `engagement/queue.json`, releases, execution evidence, and only the catalog, policy, runbook, or metrics section required by the observed trigger.
3. Apply the **idle-first gate**. A scheduled-story audit, substantive inbound item, due measurement checkpoint, planned editorial window, explicit user research request, or approved action needing verification is required before deeper work. If there is no trigger, do not inspect new external sources or draft external communication.
4. Inspect **every scheduled story** in the signed-in Medium UI before other Medium research. Report its title, exact IST schedule, time remaining, story/publication state, preview/featured image, topics, canonical URL, subscriber-email, paywall, and release-risk alerts. Do not change any setting.
5. Reconcile due 48-hour, 7-day, and 28-day story checkpoints. Inspect the signed-in Medium UI only when read-only account evidence is needed.
6. Separate evidence from hypotheses. Diagnose the path from presentation to view to read to follow/subscribe; do not infer a defect from a tiny sample.
7. Inspect only the source-specific stories, publications, and official references needed for the current decision. Do not begin new opportunity research if the approval queue is at capacity.
8. Prepare the limited set of story briefs, audit recommendations, publication-fit packages, and response candidates permitted by policy only after a qualifying signal.
9. Add only compliant response candidates to `engagement/queue.json` with `scripts/manage_engagement_queue.py`. Do not queue low-score, stale, duplicative, generic, or capacity-exceeding work.
10. Return a concise chat report: scheduled-story audit, findings, metrics, evidence, draft text/settings, expected outcome, and approvals required. For an idle cycle, state that no action is recommended and name the next checkpoint.
11. Commit and push only validated, privacy-safe preparation changes. Public actions are executed only after exact approval and visible verification.

## Overnight division of work

| IST time | Primary focus | Required output |
| --- | --- | --- |
| 11 PM | Catalog, notifications, schedules, and metrics | complete scheduled-story release check, ranked audit backlog, and any inbound items needing a response |
| 1 AM | Topic and source research | up to two source-backed story briefs |
| 3 AM | Architecture and editorial review | outlines, visual/code plans, evidence gaps, and human-authorship flags |
| 5 AM | Distribution and publication fit | settings/preview/navigation diagnosis and selective submission packages |
| 7 AM | Conversation and growth review | up to two response candidates plus measured experiment recommendations |

## Approval packet

For every candidate action, include:

- Exact target and stable public link.
- What was specifically read or observed.
- Priority score and why the work is timely.
- Exact response, edit, story settings, or submission package.
- Expected metric and review checkpoint.
- Explicit action-time approval language.

For a scheduled story, also include the intended Medium schedule, subscriber-email and paywall settings, publication destination, topics, canonical URL, preview/featured-image status, and a clear statement that no setting was changed.

If there is no qualifying action, say so plainly and report the next measurement checkpoint instead of manufacturing an engagement batch.
