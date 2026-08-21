# Figure map — A $2.4M Account Is Escalating. Should the AI Agent Act?

All quantitative values are synthetic scenario data. Diagrams are production design patterns, not claims about a deployed system.

Palette policy: two-root cap (teal and gold) with rust for high-risk exceptions, blue for evidence/observation, and neutral ink. Every distinction also uses position, label, shape, or line style.

| Figure | Analytical question | Form | Supported takeaway |
|---:|---|---|---|
| 1 | Account escalation snapshot | Scorecard | The account is commercially material, time-constrained, and evidentially conflicted. |
| 2 | Autonomy boundary by impact and uncertainty | Decision matrix | High-impact actions move to approval or denial as evidence uncertainty rises. |
| 3 | Production control architecture | Architecture diagram | The agent proposes; independent control services authorize, execute, verify, and recover. |
| 4 | Escalation event timeline | Timeline | The decision is shaped by a sequence of changing facts, not a single CRM record. |
| 5 | Evidence bundle anatomy | Structured schema | Every proposed action should carry a versioned, attributable evidence package. |
| 6 | Evidence provenance graph | Directed graph | Claims remain traceable to source records and contradictions stay visible. |
| 7 | Evidence freshness decay | Multi-series line | Different evidence types expire at different rates and should not share one freshness rule. |
| 8 | Evidence quality matrix | Heatmap | No source is uniformly trustworthy across provenance, freshness, completeness, and conflict. |
| 9 | CRM action taxonomy | Ranked bar | Risk rises sharply when the agent crosses from preparation into commercial commitment. |
| 10 | Action-level risk model | Weighted decomposition | Action risk combines impact, irreversibility, uncertainty, scope, and control strength. |
| 11 | Modeled loss distributions | Distribution | A bounded approval design compresses the tail even when median loss changes modestly. |
| 12 | Confidence threshold trade-off | Dual line | Model confidence is not authority; higher thresholds trade automation for lower exception risk. |
| 13 | Human approval policy matrix | Heatmap | Approval depends on action class and commercial exposure, not merely model confidence. |
| 14 | Maker-checker approval flow | Swimlane | The proposer, approver, credential issuer, and executor remain distinct. |
| 15 | Approval latency trade-off | Line with benchmark | Faster review helps the deal until rushed approvals create more expected loss. |
| 16 | Approval packet design | Decision card | Approvers need deltas, evidence conflicts, limits, and rollback—not a prose summary. |
| 17 | Authority envelope | Structured control object | Authority binds principal, actor, action, resource, purpose, limits, time, tool, and evidence. |
| 18 | Permission scope lattice | Hierarchy | Each step narrows standing CRM privilege into one permitted transaction. |
| 19 | Permission lease lifecycle | State flow | A leased permission is issued late, used narrowly, verified, and then revoked or expires. |
| 20 | TTL and scope exposure | Heatmap | Longer leases and broader account scope multiply modeled exposure. |
| 21 | Delegated token exchange | Sequence diagram | The downstream tool receives both the accountable subject and current agent actor. |
| 22 | Pre-action verification gates | Stage progression | The tool refuses execution until evidence, policy, approval, lease, and preconditions agree. |
| 23 | Post-action verification loop | Control loop | A successful API response is not proof that the intended business state exists. |
| 24 | Action receipt schema | Structured record | The receipt joins intent, authority, decision, execution, observation, and recovery pointers. |
| 25 | End-to-end observability trace | Trace timeline | One trace correlates agent planning, policy, approval, credential, tool, and verification events. |
| 26 | Failure-mode risk matrix | Risk matrix | The design prioritizes high-impact failures that can escape ordinary API monitoring. |
| 27 | Containment stack | Layered decomposition | Independent bounds reduce the blast radius even if one control fails. |
| 28 | Recovery state machine | State machine | Recovery is designed before action: freeze, revoke, compensate, reconcile, and close. |
| 29 | Operational reconciliation view | Dashboard | Operators need action, evidence, approval, verification, and recovery metrics together. |
| 30 | Production rollout roadmap | Stage roadmap | Autonomy expands only after evidence, controls, and recovery performance meet gates. |

Renderer: reproducible Matplotlib PNG, 1600×900. Final QA surface: responsive GitHub Pages article and mobile viewport.
