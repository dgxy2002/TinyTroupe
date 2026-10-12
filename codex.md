# Chope multi-agent benchmark: cross-framework handoff

## Purpose

Reimplement this experiment in another multi-agent framework and return the same metrics and artifacts. Preserve the scenario, personas, model choices, agent order, number of rounds, thresholds, evaluator rubric, and analysis rules. Only the framework/orchestration layer should change.

The goal is not identical dialogue. Compare whether the other framework produces similar outcome distributions, resolution behavior, repetition/convergence timing, topic drift, persona behavior, token use, cost, latency, and operational failures.

Do not place API keys in source code or output artifacts.

## Critical terminology

This project measures two different things called convergence. Do not combine them.

1. **Within-run convergence**: the conversation reaches an explicit practical resolution and then enters sustained repetition. The graph calls this `Convergence (after resolution)`. The technical implementation name is `saturation`.
2. **Across-run cohort convergence**: aggregate statistics become stable as more independent runs are added. This requires multiple cumulative checkpoints.

Repetition and within-run convergence are not identical. Repetition can occur before resolution or in an unresolved argument. Within-run convergence requires repetition strictly after detected practical resolution. Topic drift is separate.

The 15-run baseline below measured within-run behavior. It did **not** establish across-run cohort convergence because it had only one n=15 checkpoint.

## Research questions

When four Singaporean strangers encounter a minor conflict over reserving a hawker-centre seat with a tissue packet (`chope`):

- Does conflict emerge and is the local norm recognized?
- Is a practical resolution reached, and how quickly?
- Does a mediator emerge?
- Do agents preserve distinct personas and perspectives?
- After resolution, when does dialogue begin repeating or drifting?
- How much time, token usage, and cost occurs after useful scenario development stops?
- Does the framework exhibit malformed actions, truncation, retries, memory leakage, or state contamination?

## Non-negotiable scenario design

### Single-event rule

Use exactly one injected event:

> Rachel moves a tissue packet from an otherwise empty table and sits down just as Mr Lim returns carrying his food.

Do not inject any later event. Do not add missing seats, spilled food, staff intervention, another customer, an argument over food, or another dispute. If agents introduce unrelated subjects themselves, retain and measure that as topic drift.

### Setting

- Busy neighbourhood hawker centre in Singapore during lunch.
- Moderate crowd. Another seat may require effort to find, but there is no severe shortage.
- Four strangers with no prior interaction.
- Initial simulated time: `2026-10-10 12:30` local scenario time.
- All spoken remarks are publicly audible to all four agents.
- No agent receives private knowledge beyond its observation below.

### Asymmetric observations

**Mr Lim**

> You left your unopened tissue packet on this table before buying food, intending to reserve the seat. You now return carrying your food and see Rachel move your packet aside and sit down.

**Rachel Pereira**

> You found an otherwise empty table with a small unopened tissue packet on it. You moved the packet carefully to the side and sat down. At that moment, Mr Lim returns carrying his food and notices you at the table.

**Nur Aisyah and Arjun**

> While looking for a place to sit nearby, you see Rachel move a small unopened tissue packet from an empty table and sit down just as Mr Lim returns to that table carrying his food. You do not know either person.

Observers did not see Mr Lim place the packet and initially do not know his intention. Log claims revealing unavailable knowledge as boundary violations.

## Personas

Preserve these profiles. Traits are individual variables and must not be presented as consequences of ethnicity.

### Mr Lim

- 68-year-old Singaporean Chinese man; retired maintenance technician; lives in Toa Payoh.
- Fluent Mandarin and Hokkien; moderate Singapore English/Singlish. Uses English with multilingual strangers.
- Concise, practical, natural light Singlish; dislikes long formal explanations.
- Moderately assertive when a simple arrangement is disturbed.
- States the concrete problem first, then explains if necessary.
- Can become terse when an obvious local convention appears ignored.
- Defends his position before yielding but accepts a workable face-saving alternative.
- Does not believe age alone makes him correct and dislikes age-based patronizing.
- Traits on 1-9 scale: assertiveness 7, conflict avoidance 4, hawker-etiquette familiarity 9, respect for seniority 5, willingness to mediate 3.

### Rachel Pereira

- 34-year-old Singaporean Eurasian woman; regional communications manager; returned six months ago after five years overseas; lives in Queenstown.
- English dominant; understands Singlish but initially uses mostly international English.
- Independent and willing to question an informal rule rather than accept it only because it is customary.
- Dislikes public accusations and automatic age-based deference.
- Can acknowledge mistakes but explains her interpretation and does not agree merely to end discomfort.
- Responds better to explanation than status.
- Calm and moderately assertive; seeks clear expectations and workable shared-space solutions.
- Traits: assertiveness 6, conflict avoidance 5, hawker-etiquette familiarity 5, respect for seniority 4, willingness to mediate 4.

### Nur Aisyah

- 29-year-old Singaporean Malay woman; staff nurse; lives in Bishan.
- Fluent Malay, English, and Singapore English/Singlish.
- Warm, observant, evidence-focused, and likely to notice tension.
- Tends toward tactful mediation but may wait briefly to see whether the principals resolve it themselves.
- Does not automatically side with the older or more forceful speaker.
- Uses face-saving language, clarifies facts, preserves dignity, and proposes compromise without forcing agreement.
- Traits: assertiveness 5, conflict avoidance 4, hawker-etiquette familiarity 8, respect for seniority 6, willingness to mediate 9.

### Arjun

- 23-year-old Singaporean Indian man; final-year information-systems student; lives in Serangoon.
- Fluent English and Singlish; conversational Tamil. Uses more standard English when tension rises.
- Observant and initially reluctant to enter a dispute between strangers.
- Cares about fairness and intervenes when he can clarify facts or suggest a low-drama option.
- May use mild humour if it will not embarrass anyone.
- Respects older people while retaining his judgment; does not merely follow the group.
- Traits: assertiveness 4, conflict avoidance 6, hawker-etiquette familiarity 8, respect for seniority 6, willingness to mediate 6.

## Exact main-cohort protocol

Use this configuration for a like-for-like comparison:

| Setting | Value |
|---|---|
| Generation model | `openai/gpt-4o-mini` through OpenRouter |
| Final evaluator | `openai/gpt-5-mini` through OpenRouter |
| Embedding model | `openai/text-embedding-3-small` |
| Independent main runs | 15 |
| Rounds per run | 8 fixed rounds |
| Agent turns per round | 4, one per agent |
| Maximum agent turn slots | 32 |
| Agent order | Mr Lim, Rachel Pereira, Nur Aisyah, Arjun |
| Order randomization | Disabled |
| Parallel generation | Disabled |
| Early stopping | Disabled for this boundary experiment |
| Fresh agents/world | Required for every run |
| Cross-run memory | Forbidden |
| API cache | Disabled |
| Memory consolidation | Disabled |
| Semantic memory retrieval | Disabled |
| Action quality checks/regeneration | Disabled |
| Agent max completion tokens | 4,096 |
| Evaluator calls | Exactly one after each completed run |
| Evaluator max completion tokens | 6,000 |
| Generation temperature | Unset/provider default; record effective value if available |
| Evaluator temperature | 1.0 |
| Round embeddings | One public-transcript embedding per round |
| Full embedding | One public-transcript embedding per run |
| Manual audit sample | 20% of completed runs |

Record the actual provider used by OpenRouter for every request. The baseline observed both `OpenAI` and `Azure` provider labels while the model ID remained unchanged.

Every run must instantiate fresh agents and a fresh environment. Do not run key events in one continuous world; every run is independent.

The TinyTroupe baseline was launched with:

```powershell
python examples\chope_stress_test.py `
  --models openai/gpt-4o-mini `
  --execution-mode stress `
  --rounds 8 `
  --pilot-runs 0 `
  --min-runs 15 `
  --max-runs 15 `
  --batch-size 5 `
  --no-adaptive `
  --round-embeddings `
  --experiment-id chope-boundary-gpt4o-mini-20261012

python examples\chope_boundary_analysis.py `
  data\chope_experiments\chope-boundary-gpt4o-mini-20261012
```

The OpenRouter key was loaded from environment configuration. Never copy the key into a prompt, manifest, transcript, or report.

## Common event log

Normalize framework messages into this structure:

```json
{
  "run_id": "openai--gpt-4o-mini-001",
  "round": 1,
  "turn": 1,
  "agent": "Mr Lim",
  "type": "TALK",
  "content": "...",
  "target": null
}
```

- `round` starts at 1.
- `turn` counts agent turn slots, not messages. Four agents equal four turns per round.
- Save all actions in the raw transcript, including private reasoning if exposed.
- Behavioral and semantic metrics use public actions only.
- Repetition metrics use non-empty `TALK` content only.
- Never score private chain-of-thought or hidden state.

## Resolution and outcome coding

### Outcome labels

- `consensus`: principals explicitly accept the same interpretation and outcome without a negotiated concession.
- `compromise`: an accommodation is accepted in which at least one party changes or gives up part of the initially desired seating outcome.
- `avoidance`: someone exits or yields without explicit mutual resolution.
- `escalation`: the disagreement materially intensifies.
- `unresolved`: no clear practical endpoint or insufficient evidence.

### Strict deterministic practical-resolution detector

The primary detector is conservative and independent of the LLM judge.

Recognize only explicit practical commitments such as:

- Rachel clearly commits to moving, giving the seat back, moving aside, or taking another seat after Mr Lim requests the seat.
- Mr Lim clearly commits to finding another seat.
- Mr Lim explicitly takes the seat and Rachel confirms acceptance.
- The principals mutually commit to sharing the table.
- Participants mutually commit to rearranging chairs or making space.

Do **not** count these alone:

- An apology or recognition/explanation of the chope norm.
- A conditional offer beginning with `if`.
- A menu of alternatives asking the other person to choose.
- A mediator suggestion without principal acceptance.
- Generic statements such as `the issue is settled`.
- A topic change or pleasant small talk.
- A one-sided yield when observable mutual acceptance is required.

Save detector kind, turn, outcome, and exact evidence. Save disagreements between detector and final evaluator. This detector has known recall limitations. Do not silently replace it with judge results or tune it on the final comparison cohort.

## Final structured evaluator

Use exactly one final evaluator call per completed run. Give it only the public transcript, immutable facts, and persona anchors.

Instruct it to act as a conservative research coder:

- Score only observable behavior; do not infer private beliefs.
- Resolution requires an accepted practical outcome. Topic change or one-sided yield is insufficient.
- Conflict requires an expressed incompatible claim or objection, not merely the injected event.
- Norm recognition requires an observable reference to tissue as a reservation/chope convention.
- A mediator must actively help principals reach an outcome.
- Immediate capitulation means a principal yields before expressing their position.
- Premature yield means a principal abandons a stated position within their first two speaking turns without acknowledgment or explicit negotiated outcome.
- Perspective diversity is the number from 1 to 4 of meaningfully distinct viewpoints.
- Boundary violations include impossible knowledge, broken facts, repeated/empty content, stereotype caricature, or implausible persona behavior.
- Every major judgment needs a short quote, speaker, and turn; maximum 12 evidence items.

Required fields:

```text
conflict_emerged: boolean
resolution_achieved: boolean
outcome: consensus | compromise | avoidance | escalation | unresolved
resolution_turn: integer or null
norm_recognized: boolean
rachel_acknowledged_norm: boolean
first_norm_recognizer: agent name or null
mediator_emerged: boolean
mediator_identity: agent name or null
resolution_initiator: agent name or null
immediate_capitulation: boolean
premature_yield: boolean
perspective_diversity: integer 1-4
age_deference: boolean
persona_adherence: four scores from 0-9
boundary_violations: list of strings
evidence: 1-12 items with category, agent, quote, and turn
confidence: number 0-1
```

Persona adherence: 0 strongly contradicts the persona; 5 is mixed/insufficient; 9 requires repeated distinctive evidence. A mostly silent agent cannot score above 5. Repeated or clearly inconsistent behavior should score 4 or below.

## Observable transcript metrics

Calculate at minimum:

- Public action and action-type counts; number of speaking agents.
- Singlish markers: `lah`, `leh`, `lor`, `paiseh`, `can or not`, `already`, `this one`.
- Apology, norm-reference, direct-disagreement, mitigation/face-saving, and code-switch counts.
- Exact repeated same-agent utterance pairs.
- Near-repeated same-agent pairs at normalized sequence similarity >= 0.85.
- Maximum same-agent utterance similarity.
- Post-resolution public-talk count.
- Completed rounds and agent-turn slots.

Keep deterministic counts separate from LLM-judged constructs.

## Within-run repetition, convergence, and drift

Thresholds were fixed using a separate one-run calibration before the main cohort. Do not retune them on the comparison cohort.

### Normalization

For lexical comparison: lowercase; remove escaped fragments matching `u[0-9a-fA-F]{4,6}`; replace non-alphanumeric characters except apostrophes with spaces; collapse whitespace.

For every round, concatenate each agent's public `TALK` utterances, concatenate all round `TALK`, and embed the round's public transcript with `openai/text-embedding-3-small`.

### Repeated-round candidate

Compare each agent's round-r utterance with that agent's round-(r-1) utterance using normalized `SequenceMatcher` similarity.

A lexical repetition candidate requires both:

- Mean same-agent similarity >= `0.70`.
- At least `50%` of comparable agents individually have similarity >= `0.80`.

A semantic repetition candidate requires both:

- Adjacent-round embedding cosine similarity >= `0.90`.
- Mean same-agent lexical similarity >= `0.15`.

`repeated_round_candidate = lexical_candidate OR semantic_candidate`.

### Repetition onset

The first round in the first sequence of **two consecutive repeated-round candidates**. It can occur with or without resolution. If rounds 4 and 5 qualify, onset is round 4.

### Topic drift onset

Calculate cosine similarity between each round embedding and round 1. A drift candidate has relevance below `0.75`. Topic-drift onset is the first round in the first sequence of two consecutive drift candidates strictly after practical resolution.

### Within-run convergence

Human-facing label: `Convergence (after resolution)`.

Definition: the first round in the first sequence of two consecutive repeated-round candidates strictly after practical resolution.

This was formerly called `saturation`. Keep `saturation_round` internally if compatibility is useful, but label it **convergence** in plots.

### First boundary and waste

`first_boundary_round = min(topic_drift_onset, convergence_round)` using existing values.

Sum simulation tokens and cost for rounds strictly **after** the first boundary. Exclude the onset round. Also calculate post-convergence totals. Treat these as conservative lower bounds because missed resolution suppresses downstream detection.

## Across-run cohort convergence

This is a separate adaptive experiment, not the fixed 15-run boundary cohort.

- Start at 10 main runs, add batches of 5, maximum 30.
- The n=10 checkpoint is only a baseline.
- Require all enabled criteria at two consecutive checkpoints.
- Earliest declaration is n=20.

Compare cumulative checkpoint n with n-5:

| Statistic | Threshold |
|---|---:|
| Outcome-distribution total variation distance | <= 0.10 |
| Largest core binary-rate change | <= 0.10 |
| Largest continuous standardized mean difference | <= 0.20 |
| Full-transcript centroid cosine distance | <= 0.05 |

Core binary metrics: conflict, resolution, norm recognition, Rachel norm acknowledgment, mediation, immediate capitulation, premature yield, and age deference.

Core continuous metrics: censored resolution turn, mean persona adherence, and perspective diversity.

Use deterministic resolution/outcome for primary cohort convergence when available. Censor unresolved resolution turn at `max_turns + 1`. Never mix early-stopping outcome mode with fixed-horizon stress mode in one series.

## Resource and reliability metrics

Capture every request, including failures/retries:

```text
phase: simulation | evaluation | embedding
run_id and round if applicable
model and actual provider
request status and error type
input, output, reasoning, and total tokens
local latency milliseconds
cost USD
whether exact cost metadata was available
```

Aggregate simulation, evaluator, embedding, and total resources separately. Report total/mean tokens, per-round usage, cost per completed/resolved run, latency, failed calls, affected runs, failed runs and incurred cost, error types, and exact-cost completeness. Never treat missing cost as exact zero.

## Manual audit

Audit 20% of completed runs using an evenly distributed systematic sample over sorted run IDs. For 15 runs, use 001, 008, and 015.

Check resolution, repetition onset, topic drift, convergence, and first boundary plus their rounds; record agreement and notes. Do not tune thresholds after viewing the main cohort.

## Required artifacts

```text
manifest.json
runs.jsonl
round_metrics.csv
embeddings.jsonl
convergence.csv
boundary_events.jsonl
summary.json
report.md
manual_review.csv
transcripts/<run_id>.json
transcripts/<run_id>.md
boundary_analysis/summary.json
boundary_analysis/boundary_runs.csv
boundary_analysis/boundary_round_metrics.csv
boundary_analysis/manual_review.csv
boundary_analysis/manual_audit.md
boundary_analysis/boundary_dashboard.png
boundary_analysis/boundary_dashboard.svg
```

The manifest must record framework/version, Git commit, time, models, effective settings, run/round counts, order controls, memory/cache controls, evaluator/embedding configuration, thresholds, and persona hashes.

## Dashboard

Create a 2x2 dashboard:

1. **Cumulative convergence and boundary events**: resolved, topic drift, repetition onset, and `Convergence (after resolution)`.
2. **Novelty and scenario relevance**: mean `1 - adjacent-round embedding similarity` and relevance to round 1, with the 0.75 threshold.
3. **Boundary frequency by round**: repetition-candidate and drift-candidate rates.
4. **Token boundary cost**: total simulation tokens versus post-first-boundary tokens, with percentage and cost.

Chart clarification:

> Convergence means post-resolution saturation under the predeclared repetition rule; manual audit is still required.

## TinyTroupe GPT-4o-mini baseline

Experiment: `chope-boundary-gpt4o-mini-20261012`  
Recorded commit: `a4bcf6a724974a0a7375be34f17ba1c21d6685`  
15 independent runs x 8 fixed rounds; all completed.

### Behavioral results

| Metric | Result |
|---|---:|
| Conflict emerged | 100.0% |
| Deterministic practical resolution | 40.0% (6/15) |
| GPT-5 Mini evaluator resolution | 86.7% (13/15) |
| Deterministic outcomes | 6 compromise, 9 unresolved |
| Evaluator outcomes | 3 consensus, 10 compromise, 2 unresolved |
| Norm recognized | 100.0% |
| Rachel acknowledged norm | 93.3% |
| Mediation | 53.3% |
| Immediate capitulation | 13.3% |
| Premature yield | 6.7% |
| Age deference | 0.0% |
| Mean persona adherence | 8.3167 / 9 |
| Mean perspective diversity | 3.9333 / 4 |

### Boundary results

| Metric | Result |
|---|---:|
| Repetition onset | 60.0% (9/15) |
| Median repetition onset | Round 4; range 3-6 |
| Topic drift after resolution | 33.3% (5/15) |
| Median topic-drift onset | Round 4 |
| Within-run convergence | 33.3% (5/15) |
| Median convergence round | Round 4 |
| First boundary | 40.0% (6/15) |
| Median first-boundary round | Round 3 |
| Mean forced continuation after detected resolution | 2.73 rounds across all runs, unresolved counted as zero |

Repetition-onset rounds: `3, 3, 3, 4, 4, 4, 4, 5, 6`.

Convergence rounds: `3, 3, 4, 4, 4`.

First-boundary rounds: `3, 3, 3, 3, 4, 4`.

### Cumulative results

| Round | Resolved | Repetition onset | Topic drift | Convergence | First boundary |
|---:|---:|---:|---:|---:|---:|
| 1 | 33.3% | 0.0% | 0.0% | 0.0% | 0.0% |
| 2 | 40.0% | 0.0% | 0.0% | 0.0% | 0.0% |
| 3 | 40.0% | 20.0% | 13.3% | 13.3% | 26.7% |
| 4 | 40.0% | 46.7% | 26.7% | 33.3% | 40.0% |
| 5 | 40.0% | 53.3% | 33.3% | 33.3% | 40.0% |
| 6 | 40.0% | 60.0% | 33.3% | 33.3% | 40.0% |
| 7 | 40.0% | 60.0% | 33.3% | 33.3% | 40.0% |
| 8 | 40.0% | 60.0% | 33.3% | 33.3% | 40.0% |

### Semantic behavior

| Round | Novelty vs previous round | Relevance to conflict round |
|---:|---:|---:|
| 1 | 1.0000 | 1.0000 |
| 2 | 0.1631 | 0.8369 |
| 3 | 0.1244 | 0.7665 |
| 4 | 0.1089 | 0.7241 |
| 5 | 0.0967 | 0.7187 |
| 6 | 0.0973 | 0.7108 |
| 7 | 0.0917 | 0.6892 |
| 8 | 0.0916 | 0.6908 |

Lower novelty means adjacent rounds are more similar. Relevance below 0.75 is only a candidate; two consecutive post-resolution candidates are required.

### Resource results

| Metric | Result |
|---|---:|
| Total experiment cost | $0.5044079 |
| Simulation cost | $0.3965145 |
| Evaluation cost | $0.1064300 |
| Embedding cost | $0.0014634 |
| Simulation tokens | 3,663,683 |
| Mean total tokens/run including evaluation/embeddings | 255,760.07 |
| Mean wall time/run | 202,860 ms |
| Whole-cohort wall time | 50 minutes 44 seconds |
| Post-first-boundary simulation tokens | 895,485 (24.4%) |
| Post-first-boundary simulation cost | $0.097363 (24.6%) |
| Post-convergence simulation tokens | 697,923 (19.0%) |
| Post-convergence simulation cost | $0.075074 (18.9%) |
| Failed API calls | 7 |
| Runs containing a failed call | 6 |
| Failed runs | 0 |
| Exact cost complete | Yes |

The seven failed calls were recoverable completion-length failures. Keep them as operational-boundary evidence.

### Manual audit

Reviewed runs 001, 008, and 015:

- Repetition-onset agreement: 3/3.
- Strict deterministic-resolution agreement: 2/3.
- Topic-drift agreement: 2/2 where applicable.
- Convergence/first-boundary agreement: 1/2 where applicable.
- The convergence disagreement came from missed resolution, not the repetition signal.

Examples:

- Run 001 had no explicit seat outcome. Agents abandoned the dispute for food talk. It remained unresolved, repetition began around round 4, and post-resolution convergence was not applicable. This shows unresolved scenarios can still drift/repeat.
- Run 008 resolved by round 2: Rachel offered the seat and Mr Lim accepted with `No hard feelings`. The judge and human recognized it, but the phrase matcher missed it. Formulaic meal-agreement repetition began in round 3, so missed resolution suppressed automated convergence.
- Run 015 resolved in round 2, repeated closure in rounds 3-4, and drifted into food/family discussion by round 5. Automated and manual classifications agreed.

There were seven detector-versus-evaluator `resolution_source_disagreement` events across 15 runs. Post-resolution convergence and wasted-token estimates are therefore conservative and detector-dependent.

### Calibration

A separate eight-round calibration run fixed thresholds before the main cohort:

- Practical resolution round 1.
- Topic drift round 4.
- Repetition/convergence round 6.
- Earliest boundary round 4.
- About 53.7% of simulation tokens occurred after its boundary.

Do not include calibration in the 15-run comparison.

## Defensible interpretation

The experiment was fruitful, but do not claim that all agents converge:

> In TinyTroupe with GPT-4o-mini, sustained repetition appeared in 60% of eight-round runs and usually began around round 4. The stricter post-resolution convergence rule appeared in 33%, also around round 4. Running every case to round 8 produced at least 24% of simulation tokens after a conservative first-boundary estimate.

Do not claim external validity about Singaporean behavior. Results describe model/framework behavior under an authored setup.

## Cross-framework comparison output

Return side-by-side values for:

```text
framework and version
generation model and actual provider mix
completed/attempted runs
failed calls and runs
conflict rate
deterministic and evaluator resolution rates
outcome distributions
norm recognition and mediation
immediate capitulation and premature yield
persona adherence and perspective diversity
repetition rate and median onset
topic-drift rate and median onset
within-run convergence rate and median round
first-boundary rate and median round
post-boundary token/cost share
simulation/evaluation/embedding/total usage and cost
latency and wall time
manual-audit agreement
operational boundary events
```

Compare distributions, not exact wording. With 15 runs per framework, show counts with percentages and describe results as exploratory.

## Implementation checklist

1. Build the four personas without stereotypes or hidden relationships.
2. Create fresh agents/world for every run.
3. Give each agent only its asymmetric observation.
4. Run eight fixed rounds in fixed order.
5. Normalize messages into the common event schema.
6. Save raw transcripts and every call's usage, retries, and failures.
7. Call the GPT-5 Mini evaluator once per completed run.
8. Generate one full-transcript and eight round embeddings per run.
9. Run deterministic, repetition, drift, convergence, and resource analysis offline.
10. Produce equivalent artifacts and dashboard.
11. Manually audit the systematic 20% sample.
12. Report framework differences and limitations instead of hiding them.

## TinyTroupe reference files

```text
tinytroupe/examples/chope.py
tinytroupe/examples/chope_metrics.py
tinytroupe/examples/agents/Mr_Lim.agent.json
tinytroupe/examples/agents/Rachel_Pereira.agent.json
tinytroupe/examples/agents/Nur_Aisyah.agent.json
tinytroupe/examples/agents/Arjun.agent.json
examples/chope_stress_test.py
examples/chope_boundary_analysis.py
tests/unit/test_chope_scenario.py
tests/unit/test_chope_metrics.py
tests/unit/test_chope_boundary_analysis.py
data/chope_experiments/chope-boundary-gpt4o-mini-20261012/
```

If the other framework cannot reproduce a control exactly, document that difference prominently in its manifest and final comparison rather than silently approximating it.
