# 99.5% Accurate—and Still Wrong 500 Times

### The human-review math missing from enterprise AI dashboards

At an assumed 100,000 AI-assisted decisions per month, 99.5% correctness implies 500 expected errors. The operating decision is whether the organization can detect and contain the consequential subset before those errors harm a customer or change an important record.

This is a worked scenario, not a measured customer result. It does not establish that an evaluation-set accuracy score will carry over to production. The useful outcome is a review contract whose assumptions can be checked.

## Start with the populations

Let `E` mean an incorrect decision under an independently adjudicated label. Let `H` mean that the error meets the organization's predefined high-impact criterion. Let `D` mean the end-to-end control detects that high-impact error **in time to prevent the consequential effect**.

For a fixed operating window:

```text
Expected high-impact escapes = N × P(E) × P(H | E) × [1 − P(D | H,E)]
```

This uses conditional populations; it does not assume independence. The last probability includes routing into review, reviewer detection and intervention timing. If the available metric is reviewer recall only among routed cases, it is not this end-to-end probability.

For example, 80% routing recall followed by 80% timely detection among routed high-impact errors gives 64% end-to-end detection under those conditional definitions. The original five-escape scenario requires **80% end-to-end** recall, not 80% at each stage.

| Assumed quantity | Value | Denominator or meaning |
| --- | ---: | --- |
| Monthly decisions | 100,000 | All eligible decisions in the modeled workflow |
| Error probability | 0.5% | Incorrect decisions / all decisions |
| High-impact share | 5% | High-impact errors / all errors |
| Timely end-to-end recall | 80% | High-impact errors intercepted before effect / all high-impact errors |
| Expected escapes | 5 | `100,000 × 0.005 × 0.05 × 0.20` |

The result is an expectation. A particular month could have a different count. Neither the table nor its inputs are a deployment benchmark.

## Test sensitivity before arguing over the headline

Holding the assumed error rate and severity mix constant gives 25 expected high-impact errors before intervention:

| Timely end-to-end recall | Expected detections | Expected escapes |
| --- | ---: | ---: |
| 50% | 12.5 | 12.5 |
| 80% | 20 | 5 |
| 95% | 23.75 | 1.25 |

Fractional counts are valid expectations, not observed fractions of incidents. This is sensitivity analysis, not a confidence interval. At 64% end-to-end recall in the two-stage example, expected escapes would be nine.

Before reducing review coverage, ask which input the evidence supports and which remains assumed. A small change in the high-impact mix can overwhelm a small improvement in average accuracy.

## Accuracy and loss answer different questions

Accuracy gives each labeled evaluation item equal weight. Business effects do not carry equal consequences. A misclassified internal note and an incorrect customer entitlement can have the same error indicator and very different recovery needs.

For a per-decision model with mutually exclusive outcome categories:

```text
Expected loss = Σ P(outcome category j) × E[loss | category j]
```

If categories overlap, summing them can count the same loss twice. If several actions belong to the same customer incident, model that shared exposure rather than pretending the actions are independent. Report consequence bands, recovery assumptions and uncertainty separately from the expected incident count.

A modeled loss avoided is not automatically realized financial benefit. The baseline, control costs and counterfactual need evidence. For elapsed waiting and released staff capacity, the companion [3-Minute Decision article](https://www.linkedin.com/pulse/3-minute-decision-took-3-weeks-ship-aditya-singh-kmejc/) treats those distinctions explicitly.

## Measure the cases the control did not surface

An evaluation using only alerts cannot estimate how many errors escaped. It samples the detector's own findings.

Build a decision register containing the eligible population, time, risk tier, policy/model versions, routing result, reviewer decision, intervention time and eventual adjudication. Keep protected source evidence under controlled access rather than copying customer records into an analytics export.

Then sample both reviewed and unreviewed decisions. Stratify by risk tier and other material differences, select randomly within strata, and retain each item's inclusion probability. Have qualified reviewers assess the outcome against a written rubric; independently adjudicate disagreements and record unresolved labels. Where practical, blind the adjudicator to the original system decision.

A design-weighted descriptive estimate can use inverse inclusion weights `wᵢ = 1/πᵢ`:

```text
Estimated timely recall = Σ wᵢ × I(high-impact error intercepted in time)
                         / Σ wᵢ × I(high-impact error)
```

This ratio estimate needs uncertainty appropriate to the actual sampling design. Do not apply a simple unweighted binomial interval to clustered, unequally sampled customer decisions and claim equivalent precision. Confirmed incidents collected outside the probability sample remain important evidence, but must not be mixed into the estimator without a defined inclusion/deduplication rule.

For a genuinely independent simple binomial sample, Wilson or exact intervals can communicate uncertainty better than an unsupported point estimate, especially with few failures. [NIST confidence-interval guidance](https://www.itl.nist.gov/div898/handbook/prc/section2/prc241.htm).

One deliberately simplified calculation shows why “we saw none” is weak evidence. With zero observed failures in 100 independent trials, the one-sided 95% exact upper bound is `1 − 0.05^(1/100)`, approximately **2.95%**. That is a bound on the trial-level probability under the stated model, not on the size of any future loss. A deployment with dependent events needs a different design.

If adjudication finds no high-impact errors, report recall as **not estimable**, not 100%. State the sample size, observed events and uncertainty. Choose the next sample using a precision/risk requirement rather than copying a fixed audit percentage.

## Seven measures with explicit denominators

| Measure | Definition and boundary |
| --- | --- |
| Review coverage | Reviewed decisions / eligible decisions, by risk tier and window |
| High-impact timely recall | Adjudicated high-impact errors intercepted before effect / estimated high-impact errors in the eligible population |
| False-accept rate | Reviewer-approved unacceptable decisions / adjudicated unacceptable decisions presented to review |
| False-reject rate | Reviewer-rejected acceptable decisions / adjudicated acceptable decisions presented to review |
| Validated override precision | Overrides upheld by adjudication / adjudicated overrides; show how many await adjudication |
| Containment and recovery time | Detection-to-containment and detection-to-recovery distributions, plus the age/count of unresolved cases |
| Residual expected loss | Estimated remaining loss per 1,000 eligible decisions, with assumptions/range and review minutes per 100 decisions |

The false-accept definition above is different from “unacceptable outcomes among all approvals.” Both can be useful, but they answer different questions. Do not change denominators while comparing teams or releases.

Report median and p95 times only when there are enough observations to interpret them. Do not remove unresolved incidents from the dashboard simply because they have no completed recovery duration; show their age alongside completed-case statistics.

## Route review by consequence and ability to intervene

A low-consequence, reversible workflow may support bounded automated execution with sampling and an appeal path. A material but recoverable workflow may require risk-based routing, post-action sampling and recovery service levels. High-consequence or difficult-to-reverse actions need pre-action review with the context, expertise and authority to stop execution; some require dual control.

These are operating design choices. A sales recommendation, pricing exception and regulated decision cannot share an undifferentiated human-review rule. Applicable legal requirements must be assessed separately for the specific system, role and jurisdiction.

Reviewing everything can still fail if the reviewer is overloaded or cannot prevent the effect. Lower review coverage may perform better only if routing, timely detection and sampling evidence support that conclusion. Treat it as a proposition to test, not an argument to remove people.

NIST's AI RMF connects measurement to deployment context and control effectiveness. Its Playbook recommends documenting human oversight, errors, overrides, response time and adjudication. Those resources inform this scorecard; they do not prescribe the numerical assumptions above. [AI RMF Core](https://airc.nist.gov/airmf-resources/airmf/5-sec-core/), [Playbook: Measure](https://airc.nist.gov/airmf-resources/playbook/measure/).

## The release decision

Before expanding autonomy, require the measurement owner to show the eligible population, sampling design, adjudication rubric and unresolved cases. Then review the estimated escape rate with its uncertainty, consequence distribution, review cost and recovery capacity.

The [companion bundle](https://github.com/singhaditya21/Medium/tree/main/linkedin/article-quality-revisions-2026-09-14) includes `test_calculations.py`, which checks the five-escape scenario, two-stage detection example, sensitivity table, waiting-cost examples and zero-failure bound. It validates arithmetic, not the assumed inputs. Run `python3 -m unittest -v test_calculations` in the companion directory.

**Which unreviewed part of your workflow could contain consequential errors that today's dashboard cannot estimate?**
