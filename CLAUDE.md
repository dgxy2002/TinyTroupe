# CLAUDE.md

Working notes for the conflict-simulation research in `research_questions/`. Read
`reference folders/handover.md` first; this file records what was added after it and what
the calibration runs showed. Nothing here is evidence about real cultural groups.

## Research constraints (from the user)

- Agents get **no resolution goal**, no required agreement, and no target ending. Conflict
  is set by the scenario; settling it is left to the agents. An external LLM evaluator
  judges the transcript after the run.
- Cultural background is a controlled prompt treatment, not a behavioural instruction.
- Never overwrite or delete anything under `research_questions/outputs/` or
  `reference folders/`. Use a fresh `--experiment-id` for every run.
- Keep the frozen S02 (`s02_presets.py`) untouched as the reference condition. New ideas go
  in new scenario variants.
- Report unresolved and weak runs, not only favourable ones. Do not change the evaluator
  after seeing results unless its version changes and all compared runs are re-evaluated.
- Be sceptical of outside suggestions; test them rather than applying them wholesale.

## What was added

All changes are additive and uncommitted. Existing tests (29) still pass; no new tests
were written for the items below.

| File | Change |
|---|---|
| `research_questions/scenario_presets/s02_variants.py` (new) | S12-S15 variants built from S02's public opening |
| `research_questions/scenario_presets/__init__.py` | `EXPERIMENTAL_SCENARIOS` and `RUNNABLE_SCENARIOS`; `SCENARIOS` still holds only S01-S10 |
| `research_questions/simulation.py` | `TimedKitchenConflictWorld` (S13), `CleanKitchenConflictWorld` (S14/S15), `owner_only_laundry` option on the kitchen action faculty |
| `research_questions/experiment_presets.py` | Presets `calibration-s02-minimal`, `-stakes`, `-clean`, `-clean-stakes` |
| `research_questions/runner.py` | Looks scenarios up in `RUNNABLE_SCENARIOS` |

Variants (C0 uses Alex, Jamie, Casey, Robin; roles A-D):

- **S12 "minimal" (really reduced scaffolding):** S02 with the supplied
  `normative_position`, `negotiation_boundary`, and `reconsideration_criteria` replaced by
  the generic defaults in `common.py`. Those defaults and the global prompt template still
  tell agents how reconsideration should work, so this is not "no supplied reasoning". It
  also keeps S02's immediate priorities and action guidance. The preset name is kept for
  continuity with existing output folders.
- **S13 stakes:** S12 plus a private stake per role and a visible stove countdown.
- **S14 clean:** S02 opening with neutral personas. The environment reports only elapsed
  time and confirmed state: it never says a dish is ready and never narrates the odour
  fading. Only Casey can move Casey's rack (this hardcodes "only the owner may ever act" and
  blocks Casey authorising someone else; a permission state would be better). It has no
  authoritative cook-time state, so `RELEASE_STOVE` always reports a "finished dish" and an
  agent can declare itself done.
- **S15 clean + stakes:** S14 plus private stakes (A: guest in ~15 min; B: headaches from
  smells; C: tutoring in ~6 min, extractor hum audible; D: night shift in ~15 min, needs
  ~10 min at the stove).

Run example:

```powershell
python -m research_questions --preset calibration-s02-clean --api-type openrouter `
  --simulation-model openai/gpt-5-mini --evaluator-model openai/gpt-5-mini `
  --experiment-id <new-unique-id>
```

Known gaps: `scenarios.md`, `calibration_notes.md`, and the README do not mention S12-S15;
the `get_scenario` docstring still says S12-S13.

## What the runs showed

All runs: `openai/gpt-5-mini` for both simulation and evaluation (not model-family
independent), six hybrid rounds, evaluator `conflict-trajectory-rubric-v2.5`. Outputs are in
`research_questions/outputs/calibration-s02-*`.

**Three repetitions at C0** (`*-rep3-c0`):

| Condition | Final status | Substantiveness | Repetition (lower is better) |
|---|---|---|---|
| Frozen S02 | resolved, partial, unresolved | 4, 4, 3 | 3, 1, 3 |
| S12 minimal | partial x3 | 3, 4, 4 | 1, 1, 1 |
| S13 stakes | partial x3 | 3, 4, 4 | 2, 1, 1 |

**One screening run per configuration, C0-C4** (`calibration-s02-clean*-v1-c0-c4`):

| Condition | Final status | Substantiveness |
|---|---|---|
| S14 clean | 0 resolved, 3 partial, 2 unresolved | 4, 3, 3, 4, 3 |
| S15 clean + stakes | 1 resolved, 0 partial, 4 unresolved | 4, 4, 3, 4, 4 |

Naturalness and grounding were 4-5 in every run.

### Findings

1. **No clear change in substantiveness was observed in these small screens.** It averages
   about 3.4-3.8 in every condition. Removing scaffolding changed what agents talk about;
   depth did not visibly change. This does not show that persona prompts do or do not drive
   insight.
2. **Run-to-run noise is large.** Three identical frozen-S02 runs ended resolved, partial,
   and unresolved. n=3-5 per condition cannot separate a real difference from chance.
3. **Frozen S02 pre-writes its compromise.** The per-agent `negotiation_boundary` text
   matches the resolved run's final rule almost line for line, so that "resolution" is
   largely supplied.
4. **Observed association, not an effect:** 6 of 10 S14/S15 runs were unresolved, and
   earlier conditions leaned partial. S14 changed many things at once (persona reasoning,
   private facts, timed observations, environment narration, laundry permission, cooking
   completion), S15 added stakes, and the ten runs span C0-C4 with no replication. The
   cause cannot be attributed to removing scripted relief.
5. **Why runs were unresolved** (read in five transcripts; the rest rest on the evaluator's
   stated reasons only):
   - The standing rule ("must the cook ventilate?") was deferred to "later" in all nine
     non-resolved runs. The extractor is a free fix turned on in round 1, so nothing forces
     the rule to be decided.
   - In S15 the stakes make A's ~12-15 minute dish collide with D's 10-minute need, and
     six rounds is only ~10 simulated minutes. That unresolved outcome is partly by
     construction.
   - Without S13's countdown, cook-time estimates drift ("five minutes" repeated).
6. **Stakes help concreteness, not depth.** They produced real trade-offs (A needs 12
   minutes, D leaves in 5) but pulled talk toward minute-by-minute scheduling.
7. **One unscripted idea appeared:** in S15-C1 a weekly "ventilation lead" rota was
   proposed. One run; not a rate.
8. **Removing the owner-only rule on the laundry action produces consent violations.** When
   anyone could `MOVE_LAUNDRY`, Jamie moved Casey's rack unasked in four of six S12/S13
   transcripts read. S14/S15 restrict the action to Casey.

### Current interpretation (a best reading, not a finding)

The limit on insight looks more like the scenario than the persona prompts: a cheap fix
exists and deferring the rule costs nothing, so agents have no reason to argue it out.
Persona and scenario were never varied independently, only one model was used, and
n is small, so this is untested.

## Open issues to check before more runs

- **Duplicate lines in S15-C1 round 6 (verified):** not a recording bug. Arjun emitted the
  same TALK twice in one response, once targeted at John and once at Fatimah. The
  transcript renderer omits targets, so it looks duplicated. Fix: one public TALK per turn
  and show targets in the transcript. The S13 round-5 duplicate was not checked.
- **Casey's missing reply in S14-C0 (verified):** a scheduling artifact, not silence. In
  round 6 the scheduler gave slot 1 to Robin (`open_floor_self_selection`) and slot 2 to
  Alex, and Casey was never selected. The direct-reply streak carried over from round 5.
  The scheduler log does not distinguish "chose DONE" from "never selected".
- **Unmodelled actions counted as real (verified):** in S15-C2 agents discuss a lid, lower
  heat, and stepping out, none of which are actions. Fatimah says "I've put a lid on" and
  the evaluator treats it as a mitigation, so the groundedness score of 5 is too generous.
- **Provenance:** every new manifest records commit `69263cc` (HEAD) although S12-S15 and
  the world mechanics are uncommitted. Manifests hash scenario data and the agent prompt but
  not `simulation.py` or the dirty diff, so these runs are not reproducible from the manifest
  alone. Commit before more runs, or record a diff hash.
- One S15-C1 "resolved" label rests on "draw names tonight"; the rubric says a promise is
  not a settlement, so this label is arguable.
- Transcripts read in full: S02 R01-R03, S12 R01-R03, S13 R01-R03 (partly), S14-C0 and C2,
  S15-C0, C1, C4. S14-C1, C3, C4 and S15-C2, C3 are unread.

## Suggested next steps

1. Give the rule question a reason to be decided now (a cost to deferring, or no free
   fix), without stating any outcome.
2. Fix the timing: longer horizon or shorter cook time so the stove does not decide the
   outcome.
3. Add an evaluator field separating supplied reasoning from new reasoning (a version
   change; re-evaluate all compared runs).
4. Vary one factor at a time and use at least 8-10 repetitions per cell; try a second
   simulation model.
5. Only after a design is chosen and frozen, run C0-C4 or the F00/F10/F01/F11 factorial
   with adequate replication.

## Conventions

- Console output can show mojibake for dashes; source files are UTF-8. Do not "fix" text
  from console rendering alone. Print with `PYTHONIOENCODING=utf-8` when reading evaluator
  text.
- Role IDs A-D are stable in data; display names differ by configuration (C0 neutral;
  C1-C4 follow the background label).
