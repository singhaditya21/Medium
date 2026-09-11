# LinkedIn editorial bundle: shared context

Read [LINKEDIN-INTEGRATION.md](LINKEDIN-INTEGRATION.md) before any bundle skill.
This shared index is not a registered skill; the 11 entrypoints are under `skills/`.

## Voice rules

Use [references/voice-profile.md](references/voice-profile.md) for this account.
Preserve factual accuracy, source-specific technical depth, concise paragraphs
and natural wording. Do not invent personal experience or metrics. Upstream
[voice rules](references/voice-rules.md) are optional stylistic suggestions only;
local policy, approved text and user preferences override them.

## URLs and execution

Use observed LinkedIn post/comment URLs and the matching native UI reply control.
Do not infer one URN type from another, invoke missing upstream `lib` functions,
or call posting APIs. `linkedin-engage-network` supplies the Chrome workflow.
The integration contract contains the full approval and privacy boundary.
