# CLAUDE.md

Working notes for the conflict-simulation research in `research_questions/`. Read
`reference folders/handover.md` first; this file records what was added after it. Nothing
here is evidence about real cultural groups.

## Research constraints (from the user)

- Agents get **no resolution goal**, no required agreement, and no target ending. Conflict
  is set by the scenario; settling it is left to the agents. An external LLM evaluator
  judges the transcript after the run.
- Cultural background is a controlled prompt treatment, not a behavioural instruction.
- Do not overwrite or delete anything under `research_questions/outputs/` or
  `reference folders/` unless the user explicitly asks. Use a fresh `--experiment-id` for
  every run. (On 2026-11-03 the user explicitly asked for the timed-round output folders to
  be deleted; see "Timer removal".)
- Keep the frozen S02 (`s02_presets.py`) as the reference condition. New ideas go in new
  scenario variants. (The timer text in S02, S04 and S06 was removed at the user's explicit
  request on 2026-11-03; nothing else in them changed.)
- Report unresolved and weak runs, not only favourable ones. Do not change the evaluator
  after seeing results unless its version changes and all compared runs are re-evaluated.
- Be sceptical of outside suggestions; test them rather than applying them wholesale.

## Timer removal (2026-11-03)

The user decided that simulated time between rounds does not suit the live, back-to-back
conversational style being studied. Rounds are now turn order only.

- `run_one_round` no longer passes a time step, and `run_hybrid_round` no longer takes
  `timedelta_per_round`, so the world clock stays at `initial_datetime` for every scenario.
  `UNTIMED_SCENARIO_IDS` and `TimedKitchenConflictWorld` were deleted; S13 now uses
  `KitchenConflictWorld`, and S14-S18 and S20 no longer report elapsed minutes.
- The "Two (more) minutes / Twenty seconds have passed" wording was removed from the round
  observations of S02, S04 and S06 and from the world classes. The state reports and the
  S02 round-2 "dish is ready" line remain. Scenario facts that are not about the clock
  (a ten-minute cook, "within two minutes" demands, private stakes measured in minutes)
  were left alone, and they may now read oddly with no clock.
- Result tables and findings that rested on timed runs were removed from this file and
  from `research_questions/calibration_notes.md`. Git history holds the removed text.
- **Status:** the code compiles, but the unit tests could not be run because `chevron` is
  not installed in the available Python. Two tests were edited to drop timer wording.
  Run the suite before relying on these changes.
- **Output folders:** 43 timed-run folders under `research_questions/outputs/` were deleted
  (all tracked in git, so `git checkout` restores them). Remaining: `calibration-s04-v2-01`,
  `calibration-s04-v2-02-gpt41mini`, `focused-pilot-20261029-021546`,
  `smoke-20261029-021206`, and the S06 folders (`calibration-s06-v1-02-clean`, `-03-clean`,
  `-04-final`).

## What exists

| File | Contents |
|---|---|
| `research_questions/scenario_presets/s02_variants.py` | S12-S20 variants built from S02's public opening |
| `research_questions/scenario_presets/__init__.py` | `EXPERIMENTAL_SCENARIOS` and `RUNNABLE_SCENARIOS`; `SCENARIOS` still holds only S01-S10 |
| `research_questions/simulation.py` | `CleanKitchenConflictWorld` (S14-S18, S20), `owner_only_laundry` option on the kitchen action faculty |
| `research_questions/experiment_presets.py` | Presets `calibration-s02-minimal`, `-stakes`, `-clean`, `-clean-stakes`, `-personality`, `-reasons`, `-recurrence`, `-recurrence-stakes`, `-conversation` |
| `research_questions/runner.py` | Looks scenarios up in `RUNNABLE_SCENARIOS` |

Variants (C0 uses Alex, Jamie, Casey, Robin; roles A-D):

- **S12 "minimal":** S02 with the supplied `normative_position`, `negotiation_boundary`, and
  `reconsideration_criteria` replaced by the generic defaults in `common.py`. Those defaults
  and the global prompt template still tell agents how reconsideration should work, so this
  is not "no supplied reasoning". It keeps S02's immediate priorities and action guidance.
- **S13 stakes:** S12 plus a private stake per role.
- **S14 clean:** S02 opening with neutral personas. The environment reports only confirmed
  state: it never says a dish is ready and never narrates the odour fading. Only Casey can
  move Casey's rack (this hardcodes "only the owner may ever act" and blocks Casey
  authorising someone else; a permission state would be better). There is no authoritative
  cook state, so `RELEASE_STOVE` always reports a "finished dish" and an agent can declare
  itself done.
- **S15 clean + stakes:** S14 plus private stakes (A: guest in ~15 min; B: headaches from
  smells; C: tutoring in ~6 min, extractor hum audible; D: night shift in ~15 min, needs
  ~10 min at the stove). D's stake collides with A's cook time by construction.
- **S16 personality:** S14 with a fuller, role-fixed `interaction_style` as the only change.
- **S17 brief reasons:** S14 plus one sentence appended to every role's
  `behavioral_guidance`: "When you refuse a request or make a counter-proposal, say briefly
  why, in your own words." It lives in the scenario data, not the mustache file.
- **S18 recurring odour:** S14 plus one public sentence in the shared setting: Robin plans to
  cook a strongly scented dish on the same stove as soon as it is free, so the odour will
  recur within minutes. It states no rule or outcome.
- **S19 conversation only:** S14 opening, roles, priorities, and private facts, with no
  physical actions, no state reports, and neutral default behavioural guidance. It uses a
  plain `FaceToFaceWorld`. Anything agreed exists only in speech. It still carries S14's
  stove, ten-minute cook and rain-blocked window, which agents then have to improvise around.
- **S20:** S18 plus private stakes for A, B, C; D unchanged.

Known gaps: the README does not mention S12-S20; no tests cover S12-S20 or the owner-only
rule.

Run example:

```powershell
python -m research_questions --preset calibration-s02-clean --api-type openrouter `
  --simulation-model openai/gpt-5-mini --evaluator-model openai/gpt-5-mini `
  --experiment-id <new-unique-id>
```

## Where the earlier results stand

The earlier calibration runs (S02, S12-S20, S04 and others) all used a 2-minute step and have
been removed, so no result table is kept here. What survives as design guidance, not as
findings:

- Substantiveness stayed in a narrow band across many variants (persona text, personality,
  a reason rule, private stakes, recurrence), and run-to-run noise was large. n of 3-5 per
  condition could not separate a real difference from chance.
- Frozen S02 pre-writes its compromise through the per-agent `negotiation_boundary` text, so
  a "resolution" there is largely supplied.
- A cheap fix (turning on the extractor) lets agents defer the standing-rule question at no
  cost; this looked like the main limit on depth. Untested as a cause.
- Removing the owner-only rule on the laundry action produced consent violations (Jamie
  moving Casey's rack unasked) in most S12/S13 transcripts read; S14+ restrict the action.
- Timed rounds invited minute-counting ("three more minutes") rather than rule negotiation.

### Research notes (web search, summaries only; not verified in full text)

- Agents rarely sustain disagreement even when preferences are maximally opposed; prompting
  for disagreement (low-agreeableness personas) can overshoot into dysfunction, and part of
  the effect is loaded adjectives, not disposition.
- Agents do worse with private information than with shared information (Sotopia and
  follow-ups) and tend to disclose most of it early or not at all.
- Structural and information-flow changes look more promising than exhortation, but most
  evidence is on reasoning or payoff tasks, not conversation quality. Forced opposition is
  close to scripting and was ruled out.
- Persona prompts may give an appearance of diversity without behavioural differences.
- `reference folders/tinytroupe_conflict_strategy_implementation_3oct2026.md` proposes an
  11-strategy conversational taxonomy (ASSERT ... WITHDRAW). Assessed as useful for post-hoc
  annotation, not as a generation-time instruction (that would tell agents what move to
  make). Not implemented.

## Open issues

- **Direct-reply duplicates:** an agent can emit the same TALK twice in one response with
  different targets; the transcript renderer omits targets, so it looks like a duplicate.
  Fix: one public TALK per turn and show targets in the transcript.
- **Scheduler log ambiguity:** it does not distinguish "chose DONE" from "never selected".
- **Unmodelled actions counted as real:** agents describe a lid, lower heat, or stepping out,
  which are not actions, and the evaluator can treat them as mitigations, inflating grounding.
- **Provenance:** manifests record the git commit and hash scenario data and the agent
  prompt, but not `simulation.py` or a dirty diff. Commit before runs, or record a diff hash.
- **Evaluator round-numbering crash (not fixed):** the evaluator sometimes returns
  misnumbered round scores (seen: `[1,3,4,5,6,7]`), which `validate_round_count` treats as
  fatal and kills the batch. `--resume` retried successfully each time. A real fix (re-ask on
  mismatch) changes pipeline behaviour.
- **Spoken agreement:** the v2.5 rubric discounts unconfirmed promises, so a conversation-only
  setup is pushed toward partial/unresolved. Whether an explicit, mutual, concrete spoken
  agreement should count as resolved is undecided; it needs a new evaluator version and
  re-evaluation of every compared run.
- **No natural ending in talk-only runs:** fixed rounds pad with closure ("Let's eat").
  A stopping rule (agents marking themselves done) is not built.

## Suggested next steps

The user's direction is conversation-only, no clock, no physical actions.

1. Rewrite S19 into a clean talk-only scenario: keep the S02 opening, roles and private
   facts, and drop the time-dependent facts (ten-minute cook, stove release, rain-blocked
   window mechanics) that only made sense with a clock and actions.
2. Add an end condition and a new evaluator version with a spoken-agreement rule.
3. Write a post-hoc strategy annotator and run it over new transcripts.
4. Run with 8-10 or more repetitions per cell, and try a second simulation model.
5. Only after a design is frozen, run C0-C4 or the F00/F10/F01/F11 factorial.

## Conventions

- Console output can show mojibake for dashes; source files are UTF-8. Do not "fix" text
  from console rendering alone. Print with `PYTHONIOENCODING=utf-8` when reading evaluator
  text.
- Role IDs A-D are stable in data; display names differ by configuration (C0 neutral;
  C1-C4 follow the background label).
