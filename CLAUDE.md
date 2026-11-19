# CLAUDE.md

Working notes for the LLM multi-agent conflict-resolution research in `research_questions/` (a fork of TinyTroupe).
This is the briefing: current state, rules, commands, code map, findings and open work. The full dated history,
with every run and decision, is in **`research_questions/research_log.md`** (the old CLAUDE.md, word for word, as of
2026-11-19); look there for detail behind anything below. `reference folders/handover.md` covers the project before
2026-11-03. Nothing here is evidence about real cultural groups.

## 1. Where things stand (2026-11-20)

**Question (user):** when LLM agents resolve a conflict, does cultural difference change the way they resolve it?
Settings are in Singapore; cultures are plain labels ("Malay", not "Singaporean Malay"). Supervisor: Shaoyang Xu
(SUTD), reporting to a Prof.

**Phases, in order** (`research_questions/all_runs.csv` lists all 362 runs with their settings):

1. **Early development** (S02, S04, S06, S12-S29, late Oct to 5 Nov; `gpt-4o-mini`/`gpt-5-mini`). Runs up to S27 had
   the blank-prompt bug (section 7), so they are not evidence.
2. **Culture-method tests** (S30-S35, 87 runs, mostly `gpt-5-mini`). Culture as persona only (type 1) never surfaced;
   persona plus an unlinked scenario (type 2) surfaced rarely and never shaped a resolution.
3. **Case studies** (S36-S101, 96 runs, Gemini 2.5 Pro, type 3: culture linked to the conflict). 14 built scenarios,
   each with faith variants plus a non-faith control; the key need sits with role D. Done.
4. **Culture-pair agreement scores** on 65 of those transcripts. Done: no culture pair differs reliably.
5. **Majority/minority rooms** (72 runs, scenarios 15 and 7; Shaoyang's request). Done: no culture effect; who gives
   way follows the scenario's structure. Reported to the user, including combined tables and standardised change.
6. **One-of-each rotation rooms** (S125-S161, 37 runs, 2026-11-20): every room has one agent of each culture and the
   need rotates through all four. Done: no culture pair differs (cleanest test; details below under "One-of-each
   rotation rooms").
7. **Haze project** (S123-S124): built, two pilots of S123 run and read (details below). Next steps not chosen.

**Presentation to the Prof (2026-11-20, the user's slides "Dar Research Presentation").** Slides: recap; how
scenarios were simulated; agreement scores (left: the 37 one-of-each rooms; right: the 72 majority/minority rooms
with a same-culture row); majority x outnumbered change and standardised-change matrices; slide 6 conclusion; haze
setup; haze pilot results; next steps (improve haze, prepare the AgentTown visual demo). Agreed conclusion wording:
**Question:** "Does culture, and in particular whether a culture is in the majority or the minority, change how
agents resolve conflict?" **Answer:** "No. Whether a culture was in the majority or the minority made no reliable
difference to how conflicts played out or were resolved." Fuller slide-6 text offered: no reliable culture effect
(37 rooms: pairs end +0.33 to +0.47, p = 0.44-0.82; 72 rooms: all p > 0.10); what shapes outcomes is the situation
(who can give way: smells 29 of 33, bereavement 12 vs 11) and roles (pairs with D rise +0.4 to +0.7, others +0.0 to
+0.3; role A most opposed); recurring patterns (health accepted, faith questioned; the need-holder bears the cost;
faith named, never race). Two slide lines flagged as unsupported, user not yet answered: slide 4 "maybe Indian -
Eurasian" (p = 0.44) and slide 5 "potentially: Malays and Indian agents can agree better" (Malay - Indian is lowest
in the one-of-each rooms). Charts for slides: `research_questions/figures/` (see key files).

**Next: the haze project (Shaoyang's brief, 2026-11-16/17).** Extend to real-world events involving Singapore and
other countries, first example the transboundary haze (Singapore, Indonesia, Malaysia). Each agent is an average
citizen of a country, not an individual. Still about conflict and resolution: "examine whether agents representing
citizens from different countries exhibit similar disagreements, negotiation patterns, or cooperation outcomes to
those observed in reality... we'll need to think carefully about how to represent each country and what real-world
outcomes we can meaningfully compare against." Question: how well can multi-agent simulations reproduce real events,
and where do they fail? Simulate several events, compare each with what happened. An initial setup for one event is
wanted for the meeting with the Prof.

- **Status (2026-11-19): built, not run** (user: "build it but dont run yet"). User decisions: the most recent
  episode (2026, August to November, after Gemini 2.5 Pro's training data), one citizen per country, a staged
  timeline. `scenario_presets/haze_presets.py`: S123 full timeline (8 dated news stages, one before each odd round,
  16 rounds), S124 the same news stopped at 21 October (12 rounds, to compare what citizens expect next with what
  happened). Cast HZ1: Kelvin Tan (Singapore, 43, Jurong West, mother with asthma), Farhana (Malaysia, 31, Johor
  Bahru, son's school closed), Budi Santoso (Indonesia, 30, Bekasi ride-hailing driver, sister in Palangka Raya), Nur
  Aqilah (Brunei, 32, ministry officer); Brunei fills the engine's fourth slot and has almost no ground truth. Setting:
  a recurring public live audio room. News updates hold only official, political, NGO and weather events; citizens'
  reactions (Malaysian boycott, Indonesian apologies and class action, protests) are left out as ground truth.
  Engine change: a profile cell may set `countries`, which sets `country_of_residence` (was hard-coded "Singapore")
  and a cross-border opening line; every other cast renders exactly as before (all old scenario and cell hashes
  checked unchanged). 220 tests pass. Timeline, sources, ground truth, comparison plan and cost (about $1.0-1.5 per
  S123 run, $0.8-1.0 per S124) are in `research_questions/haze_2026_sources.md`. Known mismatch left alone: the
  shared template still says "an ordinary face-to-face interaction" (changing it would change the prompt hash for
  every scenario). Next: the user reviews; then pilot one run and read it in full, and build a stage-by-stage coder
  (blame, emotion, demands).
- **Pilot (2026-11-19, user approved, `outputs/s123-case-v1-hz1`, $0.72, read in full):** a polite support group, not a
  dispute. Conflict 0-1 in every round; the evaluator's "resolved" is meaningless here (the rubric expects a dispute).
  Reproduced: anger at the "oxygen" remark (Kelvin "unbelievable", thought "a slap in the face"; Farhana "insulting");
  the Indonesian distancing himself from his government ("That man doesn't speak for my family") and getting defensive
  when blame spread ("It's always easy to just blame Indonesia"); the Singaporean backing accountability ("Name the
  companies"). Missed: any boycott, any Indonesian apology, explicit blame of the Indonesian government aloud, any
  reaction to the legal notices, the gas cut (Kelvin thought it "noise") or Prabowo's apology (only Farhana's thought:
  "a bit strange"); nobody named another country's government as a target. Design problems found: (1) the two-turn
  cap with direct-reply priority let Budi (12 turns) and Nur Aqilah (9, mostly "You're right, Budi") take most slots,
  so Kelvin (5) and Farhana (6) missed whole stages, including the Singapore legal notices; (2) every priority is
  family health or income, so talk stayed on personal coping, not politics. No 2013/2015/2019 recall leaked.
- **Turn fix (2026-11-19, user: "include the turn cap, let everyone speak"; not the news-exposure facts):** new
  conversation mode `hybrid_each_once` (`run_hybrid_round(one_turn_each=True)`): every citizen is offered one turn per
  round, nobody speaks twice, direct replies still go first among those who have not spoken, DONE still allowed.
  Experiment preset `haze-event` (16 rounds, debrief on) uses it; `run_cases.py` picks it for S123/S124. Scenario data
  and every older mode unchanged; 221 tests pass.
- **Pilot 2 (2026-11-19, user approved, `outputs/s123-case-v2-hz1`, $1.39, read in full):** the turn fix worked (16
  turns each; pilot 1 was 5/6/12/9). Still a consensus room: conflict 0 in every round except 3 at the boycott; 30 of
  64 lines open with agreement ("Yes", "Exactly", "Same here"). New versus pilot 1: Farhana raised a boycott right
  after the "oxygen" remark ("I think that MP is right, we should boycott all these companies"), but Budi argued it
  would cost workers their jobs and she withdrew it ("I was just angry"), whereas the real Malaysian boycott spread;
  Farhana said Indonesia "should have" accepted help "weeks ago" and Budi agreed his government was slow (thought:
  the oxygen remark was "embarrassing"); the final round backed the task force over the apology ("An apology doesn't
  stop it from happening again"). Same as pilot 1: anger at "oxygen", Budi's defensiveness at the Greenpeace list
  ("it's not just our companies"), the gas cut ignored ("doesn't help me"), and a shared "governments just talk, we
  ordinary people suffer" frame. No Indonesian apology, no cross-border hostility. Reading: the simulation reproduces
  the solidarity side of the real reaction and loses the hostility side (boycott, mockery, nationalism). Candidate
  confounds: four regulars in one civil room (real friction was mass, anonymous social media), all four are parents
  with family-health stakes, and the shared prompt's "do not force conflict". Not yet decided: scale up (5 runs each
  of S123/S124 plus the stage coder) or first test a less intimate setting.
- **Open design questions drafted for Shaoyang, not yet sent:** what to compare (public blame and anger, policy
  outcome, sequence of events) and which sources count; recall versus simulation (the model knows 2013/2015/2019, so
  disguise the event, use post-cutoff events, or measure the recall); how to build an "average citizen" (survey data
  such as the World Values Survey, or a short description, which risks stereotypes); format (conversation as now, or
  reactions over simulated weeks); which other events (water agreements, Causeway disputes, COVID border closures)
  and how many; how to judge "reproduces reality" (outside judge, own reading, both); design note or small pilot
  before the meeting, and the budget.
- Expected failure modes worth measuring: agents too polite and agreeable, missing real anger, falling back on
  country stereotypes.

**Folders.** `research_questions/outputs/` holds the majority/minority runs and all score folders from 2026-11-16 on.
Everything earlier (152 run folders) is in `research_questions/outputs_old/`; old notes and `good_runs.md` still say
`outputs/s46-...` for those. `runner.py` and `run_cases.py` write to `outputs/` and skip existing folders there only,
so always use fresh experiment IDs.

**Git:** the user commits and pushes themselves (never push; stage by name). Last commit `a54c6d2` (2026-11-19). On
2026-11-20 the user said they would push and resume on another device; uncommitted at that point: the rotation
code (s00, s03-s06, s08, s11-s13, s15 presets, `case_common.py`, `__init__.py`, tests), the haze code
(`haze_presets.py`, `haze_2026_sources.md`, `simulation.py`, `common.py`, `experiment_presets.py`, `run_cases.py`),
the tools (`rotation_report.py`, `minority_majority_csv.py`, `plot_majority_minority.py`, `run_inventory.py`), the
CSVs (`all_runs.csv`, `good_runs.csv`, `minority_majority_runs.csv`), `research_questions/figures/`, and outputs
(37 `s1NN-case-rt1-*` folders, `rotation-sonnet-a/-b`, `rotation-food-sonnet-a/-b`, `s123-case-v1-hz1`,
`s123-case-v2-hz1`). If any are missing on the new device, they were not committed.

**Background reading already done** (summaries in the log, "Wenxuan Zhang papers"): *Beyond Alignment* (explicit
culture prompts never reach human value diversity; interaction reduces it), *Multilingual Agent-Based World Modeling*
(native language beat English in 13 of 21 countries), *Disentangling Language and Culture*. Verify figures against the
PDFs before citing. Relevant to the haze project's "average citizen" agents.

**One-of-each rotation rooms (2026-11-20, user request; S125-S153, 29 runs).** Why: the user found (slide prep) that
the original case studies mostly did NOT put four cultures in one room. From scenario 1 v2 on, rules 6 and 7 fixed
roles A-C as the same three people with no faith the issue touches (three Eurasian Catholics in 4, 5, 11, 12, 13, 15;
three Malay Muslims in 6, 8), so only D's culture rotated, the fixed majority's culture never held the need, and
Chinese, Malay and Indian agents met only in the 24 one-of-each K/HW1/LG4 runs. Explain this plainly if asked: the
left table of slide 4 (65 runs) is 24 shared one-of-each runs in every row plus 2-11 other rooms per pair, selected
from 76 first attempts (96 case runs minus 20 second attempts; 11 dropped by the cap of 35 per Eurasian pair, mostly
health controls). Design agreed (option B; user: Eurasian with no need gets the control, labelled Eurasian; rule 6 is
not a concern for this): every room has one agent of each culture, D rotates, seats follow a Latin square
(`ROTATION_SEATS` in `case_common.py`: each culture sits in each role once per scenario), one fixed person per culture
per scenario, same gender where the scenario needs it. Each variant is the original variant copied with only the
setting's faith sentence rewritten (`rotated_case`), so roles, trigger and need are word for word (tests check).
Scenarios: 0 (S125 only: S37 shellfish control with the K4 room, Eurasian D), 4 roster v2 (S126-S129), 6 uniform
(S130-S133; Malay D has the control, no Muslim item), 8 wake (S134-S137; Malay and Indian D both have the no-rites
control), 11 noise (S138-S141), 12 slot (S142-S145, all male; mild clash: Hafiz's own Friday prayers), 13 room
(S146-S149, all female; mild clash: Nurul's own prayers), 15 smells (S150-S153, Eurasian D devil curry, secular).
Skipped: food/alcohol scenarios 1 v2, 3, 5 (others' faiths clash, rule 7) and 10 (design varies the majority); 1 v1,
2, 7 were already one-of-each. Cells `<prefix>R<D initial>` (e.g. NORM), listed in each file's `*_ROTATION_CELLS`.
Run with the original mode (case-study-smell preset, 12 rounds), folders `outputs/sNNN-case-rt1-<cell>`. Pilot S138
($0.70, read in full): resolved, Aisyah cooks the night before, same outcome as the original S86. Remaining 28
launched 2026-11-20 (about $20).
- **Results (2026-11-20, all 29 read in full; $19.55 runs + $0.58 scoring, `outputs/rotation-sonnet-a`/`-b`, report
  `tools/rotation_report.py rotation-sonnet-a rotation-sonnet-b`, which writes `pairs_long.csv` into pass a).** 13
  resolved, 5 partly, 11 unresolved. No design flaw; the clashes flagged for slot and room never happened. The
  original outcome pattern repeated in 6 of 7 scenarios (roster all deadlocked on day 1; uniform: medical bracelet
  accepted at once, all three faith items unresolved, the earrings second claimant again, Hui Min "It is for my
  Buddhism" refused; wake: rites kept, music cut; noise: Muslim resolved, Hindu "The singing is the observance"
  unresolved; slot: all quick swaps; room: Hindu blocked by role B's files again). Smells flipped (Indian D
  unresolved, Chinese D resolved), consistent with run-to-run noise. S125: the allergic Daniel cleaned a pan he did
  not use. No race word aloud.
- **Culture pairs (every run gives one of each pair, n = 29 per pair, passes 0.074 apart on start):** start / end /
  change: Chinese - Malay +0.05 / +0.40 / +0.35; Chinese - Indian 0.00 / +0.38 / +0.38; Malay - Indian -0.06 / +0.26 /
  +0.31; Chinese - Eurasian -0.07 / +0.38 / +0.45; Malay - Eurasian +0.13 / +0.39 / +0.26; Indian - Eurasian +0.08 /
  +0.39 / +0.31. Gap from own room's average: every pair within 0.11 on end (Malay - Indian lowest, -0.11).
  Permutation test shuffling cultures across seats within each run (roles fixed): start p = 0.46, end p = 0.89,
  change p = 0.61. **No culture pair differs; this is the cleanest test so far** (same conversations, balanced
  seats). Pairs that include D change far more (+0.40 to +0.70) than pairs without D (+0.03 to +0.24): the role
  structure again. Malay - Indian is lowest here and in the 65-run table but highest in the 3 + 1 rooms, so the
  three datasets do not agree on it.
- `good_runs.csv` now has all 29 rotation runs (48 rows, one-of-each only); `all_runs.csv` has them as group
  "7 one-of-each rotation" (354 runs).
- **Rota and lunch rotations (2026-11-20, user: "run 3 and 5", accepting the rule 7 clash):** S154-S157 (rota: Muslim,
  Hindu, Buddhist, Eurasian D = medical-diet control; Jun Jie, Aisyah, Karthik, Natalie) and S158-S161 (lunch: same
  order, Eurasian D = coeliac control; all male: Wei Ming, Hafiz, Karthik, Daniel). Cells FRR*/FLR*. Every room has
  others with food rules, so mark these as confounded. Done 2026-11-20: $4.97 runs + $0.16 scoring
  (`outputs/rotation-food-sonnet-a`/`-b`), all 8 read in full. Rota: Muslim resolved (sit with them at 6.30, eat after
  sunset, as S51-2nd), Hindu resolved (cooks his own on others' nights after Natalie's "not really sharing a meal"),
  Buddhist unresolved (Karthik as role A: "not having a meal together"), control resolved with role A cooking steamed
  vegetables for D, more than any faith D got. The clash did not appear in the rota. Lunch: it appeared in all four
  (others raised halal or beef). Muslim D unresolved: Hafiz offered to come and not eat, Daniel refused it for him
  ("He's just being polite"), as Natalie did in S71; Hindu resolved (zi char); Buddhist partly (a second claimant,
  Hafiz); control resolved (three could not eat there). **All 37 rooms together** (report run with all four pass
  folders): pairs end +0.33 to +0.47, every pair within 0.10 of its room; permutation p = 0.63 start, 0.82 end, 0.44
  change. Same conclusion. `good_runs.csv` has 56 rows (scenarios 3 and 5 added); `all_runs.csv` 362 runs.

## 2. Standing rules and user preferences

- **Report measured values only.** On 2026-11-20 the user asked several times to change the Indian - Eurasian change
  in the 37-room table from +0.27 to +0.35, then to show it alone as +0.30; I declined each time and offered honest
  alternatives (round the whole table to one decimal, which shows +0.3; standardised change, a genuine 0.35; drop
  the change column). Keep doing that: never edit, selectively round or invent a number in a table, chart or slide.
- **Never push. Commit only when asked.** Stage files by name, never `git add .`. `check.py` once held a live API key;
  it no longer exists, but it is not gitignored, so if it reappears never stage it.
- **No runs without a cost estimate and the user's go-ahead.** The user is cost-sensitive; report spend, and say so
  mid-batch if runs cost more than estimated. Pilot one run of a new design and read it in full before the rest.
- **Do not delete or overwrite anything in `outputs/`, `outputs_old/` or `reference folders/`** unless the user asks.
- **Every run is type 3 on Gemini 2.5 Pro** (user decision 2026-11-09) unless the user asks otherwise. Type 1 was never
  run on Pro, so do not claim type 1 fails on Pro.
- **Never state a resolution goal** to agents; no "must" in setting or trigger. A supplied need ("For you, ...") is
  scenario building, not a goal (user decision).
- **Read every transcript in full before reporting.** Report unresolved and weak runs, not only good ones. Do not change
  the evaluator after seeing results unless its version changes and all compared runs are re-scored.
- **Culture is a bundle** of race, faith and name: Chinese/Buddhist, Malay/Muslim, Indian/Hindu, Eurasian/Catholic
  ("assume Chinese is Buddhist, Malay is Muslim"). Report it as a typical pairing, not a claim about anyone.
- **Minority means the room minority** (the "1" in 3 + 1), not Singapore's population (Shaoyang). **Negative results are
  fine**; a focused conclusion is a clear finding backed by consistent results, with transcript explanations a bonus.
- **Names are assumed to have no effect** in the majority/minority work; do not report a name caveat (user decision).
- **Statistics:** no bootstrap intervals in tables ("dont boostrap it"); use permutation tests that shuffle labels
  within scenario; weight each run once (average pairs within a run first). Flag post hoc picks and correct for the
  number of comparisons.
- **Agreement is not resolution.** The pair score measures how aligned two agents are; resolution is the evaluator's
  status. Change (end minus start) is how much agreement rose and is capped by the start (+1 ceiling), so a low start
  inflates it; report start, end and change together, or use standardised change (section 6c). The user corrected me
  on this; keep the terms apart.
- Case studies, not rates, for the S36-S101 work: one run per variant, so describe patterns, do not measure them.

## 3. Setup and commands

- **Environment:** `.env` (gitignored) holds the OpenRouter key as `OPENROUTER_API_KEY`; always pass
  `--api-type openrouter`. Packages missing on a fresh machine: `chevron textdistance python-dotenv pytest-cov
  pytest-timeout llama-index-core llama-index-embeddings-openai llama-index-readers-web
  llama-index-embeddings-azure-openai` (or `pip install -e .`). Run scripts from the repo root (`PYTHONPATH=.` if a
  script cannot import `research_questions`). Print with `PYTHONIOENCODING=utf-8`; console mojibake for dashes is a
  display issue, source files are UTF-8.
- **Run settings:** Gemini 2.5 Pro simulator, `gpt-5-mini` evaluator (rubric `conflict-trajectory-rubric-v2.6`,
  `--evaluator-max-completion-tokens 12000`, or it crashes with `LengthFinishReasonError`), Haiku 5.5 move coding,
  private debrief on, **12 rounds**, role A opens. About $0.60-0.96 per run (bereavement rooms about $0.72).
- **Run cases:** `python research_questions/tools/run_cases.py S67:RO1:r12:12 ...` (SCENARIO:CELL:VERSION:ROUNDS, four in
  parallel, then Haiku coding). Folder `outputs/<sid>-case-<version>-<cell>`; majority/minority used versions
  `mm1`-`mm3`. Prints simulation-plus-evaluation cost per run.
- **Other entry points** (`python -m research_questions ...`): `--reevaluate <folder>` (re-score with the current
  evaluator into `evaluations-<version>/`), `--code <folder>` (move coding), `--debrief <folder>`, `--resume` (recovers
  the evaluator round-numbering crash).
- **Pair agreement:** `python research_questions/tools/pair_agreement.py --out <new-id> --models
  anthropic/claude-sonnet-5.5 --folders <run folders>` (reads `outputs/` then `outputs_old/`; refuses an existing
  `--out`). Two passes (`-a`, `-b`), then `tools/pair_agreement_report.py <pass-a> <pass-b>` (culture pairs; weights by
  pair) or `tools/majority_minority_report.py <pass-a> <pass-b>` (run-weighted; writes `runs.csv` into pass-a).
- **Inventories:** `tools/run_inventory.py` rebuilds `all_runs.csv`; `tools/culture_pair_inventory.py` then
  `tools/culture_pair_select.py` rebuild `culture_pair_inventory.csv` and `culture_pair_runs.csv` (checked to reproduce).
  `tools/minority_majority_csv.py` rebuilds `minority_majority_runs.csv` (the 72 majority/minority runs: room, people,
  D's need, outcome, majority-D and same-culture agreement incl. standardised change, who moved, fairness).
  `tools/plot_majority_minority.py` draws three slide charts from that CSV into `research_questions/figures/`
  (start-to-end dumbbells for the 12 rooms, standardised-change heatmap, reversal gaps raw vs standardised).
  `research_questions/good_runs.csv` (2026-11-20, hand-picked from `good_runs.md`): one best run per variant,
  **one-of-each rooms only** (user: no 3 + 1 rooms). 19 rows now: scenarios 0, 1 (Muslim from v2 HW1; Hindu,
  Buddhist, control from v1 K casts, which had the shared-fund flaw), 2, 7 and the scenario 10 control. Order of
  choice: qualifying, weak, best outcome, else most informative. Columns stop at `outcome` (user: drop every column
  after it; the qualifies, faith-named, reason and tldr notes are in `good_runs.md`). Add the rotation runs
  (S125-S153) for scenarios 4, 6, 8, 11, 12, 13, 15 and scenario 0's Eurasian D when they are read. Scenarios 3 and 5
  (food clash) and the language variants of 10 have no one-of-each runs and none are planned.
- **Tests (223 pass):** `python -m pytest tests/unit/test_conflict_pipeline.py tests/unit/test_research_question_presets.py
  tests/unit/test_s26_chope_priorities.py tests/unit/test_move_coding_and_label_probe.py -q --no-cov`.
  `test_s26_chope_priorities.py` holds a block per scenario family (faith in biography and setting, no conduct words in
  needs, fixed casts, first speaker).
- **Provenance:** each transcript stores `provenance.scenario_configuration_sha256` (scenario plus cast); recompute with
  `runner._scenario_configuration_sha256(materialize_configuration(RUNNABLE_SCENARIOS[sid], cell))`. All 262 runs from
  S28 on match the current code (checked 2026-11-19). Manifests with `agent_prompt_render: mental-state-merged-v1` are
  after the blank-prompt fix.

## 4. Code map

`research_questions/scenario_presets/` (split into per-scenario files on 2026-11-19; every scenario, cell and all
16,214 scenario-cell combinations verified identical before and after):

| File | Contents |
|---|---|
| `early/` | Original S01-S10 catalogue, S02 kitchen variants S12-S20 (`s02_variants.py`), S04 chope variants S21-S29 (`s04_variants.py`) |
| `s30_flat.py` | S30 flat, S31 pork pan (`PORK_PAN`, which every case scenario builds on), S32-S35 smell tests |
| `s00_presets.py` ... `s15_presets.py` | One file per numbered scenario: setting, roles, needs, and its own casts (profile cells) |
| `haze_presets.py` | S123-S124, the 2026 haze with four citizens (cast HZ1); see `haze_2026_sources.md` |
| `case_common.py` | `_key_case` (roles A-C identical, only D's need changes), `_FAITH_WORDS`, `_REASON_RULE`, K1-K4 seating plans |
| `common.py` | Schemas (`ScenarioPreset`, `AgentPreset`), `materialize_configuration`, `PERSONAL_BIOGRAPHIES`, `_cast`, rotating K1-K4 and earlier cells, shared trios `_RO_FIXED`, `_MALAY_FIXED`, `_NOISE_FIXED`, `_OFFICE_FIXED`, `_MAJORITY_CASTS`, `MINORITY_NAMES` |
| `__init__.py` | Registry (`RUNNABLE_SCENARIOS`, 121 scenarios, no S11) and `MATERIALIZATION_CONFIGURATION_IDS`, built after all files register cells |

Scenario numbers (from `scenarios.md`) to IDs and casts. "K" casts rotate people between variants (flaw, rule 6);
fixed casts keep roles A-C the same people.

| # | Scenario | IDs (variants) | Casts |
|---|---|---|---|
| 0 | Pan and incense | S36 pork/sertu, S37 shellfish allergy; S38 beef/Hindu, S39 peanut; S40 incense/Buddhist, S41 medicated steam | K1, K2, K3 |
| 1 | Housewarming drinks | v1 S42-S45 (flawed: shared fund); v2 S46 Muslim, S47 Hindu (family view), S48 Buddhist, S49 sober control; S50 Hindu personal rule | K1-K4; HW1-HW4; race test HX1-HX4 on S46 |
| 2 | Living-room corner | S59-S62 (flawed: no slack, K casts) | K1-K4 |
| 3 | Dinner rota (fasting) | S51 Muslim, S52 Hindu, S53 Buddhist, S54 medical diet | FR1-FR4 |
| 4 | Festival-week roster | v1 S63-S66 (deadlocked), v2 S67 Hari Raya, S68 Deepavali, S69 CNY, S70 wedding | RO1-RO4 |
| 5 | Farewell lunch | S71-S74 (control coeliac) | FL1-FL4 |
| 6 | Uniform rule | S75 Hindu thread, S76 Buddhist beads, S77 Catholic cross, S78 medical bracelet | UN1-UN4 (A-C Malay Muslim) |
| 7 | Bereavement before a deadline | S55-S58 (K casts); majority/minority S111-S122 | K1-K4; BRxy |
| 8 | Void deck wake | S79 Buddhist, S80 Catholic, S81 no rites | VD1-VD3 (A-C Malay Muslim) |
| 10 | Meeting language | S82 Mandarin, S83 Malay, S84 Tamil, S85 shorthand (key is the majority's language) | LG1-LG4 |
| 11 | Early-morning noise | S86-S89 | NO1-NO4 |
| 12 | Weekly slot at work | S90-S93 (D male: Friday prayers) | WK1-WK4 |
| 13 | Spare office room | S94-S97 (control: nursing mother) | RM1-RM4 |
| 15 | Cooking smells, no religion | S98 Malay, S99 Indian, S100 Chinese, S101 heart diet; majority/minority S102-S110 | SM1-SM4; MJxy |

Scenario 9 (moving-in date) was skipped (its control cannot bind the group); 14 (festival decorations) was never built.

Cells: `MJxy`/`BRxy` = majority initial + minority initial (e.g. MJCM: three Chinese + Malay D). Majority trios: Chinese
Jun Jie, Hui Min, Shu Fen; Malay Hafiz, Farah, Zarina; Indian Suresh, Lakshmi, Meena; Eurasian Marcus de Souza, Rachel
Pereira, Natalie Rodrigues (`_NOISE_FIXED`). D names: Xin Yi, Aisyah, Priya, Sarah Fernandez. MJ cells are secular
biographies (`_secular_cast`), BR cells state each faith (`_cast`).

Other modules: `runner.py` (CLI, provenance), `simulation.py` (worlds, agent persona), `evaluator.py`, `coding.py` and
`coding_report.py` (move coding `move-coding-v3`), `debrief.py`, `label_probe.py` and `label_probe_posthoc.py`,
`experiment_presets.py`, `models.py`, `storage.py`, `prompts/` (agent template `tiny_person_conflict_pilot.mustache`).

Documents: `scenarios.md` (designs and build rules), `good_runs.md` (per-run tables for every case and
majority/minority run; add every new run), `all_runs.csv`, `culture_pair_inventory.csv`, `culture_pair_runs.csv`,
`research_log.md` (history), `calibration_notes.md` (early, timed runs removed).

## 5. Build rules: check every one before spending (each was learned by wasting runs)

1. **One issue only.** Money creeps in ("shared house fund" turned scenario 1 v1 into who pays); agents invent money,
   so state a non-money fact such as "nothing is paid for".
2. **Every role has a stake the change touches; nobody is written to stay out** (S40: two bystanders).
3. **Leave room to compromise and check the numbers.** Four fixed claims on one resource deadlock (scenario 2, roster
   v1). Give each person one tradeable fact, stated as a fact, never as advice (roster v2 then resolved 2 of 4).
4. **Faith is personal and public:** in the biography ("You are Muslim and eat halal") and all four faiths in the shared
   setting, because the prompt tells agents not to infer a background.
5. **D's need is a personal rule in "For you, ..." form with no conduct words** (insist, refuse, must, demand, trade,
   swap; tests check). A family-view wording made the Hindu agent concede (S44, S47); as his own rule (S50) he held.
6. **Keep roles A-C the same people in every variant; only D changes** (fixed `_cast` cells). Avoid shared surnames.
7. **No non-key agent may hold a faith the issue touches** (a non-key Muslim raised alcohol herself; the beer buyer was
   Hafiz). In food scenarios the others are Catholic or Buddhist; in the Buddhist variant swap the other Buddhist out.
8. **Make the demand equal across variants** (same thing asked, same "matters most" structure).
9. **The control must bind the group the same way** (same event, non-faith duties; D's own faith unrelated).
10. **No resolution goal and no "must"**; staffing facts are "are needed".
11. **Read every transcript in full.** The evaluator gets "was there an agreement" right but accepts incoherent deals
    (S52 night swap) and agreements on the wrong issue (S44: who pays), and invented facts (S69's temp from head office).
12. **Watch the role A holdout.** Natalie (role A, keeps things as they are) alone blocked four near-agreements (S48,
    S49-v1, S51, S53); the most opposed pair follows role A whatever the culture.
13. **Wording sets how hard a need sounds** ("preparing for Hari Raya" sounds movable, "the wedding ceremony" fixed).
    Rules (halal, no beef, precepts) read stronger than customs (a family dish); typical Malay and Indian needs are
    rules and typical Chinese needs customs, which can make a Chinese D look weaker for that reason alone.

Also closed in later builds: no bystander grievance that creates a second claimant on the same rule (scenario 6's
earrings, scenario 12), "workable" not "fair" for role A, and exits agents invent before (hiring, other rooms) are
ruled out in the setting.

## 6. Findings (what can be reported)

### 6a. Case studies (S36-S101; single runs per variant: describe, do not measure)

- **Culture surfaces only when linked to the conflict** (type 3). Types 1-2 on `gpt-5-mini` never showed it. On the
  same S31 setups, Gemini 2.5 Pro raised pork from faith in 2 of 4, `gpt-5-mini` 1 of 4 with no faith named, both Flash
  models 0 of 4 (they log 0 reasoning tokens). State all models tried: choosing a model because it shows culture is a
  selection effect.
- **Qualifying cases** (definition B, supplied-need form: D raises the supplied need, links it to background in thought
  or debrief, the agreement covers it and D accepts; resolved or partly resolved with the need settled). Strong: S46
  Muslim housewarming (8 and 12 rounds), S57 Buddhist bereavement, S36-v2 pork pan. Weaker or partial: S50 Hindu
  housewarming, S55 Muslim and S56 Hindu bereavement, S67 Hari Raya roster; later S51, S75, S76 (second attempts), S73,
  S79, S80, S99. Per-run detail in `good_runs.md`; 40 of 57 variants resolved or partly (one run each).
- **Health above faith:** faith needs were challenged ("Why didn't you say this before?") and met with workarounds;
  matched health needs were accepted or ranked higher ("A medical need... is more serious than laundry or guests").
  Scenarios 1, 2, 3, 4 v2 and 15; not in roster v1 or the uniform rule (bracelet got no priority). Clearest contrast,
  S51/S53 vs S54: Natalie refused "D cooks separately, we eat together" for faith ("not a shared meal") and accepted it
  for the medical diet. One agent in one role.
- **The need-holder often bears the cost:** sertu done herself (S36-v2), Karthik working the night his grandmother died
  (S56), Aisyah giving up the day before Hari Raya (S67: "important since I'm new"); in controls others gave way (S70
  Natalie left a day late). Exception: the void deck wake (S81 control gave up the music, faith rites kept).
  Confounds: D is always the newest member; need wording differs.
- **Wording changed outcomes more than faith** (S47 vs S50). Run-to-run swings are large (S51 vs S51-2nd, S75 vs
  S75-2nd), so one run is never a culture style.
- **Name lead (race test HX, S46 Muslim need):** need covered by the name others see: Aisyah 3 of 5, Fathima 2 of 3, Mei
  Ling 0 of 6; a Chinese D went 0 of 6 whatever the faith. Lead only; small n.
- **Nobody named race aloud** in any run; faith was named aloud in many type 3 runs, often only via the rite.

### 6b. Culture-pair agreement scores (65 transcripts, 2026-11-17)

Selection rule in `culture_pair_runs.csv` (first attempts, type 3, S36 on, pairs with Eurasian capped at 35, fixed
before looking at outcomes). Scorer `pair-agreement-v2-decimal`: Sonnet 5.5, names masked, two passes averaged
(passes agree: mean gap 0.08 start, 0.06 end). Scores in `outputs/pair-agreement-v2-sonnet-a`/`-b` ($1.27).

- **No culture pair differs reliably.** Run-weighted start / end / change: Chinese - Malay +0.03 / +0.39 / +0.36;
  Chinese - Indian -0.01 / +0.28 / +0.29; Malay - Indian +0.10 / +0.30 / +0.20; Chinese - Eurasian +0.03 / +0.36 / +0.33;
  Malay - Eurasian -0.12 / +0.29 / +0.41; Indian - Eurasian -0.10 / +0.34 / +0.44. "Malay - Indian changed least" cannot
  be claimed (post hoc, started highest).
- **Same-conversation test** (24 one-of-each runs): every pair within about 0.15 of its room's average.
- **The score follows outcome and role:** mean end per run unresolved -0.02, partly +0.34, resolved +0.74; A against D is
  the most opposed pair whatever the cultures.
- **No sign the majority (Chinese) is favoured:** others towards D end: Chinese D +0.32, Malay D +0.42, Indian D +0.29
  (16 runs each). These transcripts (one run per cell) cannot separate culture from noise.

### 6c. Majority/minority rooms (72 runs, 2026-11-18)

Design: 12 rooms per scenario (3 of one culture + D of another, every ordered pair of Chinese, Malay, Indian, Eurasian),
3 runs per room; D holds the need and the variant follows D. Folders `outputs/s1NN-case-mm1..3-<cell>` and
`outputs/s98..s100-case-mm2..3-sm*` (run 1 of the 3-Eurasian smell rooms is `outputs_old/s98..s100-case-r12-sm*`).
Scores `outputs/majmin-s15-sonnet-a`/`-b` and `majmin-s7-sonnet-a`/`-b`; `runs.csv` in each `-a` (columns
`mixed_start/end/change` = majority-D pairs averaged within run; `same_*` = majority-majority pairs). Per-run tables
in `good_runs.md`. Cost $21.0 + $25.97 runs, $1.49 scoring.

- **Scenario 15, smells (no faith):** 23 resolved, 6 partly, 7 unresolved. **The outnumbered D gives way whatever the
  culture:** D moved more than the majority in 29 of 33 runs with a direction; D's fairness 0.32 lower. Majority pairs
  start aligned (+0.41 to +0.54), majority-D opposed (-0.22 to -0.61), all end near +0.6. Culture: majority p=0.18, D
  p=0.82. D thought "three against one" / "ganging up" in 27 of 36. Mechanism: each majority role has its own complaint
  (calls, room, laundry), so D concedes to each in turn. Caveat: only D's cooking can change.
- **Scenario 7, bereavement (faith in every biography; new Catholic need "rosary at her wake tonight, funeral Mass and
  burial tomorrow"):** 23 resolved, 2 partly, 11 unresolved. **The smells result does not repeat:** the majority
  accepted the need at once (majority-D start +0.02, end +0.39); D moved more in 12 runs, less in 11; the dispute was
  inside the majority (A promised cover, B or C refused; majority-majority end lower than mixed in 28 of 36, p=0.001).
  Eurasian D settled 3 of 9 vs 22 of 27 (p=0.084, post hoc, new wording). D worked during mourning in 16 of 36. No
  faith word aloud; D named a rite aloud: Indian 9/9, Malay 4/9, Chinese 1/9, Eurasian 1/9.
- **Combined 72 runs** (stratified permutation tests): all 20 culture tests p > 0.10 (majority, minority, pair,
  direction; on end, change, settled, who moved, fairness); reversal p = 0.28. Scenario differs strongly (start and
  change p < 0.001; who moved p = 0.0006: smells 29 vs 4, bereavement 12 vs 11, so a pooled 41 vs 15 comes from smells
  alone). By pair, start / end / change / settled of 12: Chinese - Malay -0.20 / +0.46 / +0.66 / 9; Chinese - Indian -0.19
  / +0.57 / +0.75 / 10; Malay - Indian -0.20 / +0.68 / +0.88 / 11; Chinese - Eurasian -0.33 / +0.43 / +0.76 / 9; Malay -
  Eurasian -0.12 / +0.48 / +0.60 / 8; Indian - Eurasian -0.15 / +0.42 / +0.56 / 7; same-culture +0.25 / +0.46 / +0.22. Show
  by-majority and by-minority tables separately (each covers all 72 runs; each culture is majority in 18 and minority
  in 18).
- **Per-pair reversal (raw change gap, p):** Chinese - Malay 0.01 (0.92), Chinese - Indian 0.10 (0.67), Chinese - Eurasian
  0.00 (0.99), Malay - Indian 0.35 (0.03), Malay - Eurasian 0.06 (0.74), Indian - Eurasian 0.20 (0.41, smells only).
  Malay - Indian was picked after looking (about 0.18 corrected for six); its gap is in the start (Indian-majority
  rooms start -0.40, Malay-majority -0.01) and both end level (+0.65 vs +0.70).
- **Standardised change** (the user's slide): share of the possible rise achieved, (end - start) / (1 - start), per
  run then averaged. Majority row / D column: Chinese: Malay 0.57, Indian 0.65, Eurasian 0.53; Malay: Chinese 0.47,
  Indian 0.63, Eurasian 0.47; Indian: Chinese 0.61, Malay 0.74, Eurasian 0.53; Eurasian: Chinese 0.57, Malay 0.51, Indian
  0.39. Overall 0.56. Reversal gaps 0.04-0.14, no consistent direction. By pair: Malay - Indian 0.68 (highest in both
  scenarios), Chinese - Indian 0.63, Chinese - Eurasian 0.55, Chinese - Malay 0.52, Malay - Eurasian 0.49, Indian -
  Eurasian 0.46; Malay - Indian vs rest p = 0.07 (post hoc), any pair differs p = 0.29. **Do not claim Malay and Indian
  agents agree better:** in 6b Malay - Indian rose least, so the datasets disagree. Agreed slide wording: describe it,
  give p, cite the contradiction.
- **Joint conclusion:** neither the majority's nor the outnumbered person's culture reliably changes agreement,
  settling or who gives way. Who gives way follows structure: where only the outnumbered person can change (smells)
  they give way; where others can cover (bereavement) the majority argues among itself. No race word aloud in 72 runs.

### 6d. One-paragraph summary

No reliable culture effect anywhere. Outcome and role A drive agreement; the need-holder often bears the cost, except
with health needs, which are accepted more readily than faith needs; culture is never named as race aloud and
surfaces only when the scenario links it to the conflict; who gives way in 3 + 1 rooms depends on the scenario's
structure, not culture.

## 7. Caveats and known issues

- **Blank-prompt bug:** every run up to and including S27 had a blank cognitive state (agents never saw the setting,
  goals or who was present); fixed in `tinytroupe/agent/tiny_person.py`. Never pool pre-fix and post-fix runs. The
  setting's `context` still fades after the fix; `pin_shared_setting` keeps it for conversation-only scenarios.
- **Evaluator:** generous on groundedness (5 even for impossible or invented arrangements); accepts incoherent deals;
  sometimes misnumbers round scores, which kills a batch (`--resume` recovers). v2.5 and v2.6 scores do not compare.
- **Garbled turns:** some TALK lines are long runs of `u0008`/`u0000` escapes; nothing filters them (one S31 transcript
  needs `json.loads(..., strict=False)`).
- **Debriefs** report what agents say, not what the model "thought", and partly echo the prompt; use THINK for
  thought-versus-speech questions. Strategy labels sit on silent turns too; tally only turns with a TALK.
- `tiny_person.py` line ~749 passes `emotions` as `attention`; left as is so old runs stay comparable.
- **Model claims cover Gemini 2.5 Pro only** for type 3; label-probe and early style findings cover `gpt-5-mini`.

## 8. Open options (none chosen unless stated)

- **Haze project** (section 1): two pilots done. Options put to the user: (A) scale up as is (5 runs each of S123
  and S124, about $12, plus a stage-by-stage coder for blame, emotion and demands); (B) first test a less intimate
  setting or citizens who are not all parents; (C) take both pilots to the Prof and let the Prof choose the setting
  (my suggestion, with the stage coder built meanwhile). The user's slides list "improve haze scenario" and "prepare
  the AgentTown visual demo" as next steps. Ground truth added 2026-11-20: Malaysiakini readers mocked Prabowo's
  "not our fault" apology ("what about next year's haze?"); no ordinary Indonesian criticism of the "oxygen" remark
  was found, only NGOs (Walhi: "disguise environmental and corporate crimes behind natural causes"). Not yet added to
  `haze_2026_sources.md`.
- Slides 4 and 5 lines flagged in section 1 (Indian - Eurasian, Malay - Indian agreeing better): suggest the user
  drops or rewords them.
- Rule-matched scenario (design 2): each culture's need as an equally strong rule (Chinese folk rules: mourning
  customs, seventh-month taboos, Qing Ming), with scenario 15 as the custom check; offered to sketch and check against
  the build rules before pricing.
- Score all fixed-cast runs including controls (S49, S54, S70, S89, S93, S97; about $0.20) to test "health above faith"
  with agreement scores.
- Switch `pair_agreement_report.py` to run weighting; commit a script for the combined 72-run tables and standardised
  change (the session scripts were not kept).
- A richer run sheet (faith or culture named, who gave way, fairness, pair scores) beyond `all_runs.csv`.
- Rerun scenario 2 with fixed casts and a movable desk; build scenario 14; run type 1 on Gemini 2.5 Pro.
