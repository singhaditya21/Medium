# Figure map — Human Approval Is a Queueing System

All quantitative values are synthetic. Diagrams are reference architectures, not claims about a deployed system.

Renderer: reproducible Matplotlib PNG at 2400×1600. Each figure includes a technical analysis rail, control contract, assumptions, semantic legend, and evidence label.

| Figure | Tier | Analytical question / form | Supported takeaway | Inputs / assumptions |
|---:|---|---|---|---|
| 1 | Core | Human approval is not a checkbox · Comparison | Uniform approval routes create delay and habituation; risk-priced service classes spend review where it changes outcomes. | Reference architecture; no observed production data. |
| 2 | Core | Approval decision-service architecture · Architecture | A governed approval service separates risk scoring, eligibility, routing, review, execution, and calibration. | Reference architecture; no observed production data. |
| 3 | Core | Action-level risk decomposition · Risk model | Approval need depends on impact, likelihood, reversibility, novelty, evidence, propagation, and control strength. | Reference architecture; no observed production data. |
| 4 | Core | Expected-loss decision boundary · Formula | Review is economically rational when expected avoided loss exceeds review, delay, and residual-error cost. | Synthetic example: p_agent=.018, p_review=.004, loss=$42k, review=$18, delay=$65; review saves an illustrative $505 per action. |
| 5 | Core | Four approval service classes · Service matrix | Risk, deadline, skills, evidence, and fallback rules define distinct queues rather than one undifferentiated backlog. | Reference architecture; no observed production data. |
| 6 | Core | Erlang-C wait sensitivity · Queue heatmap | When offered load approaches reviewer capacity, expected wait rises nonlinearly and service objectives collapse. | Synthetic M/M/c model: mean service 6 minutes, 3–10 reviewers, arrivals 12–92 per hour; unstable cells are marked. |
| 7 | Core | Arrival, service, and deadline anatomy · Timeline | Approval latency includes queue, assignment, open, decision, and execution handoff—not only reviewer handling time. | Reference architecture; no observed production data. |
| 8 | Core | Backlog growth under three staffing scenarios · Scenario curves | A queue with arrival rate above effective service rate accumulates risk continuously even if daily averages look close. | Synthetic fluid model: arrivals 1,200/hour; effective capacities 900, 1,200, and 1,500/hour; initial backlog 250. |
| 9 | Core | Reviewer-skill routing graph · Bipartite graph | Eligibility, jurisdiction, product, value limit, and conflicts constrain routing before workload balancing. | Reference architecture; no observed production data. |
| 10 | Core | Separation-of-duties enforcement graph · Control graph | The proposer, evidence curator, approver, lease issuer, executor, and verifier need explicit forbidden-role combinations. | Reference architecture; no observed production data. |
| 11 | Core | Approval packet anatomy · Structured packet | A reviewer needs the exact delta, evidence, uncertainty, policy reason, alternatives, expiry, and recovery—not an agent summary alone. | Reference architecture; no observed production data. |
| 12 | Core | Evidence-quality score decomposition · Formula | Evidence quality combines required-source coverage, freshness, corroboration, conflict, provenance, and model uncertainty. | Synthetic factors: required-source .90, freshness .82, corroboration .70, provenance 1.0, conflict .25, uncertainty .18. |
| 13 | Core | Value of additional information · Value curve | Review depth should stop when expected decision improvement falls below the next evidence step's time and cost. | Synthetic saturating benefit and linear review/delay cost for three action-risk classes; not observed reviewer performance. |
| 14 | Core | Fatigue and approval error · Scenario curves | Long uninterrupted review streaks can raise synthetic miss probability while decision time appears to improve. | Synthetic fatigue curves only: miss probability and median handling time by consecutive decision number; no human-subject claim. |
| 15 | Core | Automation threshold frontier · Efficient frontier | The optimal threshold balances review spend, delay, residual loss, and hard risk constraints by action class. | Synthetic 50,000-action simulation with declared risk-score distributions and illustrative cost terms. |
| 16 | Core | Shadow-review calibration matrix · Confusion matrix | Shadow review measures where automated decisions and qualified reviewers disagree before authority expands. | Synthetic 10,000-case matrix: safe automate 7,820; correct escalate 1,410; false escalation 560; false autonomy 210. |
| 17 | Core | Approval-service operating objectives · SLO scorecard | Queue health, eligibility, decision quality, expiry, fatigue, and appeal outcomes need separate objectives and owners. | Synthetic 30-day window with deliberate critical-wait and false-autonomy breaches. |
| 18 | Core | Migration to risk-priced approval · Maturity roadmap | Teams should instrument current review work before changing thresholds, staffing, or autonomy. | Reference architecture; no observed production data. |

Palette: blue/teal for trusted or verified paths, gold for decisions, rust for risk/failure, and purple for transformation or policy context. Shape, position, and labels duplicate every color encoding.
