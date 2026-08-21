# Figure map — Your AI Agent Should Not Have a Standing Role

All quantitative values are synthetic threat-model data. Diagrams are reference designs, not claims about a deployed system.

Palette policy: hard two-root cap per chart, using teal/blue for bounded authority and observation, gold for decision controls, rust for risk, and neutral ink. Every distinction also uses labels, position, line style, or shape.

| Figure | Analytical question | Form | Supported takeaway |
|---:|---|---|---|
| 1 | Permission model comparison | Scorecard | A standing role preserves broad authority between decisions; a lease exists only for one bounded action. |
| 2 | Standing-role attack graph | Architecture diagram | One reusable credential creates multiple reachable resources and mutation paths. |
| 3 | Just-in-time lease control plane | Architecture diagram | Independent evidence, policy, approval, issuance, enforcement, verification, and recovery services bound authority. |
| 4 | Authority narrowing path | Stage progression | Each control step removes unused resources, actions, values, time, and repetitions. |
| 5 | Permission lease envelope | Structured schema | A useful lease binds principal, actor, action, resource, limits, evidence, audience, proof key, time, and use count. |
| 6 | Lease lifecycle | State machine | A lease moves through requested, evaluated, approved, issued, consumed, verified, and terminal states. |
| 7 | Lease issuance sequence | Sequence diagram | The executor receives authority only after current policy and approval checks succeed. |
| 8 | Policy decision boundary | PEP/PDP diagram | The policy enforcement point asks an external decision service and enforces returned obligations. |
| 9 | Rich authorization mapping | Field map | Business intent is translated into structured authorization details instead of a coarse scope string. |
| 10 | Exposure model | Formula decomposition | Modeled exposure depends on reachable value, scope, duration, uses, propagation, and control effectiveness. |
| 11 | TTL and scope exposure | Heatmap | Modeled exposure grows nonlinearly when credential lifetime and resource breadth expand together. |
| 12 | Compromise opportunity by TTL | Multi-series line | Shorter leases reduce the probability that a compromise window overlaps valid authority. |
| 13 | Replay containment by token mode | Grouped bar | Audience binding, sender constraint, and one-use consumption reduce replay reach. |
| 14 | Blast-radius distribution | Distribution | Leased authority compresses the loss tail in a synthetic compromise simulation. |
| 15 | Audience and resource binding | Reachability graph | A lease valid for one resource server should fail at adjacent APIs. |
| 16 | Lease policy decision tree | Decision tree | High-risk actions require evidence, eligible approval, bounded values, and live preconditions. |
| 17 | Approval-to-lease binding | Cryptographic binding diagram | Digests prevent an approved proposal from being silently changed before issuance or execution. |
| 18 | Executor validation gates | Stage bars | Execution stops unless signature, time, audience, proof, use count, policy, and preconditions all agree. |
| 19 | Concurrent-state race | Timeline | Optimistic concurrency prevents a valid lease from overwriting a newer human change. |
| 20 | Idempotent execution protocol | Sequence diagram | One action identifier makes retries safe and duplicate effects observable. |
| 21 | Action receipt chain | Structured lineage | The receipt joins intent, evidence, approval, lease, request, outcome, verification, and recovery. |
| 22 | Failure-mode control matrix | Heatmap | No single control covers theft, replay, stale context, over-scope, duplication, and downstream divergence. |
| 23 | End-to-end latency budget | Stacked bar | A lease path can remain operationally fast when control services have explicit budgets. |
| 24 | Lease control-plane SLOs | Operational scorecard | Security and reliability require measurable issuance, denial, expiry, replay, verification, and recovery signals. |
| 25 | Permission-lease rollout | Maturity roadmap | Teams should remove standing privilege action class by action class behind promotion gates. |

Renderer: reproducible Matplotlib PNG, 1600×900. Final QA surface: responsive GitHub Pages article and Medium import page.
