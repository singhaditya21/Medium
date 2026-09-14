## Define the retry contract before enabling retries

For the internal case-routing command, define the operation as one business intent against one expected case version. Repeated delivery of that intent should resolve to one recorded effect. A later routing decision is a new intent and needs new evidence and authority.

Use a stable action identifier scoped to the tenant, represented principal and operation. Bind it to the target, exact requested delta, actor, expected record version and applicable policy version. A changed payload using the same identifier is a conflict, not an update to the old request. Identical parameters alone do not establish identical intent. [AWS Builders' Library: safe retries](https://aws.amazon.com/builders-library/making-retries-safe-with-idempotent-APIs/).

The target domain must specify:

| Contract item | Required behavior for this proposed design |
| --- | --- |
| New action | Authenticate and authorize; validate current preconditions before admitting the effect |
| Same action and same payload | Return the recorded result without another mutation; authorize result access |
| Same key and different payload | Reject as an intent conflict |
| Changed record version | Stop and reassess; do not overwrite concurrent legitimate work |
| Unknown outcome | Resolve by action ID or use a supported same-key idempotent retry; do not invent a new key |
| Deduplication retention | Cover the supported retry/replay horizon; reject or reconcile expired identities instead of treating them as new |
| No domain idempotency contract | Quarantine the ambiguous action for reconciliation or an accountable operator |

An action ledger written only in the orchestrator cannot make a remote CRM mutation atomic with that ledger. The effect-owning domain must implement the required contract or expose an equivalent transactional interface. A gateway's successful request validation is not proof that the remote system changed exactly once.

For a domain under your control, the transaction can conditionally mutate the record, consume the bound approval, record the outcome and create an outbox event together. The relay can still deliver that event more than once. Every downstream side effect requires its own contract.

## The 4:47 p.m. case when the response disappears

The following identifiers and interleaving are synthetic extensions of the opening scenario:

| Step | Observed event | Required result |
| --- | --- | --- |
| 1 | Case `471`, version `7`, arrives twice | The workflow identifies duplicate input; domain enforcement still protects against replay |
| 2 | Worker A presents action `case-471-route-v7` | Current authority and expected version are checked at the effect boundary |
| 3 | Domain commits routing to enterprise support | Version becomes `8`; approval consumption, outcome and outbox event commit together |
| 4 | Response is lost after commit | Caller records outcome unknown; it does not declare failure or create another intent |
| 5 | Worker B presents the same action and payload | Recorded version-8 result is resolved, without another routing effect |
| 6 | A new command expects version `7` | It is rejected for reassessment; a new key does not bypass a stale precondition |
| 7 | Independent observer checks the effect | Verify the approved delta using an authoritative versioned observation; mismatch remains unresolved |

If another actor has already moved the record to version `9`, a current read alone does not reconstruct the version-8 effect. Use a trusted version/event history correlated to the action, or retain the outcome as unverified. Do not blindly overwrite version `9` to recreate the expected screenshot.

The separately approved customer message remains a different action. The routing approval does not authorize sending it. If incident telemetry changes the proposed promise, stop that message for reassessment even if internal routing is already complete.

## A runnable local acceptance model

The [companion bundle](https://github.com/singhaditya21/Medium/tree/main/linkedin/article-quality-revisions-2026-09-14) includes `protocol.py`, which deliberately models only one SQLite-owned domain and one operation: internal case routing. That operation's namespace is implicit in this single-purpose service. It has no network access, CRM credentials, model calls, signature validation or distributed policy cache. Its grants are trusted synthetic fixtures, not objects accepted from an untrusted client.

```python
from protocol import Command, Domain, UnknownOutcome

command = Command("IN", "ops-owner", "routing-agent", "case-471-route-v7",
                  "case-471", 7, "enterprise-support", 12)
domain = Domain("new-teaching-demo.sqlite", clock=lambda: 100)
domain.initialize(command, expires=200)  # NEW temporary teaching database only
try:
    domain.execute(command, "approval-1", lose_response=True)
except UnknownOutcome:
    assert domain.lookup(command)["version"] == 8
assert domain.inspect()["effects"] == 1
assert domain.inspect()["outbox"] == 1
```

Use the supplied test suite, which creates isolated temporary databases: `python3 -m unittest -v test_protocol`. It exercises actual concurrent connections for two workers sharing one action, both orderings of action versus revocation, lost response followed by connection restart, different payload with the same key, stale record rejection and invalid authority. An injected outbox failure must roll back the record, approval consumption and outcome. The no-contract branch is a tested policy decision, not a simulated remote CRM integration.

This model's execution route requires current valid authority even when replaying a result. After authority expires or is revoked, use a separately authorized read-only outcome-resolution route; do not reissue mutation permission merely to investigate history. The fixture's `lookup` method omits authentication and must never be exposed as a public API.

The teaching database uses serialized writes. Passing these tests does not measure production capacity, prove external-service atomicity, implement OAuth or establish a distributed revocation bound. A deployment needs its own authentication, authorization, signature validation, retention, migrations, access-controlled result lookup, failure testing and operational review. The [Passport article](https://www.linkedin.com/pulse/every-ai-agent-needs-passport-aditya-singh-qrvrc/) defines the authority boundary separately.

Report duplicate business effects per 1,000 attempted actions separately from transport success. Track unresolved outcomes by count, severity and age. A successful API response and a high receipt-coverage percentage do not establish that every business effect has been independently verified.
