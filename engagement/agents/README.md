# Shared cross-platform agent workspace

This workspace defines five logical research and review roles used by both the LinkedIn and Medium systems. They operate as hooks inside the existing platform cycles, not as a third scheduler, extra browser identity, or autonomous publisher.

## Roles

1. **Content intelligence graph** connects each pillar, story, LinkedIn post, audience signal, and follow-up question to expose gaps, reuse opportunities, and duplication risk.
2. **Evidence supply chain** keeps an inspectable claim-to-source map, flags ageing or weak evidence, and identifies the most valuable unanswered technical questions.
3. **Experiment manager** turns a measured hypothesis into a minimal, reversible test with a decision threshold and a 48-hour, 7-day, or 28-day checkpoint.
4. **Technical-art director** chooses the clearest figure, architecture, formula, code sample, or interactive artifact for the reader's decision; it does not create decorative visual volume.
5. **Portfolio conversion** links a relevant reader journey across the GitHub Pages catalog, Medium series, LinkedIn posts, and profile positioning without link spam or misleading calls to action.

## Operating contract

- The roles read only repository policy, approved release data, public or user-authorized platform evidence, and privacy-safe receipts.
- They prepare a concise recommendation with evidence, confidence, expected outcome, metric, and exact approval boundary.
- They never post, message, react, follow, publish, schedule, edit public material, change account settings, or add a new run time.
- Any action recommendation is passed to the appropriate LinkedIn or Medium approval-and-receipts role and still needs exact action-time user confirmation.

The authoritative machine-readable contract is `engagement/strategy.json` under `crossPlatformAgentSystem`.

## Token-efficiency controls

The system is **idle-first**. It does not activate every logical role in every run. A role is activated only by a decision-relevant trigger, and an idle run returns a short no-action status with the next checkpoint. It does not browse new sources, draft external communication, or enlarge the approval queue.

Deeper work is triggered only by a substantive inbound item, a due measurement checkpoint, an explicit request, an approved action that needs verification, a Medium scheduled-story audit, or the planned Medium editorial window. New discovery stops when the approval queue is full. The deterministic test matrix is in [`evaluations/dry-run-matrix.json`](evaluations/dry-run-matrix.json).
