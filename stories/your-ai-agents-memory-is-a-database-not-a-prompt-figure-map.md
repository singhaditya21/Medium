# Figure map — Your AI Agent's Memory Is a Database, Not a Prompt

All quantitative values are synthetic. Diagrams are reference architectures, not claims about a deployed system.

Renderer: reproducible Matplotlib PNG at 2400×1600. Each figure includes a technical analysis rail, control contract, assumptions, semantic legend, and evidence label.

| Figure | Tier | Analytical question / form | Supported takeaway | Inputs / assumptions |
|---:|---|---|---|---|
| 1 | Core | Memory is governed state—not appended text · Comparison | A prompt fragment lacks the provenance, time, purpose, and lifecycle controls required for consequential decisions. | Reference architecture; no observed production data. |
| 2 | Core | Enterprise agent-memory control plane · Architecture | Six independently operated planes convert heterogeneous evidence into policy-filtered, revocable decision context. | Reference architecture; no observed production data. |
| 3 | Supplemental | Source trust zones and admissible influence · Trust-zone map | Source identity and control history determine how strongly a memory may influence an action. | Reference architecture; no observed production data. |
| 4 | Core | Provenance graph for a renewal assertion · Lineage graph | Every derived assertion should remain connected to sources, transformations, reviewers, and invalidation events. | Reference architecture; no observed production data. |
| 5 | Core | Bitemporal memory-envelope contract · Structured schema | A memory record needs business validity, system knowledge time, provenance, trust, purpose, retention, and policy fields. | Reference architecture; no observed production data. |
| 6 | Core | Bitemporal truth: what was true versus what was known · Timeline | Valid time and transaction time answer different audit questions and prevent later corrections from rewriting history. | Reference architecture; no observed production data. |
| 7 | Core | Ingestion validation and promotion pipeline · Stage pipeline | Untrusted input becomes decision-eligible only after parsing, instruction stripping, provenance binding, policy, and corroboration. | Reference architecture; no observed production data. |
| 8 | Core | Indirect memory-poisoning attack graph · Attack graph | One malicious attachment can survive summarization and retrieval unless each transformation preserves provenance and trust boundaries. | Reference architecture; no observed production data. |
| 9 | Supplemental | Quarantine and adjudication state machine · State machine | Suspicious memory must remain non-influential until independently validated, corrected, or terminally rejected. | Reference architecture; no observed production data. |
| 10 | Core | Freshness decay by memory class · Scenario curves | Freshness is domain-specific: prices decay faster than contract terms, while immutable events may not decay at all. | Illustrative half-lives: price 6 h, case status 24 h, account risk 7 d, contract term 180 d; immutable events do not decay. |
| 11 | Core | Trust, corroboration, and uncertainty model · Formula decomposition | A decision-use score should expose source trust, corroboration, freshness, transformation loss, and contradiction penalties. | Synthetic example: source .82, corroboration .75, freshness .88, transform .92, contradiction .20; weights declared in story. |
| 12 | Core | Retrieval-time admissibility decision tree · Decision tree | Semantic similarity is only a candidate generator; policy, purpose, time, trust, and contradiction gates decide admissibility. | Reference architecture; no observed production data. |
| 13 | Core | Policy-filtered vector retrieval architecture · Retrieval architecture | Access and purpose filters must constrain candidate generation and re-ranking before content reaches the model. | Reference architecture; no observed production data. |
| 14 | Supplemental | Conflict resolution by source authority and time · Decision matrix | Conflicts should resolve through deterministic source authority and temporal rules—not whichever chunk ranks highest. | Ordinal reference matrix; authority and recency rules are illustrative and must be replaced by a governed source hierarchy. |
| 15 | Core | Deletion and correction propagation · Sequence | A deletion request is incomplete until derivatives, indexes, caches, prompts, and decision artifacts are reconciled. | Reference architecture; no observed production data. |
| 16 | Supplemental | Retention policy by memory class and purpose · Retention heatmap | Retention should be purpose- and class-specific, with legal holds and cryptographic erasure modeled explicitly. | Illustrative policy periods only; legal, contractual, privacy, and records-management owners must set production values. |
| 17 | Core | Memory control-plane operating objectives · SLO scorecard | Quality, freshness, provenance, deletion, poisoning, and retrieval-policy failures require separate measurable objectives. | Synthetic 30-day operating window with two deliberate breaches to demonstrate escalation behavior. |
| 18 | Core | Migration from prompt memory to governed memory · Maturity roadmap | Teams should introduce provenance and read-only retrieval before allowing learned memory to influence consequential actions. | Reference architecture; no observed production data. |

Palette: blue/teal for trusted or governed paths, gold for decisions, rust for risk/denial, purple for transformation or policy context. Shape, position, and labels duplicate every color encoding.
