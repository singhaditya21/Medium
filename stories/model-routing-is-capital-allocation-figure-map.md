# Figure map — Model Routing Is Capital Allocation

All quantitative values are synthetic. Diagrams are reference architectures, not claims about a deployed system.

Renderer: reproducible Matplotlib PNG at 2400×1600. Each figure includes a technical analysis rail, control contract, assumptions, semantic legend, and evidence label.

| Figure | Tier | Analytical question / form | Supported takeaway | Inputs / assumptions |
|---:|---|---|---|---|
| 1 | Core | Static routing versus capital allocation · Comparison | A production router allocates scarce quality, latency, verification, and loss budgets per action rather than mapping vague difficulty to model size. | Reference architecture; no observed production data. |
| 2 | Core | Risk-aware routing control plane · Architecture | Policy filters infeasible routes before an optimizer ranks eligible model, tool, context, retry, and verification bundles. | Reference architecture; no observed production data. |
| 3 | Core | Workflow cost ledger · Cost decomposition | Input and output tokens are only the visible portion of workflow cost; retries, tools, verification, delay, and recovery can dominate. | Synthetic per-workflow cost allocation; values are illustrative, not vendor prices. |
| 4 | Core | Risk-adjusted route utility · Formula map | The optimal route maximizes expected business value net of execution cost, delay, verification, and tail loss subject to hard policy constraints. | Reference architecture; no observed production data. |
| 5 | Core | Model-route capability matrix · Capability matrix | Route eligibility depends on task, tool, context, privacy, determinism, latency, and verification support—not one global model rank. | Synthetic ordinal capability assessment; not a benchmark comparison. |
| 6 | Core | Quality-cost Pareto frontier · Scatter frontier | Dominated model routes consume more cost without delivering more evaluated quality and should not receive traffic absent another constraint. | Synthetic route-level costs and evaluation scores; no provider benchmark claims. |
| 7 | Core | Risk-adjusted efficient frontier · Portfolio frontier | Adding action-weighted loss can reverse the ranking produced by average quality and token cost alone. | Synthetic scenario model with illustrative costs, probabilities, and loss weights. |
| 8 | Core | Policy-constrained route decision tree · Decision tree | Privacy, authority, action impact, novelty, and deadline gates narrow the portfolio before economic ranking. | Reference architecture; no observed production data. |
| 9 | Core | Router feature and policy pipeline · Feature pipeline | A reproducible feature contract joins task, evidence, risk, runtime, and portfolio state before policy and optimization. | Reference architecture; no observed production data. |
| 10 | Core | Router calibration curve · Reliability curve | A router probability is decision-useful only when predicted suitability aligns with observed cohort outcomes and uncertainty is visible. | Synthetic calibration sample of 20,000 routed tasks; not measured model performance. |
| 11 | Core | Out-of-distribution routing map · Embedding map | Requests far from evaluated support should abstain or use a conservative route instead of receiving a confident cheapest-model decision. | Synthetic two-dimensional projection for explanation; not a production embedding analysis. |
| 12 | Core | Cascaded inference and escalation · Sequence | A cascade spends additional inference only when uncertainty, policy, or verification evidence justifies the marginal call. | Reference architecture; no observed production data. |
| 13 | Core | Retry and tool-cost inflation · Waterfall | A nominal model call can become a much larger workflow expense after retries, context replay, tools, verification, and recovery. | Synthetic cost waterfall for one completed workflow; not current provider pricing. |
| 14 | Core | Verification budget allocation · Allocation bars | Verification capacity should follow marginal expected loss reduction rather than equal sampling or model confidence alone. | Synthetic verification budget and expected-loss-reduction estimates. |
| 15 | Core | Budget shadow-price curve · Marginal value curve | The shadow price shows where one more unit of inference budget creates enough expected business value to justify allocation. | Synthetic monthly budget and marginal-value curve; not a forecast. |
| 16 | Core | Counterfactual router evaluation · Evaluation architecture | A new policy needs logged candidate outcomes, randomized exploration, or defensible estimators; replaying only chosen routes creates selection bias. | Reference architecture; no observed production data. |
| 17 | Core | Routing service objectives · SLO scorecard | Quality floors, tail latency, budget, calibration, policy violations, OOD abstention, and loss exposure need independent objectives. | Synthetic operating scorecard with deliberate calibration and tail-loss breaches. |
| 18 | Core | Migration to governed model routing · Maturity roadmap | Teams should build cost and outcome evidence before moving from fixed routes to constrained optimization and adaptive portfolios. | Reference architecture; no observed production data. |

Palette: blue/teal for trusted or verified paths, gold for decisions, rust for risk/failure, and purple for transformation or policy context. Shape, position, and labels duplicate every color encoding.
