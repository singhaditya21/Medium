# Medium release bridge

This directory defines the repository-to-Medium release contract. It automates preparation, validation, duplicate prevention, release packaging, and approval tracking. It does not run an unattended Medium publisher.

The resumable Chrome-to-GitHub lifecycle is documented in [`SIGNED_IN_BRIDGE.md`](SIGNED_IN_BRIDGE.md).

## Why the boundary exists

Medium is not issuing new API integration tokens, and its current rules prohibit automatic, systematic, or programmatic posting and interactions. Medium's supported cross-posting route is its signed-in import tool, which backdates the story and sets the source canonical URL.

Accordingly:

- GitHub Actions never receives Medium credentials, cookies, local storage, or session exports.
- A workflow can prepare a release bundle and open an approval issue.
- A signed-in browser session can import the exact source into a private draft after a direct request.
- Publish, Schedule, publication submission, subscriber email, paywall, and final topics require action-time confirmation.

## Configure a story

Create `medium/releases/<story-slug>.json` using `medium/release.schema.json`. The safe draft defaults are enforced:

- operation: `import_to_private_draft`
- subscriber email: `false`
- paywall: `false`
- schedule: `null`
- unattended publish: `false`
- human review and final confirmation: `true`

Then run:

```bash
python scripts/build_site.py
python scripts/prepare_medium_release.py \
  --slug your-ai-agent-should-not-have-a-standing-role \
  --strict
```

The generated `release.json` is the machine-readable browser handoff. `release.md` is the human review record.

`medium/publications.json` is the reviewed duplicate-prevention registry. Every story must have exactly one entry. Record a story as `published` with its actual Medium URL immediately after a confirmed publication; do not infer publication state from the canonical URL because an imported story can keep GitHub as canonical.

## GitHub workflow

Run **Medium Release Bundle** from the Actions page with an exact story slug. The workflow:

1. rebuilds and validates the public site;
2. rejects stories marked published in the Medium registry, including imports whose canonical remains on GitHub;
3. validates AI disclosure placement and figure accessibility;
4. validates topics and safe publishing defaults;
5. uploads the release bundle;
6. opens one GitHub approval issue.

No request is sent to Medium by GitHub Actions.

## Signed-in execution

After reviewing the issue, ask Codex to import the named bundle into your signed-in Medium account. Draft import and final publication are separate actions. The first may leave a private saved draft; the second always requires confirmation of the exact target and distribution settings.

After the visible Medium result is verified, Codex records a credential-free receipt in `medium/executions/`. Merging that receipt triggers **Medium Signed-In Continuation**, which validates the result, updates the originating issue, and regenerates tracking artifacts. The receipt is the event that lets GitHub Actions continue; Chrome credentials are never transferred to the runner.

Official references:

- <https://help.medium.com/hc/en-us/articles/213480228-API-Importing>
- <https://help.medium.com/hc/en-us/articles/214550207-Importing-a-post-to-Medium>
- <https://help.medium.com/hc/en-us/articles/360033930293-Set-a-canonical-link>
- <https://help.medium.com/hc/en-us/articles/213477928-Medium-Rules>
