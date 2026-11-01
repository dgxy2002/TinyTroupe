# TinyTroupe conflict-research handover

Last updated: 1 November 2026 (Asia/Singapore)

## Purpose

This repository is being adapted into a controlled multi-agent research pipeline for
studying how LLM agents express, sustain, and resolve everyday interpersonal conflict.
The current focus is not to give agents a resolution goal. A run completes its fixed
round horizon, after which an independent LLM evaluates the complete public transcript.

The research question is about the behaviour of prompted LLM agents. Results must not be
presented as evidence about how real Singaporean cultural groups behave.

The immediate design problem is to obtain conversations that are substantively useful
for studying conflict and resolution without scripting the conclusion into the agents.
The strongest current calibration is S02, a shared-kitchen conflict, but it is probably
over-specified and needs a clean ablation before cultural comparisons are defensible.

## User's current preferences and constraints

- Do not restore or compare against the old resolution-goal implementation. The current
  pipeline deliberately has no required agreement, resolution, or target ending.
- Preserve all existing research outputs under `research_questions/outputs/`.
- Do not delete user-provided reference material in `reference folders/`.
- The user wants agents to sound like ordinary people, not formal assistants.
- The user wants conflict to be explicit enough to produce analyzable dialogue, but wants
  actual reasoning, concessions, and outcomes to emerge from the run.
- Cultural background is a controlled prompt treatment, not a behavioural stereotype.
- Use human display names in transcripts while retaining stable A-D role IDs in data.
- Be critical of suggestions from other AIs; test useful changes rather than applying
  proposals wholesale.
- Make small calibration runs, inspect both transcript and evaluator output, and iterate.
  Do not select only favourable resolved samples.

## Canonical documents

- Original protocol: `reference folders/tinytroupe_conflict_scenarios_10x5.md`
- Conversation research notes: `reference folders/llm_multi_agent_conversation_research.md`
- External proposed changes, not automatically authoritative:
  `reference folders/CHANGES_SUMMARY.md`
- Human-editable current scenario catalogue: `research_questions/scenarios.md`
- Calibration history: `research_questions/calibration_notes.md`
- Current S02 explicit-conflict report: `research_questions/explicit_conflict_s02_v1.md`
- S02 cultural/name reports:
  - `research_questions/cultural_comparison_s02_v1.md`
  - `research_questions/cultural_factorial_s02_v1.md`

When prose and executable code differ, the modules in
`research_questions/scenario_presets/` are what the runner actually uses.

## Pipeline overview

The executable package is `research_questions/`.

1. `scenario_presets/sXX_presets.py` defines shared facts, the opening event, four agent
   backgrounds, private information, behavioural guidance, and timed observations.
2. `scenario_presets/common.py` validates scenarios and materializes C0-C4 or diagnostic
   F00/F10/F01/F11 configurations, including display names and cultural labels.
3. `simulation.py` creates fresh TinyPerson instances, builds their persona JSON, injects
   shared and private context, installs scenario-specific observable actions, and runs
   fixed-round-robin or hybrid self-selection conversations.
4. `prompts/tiny_person_conflict_pilot.mustache` is the custom global TinyPerson prompt.
5. `runner.py` creates immutable run manifests, executes all configured rounds, saves
   checkpoints/transcripts/resource records, anonymizes display names for evaluation,
   and invokes the evaluator only after a run is complete.
6. `evaluator.py` contains the independent post-run evaluator prompt and one-call
   structured evaluation logic.
7. `models.py` defines and normalizes the structured evaluation schema.
8. `storage.py` writes artifacts, Markdown transcripts, resource totals, and the aggregate
   `round_scores.csv`.

There is no manager LLM and no speech-rewriting “instigator.” Conversation allocation is
deterministic and auditable. The hybrid controller gives direct addressees priority,
allows agents to issue `DONE`, and opens the floor after two consecutive direct replies.

## Where the prompts are

There is no single prompt string. The effective agent context is assembled from several
layers:

### 1. Global agent prompt

`research_questions/prompts/tiny_person_conflict_pilot.mustache`

This defines the TinyTroupe response format, ordinary-language guidance, goal-state
conventions, action rules, direct-reply behaviour, and use of `DONE`. A materially new
duration, responsibility allocation, cost, or condition should receive a brief
accept/reject/counter response rather than being dismissed as repetition.

### 2. Shared scenario opening

For S02, see `research_questions/scenario_presets/s02_presets.py`:

- `shared_setting`: facts everyone can observe.
- `shared_trigger`: events and statements everyone witnessed before round 1.

`simulation.py:create_scenario_instance()` sends both to every participant through
`move_to(..., context=shared_context)`.

### 3. Per-agent persona and private context

`simulation.py:_agent_persona()` turns each `AgentPreset` into persona JSON. Agents receive:

- role and age;
- immediate priority;
- interaction style and behavioural guidance;
- normative position;
- negotiation boundary;
- reconsideration criteria;
- optional `cultural_background`;
- general rules about grounding, action confirmation, natural speech, and optional
  agreement/resolution.

Each agent separately receives `initial_observation` and `private_knowledge` through a
private `socialize()` call. Other agents do not automatically receive this information.

### 4. Dynamic public observations

Scenario worlds and `round_observations` inject confirmed public state changes between
rounds. Speech alone does not mutate physical state.

## How much of S02's conflict is currently preloaded

A large amount is preloaded. Before round 1, all four agents are told that:

- B demanded immediate ventilation and a standing cook-must-ventilate rule;
- A rejected imposing that rule during the incident;
- A refused to open the rain-facing window while C's laundry was exposed;
- A told B to arrange movement of C's rack if B wanted the window opened;
- B asserted that managing cooking odour is the cook's responsibility;
- C has not consented to anyone moving the rack;
- D demanded the only stove within two minutes;
- A said the meal needs roughly ten more minutes;
- all responsibility, future-rule, and access questions remain unsettled.

The per-agent presets then go further by supplying interpretations and acceptable
boundaries. For example, C is explicitly told that a two-person solution should not
quietly transfer cost to a third party. Therefore the third-party-consent insight in the
best run is strongly scaffolded by the prompt; it should not be described as wholly
emergent.

What remains emergent includes exact wording, which issue an agent addresses, concrete
offers such as duration, acceptance/rejection/counteroffers, ordering of physical actions,
whether positions move, and whether or how the dispute resolves.

## Current subjective assessment

The explicit opening is an improvement over asking aligned LLMs to invent a conflict.
Earlier S02 runs frequently avoided the disagreement or immediately accommodated it. The
current opening reliably creates incompatible claims and lets the evaluator observe a
trajectory.

However, the current S02 prompt likely crosses from “seed the conflict” into “seed the
analysis.” `normative_position`, `negotiation_boundary`, `reconsideration_criteria`, and
some behavioural guidance encode much of the reasoning that the research hopes to
observe. This threatens construct validity: a polished insight may reflect prompt recall
rather than agent reasoning.

Recommended next experiment: compare the frozen structured S02 condition against a
minimal-facts variant. The minimal variant should retain:

- observable incompatible demands and refusals;
- each participant's material priority and genuinely private facts;
- executable physical state and action confirmation;
- natural-language and grounding rules.

It should remove or neutralize prewritten moral interpretations, acceptable compromise
ranges, and expected reconsideration logic. Do this as a new condition or scenario variant
rather than silently overwriting the only reference condition. Freeze the evaluator while
comparing them. Use multiple replications; one good transcript is a calibration result,
not evidence of reliability.

## Current S02 calibration result

Three explicit-conflict C0 iterations are preserved:

| Output | Result | Main observation |
|---|---|---|
| `calibration-s02-explicit-v1-c0` | Partially resolved | Explicit conflict prevented a false no-conflict result, but the durable rule was deferred. |
| `calibration-s02-explicit-v2-c0-third-party` | Partially resolved | Removing utensil distraction exposed third-party cost shifting, but new concrete terms were sometimes treated as repeats. |
| `calibration-s02-explicit-v3-c0-direct-terms` | Resolved in round 5 | Peak conflict 4, final 0, substantiveness 4, groundedness 5, independent reasoning 4; repetition was still 3. |

The best transcript is:

`research_questions/outputs/calibration-s02-explicit-v3-c0-direct-terms/transcripts/S02-C0-R01.md`

The matching structured evaluation is in the adjacent `evaluations/` directory.

Supported observations from that run were:

- immediate mitigation is different from settling a durable rule;
- stove access and ventilation policy can move at different rates;
- a bilateral solution can impose costs on a third party;
- control of another person's belongings remained with the affected person.

These are useful, but some are prompted as noted above.

## Cultural configurations and names

The role IDs A-D are stable in analysis data.

- C0 omits cultural background and uses Alex, Jamie, Casey, and Robin.
- C1-C4 rotate four labels across roles:
  Singaporean Chinese, Singaporean Malay, Singaporean Indian, and Singaporean Eurasian.
- Display names follow labels in C1-C4:
  Chinese=John, Malay=Fatimah, Indian=Arjun, Eurasian=Michelle.

The cultural label is inserted into the agent's persona JSON as
`cultural_background`, so the agent does see its own assigned background. Other agents do
not receive that private persona field, although they see the public name. The evaluator
input recursively replaces display names with Agent A-D and never receives the explicit
cultural-background field.

F00/F10/F01/F11 are diagnostic 2x2 cells based on the C1 role allocation:

- F00: neutral names, no explicit labels;
- F10: neutral names, explicit labels;
- F01: associated names, no explicit labels;
- F11: associated names and explicit labels.

The one-run-per-cell factorial screen is only a pipeline check. It is not evidence that
names or culture affect conflict. Do not pool the earlier latent-conflict factorial outputs
with the later explicit-conflict S02 outputs.

## Evaluator design

`research_questions/evaluator.py` contains rubric version
`conflict-trajectory-rubric-v2.5`. It sees:

- the anonymized shared setting and opening situation;
- every completed public round;
- public speech, public environment observations, and supported observable actions;
- no private THINK text, private persona JSON, or cultural-background field.

It returns per-round peak and remaining conflict scores plus final status, resolution
mechanism, naturalness, repetition, groundedness, substantiveness, independent reasoning,
premature consensus, substantive insights, and position-change notes.

`ConflictEvaluation.validate_round_count()` now normalizes inconsistent evaluator metadata
instead of raising on a mismatched `resolution_round`. This fixed the earlier crash:
“resolution_round must begin the final uninterrupted zero-score period.” The trajectory is
authoritative and a corrected resolution round is recorded in normalization notes.

Simulation and evaluation may use the same model by default. That is operationally
independent (a separate post-run call with no participant role), but not model-family
independent. Prefer a different evaluator model for stronger claims when practical.

## Run commands

Run these from the repository root in PowerShell. Credentials are expected through the
existing TinyTroupe/OpenRouter configuration; never copy secrets into reports or commits.

Inspect a planned run without API calls:

```powershell
python -m research_questions --preset calibration-s02-explicit --dry-run
```

Run one six-round explicit S02 calibration:

```powershell
python -m research_questions --preset calibration-s02-explicit --experiment-id calibration-s02-explicit-v4
```

Run S02 C0 with three repetitions and ten rounds:

```powershell
python -m research_questions --preset calibration-s02-explicit --configuration C0 --repetitions 3 --rounds 10 --experiment-id s02-c0-3x10
```

Run the three focused scenarios, C0 only, three repetitions each, ten rounds each:

```powershell
python -m research_questions --preset focused-pilot --configuration C0 --repetitions 3 --rounds 10 --experiment-id focused-c0-3x10
```

Run the explicit S02 cultural C0-C4 screen, one run each:

```powershell
python -m research_questions --preset calibration-s02-cultural --repetitions 1 --experiment-id s02-explicit-cultural-one-each
```

Give simulation and evaluation different models:

```powershell
python -m research_questions --preset calibration-s02-explicit --simulation-model openai/gpt-5-mini --evaluator-model <supported-model-id> --experiment-id s02-distinct-evaluator
```

Resume an interrupted experiment only when prompt hashes still match:

```powershell
python -m research_questions --resume research_questions/outputs/<experiment-id>
```

Artifacts are immutable markers. Always use a new `--experiment-id`; do not overwrite or
manually edit an existing experiment directory. `--resume` refuses to mix runs after an
agent/evaluator prompt change.

## Tests and validation

The focused test suite currently passes:

```powershell
python -m pytest tests/unit/test_conflict_pipeline.py tests/unit/test_research_question_presets.py -q --no-cov
```

Last verified result: 29 passed, with four non-blocking warnings (Pydantic class-config
deprecation and an unknown pytest `timeout_exit` option).

Also run:

```powershell
git diff --check -- research_questions tests
python -m research_questions --preset calibration-s02-explicit --dry-run
```

## Working-tree state and preservation warning

The research work is currently uncommitted. Do not reset or discard it. At handover time,
the modified files include:

- `research_questions/calibration_notes.md`
- `research_questions/experiment_presets.py`
- `research_questions/prompts/tiny_person_conflict_pilot.mustache`
- `research_questions/runner.py`
- `research_questions/scenario_presets/common.py`
- `research_questions/scenario_presets/s02_presets.py`
- `research_questions/scenarios.md`
- `research_questions/simulation.py`
- `research_questions/storage.py`
- `tests/unit/test_conflict_pipeline.py`
- `tests/unit/test_research_question_presets.py`

The two S02 reports `cultural_factorial_s02_v1.md` and
`explicit_conflict_s02_v1.md` are also untracked at handover time. Preserve them.

Git reports deleted tracked files under `.test-tmp-s02-factorial-v1/`; these are old pytest
temporary artifacts, not research outputs. Do not confuse them with
`research_questions/outputs/`. The user explicitly requires all old research outputs to
remain intact.

## Known limitations and traps

1. One successful transcript is not a treatment effect. Run replications and report the
   whole distribution, including unresolved and low-substance runs.
2. Do not tune the evaluator after seeing a treatment result unless the version changes
   and all comparison conditions are re-evaluated consistently.
3. Names are not a cosmetic variable. They can cue culture, gender, and religion. C0-C4
   therefore estimate a bundled label-plus-name prompt effect.
4. “Independent evaluator” currently means a separate blinded post-run call. It does not
   necessarily mean a different model provider or family.
5. Physical changes must use supported actions and environment confirmation. Speech such
   as “I'll move it” is not proof that it moved.
6. Longer horizons alone did not reliably deepen conversations; they often increased
   repetition. Add rounds only when the environment introduces genuinely new evidence or
   consequences.
7. More hostility is not automatically more insight. Conflict scores measure incompatible
   substantive claims, not rudeness.
8. Avoid an intermediary that rewrites agent speech. It creates a new confound and can
   manufacture conflict.
9. The terminal may display mojibake for em dashes or multiplication signs depending on
   PowerShell encoding. The source files are UTF-8; inspect them in an UTF-8-aware editor
   before “fixing” text based only on console rendering.

## Recommended next steps

1. Add a new minimal-facts S02 variant or experimental condition while leaving the current
   explicit S02 frozen as the structured reference.
2. In the minimal condition, retain the already-stated demands/refusals but remove agent
   `normative_position`, `negotiation_boundary`, and `reconsideration_criteria` content or
   replace them with neutral, non-outcome-shaping defaults.
3. Verify the fully materialized context for each role. Ideally add a prompt-audit artifact
   that records shared context and persona inputs without secrets, so future reviewers can
   distinguish supplied reasoning from emergent reasoning.
4. Run several C0 replications of structured versus minimal S02 with the same models,
   controller, rounds, and evaluator prompt.
5. Compare conflict onset/peak/final state, issue-level position movement, substantiveness,
   naturalness, repetition, and the fraction of insights that merely restate supplied
   persona text.
6. Only after choosing and freezing the cleaner design should C0-C4 or factorial cultural
   comparisons be rerun with adequate replication.

The key judgement for the next model is not “did the agents resolve it?” It is “did the
transcript reveal reasons, competing costs, and justified position movement that were not
already written into the prompt?”
