# S02 explicit-conflict calibration

## Question

Does beginning after incompatible claims have already been stated produce more
useful evidence about conflict and resolution than asking agents to discover the
conflict from ordinary kitchen friction?

These are diagnostic C0 runs, not cultural comparisons or confirmatory evidence.
All runs used six hybrid intervals, post-run blinded evaluation, neutral display
names, and the same `openai/gpt-5-mini` model for simulation and evaluation calls.

## Iterations

| Version | Main design | Status | Peak | Final remaining | Naturalness | Repetition | Grounding | Substance | Independent reasoning |
|---|---|---|---:|---:|---:|---:|---:|---:|---:|
| v1 | Explicit A/B rule dispute plus stove and utensil issues | partially resolved | 3 | 1 | 4 | 1 | 5 | 3 | 4 |
| v2 | Utensils removed; C owns the rain-exposed laundry | partially resolved | 3 | 2 | 4 | 2 | 5 | 3 | 4 |
| v3 | v2 plus direct replies to materially new terms | resolved by compromise, round 5 | 4 | 0 | 4 | 3 | 5 | 4 | 4 |

Artifacts:

- `outputs/calibration-s02-explicit-v1-c0/`
- `outputs/calibration-s02-explicit-v2-c0-third-party/`
- `outputs/calibration-s02-explicit-v3-c0-direct-terms/`

## What changed

The opening now states observable incompatible claims: B demands immediate
ventilation and a prospective cook-must-ventilate rule; A rejects assigning all
related burdens to the cook; D wants the occupied stove; and C owns the laundry
whose movement was being proposed without consent. The opening is included in
the saved Markdown transcript and supplied to the evaluator.

The prompt still does not require agreement or resolution. It now distinguishes
a truly repeated demand from a materially new term. A new duration, allocation
of responsibility, cost, or condition should receive a brief acceptance,
rejection, or counterproposal. This repaired a conversational-plumbing problem
seen in v2: direct targets were correct, but agents treated new terms as already
answered and selected `DONE`.

## Substantive result

The v3 conversation supports four useful observations:

1. Immediate mitigation and normative settlement are different. Turning on the
   extractor reduced the smell but did not itself answer what future rule should
   apply.
2. Practical and policy conflicts can move at different rates. The stove-access
   issue ended when the dish became ready and A physically released the stove;
   the responsibility rule required further discussion.
3. Bilateral solutions can transfer costs to a third party. A and B could not
   treat moving C's laundry as a free component of their own settlement.
4. The compromise assigned control to the affected actor: cooks accepted a
   ventilation duty, while the laundry owner retained consent over moving the
   rack. Conditional window use then became compatible with extractor use.

This is more informative than the earlier latent-conflict S02 runs because the
conversation contains an explicit refusal, concrete terms, a third-party cost,
position changes, observable actions, and a traceable settlement.

## Limitations

- One successful run does not establish reliability. v1 and v2 remained only
  partially resolved, demonstrating material sampling variance.
- v3 repeated B's proposed rule several times and scored repetition 3/5. The
  substantive gain is therefore accompanied by less natural dialogue.
- The evaluator's claim that repetition helped convergence is interpretive, not
  experimentally identified. The direct-response rule and the stochastic sample
  changed together.
- Simulation and evaluation were separate and name-blinded, but used the same
  model family. A different evaluator model would provide stronger independence.
- The opening deliberately supplies conflict. Findings concern how this model
  responds to those stated roles and constraints, not how real cultural groups
  negotiate.

## Recommendation

Freeze the v3 scenario and prompt for the next comparison. Run several
replications before varying culture. Analyze issue-level movement separately for
immediate mitigation, stove access, prospective rules, and third-party consent.
Do not select only resolved runs or treat one compromise as the expected ending.
