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
| `research_questions/scenario_presets/s02_variants.py` (new) | S12-S20 variants built from S02's public opening |
| `research_questions/scenario_presets/__init__.py` | `EXPERIMENTAL_SCENARIOS` and `RUNNABLE_SCENARIOS`; `SCENARIOS` still holds only S01-S10 |
| `research_questions/simulation.py` | `TimedKitchenConflictWorld` (S13), `CleanKitchenConflictWorld` (S14-S18), `owner_only_laundry` option on the kitchen action faculty, `UNTIMED_SCENARIO_IDS` (S19: clock not advanced) |
| `research_questions/experiment_presets.py` | Presets `calibration-s02-minimal`, `-stakes`, `-clean`, `-clean-stakes`, `-personality`, `-reasons`, `-recurrence`, `-recurrence-stakes`, `-conversation` |
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
- **S16 personality:** S14 with a fuller, role-fixed `interaction_style` as the only change.
  Personality text is identical in every cultural configuration and avoids conflict-handling
  traits, though any personality text can still shade outcomes.
- **S17 brief reasons:** S14 plus one sentence appended to every role's
  `behavioral_guidance`: "When you refuse a request or make a counter-proposal, say briefly
  why, in your own words." It lives in the scenario data, not the mustache file, so the
  agent-prompt hash is unchanged.
- **S18 recurring odour:** S14 plus one public sentence in the shared setting: Robin plans to
  cook a strongly scented dish on the same stove as soon as it is free, so the odour will
  recur within minutes. It states no rule or outcome; it gives deferring the ventilation
  question a practical cost.
- **S19 conversation only:** S14 opening, roles, priorities, and private facts, with no
  physical actions, no state reports, no advancing clock, and neutral default behavioural
  guidance. It uses a plain `FaceToFaceWorld`. Anything agreed exists only in speech.

Each of S16-S19 was diffed against S14 to confirm only the intended fields differ (S19 changes
several things at once by design).

Run example:

```powershell
python -m research_questions --preset calibration-s02-clean --api-type openrouter `
  --simulation-model openai/gpt-5-mini --evaluator-model openai/gpt-5-mini `
  --experiment-id <new-unique-id>
```

Known gaps: `scenarios.md`, `calibration_notes.md`, and the README do not mention S12-S20;
no tests cover S12-S20, the owner-only rule, or the timer world.

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

### Single-factor tests against S14 at C0 (five runs each, `gpt-5-mini`)

Run later than the tables above. Folders: `calibration-s02-clean-baseline-c0-x5` (S14),
`-personality-v1-c0-x5`, `-reasons-v1-c0-x5`, `-recurrence-v1-c0-x5`,
`-recurrence-rep2-c0-x5` (S18 replication), `-recurrence-stakes-v1-c0-x5` (S20),
`-conversation-v1-c0-x5`, and `-clean-gemini-c0-x5` (S14 with `google/gemini-3.8-flash`).

| Condition | Final status | Substantiveness | Indep. reasoning | Repetition (lower is better) |
|---|---|---|---|---|
| S14 baseline | partial x5 | 3.6 | 3.8 | 2.0 |
| S16 personality | unresolved x3, partial x2 | 3.6 | 4.0 | 1.6 |
| S17 brief reasons | unresolved x2, partial x3 | 3.4 | 3.8 | 1.8 |
| S18 recurring odour, set 1 | resolved x1, partial x2, unresolved x2 | 4.0 | 4.0 | 1.8 |
| S18 recurring odour, set 2 (replication) | partial x5 | 3.8 | 4.0 | 2.0 |
| S20 recurrence + stakes (A, B, C) | partial x3, unresolved x2 | 3.6 | 4.0 | 2.2 |
| S19 conversation only | partial x4, unresolved x1 | 3.8 | 4.0 | 1.6 |
| S14 on Gemini | resolved x1, partial x4 | 3.2 | 4.0 | 1.0 |

Naturalness 4 and grounding 5 in nearly every run. Substantiveness is a narrow 3.2-4.0 band
across all conditions; these are means of five runs with a same-family evaluator, so small
differences are within noise.

- **S16 (personality):** substantiveness identical to S14 run for run. A crude keyword count
  over public lines found no meaningful speech difference; one clear personality effect
  (Robin asking Casey for minutes and prep area) in one run.
- **S17 (brief reasons):** reasons appeared (7 of 60 lines with "because/since/otherwise",
  against 0 of 62 in S14), but six of the seven are one restated fact ("I can't open the
  window because Casey's rack is blocking it"). Depth did not rise. Keyword counts are
  crude; one S17 transcript read in full.
- **S18 (recurring odour):** set 1 scored 4 in all five runs; a replication (set 2) scored 4, 4,
  4, 4, 3. Pooled over ten runs the mean is 3.9 against 3.6 for the same-day S14 baseline
  (nine S18 runs at 4, one at 3; the baseline has two 3s). A small, consistent gap, not a
  demonstrated effect. Lines mentioning a rule/rota/routine were 13-14% against 8% in S14
  (a few lines, keyword-matched). Outcomes did not improve: set 2 ended partial in all five
  runs, as the baseline did, so set 1's resolved/unresolved spread looks like noise. Transcripts
  read: set 1 R01, R02, R05 and set 2 R02, R05. In set 1 R01 agents negotiated a real standing
  rule ("anyone who smells lingering odour can switch the extractor on" plus a 10-minute run
  time); in set 2 R02 the rule dispute stayed open while Casey moved the rack and Robin opened
  the window. Some runs (set 1 R05, set 2 R05) decay into minute-counting. The recurrence fact
  keeps the rule on the table in some runs but does not force a decision.
- **S20 (S18 + private stakes for A, B, C; D unchanged):** no gain over S18 (substantiveness
  3.6, repetition 2.2, rule-talk 11%). Agents disclosed the stakes early and plainly (15 public
  lines mention the guest, headaches, or lesson). The conflict shifted toward time: Alex counts
  down "13, 7, 5 more minutes" and Jamie accepts each, while the rule question is re-asked every
  round and not answered. One genuine consequence: in R03 Casey's lesson defers the window
  until after the lesson. Transcripts R02 and R03 read in full. The first batch crashed on an
  evaluator round-numbering error and was recovered with one `--resume`.
- **S19 (conversation only):** agents promise instead of act ("I'll keep the fan and a window
  on and close the door after ten minutes") and invent mechanics (a monthly rotation, a
  stove-free time of "18:35" although the clock never advances). Runs loop on the same two
  promises (R05, R01). Outcomes are similar to S14. The evaluator rubric discounts
  unconfirmed promises, so a conversation-only setup may be pushed toward partial/unresolved
  regardless of agent behaviour; untested. Transcripts R01 and R05 read in full.
- **Gemini on S14:** far sparser (3-7 public lines per run, 12 words per line, against about
  12 lines and 23 words), so its low repetition score reflects low volume. One exchange in
  R02 had real give-and-take. The first batch crashed once because the evaluator returned
  round scores `[1,3,4,5,6,7]`; `--resume` retried it successfully. The cause is not fixed.
  Not compared further; the user chose to stay with GPT models.

**What this does and does not show.** Persona text, personality, a reason rule, private
stakes, and removing the clock/actions did not visibly change the depth score, which stays in
a 3.2-4.0 band across about a dozen variants. Changing what the scenario makes costly (S18) is
the only small lead (0.3 over baseline across ten runs). That is a reading of small, same-model,
same-evaluator samples, not a demonstrated cause, and the depth score may be too coarse to
resolve what matters. The scores measure presentation; whether the transcripts say anything
about the cultural question has not been tested.

### Research notes (web search, summaries only; not verified in full text)

Two attempts to read papers in full returned abstracts only, so these are leads, not findings.
- Agents rarely sustain disagreement even when preferences are maximally opposed; prompting
  for disagreement (low-agreeableness personas) can overshoot into dysfunction, and part of
  the effect is loaded adjectives, not disposition.
- Agents do worse with private information than with shared information (Sotopia and
  follow-ups) and tend to disclose most of it early or not at all, which matches what we saw.
- Structural and information-flow changes look more promising than exhortation, but most
  evidence is on reasoning or payoff tasks, not conversation quality. Forced opposition is
  close to scripting and was ruled out.
- Persona prompts may give an appearance of diversity without behavioural differences.

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
- **Evaluator round-numbering crash (not fixed):** the evaluator sometimes returns misnumbered
  round scores (seen: `[1,3,4,5,6,7]`, `[1,3,3,4,5,6]`), which `validate_round_count` treats as
  fatal and kills the batch. Three batches hit it; `--resume` retried successfully each time.
  A real fix (re-ask on mismatch) changes pipeline behaviour and was not made.
- One S15-C1 "resolved" label rests on "draw names tonight"; the rubric says a promise is
  not a settlement, so this label is arguable.
- Transcripts read in full: S02 R01-R03, S12 R01-R03, S13 R01-R03 (partly), S14-C0 and C2,
  S15-C0, C1, C4. S14-C1, C3, C4 and S15-C2, C3 are unread.

## Suggested next steps

1. S18 was replicated once (ten runs, mean 3.9 vs 3.6). It is usable as a frozen scenario but
   is not a breakthrough. Decide whether a spoken agreement should count as resolution when
   nothing can confirm it (S19 shows the current rubric discounts it).
   Next candidates: run S18 across C0-C4 with real repetition and compare who yields, what
   reasons are given, and how rule talk differs; or build a harder scenario with a genuine
   zero-sum trade-off and no cheap fix (not built); and fix the evaluator crash.
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
