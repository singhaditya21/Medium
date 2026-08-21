# Figure map — Your AI Agent Should Not Have a Standing Role

All quantitative values are synthetic threat-model data. Diagrams are reference designs, not claims about a deployed system.

Palette policy: hard two-root cap per chart, using teal/blue for bounded authority and observation, gold for decision controls, rust for risk, and neutral ink. Every distinction also uses labels, position, line style, or shape.

| Figure | Tier | Analytical question | Form | Supported takeaway | Inputs / assumptions |
|---:|---|---|---|---|---|
| 1 | Core | Permission model comparison | Scorecard | A standing role preserves broad authority between decisions; a lease exists only for one bounded action. | Reference design; no observed production data. |
| 2 | Supplemental | Standing-role attack graph | Architecture diagram | One reusable credential creates multiple reachable resources and mutation paths. | Reference design; no observed production data. |
| 3 | Core | Just-in-time lease control plane | Architecture diagram | Decision inputs authorize issuance; the protected API consumes, enforces, verifies, and recovers. | Reference design; no observed production data. |
| 4 | Supplemental | Authority narrowing path | Stage progression | Each control step removes unused resources, actions, values, time, and repetitions. | Synthetic reachable-surface stages: 100, 52, 31, 12, 5.5, 1.6, 0.35 percent. |
| 5 | Core | Permission lease envelope | Structured schema | A useful lease binds principal, actor, action, resource, limits, evidence, audience, proof key, time, and use count. | Reference design; no observed production data. |
| 6 | Core | Lease lifecycle | State machine | Reservation, effect observation, ambiguity, verification, and recovery are explicit durable states. | Reference design; no observed production data. |
| 7 | Core | Lease issuance sequence | Sequence diagram | The executor receives authority only after current policy and approval checks succeed. | Reference design; no observed production data. |
| 8 | Supplemental | Policy decision boundary | PEP/PDP diagram | The policy enforcement point asks an external decision service and enforces returned obligations. | Reference design; no observed production data. |
| 9 | Supplemental | Rich authorization mapping | Field map | Business intent is translated into structured authorization details instead of a coarse scope string. | Reference design; no observed production data. |
| 10 | Supplemental | Exposure model | Formula decomposition | Modeled exposure depends on reachable value, scope, duration, uses, propagation, and control effectiveness. | Illustrative V=USD 2.4M, S=.05, U=1, P=1.2, C=.70; output USD 43.2k. |
| 11 | Core | TTL and scope exposure | Heatmap | A declared sensitivity index rises when credential lifetime and resource breadth expand together. | Index = sqrt(records) × (TTL/30s)^.55, normalized to 100 at 100 records and 60 minutes. |
| 12 | Supplemental | Compromise opportunity by TTL | Multi-series line | Shorter leases reduce the probability that a compromise window overlaps valid authority. | Poisson opportunity rates per second: 1/7200, 1/1800, 1/450. |
| 13 | Supplemental | Replay containment by token mode | Grouped bar | Audience binding, sender constraint, and one-use consumption reduce replay reach. | Fixed scenario indexes; bearer baseline = 100. Values are not observed calls. |
| 14 | Supplemental | Blast-radius distribution | Distribution | Leased authority compresses the loss tail in a synthetic compromise simulation. | Seed 21; 20,000 lognormal draws per model; parameters are declared in the story. |
| 15 | Core | Audience and resource binding | Reachability graph | A lease valid for one resource server should fail at adjacent APIs. | Reference design; no observed production data. |
| 16 | Supplemental | Lease policy decision tree | Decision tree | High-risk actions require evidence, eligible approval, bounded values, and live preconditions. | Reference design; no observed production data. |
| 17 | Supplemental | Approval-to-lease binding | Cryptographic binding diagram | Digests prevent an approved proposal from being silently changed before issuance or execution. | Reference design; no observed production data. |
| 18 | Core | Executor validation gates | Stage progression | Cryptographic, sender, authority, freshness, consumption, and effect gates are independently mandatory. | Reference gate contract only; no pass-rate or production-volume claim. |
| 19 | Supplemental | Concurrent-state race | Timeline | Optimistic concurrency prevents a valid lease from overwriting a newer human change. | Reference design; no observed production data. |
| 20 | Core | Idempotent execution protocol | Sequence diagram | One action identifier makes retries safe and duplicate effects observable. | Reference design; no observed production data. |
| 21 | Core | Action receipt chain | Structured lineage | The receipt joins intent, evidence, approval, lease, request, outcome, verification, and recovery. | Reference design; no observed production data. |
| 22 | Core | Failure-mode control matrix | Heatmap | No single control covers theft, replay, stale context, over-scope, duplication, and downstream divergence. | Reference design; no observed production data. |
| 23 | Core | End-to-end latency budget | Stage bars with cumulative line | Direct stage budgets reveal where the control-path objective is spent. | Synthetic p95 stage budgets in ms: 12, 28, 18, 42, 6, 110, 75, 16; total 307. |
| 24 | Supplemental | Lease control-plane objectives | Target-versus-actual scorecard | Every operating objective needs a target, actual result, and visible pass or breach state. | Synthetic 30-day targets and actuals; one deliberate verification-mismatch breach. |
| 25 | Core | Permission-lease rollout | Maturity roadmap | Teams should remove standing privilege action class by action class behind promotion gates. | Reference design; no observed production data. |

Renderer: reproducible Matplotlib PNG, 1920×1280. Every plate uses a compact deep-dive header, a figure-specific technical analysis rail, a control contract, declared assumptions, and a semantic legend. Final QA surface: responsive GitHub Pages article and Medium import page.
