# LinkedIn agent policy

## Hard boundaries

- Use the existing Codex automation and Chrome session only. Do not use an OpenAI API key, API-backed service, exported cookies, session files, passwords, or private URLs.
- Prepare research, drafts, scores, and approval packets automatically; never post, comment, reply, message, react, follow, connect, repost, publish, or schedule without exact action-time user approval.
- Treat each outbound comment, post, and DM as representational communication by the user. Approval of one item never approves another.
- Read the watchlist before drafting any follow-up. Do not create a generic check-in, repeat a thread that is awaiting an inbound reply, or create a duplicate response.
- Do not tag people merely for reach. A tag must be relevant to the source discussion and render correctly before a live action is reported as complete.
- Do not retain private conversation text, private LinkedIn URLs, browser state, or credentials in Git. Record only the allowed receipt fields after a verified action.

## Research and quality limits

- Run every two hours; inspect at most five source-specific profiles or posts in a cycle.
- Accumulate up to 50 distinct comment opportunities and 50 individually reasoned DM prospects during a rolling 24-hour window. This is a research target, never a sending target.
- Put no more than five LinkedIn comments or replies into one approval batch, as required by `engagement/queue.json`.
- Draft at most five DMs per cycle and one post concept per cycle. Prioritize novelty and relationship relevance over volume.
- A candidate requires a priority score of at least 0.70, source-specific evidence, a non-duplicative contribution, and a clear reason the user's enterprise-AI, CRM, RevOps, or governance expertise helps the conversation.

## Quality tests

- A comment adds an operational implication, metric, implementation trade-off, or constructive challenge; it does not restate the source.
- A DM explains the genuine reason for outreach and does not use a generic networking template, a pitch, or an unexplained link.
- A post has a distinct hook, a specific operating insight, and an optional series/Medium connection only when it adds value.
- Every proposed action identifies the exact public target, proposed text, intended tags, evidence, and why now.
