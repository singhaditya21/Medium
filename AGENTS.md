# Repository operating instructions

## LinkedIn work

Use `linkedin/agents/policy.md`, `engagement/strategy.json`, and the relationship
watchlist before LinkedIn research or action. The signed-in Chrome workflow is
provided by the installed `linkedin-engage-network` skill.

The 11 repository-local editorial skills in `.agents/skills/` supplement that
workflow. Before using any of them, read `.agents/LINKEDIN-INTEGRATION.md`.
It supersedes conflicting upstream API, reaction, cadence, voice, and publishing
instructions. Read only the skill and references relevant to the current signal.

No OpenAI API, Apify, Publora, Pixfaro, detector service, custom poster, exported
session, or unattended public action is authorized. Show exact targets, wording,
mentions, media and settings, then obtain action-time confirmation. A comment
approval does not approve a reaction, DM, follow, connection, or additional post.
Recheck context and duplicates immediately before execution; visibly verify it.

Preserve LinkedIn and Medium schedules, existing text/settings/media outside the
approved scope, and unrelated working-tree changes. Never commit private DMs,
private URLs, credentials, cookies or browser state. Record only verified actions.

## Validation

For local LinkedIn skill changes run `python3 scripts/validate_linkedin_skills.py`
and `python3 scripts/validate_engagement_automation.py`. A static validation pass
does not prove the Chrome connection or a live action succeeded.
