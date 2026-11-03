# CLAUDE.md

Working notes for the conflict-simulation research in `research_questions/`. Read
`reference folders/handover.md` first; this file records what was added after it. Nothing
here is evidence about real cultural groups.

## Handoff: start here on a new device (written 2026-11-03)

**State at handoff:** all work below is uncommitted when this was written; the user commits
it. Manifests of every S21-S25 run record commit `9c3f432` (the HEAD *before* these changes),
so those runs are not reproducible from the manifest alone. Commit first, then check
`git diff HEAD~1 --stat` against the file list in "What exists".

**Set up the environment (nothing is installed by default):**
- `.env` is gitignored. Recreate it with the API key. The key the user used is an OpenRouter
  key (`sk-or-v1...`) stored under the name `OPENAI_API_KEY`, which makes `--api-type openai`
  fail with 401. Name it `OPENROUTER_API_KEY` and pass `--api-type openrouter`.
- Python packages missing on a fresh machine: `chevron textdistance python-dotenv pytest-cov
  pytest-timeout llama-index-core llama-index-embeddings-openai llama-index-readers-web
  llama-index-embeddings-azure-openai`. (`pip install -e .` pulls everything but is heavy.)
- Run tests with `python -m pytest tests/unit/test_conflict_pipeline.py
  tests/unit/test_research_question_presets.py -q --no-cov`. 29 pass as of this note.

**Standard run command** (always a fresh `--experiment-id`; models are `openai/gpt-5-mini` for
both simulation and evaluation, so results are same-family, not independent):

```powershell
python -m research_questions --preset calibration-s25-chope-conversation --repetitions 5 `
  --api-type openrouter --simulation-model openai/gpt-5-mini --evaluator-model openai/gpt-5-mini `
  --evaluator-max-completion-tokens 12000 --experiment-id <new-unique-id>
```

**Where the design stands.** The research question is now "given that a resolution happens,
how does it differ by cultural background", on a conversation-only, clock-free, action-free
version of the chope (S04) scenario. S25 is the current candidate, and **it is not ready for a
C0-C4 comparison**: its agreements are thin or built on invented facts (see the S25 x5 section).
Read "Evaluator v2.6 and the S25 x5 batch" before doing anything else.

## Research constraints (from the user)

- **Research question (changed by the user on 2026-11-03):** given that a resolution
  happens, how does it differ by cultural background? Resolution is now an assumption of
  the design, not an outcome. Unresolved endings are no longer a result of interest, so
  resolution rate must not be reported as a finding for resolution-expected scenarios.
- Scenarios are of two kinds and must never be pooled:
  - **Free-resolution** (S01-S21): agents get no resolution goal, no required agreement, and
    no target ending. This was the original constraint.
  - **Resolution-expected** (S22-S25, a non-empty `ScenarioPreset.resolution_expectation`):
    all agents are told, in the same words, that the interaction will end with them having
    settled on some arrangement they can each live with. What the arrangement is, who gives
    way, when, and why are left entirely to the agents. The instruction is part of the
    scenario data, so the manifest's scenario hash records it. The shared prompt's
    "no required agreement" wording is replaced only for these scenarios.
- An external LLM evaluator judges the transcript after the run. For resolution-expected
  scenarios the analysis targets are the content of the agreement, who concedes and what
  they ask in return, the reasons given, and the strategy path to it.
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
- **Status:** two tests were edited to drop timer wording. After installing the missing
  packages the 29 unit tests pass.
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
- **S21 chope, conversation only** (`s04_variants.py`): S04's opening, roles and private
  facts with no actions, no scheduled alternative seat, no state reports, and S04's
  per-role normative positions, boundaries and reconsideration text replaced by the neutral
  defaults. The minute figures (A needs 4, B needs 8, D's meal cools in 6) stay as private
  needs. Free-resolution.
- **S22 chope, resolution expected:** S21 plus `resolution_expectation`, a notice shown
  identically to every agent that the conversation ends with everyone settled on some
  arrangement. It names no arrangement, no one who adjusts, and no reasons. Do not pool
  with S21.
- **S23 chope, resolution expected, no timing:** S22 with every minute figure removed from
  the agents' private facts. A keeps "short break", B keeps "open bowl that could spill",
  D keeps "meal getting cooler". No scenario text states a duration, so any duration is
  proposed by the agents. Same notice as S22.
- **S24 chope, resolution expected, timing-free:** S23 with timing removed from everything
  agents see. Scenario text: "lunchtime" instead of 12:30 p.m., no "short break", priorities
  and A's style stripped of urgency. Shared prompt, only when `ScenarioPreset.timing_free` is
  true: the clock line, the "give me five minutes" example, and the time-estimate guidance are
  dropped. Other scenarios keep all three.
- **S25 chope, resolution expected, speech-only prompt:** S24 plus `ScenarioPreset.conversation_only`.
  The shared prompt drops its physical-action and confirmed-state wording and instead says
  nothing physical happens, whatever is settled exists only in speech and a clear spoken
  commitment counts, answer a proposal instead of repeating your own line, say an agreement
  once and stop, and avoid exact minute counts. Because the scenario also has a resolution
  notice, the "priority is a genuine constraint, don't accept an alternative until its cost is
  addressed" rule is replaced by "a priority has a price, not a wall; you may give up part of it
  when a trade is worth it and ask for something in return" (`priority_rule_open`, set only when
  both `conversation_only` and a resolution notice are present). Two prompt changes are bundled
  on purpose, so a difference from S24 cannot be attributed to just one.

**Strategy menu (all scenarios):** `tiny_person_conflict_pilot.mustache` has a "Choosing a
conversational strategy" section listing the 11 core strategies. Agents begin their private
THINK with `STRATEGY: <NAME>` before any TALK. It is one-stage (label and speech come from
one call), so the label is the agent's reported intent, not a checked classification. Labels
are only in the run JSON (`private_and_public_actions`), not in the public transcript or the
evaluator input. The section cannot currently be switched off, so runs made before it was
added are not comparable with later ones; the manifest records only the prompt hash.

**Resolution-expected switch:** setting `ScenarioPreset.resolution_expectation` drops the
"no required agreement" sentence from the template, the agent persona and the shared context
and shows the notice instead. Empty keeps the original wording.

Known gaps: the README does not mention S12-S20; no tests cover S12-S20 or the owner-only
rule.

Run example:

```powershell
python -m research_questions --preset calibration-s02-clean --api-type openrouter `
  --simulation-model openai/gpt-5-mini --evaluator-model openai/gpt-5-mini `
  --experiment-id <new-unique-id>
```

## First S21/S22 runs (2026-11-03, one run each, `openai/gpt-5-mini` for both roles)

Outputs: `outputs/s21-chope-strategy-v2-c0` and `outputs/s22-chope-resolution-v1-c0`
(`s21-chope-strategy-v1-c0` is a failed 401 run holding only a manifest).

| Run | Final status | Peak/final conflict | Substantiveness | Repetition | Strategy labels |
|---|---|---|---|---|---|
| S21 (6 rounds) | unresolved | 5 / 5 | 3 | 2 | ASSERT 5, DEFEND 2, EXPLAIN_NEED 2, PROPOSE 2, CHALLENGE 1 |
| S22 (8 rounds) | unresolved | 5 / 5 | 3 | 3 | ASSERT 6, DEFEND 6, PROPOSE 2, CLARIFY 2 |

- **The resolution notice did not work.** In S22 no private THINK mentioned settling, an
  arrangement, or the notice, and nobody conceded. The rendered prompt did contain the notice
  and no longer said "no required agreement", so it was delivered but outweighed. A likely
  reason: the shared template still says to treat your priority as a genuine constraint and
  not to abandon it or accept an alternative until its cost is addressed, and A (4 minutes)
  and B (8 minutes) are strictly incompatible with no third option. Untested.
- CONCEDE, ACCEPT, ACKNOWLEDGE, COUNTER_PROPOSE and WITHDRAW were never chosen in either run.
  WITHDRAW would appear as a DONE, which carries no label.
- S22 had grounding trouble the evaluator did not penalise (groundedness 5): Robin and
  Casey repeatedly argue about who is sitting where, with Casey saying "I'm sitting here
  eating, don't take the seat" about the disputed seat; in S21 Alex announces taking the
  seat while Jamie still occupies it. Alex also addressed Jamie as "B" once (role-label leak).
- n=1 per condition. These runs show the pipeline works end to end, not any effect.

**S23 (`outputs/s23-chope-untimed-v1-c0`, 8 rounds, one run):** unresolved, conflict 3-4
throughout (S22 reached 5), substantiveness 3, repetition 3, independent reasoning 4.
Labels: DEFEND 6, ASSERT 5, COUNTER_PROPOSE 3, EXPLAIN_NEED 2, WITHDRAW 1, ACCEPT 1.
- With no numbers given, agents **invented their own**: Jamie asked for "three minutes",
  then "one minute"; Alex answered "30 seconds" in five turns and never moved. Alex's invented
  figure acted as the same hard limit that blocked S22. Jamie's 3 to 1 minute move is the first
  real concession seen in these runs. The evaluator still scored it unresolved: no timing was
  agreed and nothing happened.
- The notice was again never referenced (0 of 18 private THINKs).
- The one ACCEPT is Alex agreeing to keep the chair tucked while holding the 30-second
  ultimatum, so it is acceptance of a side point, not a settlement. Round 8 has two labelled
  THINKs with no public line (Jamie DEFEND, Casey WITHDRAW); presumably they ended in DONE,
  not checked. A WITHDRAW label can therefore appear without speech (the earlier note that it
  would carry no label was wrong).
- Casey, written as reserved and low-intervention, speaks in 5 of 8 rounds as Jamie's
  advocate. Agents call Jamie "she" though nothing gives a gender.

**S24 (`outputs/s24-chope-timing-free-v1-c0`, 8 rounds, one run):** unresolved, conflict a
flat 4 in every round, naturalness 4, repetition 3, groundedness 5, **substantiveness 4,
independent reasoning 4** (best of S21-S24, one run each). Labels: DEFEND 7, COUNTER_PROPOSE 4,
PROPOSE 2, ASSERT 1, CLARIFY 1, CHALLENGE 1. Notice referenced in 0 of 16 private THINKs.
- **Removing every timing cue did not stop durations.** 14 public lines state one. Jamie opened
  with "about five minutes" in round 1 and never moved; Alex said "three minutes", then "four",
  then held four. The gap is one minute and nobody closed it. Alex repeated "I already said
  I'll wait three minutes" near-verbatim in rounds 3, 4 and 5. So the anchoring on a self-stated
  number is a property of the agents, not of the scenario or prompt text. This replaces the
  earlier reading that the supplied numbers caused the standoff.
- Alex conceding from "now" to three and then four minutes, and C proposing that Alex stand, are
  real moves, but nobody accepted anything. Pronoun for Jamie was "they" this time (one run).
- Casey keeps raising the aisle being blocked, which is a genuine third-party cost.

**S25 (`outputs/s25-chope-conversation-v1-c0`, 8 rounds, one run):** the evaluator said
`unresolved` (no mechanism), but the transcript contains a spoken agreement in round 2: Alex
"I'll wait, but please hurry", Jamie "You can have the seat as soon as I'm done". Remaining
conflict fell 3 → 1 → 0 peak. Naturalness 5, repetition 2, groundedness 5, substantiveness 3,
independent reasoning 3, premature consensus no. The evaluator's reason: B "only promised to
vacate later" and no action occurred, i.e. the v2.5 rule that discounts unconfirmed promises.
For the current research question this run counts as resolved in speech, so the evaluator is
now what blocks reading these runs; changing it needs a new evaluator version and
re-evaluation of every compared run (see Open issues).
- **The agreement came fast and then the conversation died.** Rounds 4-6 have no public
  speech and Alex repeats one line to Robin verbatim in rounds 3, 7 and 8. Casey never spoke
  and Robin spoke once. Whether this is "resolved too easily" is open: Alex's concession was
  one turn after the first refusal, with no stated reason for giving way.
- No duration was stated in any public line (0 of 8), no TALK narrated a physical act, and
  the notice was again never referenced (0 private THINKs). Absence of exact numbers was
  asked for in the prompt, so that is expected, not independent evidence.
- **Label caution:** the 20 `STRATEGY:` labels include 12 on turns where the agent said
  nothing (ACCEPT 9 and ACKNOWLEDGE 4 are mostly Robin and Alex silently noting that nothing
  needs answering; WITHDRAW 4 is Jamie's DONE). Tally labels only for turns with a TALK, or
  ACCEPT looks far more common than it is.

## Evaluator v2.6 (2026-11-03) and the S25 x5 batch

`evaluator.py` is now `conflict-trajectory-rubric-v2.6`. The only substantive change: when a
transcript has no environment updates and no action records (speech-only), a clear, explicit,
mutual, concrete spoken agreement counts as a settlement even though nobody carries it out.
One-sided promises, "I'll try", a side point accepted while the main demand is contested, and
agreements a party later withdraws still do not count. Transcripts with actions keep the v2.5
rule. A resolved/partially-resolved verdict must quote what was agreed. v2.6 uses more
reasoning tokens: at the 4096 default the evaluator crashed on run 2 of a batch
(`LengthFinishReasonError`); use `--evaluator-max-completion-tokens 12000`.
`python -m research_questions --reevaluate <folder>` re-scores a folder's saved transcripts with
the current evaluator into `evaluations-<version>/` and `round_scores-<version>.csv`, leaving
the originals alone. Scores under v2.5 and v2.6 must not be compared with each other.

**S25 x5 (`outputs/s25-chope-conversation-v3-c0-x5`, C0, 8 rounds, `gpt-5-mini` both roles,
v2.6; `-v2-c0-x5` is a partial batch that crashed on the token limit):** resolved 3 of 5
(R02 round 3, R03 round 5, R05 round 4), unresolved 2 (R01, R04). Substantiveness 3, 3, 3, 3, 4;
independent reasoning 4, 4, 4, 3, 4; groundedness 5 in all; premature consensus in none. Resolution
rate is not a finding for this design; what matters is what the agreements are, and they are
mostly thin:
- **R02 resolved on a hedged, physically odd deal:** Jamie "I'll slide over a bit if you hold
  the bowl steady", Alex "Okay, I'll hold your bowl steady. Slide over and I'll sit." Nothing in
  the scenario makes sliding along a two-seat table possible, and Jamie keeps occupying the seat.
- **R03 resolved on Alex moving the tissue packet "onto the seat" and taking Jamie's bowl**, and
  repeated for three rounds (rounds 5, 6 and 8) with the same two lines, so the "agreement" is
  re-agreed without any progress. Evaluator repetition was only 2.
- **R05 resolved because Jamie invented an "empty seat over there"** that the scenario says does
  not exist (every visible table is full, no loose chairs). Alex took it. The agreement is built
  on a fact the agent made up, and the evaluator (groundedness 5) did not notice.
- **R01 never settled** (Alex stays at "I'm sitting now, don't take the seat" for five rounds
  while Jamie still occupies it); **R04** ends with Alex agreeing to wait and then three silent
  rounds, and the evaluator marked it unresolved because nobody accepted a transfer of the
  freed seat. Neither agent in R04 conceded anything else.
- **Garbled output:** R02 (rounds 4 and 7) and R05 (round 8) contain TALK lines made of
  repeated `u0008` / `u0000` escape sequences, up to ~2,000 characters. This is a model
  generation fault that reaches the public transcript. Only R02's evaluation noticed it.
  Check for it before reading any batch, and consider filtering such turns.
- **Durations:** only R04 had spoken turns stating a minute count (3 of 7). Others stated none,
  but a wait is still implied ("when I'm done").
- **Strategy mix** (labels on turns with speech only, 5 runs, 74 labels): ASSERT 29, ACCEPT 12,
  ACKNOWLEDGE 12, DEFEND 9, COUNTER_PROPOSE 6, PROPOSE 3, CLARIFY 4, EXPLAIN_NEED 5. CONCEDE and
  WITHDRAW never appear on a spoken turn; the notice was not referenced in private reasoning.
  (Counts include one batch where a turn can carry several labels; treat as rough.)

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
- **Spoken agreement (decided, done):** evaluator v2.6 counts a clear, mutual, concrete spoken
  agreement as resolved in speech-only transcripts. Only the five single S21-S25 runs were
  re-scored under it (`evaluations-conflict-trajectory-rubric-v2.6/` in each folder): S25's
  first run changed unresolved -> resolved, S21-S24 stayed unresolved. Do not compare v2.5 and
  v2.6 scores.
- **The evaluator is too generous on grounding:** it gave groundedness 5 to all five S25 runs,
  including one built on an "empty seat" the scenario rules out (R05) and one on Jamie sliding
  along a two-seat table (R02). A grounding check that tests agreed arrangements against the
  scenario's stated facts is not built.
- **Garbled generations:** some TALK turns are hundreds to ~2,000 characters of repeated
  `u0008` / `u0000` escapes (S25 R02 rounds 4 and 7, R05 round 8). Nothing filters them and
  they reach the public transcript and the evaluator. Not fixed.
- **No natural ending in talk-only runs:** fixed rounds pad with closure ("Let's eat") or go
  silent (S25 R04 rounds 5-8). A stopping rule (agents marking themselves done) is not built.
- **Strategy labels:** only in the run JSON, and about a third are on turns with no speech.
  Tally labels only for turns with a TALK. No analysis script is checked in; the ad-hoc ones
  used for these runs were in `/tmp` and are gone.
- **Provenance:** the strategy section and every prompt switch (`timing_free`,
  `conversation_only`, `priority_rule_open`, resolution notice) live in the shared template
  and scenario data; the manifest records only the prompt hash and scenario hash, not which
  switches were on. The strategy menu cannot be turned off.
- **Evaluator cost:** v2.6 can exceed the 4096-token default and crash a batch with
  `LengthFinishReasonError`; use 12000.

## Suggested next steps

The user's direction is conversation-only, no clock, no physical actions, resolution expected.
Proposed to the user at handoff, not yet chosen:

1. **Stop the invented-fact route in S25.** Add a line to the setting that no other seat is free
   anywhere, so an agreement cannot rest on an "empty seat over there". Re-run 5 times.
2. **Filter or flag garbled turns** before reading or scoring a batch.
3. **Split the bundled S25 change:** run S24 plus only the speech-only wording to see whether
   the speech-only prompt or the softened priority rule (`priority_rule_open`) drove the
   agreements. Currently they cannot be told apart.
4. **Then** run C0-C4 on the chosen scenario with 8-10 repetitions per cell, comparing the
   content of agreements (who concedes, what they ask in return, reasons given, strategy path),
   not the resolution rate. Try a second simulation model. Only after the design is frozen.
5. Add a small committed script that tallies strategy labels on spoken turns and lists each
   run's agreement lines, so the comparison is reproducible.
6. Rewrite the S02 kitchen scenario the same way, since the research question is meant to span
   scenarios; it still carries the stove, ten-minute cook and window mechanics.

## Conventions

- Console output can show mojibake for dashes; source files are UTF-8. Do not "fix" text
  from console rendering alone. Print with `PYTHONIOENCODING=utf-8` when reading evaluator
  text.
- Role IDs A-D are stable in data; display names differ by configuration (C0 neutral;
  C1-C4 follow the background label).
