# Signed-in Medium execution bridge

The bridge is a resumable human-in-the-loop state machine. GitHub Actions prepares and validates work, the user initiates the exact Medium action in a signed-in Chrome session, and a credential-free receipt causes Actions to continue.

```text
GitHub prepared
  -> awaiting signed-in execution
  -> user initiates exact action in Chrome
  -> visible Medium result verified
  -> receipt and resulting repository state committed
  -> GitHub continuation workflow validates and resumes
```

## Why Chrome and GitHub remain separate

A GitHub-hosted runner cannot access the Chrome profile on the user's Mac. The repository therefore never exports or stores Medium passwords, cookies, browser storage, access tokens, private draft URLs, account email addresses, or subscriber-level information. GitHub Actions does not use Playwright, Selenium, a headless login, or a session replay against Medium.

## Release execution

1. Run **Medium Release Bundle** with one exact story slug.
2. The workflow validates the story, uploads the bundle, and opens a labeled issue in `awaiting-signed-in-execution`.
3. Sign in to Medium in Chrome.
4. Ask Codex to execute the exact release issue. A private-draft import and a public Publish are separate operations.
5. For a public Publish or Schedule action, Codex shows the exact title, topics, publication, canonical URL, email choice, paywall choice, and timing and obtains action-time confirmation.
6. Codex verifies the persisted Medium state and runs `scripts/record_medium_execution.py`.
7. The resulting receipt and any registry changes are committed through a pull request.
8. After merge, **Medium Signed-In Continuation** validates the receipt, comments on the originating issue, changes its labels, and closes it when the public result is complete.

Example after a private draft has been visibly verified:

```bash
python scripts/record_medium_execution.py draft-imported \
  --story-slug STORY_SLUG \
  --issue-number ISSUE_NUMBER \
  --confirmation-scope "Import this exact GitHub Pages story into a private Medium draft; do not publish" \
  --verification "Medium showed the expected title and saved draft state"
```

Example after a public publication has been confirmed and visibly verified:

```bash
python scripts/record_medium_execution.py story-published \
  --story-slug STORY_SLUG \
  --issue-number ISSUE_NUMBER \
  --medium-url PUBLIC_MEDIUM_URL \
  --canonical-url GITHUB_PAGES_CANONICAL_URL \
  --topic "TOPIC_ONE" \
  --topic "TOPIC_TWO" \
  --subscriber-email false \
  --paywall false \
  --confirmation-scope "Publish the reviewed story with the named topics and final settings" \
  --verification "Public Medium URL rendered the expected story and settings"
```

## Analytics continuation

A metrics refresh is a user-initiated, read-only review of the signed-in Medium Stats and Audience pages. It produces:

- `analytics/snapshots/YYYY-MM-DD.json` with aggregate values only;
- an updated `analytics/engagement-baseline.json` and dashboard source;
- a `stats_captured` receipt linked to the monthly GitHub issue.

The continuation workflow validates snapshot chronology and consistency, then produces `snapshot-history.csv` and a bridge summary. It does not scrape Medium on a schedule.

## Response continuation

`engagement/queue.json` holds no more than five carefully reviewed candidates. Each candidate names one Medium story, its author, specific evidence from the story, the reason to engage, and the full proposed response.

The queue does not grant posting permission. Immediately before responding, Codex presents the exact target and exact public text for confirmation. After the response is posted and its public URL verified, a `response_posted` receipt updates the queue and resumes GitHub reporting.

## Repository states

| Label | Meaning |
|---|---|
| `awaiting-signed-in-execution` | GitHub preparation passed; no Medium result is claimed |
| `medium-draft-saved` | The private draft state was visibly verified |
| `medium-published` | The final public URL and settings were visibly verified |
| `medium-stats-captured` | An aggregate signed-in read-only snapshot was committed |
| `medium-response-posted` | One approved public response URL was visibly verified |

## Integrity boundary

- The user's login stays in Chrome.
- Every Medium action originates from an explicit user request.
- Public stories and responses receive action-time confirmation.
- GitHub Actions validates receipts but never creates proof of an action it did not perform.
- No mass, recurring, or unattended interactions are supported.
