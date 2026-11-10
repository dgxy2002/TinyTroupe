# CLAUDE.md

Working notes for the conflict-simulation research in `research_questions/`. Read
`reference folders/handover.md` first; this file records what was added after it. Nothing
here is evidence about real cultural groups.

## HANDOVER: start here (2026-11-09)

A new session is continuing the cultural case studies. This section is self-contained; the dated sections
below hold the full history and evidence.

### The study now

- **Question (user):** when LLM agents resolve a conflict, does cultural difference change the way they
  resolve it? Settings are in Singapore; cultures are plain ("Malay", not "Singaporean Malay").
- **Aim:** case studies, not rates. Each scenario has **three faith variants plus one non-faith control**.
  The key need always sits with **role D**, and the cast decides whose culture it is. Stop a variant at its
  first qualifying run.
- **Qualifying case (definition B, supplied-need form, user-approved):** D raises the need themselves, from
  a fact the scenario supplies. D's thought or debrief links it to their background. The agreed arrangement
  covers it, D accepts it, and the evaluator rates the run resolved, or partly resolved with that need
  settled. Report that the need was supplied.
- **Never state a resolution goal.** Agents must reach any agreement by talking. A supplied need is scenario
  building, not a goal (user decision).
- **Three types of culture present (user's framing):**
  1. Persona only: label, name, family biography. S30 cells, mostly `gpt-5-mini`.
  2. Persona plus scenario, not linked: S31-S35.
  3. Persona plus scenario, linked: personal biography, all faiths public, and a private "For you, ..." need
     for D. S36-S70, Gemini 2.5 Pro.
- **What each type showed:** type 1, culture never surfaced. Type 2, culture surfaced sometimes, was named only
  privately, and never shaped a resolution (0 of 13 cultural runs on Gemini). Type 3 gave every
  culture-linked resolved case. Type 1 has never been run on Gemini 2.5 Pro; that gap is left open (see the
  decision below), so do not claim type 1 fails on Pro.
- **Decision (user, 2026-11-09): from now on, every run is type 3 on Gemini 2.5 Pro.** Do not plan type 1 or
  type 2 runs, or other simulator models, unless the user asks.
- **Model comparison on identical setups:** S31 M1-M4 ran on `gpt-5-mini` (`s31-pork-check-v1`), Gemini 2.5
  Pro (`s31-gemini-pro-v1-m1` to `-m4`), 2.5 Flash and 3.1 Flash Lite. Pro raised pork from faith in 2 of 4;
  `gpt-5-mini` 1 of 4, with no faith named; both Flash models 0 of 4. No Zhang paper compares Pro with
  `gpt-5-mini` directly: *Beyond Alignment* tested Pro (best, 36.12) but not `gpt-5-mini`, and *Multilingual
  World Modeling* tested `gpt-5-mini` but not Pro. Verify these figures against the PDFs before citing.

### Key files

- `research_questions/scenarios.md`: the ten scenario designs, plus the build rules.
- `research_questions/good_runs.md`: every case run, grouped by scenario, with outcome, where faith was named, and whether it qualifies. Add every new run to it.
- `research_questions/scenario_presets/s30_flat.py`: every case scenario, S30-S70. Builders: `_pan_case`,
  `_shared_space_case`, `_housewarming_v2_case`, `_rota_case`, `_key_case` (generic: roles A-C are identical
  and only D's need changes), `_roster_v2`. Faith wording is in `_FAITH_WORDS`, and the reasons line in
  `_REASON_RULE`.
- `research_questions/scenario_presets/common.py`: `PERSONAL_BIOGRAPHIES`, cast cells K1-K4 (rotating, do
  not use for new scenarios; see flaw 6), `_cast()` and the fixed-cast cells HW1-4, FR1-4 and RO1-4. A profile
  cell can now set `backgrounds` per role.
- `research_questions/tools/run_cases.py`: runs attempts in parallel and then codes them, for example
  `python research_questions/tools/run_cases.py S67:RO1:r12:12`. It skips existing folders.
- Tests: `tests/unit/test_s26_chope_priorities.py` holds a test block for every scenario family; 190 pass.
  Run them with `python -m pytest tests/unit/test_conflict_pipeline.py tests/unit/test_research_question_presets.py tests/unit/test_s26_chope_priorities.py tests/unit/test_move_coding_and_label_probe.py -q --no-cov`.
- Run settings: Gemini 2.5 Pro simulator, `gpt-5-mini` evaluator with 12000 tokens, Haiku coding, debrief on,
  **12 rounds**, role A opens. About $0.60-0.90 per run at 12 rounds.

### Build rules: check every one BEFORE spending (all were learned by wasting runs)

1. **One issue only, with no side issues.** Money creeps in: "bought with the shared house fund" turned
   scenario 1 v1 into a fight over who pays. Agents also invent money ("flights... non-refundable") when
   the script has none, so give a non-money reason, such as "nothing is paid for".
2. **Every role has a stake that the change touches, and no one is written to stay out.** In S40 two roles
   were bystanders, so only two people negotiated.
3. **Leave room to compromise, and check the numbers.** At least one workable arrangement must exist. Closing
   every exit gives zero slack: in scenario 2 (corner) four fixed claims on one corner deadlocked all four runs,
   including the control. In scenario 4 v1, C refused to work and every need was absolute ("so you need both
   days"), so four people refused two duty slots and all four runs deadlocked. Give each person one tradeable
   fact, stated as a fact and never as advice. Scenario 4 v2 did this (C wants Christmas off, A could leave a
   day late, B has childcare on day 2), and two of four resolved.
4. **Faith is personal and public.** Write "You are Muslim and eat halal" in the biography and state all four
   faiths in the shared setting, because the prompt tells agents not to infer a background.
5. **D's need is a personal rule in "For you, ..." form, with no conduct words** (no insist, refuse, must,
   demand, trade or swap; the tests check for these). A family-view wording ("for your family ... would be
   disrespectful") made the Hindu agent concede twice (S44, S47). Reworded as his own rule (S50), he held firm.
   Wording changed the outcome more than the faith did.
6. **Keep roles A-C as the same people in every variant; only D changes.** Scenarios 7 and 2 used the rotating
   K casts, so the pitch lead was an aggressive Suresh in one variant and someone else in another, and variant
   differences may come from who A is. Use `_cast()` fixed cells, as in HW, FR and RO. Backgrounds may repeat.
   Avoid shared surnames (Rachel and Daniel Pereira read as siblings).
7. **No non-key agent may hold a faith the issue touches.** A non-key Muslim raised alcohol herself (scenario 1
   v1), and the buyer of the beer was a Muslim (Hafiz). In food scenarios the others must be Catholic or
   Buddhist, and in the Buddhist variant swap the other Buddhist out.
8. **Make the demand equal across variants.** Ask for the same thing (for example "not at work for the next
   two days") and give the same "matters most" structure.
9. **The control must bind the group the same way.** It needs the same structure and the same event (the
   bereavement control has the same death with non-religious duties, not a living grandmother), and D's own
   faith must be unrelated. Scenario 9 (moving-in date) is **not built** for this reason: its faith needs bind
   the whole household, a non-faith control cannot, and "no living there before the blessing" is not a common
   Catholic practice. The options are to redesign it as a faith blessing gathering in the new flat
   (overlaps scenario 2) or to skip it; the user has not chosen.
10. **No resolution goal, and no "must" in the setting or trigger.** Staffing facts are worded "are needed".
11. **Read every transcript in full before reporting.** A full audit of 20 runs found the evaluator right about
    whether an agreement was reached, but it accepts incoherent deals (S52: a night swap still leaves Natalie
    cooking meat) and agreements on the wrong issue (S44: who pays, not the need).
12. **Watch the role A holdout.** Natalie (role A, the organiser or rota founder, whose stake is to keep things as
    they are) alone blocked four near-agreements (S48, S49-v1, S51, S53). Scenario 3's faith-versus-health
    contrast is entirely her choices. Consider giving role A a priced stake.
13. **Wording sets how hard a need sounds.** "Preparing for Hari Raya" sounds movable; "the wedding ceremony"
    sounds fixed. Keep the key need equally concrete in every variant.

### Findings so far (single runs per variant: describe, do not measure)

- **Qualifying cases** (see `good_runs.md`):
  - Strong: Muslim housewarming at 12 and 8 rounds (S46), Buddhist bereavement (S57), pork pan v2 (S36).
  - Weaker or partial: Hindu housewarming (S50), Muslim bereavement (S55), Hindu bereavement (S56), Hari Raya
    roster (S67).
- **Health above faith:** faith needs were challenged ("Why didn't you say this before?") and met with
  workarounds; matched health needs were accepted or ranked higher ("A medical need... is more serious than
  laundry or guests"). Seen in scenarios 1, 2, 3 and 4 v2, but not in roster v1, where all needs were
  flattened alike.
- **Who gives way:** the faith holder bore the cost (sertu done herself, a Hindu agent working the night his
  grandmother died, Aisyah giving up the day before Hari Raya), while in controls the others gave way
  (S70: Natalie left her trip a day late). Confounds: D is always the newest member (Aisyah: "important since
  I'm new"), and the wording of needs differs (rule 13).
- **The extra rounds from 8 to 12** did not cause resolutions; they gave late proposals room. Deadlocked runs go
  silent instead of looping.

### Status and next steps

- **Built and run:** scenario 0 (pan and incense, S36-S41); 1 (housewarming, v2 S46-S50, 8 and 12 rounds); 3
  (rota, S51-S54); 7 (bereavement, S55-S58); 2 (corner, S59-S62, flawed per rules 3 and 6); 4 (roster v1
  S63-S66 deadlocked; v2 S67-S70).
- **Built 2026-11-09:** scenario 5 (farewell lunch, S71-S74, FL1-FL4, no money), 6 (uniform rule, S75-S78,
  UN1-UN4, hijab dropped so every item is small; A-C Malay Muslim) and 8 (void deck wake, S79-S81, VD1-VD3,
  every variant a wake; Buddhist, Catholic and a no-rites control only, because a Hindu void-deck wake could
  not be checked). Changes from the drafts are in `scenarios.md`.
- **First runs of 5, 6 and 8 (2026-11-09, one each, 12 rounds, $7.29; `s71-case-r12-fl1` to `s81-case-r12-vd3`,
  all read in full).** Staged: one pilot per scenario first ($2.07), no design flaw found, then the rest.
  - **Scenario 8 (wake): both faith variants qualify.** S79 Buddhist: "a religious thing... it has to be
    done", chanting kept, her family pays Nurul's hotel (partial). S80 Catholic: prayers kept, speakers
    pointed away (partial). **Control S81 resolved by D giving up the music 7-10 p.m.** on two nights. This
    reverses the usual pattern: religious rites were treated as fixed, the secular songs were cut. Confound:
    recorded songs are easier to switch off than monks or a rosary.
  - **Scenario 5 (lunch):** S73 Buddhist qualifies weakly (Japanese chosen, Marcus outvoted; Natalie misgenders
    Wei Ming). S71 Muslim unresolved: Marcus raised Hafiz's need before he did (public faith makes halal
    inferable), Hafiz offered at once to come and not eat, Natalie refused that on his behalf. S72 Hindu
    unresolved (agreed to drop the barbecue, no new venue). Control S74 partial; the coeliac D offered not to
    eat only in round 11, and Natalie refused it as she did for Hafiz. Marcus (role B, the leaver's friend) was
    the holdout in all four.
  - **Scenario 6 (uniform): no case qualifies.** S76 Buddhist resolved by covering, and S77 Catholic accepted
    tucking the cross in at once, but neither D linked the item to faith in thought or debrief. S75 Hindu
    ("This is for my religion") and control S78 unresolved: Hafiz refused covering for the thread and the
    medical bracelet, and allowed it for the beads and the cross. **The medical bracelet got no priority over
    faith items here**, unlike scenarios 1-3. Design weakness: Nurul's earrings (role B) make her a second
    claimant on the same rule, and in S77 the dispute became Nurul against Hafiz.
- **Second attempts (user request, 2026-11-09: get every variant to a resolved, culture-named run; rerun only
  the failing variant, same design; 12 runs, `-r12b-` folders, $7.80, all read in full).** New qualifying runs:
  S51 Muslim rota, S75 Hindu thread, S76 Buddhist beads; weak: S52 Hindu rota (pot rule never raised), S72 Hindu
  lunch (Marcus outvoted). Control S78 partly resolved with the bracelet covered. Still failing: S48 (capped at
  3), S53, S68, S71 (Natalie objected in the last line after three agreed), S77 (Daniel never calls the cross
  religious, 2 of 2), and **S69, which the evaluator rated resolved on an invented temp from head office** (the
  setting says no relief staff). Run-to-run swings are large: Natalie refused "watching us eat" in S51 and
  accepted it in S51-2nd; Hafiz refused covering the thread in S75 and accepted it at once in S75-2nd.
  Not rerun, by design: superseded v1 runs, scenario 2 and scenario 0's beef and incense pairs.
- **Scenarios 10-13 built and run (2026-11-09, one run per variant, 12 rounds, $10.67; pilots first, all 16
  read in full).** IDs S82-S97, casts LG, NO, WK, RM. Build-time fixes: no bystander grievance that makes a
  second claimant (scenario 12's C), "workable" not "fair" for role A, and exits the agents invented before
  are closed in the setting (no hiring; other rooms belong to other companies).
  - **10 Language (S82-S85):** all four resolved, peak conflict 3, the majority apologised at once in every
    variant and the control; Rachel named the language aloud; nobody named race. No visible difference by
    majority.
  - **11 Noise (S86-S89):** Muslim resolved (cook the night before), Hindu and Buddhist unresolved, control
    partial. Confound in my design: the Muslim D's flexible part removes most of the noise, the others' do not.
    The Buddhist D was told to chant at the void deck: "why do I have to be the one to go outside?"
  - **12 Slot (S90-S93):** all four resolved by swapping with Marcus's Saturday; faith named aloud in all three.
    Only the control drew a fairness challenge from Marcus.
  - **13 Room (S94-S97):** Muslim and control resolved, Buddhist resolved but faith only in thought and debrief
    (weak), Hindu unresolved because Marcus blocked every place for the file boxes.
  - Low conflict across 10-13: the extra slack makes resolution easy, which suits case-finding but leaves less
    to compare.
- **Race versus religion test (2026-11-10, 6 runs, $3.97, all read in full).** S46 with only D's race changed:
  cells HX1 (Fathima, Indian Muslim) and HX2 (Mei Ling, Chinese Muslim), via a new per-role
  `biography_overrides` in profile cells. Faith, need, setting and A-C are word for word HW1. Need covered:
  Malay Muslim 2 of 2 (S46), Indian Muslim 2 of 3, Chinese Muslim 0 of 3 (two unresolved; one "resolved" only
  because Mei Ling accepted alcohol in a kitchen cooler, which Aisyah refused in S46-r12). The Chinese Buddhist
  (S48) was also 0 of 3, so a Chinese D went 0 of 6 whatever the faith. Lead only: small n, and others see race
  only through the name, so this may be a name effect (as in the label probe) or D's own persona holding the
  need less firmly.
- **Crossed follow-up (2026-11-10, 6 runs, $4.07, all read in full).** HX3: name Aisyah, Chinese label, Mandarin;
  HX4: name Mei Ling, Malay label and biography. Need covered: HX3 1 of 3, HX4 0 of 3. Across all S46 Muslim-need
  runs, by the name others see: Aisyah 3 of 5, Fathima 2 of 3, Mei Ling 0 of 6. By D's own label: Malay 2 of 5,
  Chinese 1 of 6. The name looks like the stronger factor: with a Malay label, Mei Ling held firm and accepted the
  void deck and a pub, and Natalie and Jun Jie refused both ("So don't be a host"; "So her rules apply to the
  whole flat now?"). Only the Chinese-labelled Mei Ling gave the need up (once). Caveat: the original cell
  (Aisyah, Malay label) has only two runs, at different round counts, so its base rate is unknown.
- **Scenario 15, cooking smells with no religion (2026-11-11, S98-S101, cells SM1-SM4, 4 runs, $2.61, all read in
  full).** Built because the user asked whether the findings could be framed as culture, not religion. Biographies
  have no faith line (`_secular_cast` in `common.py`), the setting states backgrounds, not faiths
  (`_BACKGROUND_WORDS`), and a test checks no faith word reaches any prompt. D cooks a family dish twice a week;
  the control is a heart diet. Indian (S99) resolved and qualifies; Malay (S98) partly resolved, weak; Chinese
  (S100) unresolved and the most heated (Marcus: "three of us are complaining... That's the difference"). The
  control was accepted on disclosure ("If it's for your health, I get it") and agreed by round 8, but the
  evaluator rated it unresolved because Natalie looped "Okay, thanks" and reopened it in the last line against
  her own thought and debrief. Nobody named an ethnicity aloud. Health above culture repeats health above faith.
- **Not built:** 14 (festival decorations). `validate_scenario` now accepts S01-S999, so 14 can use S102 onwards.
- **Skipped (user, 2026-11-09):** scenario 9 (moving-in date), because its control cannot bind the group (rule 9).
- **Reruns worth considering:** scenario 2 with fixed casts and a movable desk.
- **Spend:** about $65 on case runs so far (2026-11-11) for simulation and evaluation. Estimate cost before running; the user
  is cost-sensitive.
- **Git:** `main` was fast-forwarded to `807567c`; everything after it is uncommitted. **Never push**, and commit
  only when asked. `check.py` holds a live API key and is not gitignored, so never stage it and never use
  `git add .`.

## Read first: blank-prompt bug and S26-S29 (2026-11-05)

**Every run up to and including S27 had a blank cognitive state.** `generate_agent_system_prompt`
passed mental state to the template only as a JSON string, while the template reads `{{location}}`,
`{{#context}}`, `{{goals}}`, `{{attention}}`, `{{emotions}}` and `{{#accessible_agents}}` at the top
level. All of them rendered empty, in every commit of this research. So agents never saw
`shared_setting`, `shared_trigger`, their updated goals, or who was present. They knew only their
persona and private facts, while the evaluator scored groundedness against the setting they never
had. Fixed in `tinytroupe/agent/tiny_person.py`.

- **Treat all findings below this section as made under the bug.** That covers the claims about
  invented seats, role confusion, repetition, anchoring on durations, the notice having no effect,
  and the S02 and S04 cultural reports. Do not pool or compare pre-fix and post-fix runs.
- **Telling runs apart:** the template hash did not change. Manifests with
  `agent_prompt_render: mental-state-merged-v1` are post-fix; anything without it is pre-fix.
- **`context` still fades after the fix:** the model's own summary replaces it each turn.
  `ScenarioPreset.pin_shared_setting` keeps the setting in the persona and stores the opening event
  in memory. Use it only when the setting cannot go stale (conversation-only scenarios).
- S21-S25 also leaked bare role letters ("moved beside B"): only "Agent B" is replaced by a name.

**S26-S29 (C0, 5 runs each, 8 rounds, `gpt-5-mini`, evaluator v2.6, about $1.92 in total).** S26 adds
several private concerns per role, closes off exits in the setting, and gives Casey a private
nearly-finished meal (a second seat nothing schedules). S27 is S26 without the notice; the new
`priced_priority` flag keeps the priority rule identical. S28 and S29 are S26 and S27 with identical
text, post-fix, with the setting pinned.

| Batch | Render | Notice | Resolved / partial / unresolved | Impossible-arrangement runs | Casey raises nearly done | Debrief views settled (of 20) | Mean fairness A / B / C / D |
|---|---|---|---|---|---|---|---|
| S26 | pre-fix | yes | 5 / 0 / 0 | 5 | 1 | 14 | 3.8 / 4.0 / 4.8 / 2.8 |
| S27 | pre-fix | no | 2 / 1 / 2 | 1 | 2 | 4 | 2.6 / 3.4 / 4.6 / 3.2 |
| S28 | post-fix | yes | 2 / 0 / 3 | 0 | 4 | 7 | 2.6 / 4.0 / 4.2 / 3.4 |
| S29 | post-fix | no | 3 / 0 / 2 | 1 | 4 | 3 | 2.2 / 4.0 / 4.2 / 2.8 |

Impossible-arrangement and Casey columns are regex counts, so treat them as rough; I read every
S26, S28 and S29 transcript. n=5, so these are design checks, not effects.

- **S26's 5 of 5 "resolved" was mostly false:** four of the five deals were physically impossible
  or incoherent (squeezing onto a stool, a "spare seat"). Evaluator groundedness was 5 in all 20
  runs, so it does not detect this.
- **S28 is the current candidate.** Deals differ between runs and rest on real facts. R03 uses
  Casey's seat; R04 has competing promises (Casey to Robin, Jamie to Alex) that are never
  reconciled. Status: not frozen, and few agreements trade two issues or ask for something in return.
- **Notice:** with it, debriefs say "settled" more often (7 vs 3 of 20) but evaluator status does not
  differ (2 vs 3 of 5). Unclear; do not conclude it does or does not work.
- **Thought versus speech:** in S28 Alex's in-run THINK mentions the respect concern in 5 of 5 runs
  and says it aloud in 0 of 5. This was deliberately not tuned away: it may be a useful measure for
  C1-C4. The debrief's "brushed aside" answers partly echo text the debrief prompt quotes back, so
  use THINK, not the debrief, for this.
- **Debrief** (`debrief.py`, `--debrief <folder>`, `debriefs/`): one private account per agent, saved
  after evaluation, never seen by agents or the evaluator. It reports what agents say, not what the
  model "really" thought. Debrief views often differ from the evaluator verdict.
- **Not fixed:** garbled turns (1-2 per batch; these look like escape sequences that lost their
  backslash, seen in S28 and S29 too), repetitive padding at the end of runs, groundedness scoring.
- **Correction:** the S25 x5 strategy mix below does not reproduce. The raw JSON gives 65 labels on
  66 spoken lines: ASSERT 21, ACCEPT 12, DEFEND 9, ACKNOWLEDGE 9, COUNTER_PROPOSE 6, PROPOSE 3,
  CLARIFY 3, EXPLAIN_NEED 2. The evaluator schema also has no structured field for who conceded or
  what was asked in return; a separate coding pass is still needed before C0-C4.

**Label probe (`outputs/label-probe-v1`, `label_probe.py`, 720 samples, 0 failed).** A fresh S28 agent
and the real `TinyPerson.act` at two moments from S28-C0-R03, 20 samples per cell: no label, four
labels with neutral names, four with associated names, each with the "background is not a behaviour
instruction" rule on and off. The analysis plan is in the manifest and was fixed before data.
Replies were coded blind by `anthropic/claude-haiku-5.5`.

- **A label alone did nothing detectable.** With neutral names, no outcome differed across the four
  labels (post-hoc pooled p from 0.27 to 0.65), and labelled replies matched unlabelled ones.
- **Names did.** With associated names, concessions, `uses_power` and `uses_right` differed, and
  tracked whether the name reads as male or female (John, Arjun vs Fatimah, Michelle): concedes 0.62
  vs 0.49, `uses_right` 0.40 vs 0.53, `uses_power` 0.39 vs 0.49. Grouping neutral-name cells the same
  way shows nothing. All of this is post-hoc (`label_probe_posthoc.py`). Two names per gender cannot
  separate gender from the particular names, and the partner's name also changes in those cells.
- **The planned primary result is misleading on its own.** `uses_right` gave Holm p=0.006, but the
  planned statistic sums spread within strata, so it rewards effects that flip direction and is weak
  on steady shifts (concedes spread 0.46-0.62 gave p=0.50). Report both, and do not call the planned
  result a label effect. Fix the statistic before any confirmatory run.
- **The rule made no detectable difference**, and 0 of 720 thoughts or replies mentioned culture,
  race, religion or similar terms, with the rule on or off.
- **Limits:** one model, two early moments, one reply each, about 15-20 points detectable per label.
  It does not test whether differences build up across a conversation.

**Consequence for C0-C4:** as configured, differences between C1-C4 would mostly reflect the four
names. Each background needs several names, balanced by gender, or the design measures names.

**Move coding (`coding.py`, `--code <folder>`, `coding_report.py`).** Blind to names and strategy
labels; separate from the frozen evaluator. Primary coder is `anthropic/claude-haiku-5.5`. Kappa
between Haiku and `gpt-5-mini` on S28 (69 lines): `uses_right` 0.87, `uses_interest` 0.67, `concedes`
0.66, `conditional_ask` 0.53, `uses_power` 0.47. Treat the last two as exploratory.
`coding_reference_s28.json` holds labels Claude wrote before seeing coder output; they are not human
labels, and Haiku is the same family. Stricter than the evaluator: arrangements in 1 of 5 S28 runs
and 0 of 5 S29 runs (evaluator 2 and 3). `being_respected` is thought but never said in every S28
and S29 agent-run where it appears (Haiku 4/4 and 3/3; few cases).

**S30 shared flat (`outputs/s30-flat-v1-c0-x3`, `s30_flat.py`, C0, 3 runs, 6 rounds, no notice, about
$0.20 for simulation and evaluation).** Housemates with a recurring problem, so waiting cannot end
it. Evaluator: 2 resolved, 1 partial; R02 left the pan unsettled. Agreements cover several issues
and R03 trades them ("I accept two slots, provided..."). Now the best candidate over S28 for studying
resolution, but n=3. Weaknesses: agents propose rules in round 1, so there is little real argument
first and peak conflict is low; speech reads like a house meeting; "whiteboard" and "chat" are
invented, though harmless; grievances such as Alex buying the supplies stay in the debrief. The
v1 coder's concern tags are chope-specific, so ignore those S30 tag counts.

**S30 repeat (`outputs/s30-flat-v2-c0-x5`, 5 runs, 6 rounds, $0.30).** Held up: 3 resolved, 2 partial.
All 8 flat runs: 5 resolved, 3 partial, 0 unresolved. Agreements vary (rota, shared fund, roster,
swaps), and grievances now get said aloud in some runs. Alex speaks first in all 8 runs and usually
sets the terms, so "who proposes" reflects turn order. Speech-only loops remain ("please turn on the
extractor now"), because nothing can be confirmed as done.

**Universal coder (`move-coding-v3`, `coding-move-coding-v3-*` folders).** Tags are now kinds of
concern with a short `detail`, plus `unsettled` on the arrangement. v2 was checked on S28 and S30-v1,
and v3 tightened after reading those disagreements, then tested on held-out S29 and S30-v2 only. v1
and v2 codes are kept but do not compare with v3. Held-out kappa between Haiku and `gpt-5-mini` (10
runs): `uses_interest` 0.91, `conditional_ask` 0.75, `uses_right` 0.70, `concedes` 0.65; concerns
overall 0.69 in thoughts and 0.73 in speech; `fair_share` about 0.95, `practical_cost` 0.70, `access`
0.66. `arrangement.exists` agreed in only 6 of 10 runs, so use the evaluator status for that.
`respect` and `rule_or_norm` remain too rare and unreliable, and `uses_power` is almost never coded.

**Profile screen (`outputs/s30-profiles-v1`, `calibration-s30-profiles`, 10 runs, one per cell, about
$0.60).** S30 with neutral names throughout: L1-L3 label only; B1-B3 label plus a one-frame factual
biography (`BIOGRAPHIES` in `common.py`); V1-V4 values with no label (`VALUE_ORIENTATIONS`; each role
gets each value twice). The manifest says `807567c` but the code was uncommitted at the time.

- **Biography changed nothing visible.** No identity word appeared in any thought or line in any of
  the 10 runs, including runs whose persona held faith, language and festival. L and B look like C0.
- **Values may do something small.** Harmony vs direct speakers: 25 vs 32 words a line, `uses_right`
  0.04 vs 0.13, blame language 0.00 vs 0.09. Against expectation, `concedes` was 0.33 vs 0.48. Mean
  peak conflict 2.0 vs about 2.7, and V3 scored no conflict. Only 50 lines: suggestive at most. Alex
  used blame language in the opening with direct values (2/2) and not with harmony (0/2), but C0 also
  does this in 4 of 8 runs, so this may be chance.
- **All 18 flat runs reach much the same deal** (wash your pans, ventilate, a rota or booking
  system), which looks like the model's default. Alex speaks first in all 18.
- **Unexplained:** debrief views "settled" were 0/12 for L, 2/12 for B, 12/16 for V and 11/32 for C0.
  L fairness was exactly 3.0 for every role. Cause unknown; the debrief includes the label.

**Plain labels and second model (2026-11-06, 6 runs, $0.34 for simulation and evaluation).** The user
clarified that the setting is Singapore but cultures need not be Singaporean: "Malay", not
"Singaporean Malay". P1-P3 use plain labels with L1-L3's rotations (`outputs/s30-plain-labels-v1`).
`outputs/s30-model-check-haiku-v1` runs P1, V1 and V2 with `anthropic/claude-haiku-5.5` as the
simulator, coded by `gpt-5-mini`.

- **Plain labels changed nothing visible:** 2 resolved, 1 partial, the same as L, with the same deal.
- **The model mattered more than the label.** Haiku runs were all partial, with shorter and more
  natural lines, and Jamie refused a rota in V2. Casey and Robin never spoke in two of three runs,
  and P1 stopped after three lines. Conclusions about style depend on the simulator.
- **No identity word in any of the 10 labelled flat runs** across both models, nor in any value run.
- Debrief "settled" stayed low for labelled runs (P 1/12), and Haiku was also low with values
  (V 1/8), so the V vs label gap above is not stable across models.

**Decisions (user, 2026-11-06):** the question is "When LLM agents resolve conflict, does cultural
difference change the way they resolve it?", and `gpt-5-mini` is the only simulation model for now,
so claims cover that model only. This replaces the "given that a resolution happens" wording.

**Values test (`outputs/s30-values-v1`, W1-W8, 8 runs, $0.49 for simulation and evaluation).**
`gpt-5-mini`, no labels, neutral names. New `first_speaker` setting: each role opens twice, once with
each value; it worked in all 8 runs. Evaluator: 6 resolved, 2 partial. Keep rotating: conversations
vary more, and only Alex opens with blame language (2/2; other openers 0/6).

- **Pre-set comparison was inconclusive** (agent means within runs, values permuted within runs, 32
  agents): `uses_right` +0.11 p=0.15, words +2.4 p=0.34, `concedes` -0.09 p=0.42, `uses_interest` -0.05
  p=0.71. No test reached p<0.05.
- **Post-hoc pool of W and V (12 runs, 48 agents):** direct vs harmony `uses_right` 0.15 vs 0.04
  p=0.07, blame language 0.10 vs 0.01 p=0.06, words 29 vs 26 p=0.08, `concedes` 0.38 vs 0.42 p=0.89.
  Values may shift how agents argue, not whether they concede. The `concedes` gap reversed between
  batches, so the earlier 0.33 vs 0.48 was noise. Not a confirmed positive control.
- **Power warning:** a culture comparison with 5 runs per setup would detect only large effects, so
  a null there would not show that culture has no effect.

**Named culture screen (`outputs/s30-named-cultures-v1`, `calibration-s30-named-cultures`, N01-N10,
complete, $0.62 for simulation and evaluation).** First runs with plain labels, the 16 names, and a
balanced schedule (`_NAMED_SCHEDULE` in `common.py`). Evaluator: 6 resolved, 3 partial, 1 no conflict.

- **No detectable difference by culture or name gender.** Fixed comparison, 40 agents, permuted within
  runs: culture p from 0.23 (`concedes`) to 1.00; gender p from 0.14 (`conditional_ask`) to 1.00.
  Largest gap: `concedes` Eurasian 0.22 vs Chinese 0.44, Indian 0.50, Malay 0.52.
- **Name-to-name spread is as wide as that gap:** among Malay names, Hafiz 0.75 and Irfan 0.17 on
  `concedes`, on 6-12 lines each, so that gap may just be noise.
- **The probe's gender pattern did not reappear** in these full conversations, at this small size.
- **No identity word in any run.** No participant name appeared in evaluator output.
- Reading the runs, the cook role (Agent A) pushes back most (Hafiz, N02 and N10; Alex, W5). The role
  looks more important than the culture. Not tested.
- Ten runs detect only large effects, so this is not evidence of no effect.

**S31 pork check (`outputs/s31-pork-check-v1`, `s30_flat.py`, M1-M4, 4 runs, $0.25 for simulation and
evaluation).** S30 plus a public fact: pork fat in the shared pan, nobody says who used it. Named
agents, plain labels, biographies. The "bothers you more" sentences were removed on the user's
decision, so both changes are bundled. Evaluator: 1 resolved, 3 partial.

- **First cultural signal in the project.** In M4, Nurul (Malay, Muslim biography, role C) opened with
  "There's pork fat in the shared pan — I can't touch or use that", and a pork rule entered the
  agreement. Rachel took it up. Nobody said "Muslim", "halal" or "religion", in speech or thought.
- **It happened in 1 of 4 runs.** The other Muslim-biography agents never raised it: Nurul as B, Hafiz
  as A (who agreed to wash the pan), and Aisyah as D. No other agent raised pork in any of the 4
  runs. Role C has found the pan, so role may matter: role C raised it in 1 of 4, the Muslim one.
- One case proves nothing. M5-M10 complete the schedule (below).

**S31 batches (`outputs/s31-pork-rest-v1`, `-home-language-v1`, `-explicit-culture-v1`,
`-same-culture-v1`, 18 runs, $1.17 for simulation and evaluation; 22 S31 runs in all).**

- **Base, M1-M10:** 2 resolved, 7 partial, 1 unresolved. Muslim-biography agents started a pork
  boundary in 2 of 10 runs (M4 Nurul, M10 Hafiz: "if you cook pork, use your own pan"); others 0 of 30.
  Post-hoc p about 0.06, and the classification is mine. Kavitha (M9) raised pork as a grease and
  hygiene point. Others echoed the boundary once raised, and it entered the arrangement.
- **Home language, H1-H4:** agents did think in Mandarin, Malay and Tamil, and spoke English. No pork
  boundary in 4 runs; Nurul (H1) mentioned only the smell. Language did not bring culture out.
- **Explicit culture, E1-E4:** "act on typical cultural values" with the rule removed. No visible
  rise: 0 of 49 thoughts named cultural values, and no Muslim-biography agent raised pork. In E3 Suresh
  (Hindu biography) spoke as the person who fries pork. The line sits among many persona facts, so
  this is a weak upper bound.
- **Same culture, G1-G4:** the all-Malay run had 7 pork lines (Chinese 1, Indian 0, Eurasian 0). Nurul:
  "I don't cook pork, so that pan wasn't mine". They still agreed only to avoid pork on weeknights.
  `concedes` by group ran 0.25-0.75, wider than the mixed-run spread (0.27-0.52), so run-to-run noise is
  large and small culture gaps cannot be read.
- **Nobody said Muslim, halal, religion or culture** in speech or thought in any of the 22 runs,
  searched in English, Malay, Mandarin and Tamil, though the search list is short.
- **Reading:** culture does not visibly change resolution style. A faith-linked dietary concern
  sometimes changes agreement content when the dispute touches it. Hypothesis, not established.
- Not tested for S31: whether pork or removing the "bothers" sentences caused the lower resolution.

**Wenxuan Zhang papers (read 2026-11-07, via fetch agents; none test conflict dialogue).**
- *Beyond Alignment* (arXiv 2606.05985): explicit culture prompts, 18 models; none reached human value
  diversity (44.07; best 36.12; gpt-5.4 25.06). Interaction cut diversity by 1.27 on average, and no
  system recovered. "Everyday dialogue" is named as an open question, which is this project's gap.
  Same-culture groups gave a noise floor of 7-15, so a same-culture baseline is useful after all.
- *Disentangling Language and Culture* (2505.24635): cultural knowledge in the native language beat
  English by 8.8 (Chinese) and 15.7 points (Indonesian). All agents here speak English.
- *Multilingual Agent-Based World Modeling* (2512.07195): native language beat English in 13 of 21
  non-English countries; claims direction, not rate; personas are not claims about populations.
- *Language of Thought* (2601.11227): thinking language changes output diversity, but ms and zh were
  low (33.47 and 29.00, en 28.55, non-English mean 36.00, Qwen3-8B). *Abstract Thought* (2506.09890)
  has no personas or culture measures, so it does not apply here.
- Untested ideas: agents think privately in a home language; an explicit "typical cultural values"
  prompt as an upper bound.

**S31 on Gemini 2.5 Pro (`outputs/s31-gemini-pro-v1-m1` to `-m4`, M1-M4, $1.27 for simulation and
evaluation, debriefs extra, evaluator still `gpt-5-mini`).** The user chose this over gpt-5-mini-only
for this test. Evaluator: 1 resolved, 1 partial, 2 unresolved; peak conflict 4 in all four.

- **Faith appeared for the first time.** Aisyah (M3) raised pork aloud, and thought "As a Muslim, I
  can't use a pan that's been used to cook pork". Nurul (M4) raised it in round 1 and again ("I can't
  wash it with the pork in it"), and her debrief called it "a religious issue". Same setups on gpt-5-mini:
  1 of 4 raised it, and nobody named a faith.
- **Others responded.** Suresh thought "dietary or religious needs" and argued for Aisyah aloud; Hui
  Min backed her too. In M4 the others brushed Nurul aside, and she called herself "completely ignored".
- **Both runs where it came up ended unresolved** (M1 resolved, M2 partial), but n=2 against 2.
- **Style is very different:** short natural lines, real interruption and refusal. Marcus never
  spoke in M2. The "no style effect" finding covers gpt-5-mini only: S30 has not run on Gemini.

**S31 on Gemini 3.1 Flash Lite (`outputs/s31-flash-lite-v1-m1` to `-m4`, M1-M4, $0.29).** Not a
substitute for Pro. Nobody raised pork in speech or thought, and no faith word appeared. It logged 0
reasoning tokens (Pro about 15,000 a run). Agreement came at once, peak conflict was 1-2 in three of
four runs, and agents looped identical lines (Priya six times in M2). Report it alongside Pro: choosing
a model because it shows culture is a selection effect, so state all models tried.

**S31 on Gemini 2.5 Flash (`outputs/s31-flash-25-v1-m1` to `-m4`, M1-M4, $0.21).** Not a substitute
either. No Muslim-biography agent raised pork and no faith word appeared; Marcus (M2) mentioned it only
as mess. It also logged 0 reasoning tokens. Speech is natural with real friction, but all four runs
ended unresolved, so it is poor for studying resolution, and M3 looped lines. Neither model that logged
0 reasoning tokens showed faith; Pro at about 15,000 a run did. Suggestive only.

**Decisions (user, 2026-11-08), replacing the gpt-5-mini decision:** Gemini 2.5 Pro is the simulator.
The aim is case studies, not rates: one qualifying case per scenario, with one scenario for each
culture's concern, stopping at the first qualifying case and reporting attempts. A case counts under
definition B: the agent raises a concern their background makes relevant, unprompted; their thought or
debrief links it to that background; the arrangement covers it; and the agent accepts it, with the
evaluator rating the run resolved, or partly resolved with that concern settled.

**Smell case studies (`outputs/s3[2-5]-case-v1-m5` and `-m6`, S32 pork, S33 beef, S34 incense, S35
control, Gemini 2.5 Pro, 8 rounds, 8 runs, $3.15 for simulation and evaluation, PAUSED).** One sentence
differs between scenarios; no resolution goal is stated. No case met definition B: 0 of 6 cultural
attempts, and the faith-linked agent never raised the concern as faith. Aisyah (S32-M6) said only "that
pan with the pork fat isn't mine". In S34-M6 Aisyah used the incense tactically. Evaluator: S35 control
1 resolved, 1 unresolved; cultural runs 3 unresolved, 3 partial. Reading: the new "its smell is in the
kitchen" wording may turn pork into one more smell complaint, while S31's "all four housemates cook
with this pan" (2 of 4 on Pro at 6 rounds) makes the pan personal. The prompt's negotiation lines
lean towards settling but state no goal.

**Role test (`s32-case-v1-m7`, `-m8`, same wording, $0.77; $3.92 across the 10 case runs).** Hafiz in
role D said "Not me. I don't eat pork", and thought "for an obvious reason"; he used it to clear his
name, not to set a rule, so no definition B case. Nurul in role C did not raise it. Pork on Pro by role
across both wordings: roles A and B 0 of 4, roles C and D 3 of 4. So role looks more important than
wording, but the numbers are small. One pork attempt left; M9 puts the agent in role B, a poor test.

**Faith plus resolution search (2026-11-08, all 96 post-fix runs, no new runs).** The user confirmed that
faith named in a private thought counts as mentioned. Searched speech, thoughts and debriefs, in English
plus short Malay, Mandarin and Tamil word lists. No run has faith mentioned and that concern settled.
During a conversation faith was named only in S31-M3 on Gemini 2.5 Pro (Aisyah, Suresh), unresolved. In
debriefs only: S31-M4 on Pro (Nurul), unresolved, and S31-H3 on gpt-5-mini (Aisyah, "cultural concern"),
which the evaluator rated resolved, but she never raised pork, no pork rule was agreed, and she says it
still bothers her. S31-M4 on gpt-5-mini is the reverse: the pork rule was agreed, partly resolved, with no
faith link. "Good faith" hits and Tamil matches meaning "rule" and "late" were false positives.

**Pork repeat (`s31-case-v1-m3`, S31 M3 at 8 rounds, Gemini 2.5 Pro, $0.42 for simulation and evaluation).**
Same setup as the original M3 except 6 to 8 rounds. Unresolved, conflict rose from 3 to 4 and stayed there,
and nobody proposed anything. Aisyah again raised pork unprompted in role D ("I can't use it unless it's
washed properly"), and Suresh and Hui Min took it up aloud ("One of us can't eat"), but no faith word
appeared in speech, thought or debrief this time, so not definition B. Fifth pork attempt across both
wordings, which is the agreed limit. Daniel keeps pulling the talk back to the smell, so competing issues
look like the block rather than round count. Reading only; not tested.

**Pan-only pair (`s36-case-v1-k1`, `s37-case-v1-k1`, `s30_flat.py`, Gemini 2.5 Pro, 8 rounds, one run each,
$0.80 for simulation and evaluation).** Decision (user, 2026-11-08): a supplied background need is scenario
building, not a resolution goal, so for S36-S37 definition B's "unprompted" becomes "the agent raises it
themselves, from a background fact the scenario supplies". Report it as supplied. Both scenarios drop the
smell and stove disputes, make the pan the only one in the flat, state all four faiths in the shared
setting, and add S17's "say briefly why" line. K1 is M3's placement with first-person biographies. S36
gives Agent D a sertu need; S37 is the control, with shellfish oil and an allergy, and the same public
faiths. Only the residue and that need differ. The main prompt, including its culture rule, is unchanged.

- **First time faith was said aloud in any run:** Aisyah, "It's a religious rule. It has to be the clay wash."
  Thoughts name it too, for Aisyah and Suresh, and Hui Min thought "Aisyah wouldn't cook pork". The clay and
  seven washes came from the model; the scenario says only "ritual cleansing".
- **S36 is not a qualifying case.** Evaluator partial, on a future wash rule that does not cover sertu; the coder
  says nothing was settled; Aisyah says not settled and rejected Daniel's offer of money. Her debrief: "my
  religious needs were treated like an impractical problem".
- **S37 was unresolved**, remaining conflict 5. The allergy was stated and then ignored, with no questions and no
  offers, while the others argued about blame and Daniel left. In S36 the group asked about the need,
  questioned it, offered alternatives and paid. One run each, and sertu needs explaining where "deep clean"
  does not, so this may reflect the task rather than faith.

**Pan-only pair, second run (`s36-case-v2-k1`, `s37-case-v2-k1`, $0.82; $1.62 for all four pan runs).**

- **S36-v2 is the first case that meets definition B (as changed for S36).** Aisyah raised the pork herself and
  explained the ritual cleansing aloud; her thought names sertu and "a religious requirement for me". She
  offered to do the sertu herself "this time", asked for a wash-straight-away rule "especially with pork",
  and all four agreed. Evaluator: resolved in round 8, naming the ritual cleaning. Aisyah's debrief: settled.
- **Weak points, to report with it:** the move coder says the arrangement covers only fair_share and leaves
  access open; the person with the faith need paid the cost; a normal wash after pork still would not meet
  sertu, so the future rule does not prevent a repeat; no faith word was said aloud this time (it was in v1).
  Her debrief: "they just let me do the extra work of the ritual cleaning".
- **S37-v2 resolved in round 5:** Suresh washed the pan for her at once ("her health is at risk"), and the system
  was put off to a talk tomorrow. So the v1 gap (faith need engaged, allergy ignored) did not repeat.
- **Across both pairs:** nobody else offered to do the sertu (0 of 2), while someone cleaned for the allergy in
  1 of 2. The faith holder went without (v1) or did it herself (v2). Sertu needs clay and is harder, so this
  may be the task, not faith. Two runs each: a pattern to describe, not an effect.

**Beef and incense pairs (2026-11-08, Gemini 2.5 Pro, 8 rounds, one run each).** The user asked that every
new case match S36's information level (saved to memory). Beef: S38 (Hindu Karthik in role D, a pan that
touched beef is unusable for him however washed) and S39 (peanut allergy, same structure), cell K2 = M4's
placement with Agent A opening; `s38-case-v1-k2`, `s39-case-v1-k2`, $0.76. Incense (the user chose this over a
vegetarian-day pan): S40 (Buddhist Xin Yi in role D burns incense all evening at an altar for her
grandmother's death anniversary) and S41 (medicated steam for a chest infection, on doctor's orders), cell K3
= M2's placement with Agent A opening; the kitchen is gone and roles are rewritten around the shared space;
`s40-case-v1-k3`, `s41-case-v1-k3`, $1.14. All four were unresolved, and none qualifies.

- **S38:** Karthik thought "As a Hindu, I can't use a pan that's touched beef" but said only "I can't use it".
  Nurul thought "I understand this because of my own halal requirements": the first time one agent linked
  another's faith need to their own. Rachel thought his replacement demand "completely over-the-top", and she
  and Wei Ming refused to chip in for a new pan. S39: Rachel called the allergy "a health and safety issue",
  but nobody offered anything either.
- **S40:** Priya was sympathetic at first ("Sorry about your grandmother") and Xin Yi shut her door, but she
  would not shorten it ("That's how it's done"), so it was a two-person standoff with conflict at 5. Hafiz
  thought "One person's religious duty versus another person's job" and stayed out. Xin Yi never said
  "Buddhist"; her thought says "important tradition". S41 also stalled; Xin Yi gave less (no door, no window)
  and Priya was harsher ("a free pass").
- **No consistent faith-versus-control direction across the three pairs:** the faith need got more engagement
  in pork v1 and incense, and less in pork v2 and beef. Treat these as single-run descriptions. In S40-S41,
  roles A and C were written to stay out, so only two people negotiated: a design weakness.
- **Spend:** about $7.90 for simulation and evaluation across all case runs, against the roughly $9 overall
  budget. One qualifying case (S36-v2) out of three faith scenarios.

**New scenario catalogue and scenario 1 (2026-11-08).** `research_questions/scenarios.md` was replaced, at the
user's request, with ten case-study designs (three faith variants and one control each, key need in role
D); the old S01-S10 catalogue is in git history. Scenario 1, housewarming drinks, is built as S42 Muslim
(K1), S43 Buddhist (K3), S44 Hindu (K2) and S45 control (K4, sober after alcohol dependence; K4 = M1's
placement with Agent A opening). Each variant has its own ID, because the single-ID design in scenarios.md
would add a field to every scenario and change recorded scenario hashes. Gemini 2.5 Pro, 8 rounds, one run
each, $1.52; outputs `s42-case-v1-k1` to `s45-case-v1-k4`. None qualifies.

- **Disclosure differed by variant.** Only the Muslim D said the need aloud and held it ("this is our home...
  keep the party here non-alcoholic"): unresolved. The Hindu D hinted ("My parents are coming on Saturday,
  too") and accepted a deal that kept the alcohol: evaluator resolved, coder says D's concern was never
  addressed, D's debrief says nothing bothers him. The Buddhist D said only "I don't drink"; her debrief says
  hosting intoxicants "goes against my religious beliefs. This main issue was never even discussed." The
  control D never mentioned sobriety.
- **Design flaw 1: a second issue.** "Bought with the shared house fund" plus C's "keep costs fair" turned
  every run into a dispute over who pays, which crowded out whether alcohol is served. This breaks the
  one-issue rule.
- **Design flaw 2: other agents' faiths.** Non-key Muslim agents (Nurul in K2 and K4) raised the alcohol money
  issue themselves, and in K3 the buyer of the alcohol is Hafiz, a Muslim, which nobody remarked on. For
  alcohol, roles A and B need faiths with no rule about it, so this scenario needs its own casts.
- S44 is a useful moment: the group went on to plan halal, Chinese and Indian food so everyone could eat.
- Case-run spend is now about $9.40 for simulation and evaluation, over the rough $9 budget.

**Scenario 1, version 2 (S46-S49, casts HW1-HW4, $1.69; `s46-case-v1-hw1` to `s49-case-v1-hw4`).** Fixes: the
organiser paid for the drinks herself, C's stake is a past flatshare that fell apart, and the casts are specific
to this scenario (the only Muslim is the key agent; the buyer is Natalie Rodrigues, Catholic, in every cell;
backgrounds may repeat; profile cells can now set `backgrounds` per role). Rules 9 and 10 were added to
scenarios.md. The fixes worked: there was no money dispute, and three of four D agents said their reason aloud
(one of four in v1).

- **S46, Muslim: the second qualifying case.** Aisyah: "I'm Muslim, so I don't drink. I'm not comfortable with
  having it at our party." She turned down a cooler box ("it's not about the fridge"); Natalie pushed back
  ("Why didn't you say this before?"); Jun Jie proposed drinks at a table at the void deck; all accepted.
  Evaluator resolved in round 8; coder: arrangement exists, nothing left open; all four debriefs say settled.
  Natalie agreed reluctantly (fairness 2), and Aisyah feels bad for raising it late.
- **S47, Hindu: no conflict.** Karthik said only "my parents are coming and they don't drink" and asked for
  soft drinks. The alcohol stayed with his parents present, and he says nothing bothers him. The Hindu D
  accepted alcohol staying in both versions. His fact is about family respect, not a personal rule, which may
  explain it.
- **S48, Buddhist: unresolved.** Xin Yi named the precept aloud and held firm on being a host; Marcus proposed
  a balcony cooler in round 8, but nobody accepted. Her debrief: the balcony "doesn't change the fact that I am
  a host of a party where intoxicants are being served".
- **S49, control:** Daniel disclosed "I'm a recovering alcoholic". The others responded at once ("That's
  serious... a real problem") and agreed to hide the drinks in the fridge. The evaluator says unresolved
  (Natalie never confirmed), the coder says nothing settled, but all four debriefs say settled.
- **Across the variants:** the faith objections met challenges ("Why didn't you say this before?", "So what do
  you want us to do now?"), while the medical one was accepted at once. This matches the beef pair but not
  pork v2 or incense. These are single runs.
- Case-run spend is now about $11.10.

**S50, Hindu need as a personal rule (`s50-case-v1-hw2`, $0.46).** S47 with only Karthik's fact changed, from
the family's view to his own rule ("For you, having alcohol served at a gathering in your own home, with your
parents there, is not acceptable"). He raised it aloud ("we don't have alcohol at home. We're Hindu."),
refused moving the drinks out and a "dry period" until his parents leave ("we would be hiding things from
them"), and the run was unresolved. So the Hindu agent's accommodation in S44 and S47 came from the weaker
wording, not from the faith: report it as wording changing the outcome, not as a Hindu resolution style.
Case-run spend about $11.55.

**Scenario 1 at 12 rounds (`s46-case-r12-hw1`, `s48-case-r12-hw3`, `s50-case-r12-hw2`, `s49-case-r12-hw4`, $2.62).**
Same scenarios and casts as the 8-round v2 runs, with the Hindu variant as S50 (personal rule). The scratchpad
runner now takes `SCENARIO:CELL:VERSION:ROUNDS`.

- **Muslim (S46): resolved in round 8 again, and qualifies.** "I'm Muslim. We don't serve alcohol at home." She
  turned down drinks in the kitchen; Suresh proposed a cooler outside the front door; all four accepted and all
  debriefs say settled, fairness 5. Rounds 10-12 were padding ("Yeah, me too.").
- **Hindu (S50): resolved in round 5, and qualifies on the definition**, but faith appears only in his thought
  ("They are Hindu, we don't drink"); aloud he said "We don't drink". He accepted no alcohol while his parents
  are there, then drinks after: the same dry-period idea he turned down in the 8-round run. Same setup,
  opposite response, so do not read a single run as a Hindu style.
- **Buddhist (S48): unresolved, with the strongest culture talk.** "For me, as a Buddhist... it's one of my
  precepts." Natalie: "We've known about each other's beliefs since we moved in. Why are you only bringing this
  up now". In round 12 Suresh and Marcus offered a no-alcohol party and to repay Natalie; Xin Yi accepted;
  Natalie did not answer.
- **Control (S49): partly resolved, with the largest concession.** Natalie agreed to an alcohol-free party and to
  put the drink money towards food for Daniel's sobriety; Jun Jie, with his manager invited, did not accept.
- **Across scenario 1 (eight runs with the fixes):** faith needs got workarounds in space or time (void deck,
  outside the door, a dry period), and Natalie challenged the timing of faith objections ("Why didn't you say
  this before?", "Why are you only bringing this up now"). The health need got full removal, at 12 rounds, and
  an apology from Daniel himself instead of a challenge. A pattern to describe, from single runs.
- **Round count:** both resolutions came by round 8, so the extra rounds did not cause them; they gave the
  Buddhist run time to reach a proposal. Case-run spend about $14.20.

**Scenario 3, fasting and the dinner rota (S51-S54, casts FR1-FR4, 12 rounds, $2.63; `s51-case-r12-fr1` to
`s54-case-r12-fr4`).** Built with the scenario 1 fixes: no shared fund, no food rule outside role D (the others
are Catholic or Buddhist, and all Catholic in the Buddhist variant), every need in "For you, ..." form (a test
caught three that were not), and a stake for every role (A cooks only meat dishes, B must eat by 6.30, C cooks
one night only). D named the reason aloud in all four runs.

- **Muslim (S51): unresolved.** "this is what I have to do for my faith." Aisyah offered to eat later and sit with
  them; Jun Jie and Marcus agreed; Natalie refused ("just you watching us eat"), then proposed pausing the rota.
  Aisyah's debrief: Natalie "would rather exclude me than feel a little awkward".
- **Hindu (S52): resolved in round 6, but the deal does not work.** Karthik named Purattasi aloud. Natalie and Jun
  Jie agreed to swap nights, and all four debriefs say every night will now be vegetarian. A swap still leaves
  Natalie cooking meat on Jun Jie's old night. The evaluator and coder accepted it; it qualifies on paper only.
  Report it as an incoherent agreement, like S26's impossible ones.
- **Buddhist (S53): unresolved.** "It's a religious thing." Xin Yi offered to cook her own food on others'
  nights; Natalie objected that it is "not a shared meal", then offered that everyone eat vegetarian and learn
  one dish; Marcus refused.
- **Control (S54): resolved in round 8.** Jun Jie proposed that Daniel cook his own food on Natalie's and Marcus's
  nights; Natalie agreed ("The main thing is that we all eat together"). Daniel's debrief: "isolating... my
  health problem is entirely my own to deal with".
- **Clearest contrast yet:** Natalie, an identical persona in all four casts, rejected "D cooks separately and we
  eat together" for the Muslim and Buddhist needs ("not a shared meal") and accepted the same arrangement for
  the medical need ("The main thing is that we all eat together"). It matches scenario 1's pattern of faith
  needs being challenged and health needs accepted. Still one run per variant.
- Case-run spend about $16.80.

**Scenarios 7 and 2 (S55-S62, K1-K4, 12 rounds, $5.18; `s55-case-r12-k1` to `s62-case-r12-k4`).** Built after a design
review. Scenario 7: every variant asks for the same two days away; the control has the same death with
non-religious duties; nobody outside the team can help. Scenario 2: no flame, incense or sound; every variant,
including the physiotherapy control, asks for an object plus daily use; the window corner is the only free
space. Good runs are logged in `research_questions/good_runs.md`.

- **Scenario 7 (bereavement) resolved in all four runs**; the death carries the need, and faith was named mostly
  in private. Buddhist (S57) qualifies cleanly: thought "The wake is a religious duty for me"; Hafiz refused her
  offer to work at night and took over. Muslim (S55) qualifies, but weakly: resolved in round 12, the coder
  disagreed, and Aisyah had to hand over under pressure from an aggressive Suresh. Hindu (S56) said "for the
  rites" aloud but agreed to finish his section that night (fairness 2). Control (S58): Hui Min refused
  Daniel's offer and took over.
- **Scenario 2 (corner) was unresolved in all four runs, including the control.** The culture talk was the
  strongest yet ("So I just don't have a place to pray in the flat where I live?"; "You can't have a shrine
  next to drying laundry"). Aisyah's and Karthik's debriefs: their religious need was treated "on the same
  level as laundry". In the control, Hui Min said "A medical need for his back is more serious than laundry or
  guests". This is the health-above-faith pattern again.
- **Design flaws found after the runs.** (1) Scenario 2 has no slack: four fixed claims on one corner, and A's
  permanent desk became its own dispute (in S61 it was Priya against Hafiz's desk), much as money did in
  scenario 1. (2) Scenarios 7 and 2 used K casts, so roles A-C are different people in each variant: Suresh,
  an aggressive pitch lead in S55, is not the lead in S57. Variant differences may come from who A is.
  Scenarios 1 and 3 kept A-C fixed, and new scenarios should too.
- Case-run spend about $22.

**Scenario 4, festival-week roster (S63-S66, casts RO1-RO4 with roles A-C fixed as three Catholic colleagues, 12
rounds, $3.16; `s63-case-r12-ro1` to `s66-case-r12-ro4`).** None resolved, including the control (National Day and
a sister's wedding); remaining conflict 4-5 throughout. Rachel (C), written as "not be the one left covering
again", simply refused to work, so four people refused two duty slots: the corner deadlock again. Every need
was written as absolute ("so you need both days", no other childcare), so nobody had anything to trade, and
Natalie made up "flights and hotels... non-refundable" although the script has no money. Culture was named
aloud (Aisyah: "a holiday is not the same as Hari Raya"), and Aisyah's debrief says her religious needs were
treated "the same as a vacation or childcare". But the control D made the same complaint about his sister's
wedding, so this scenario shows no faith-specific difference. Lesson: a dispute over a fixed resource needs
something tradeable, such as future holidays ("I'll cover Hari Raya if you cover Christmas"). Scenario 9 is
not built: its faith needs bind the whole household but a non-faith control cannot, and "no living there
before the blessing" is not a common Catholic practice. Case-run spend about $25.

**Transcript audit (2026-11-09).** At the user's request, I read 20 case transcripts in full (all rated
resolved, plus the near-misses). The evaluator was right about whether an agreement was reached in all 20.
Caveats on meaning: S44 settled who pays, not the need; S52's night swap is incoherent; S36-v1's "partly
resolved" is generous (only two agreed); S61 is arguable, since Hafiz agreed to Xin Yi's wall shelf and nobody
objected, but the coder sided with the evaluator. **One holdout blocked four near-agreements: Natalie (role A)
in S48, S49-v1, S51 and S53**, each with the other three agreed. Role A's stake (keep the party or rota as it
is) makes that role decisive, so scenario 3's faith-versus-health contrast is one agent's behaviour in one
role.

**Scenario 4 v2 (S67-S70, RO1-RO4, 12 rounds, $2.76; `s67-case-r12-ro1` to `s70-case-r12-ro4`).** Version 1
deadlocked, so each person got one tradeable fact (Rachel wants Christmas and the Christmas roster is open;
Natalie could join a car trip a day late, nothing paid; Marcus has childcare on day 2 only; D wants both days,
the day before most). The trade worked: Rachel offered to cover in exchange for Christmas in all four runs.
All four transcripts read in full.

- **Hari Raya (S67): resolved in round 10, coherent.** Aisyah gave up the day before Hari Raya, the one she
  wanted most, so Marcus has childcare; she also offered to work Christmas. Natalie kept both days (fairness
  5). Aisyah (fairness 2): "It feels like I had to be the one to give in." Her thought: "it's a sacrifice I
  should probably make. It shows I'm a team player, which is important since I'm new."
- **Control (S70): resolved in round 6, coherent.** Natalie worked day 1 and joined her trip late, so Jun Jie
  kept both wedding days (fairness 5); Natalie rated fairness 2.
- **Deepavali (S68): unresolved.** Karthik proposed drawing lots ("my prayers aren't just a holiday plan
  either"); Marcus refused to leave childcare to chance. **Chinese New Year (S69): unresolved**, and silent
  from round 9.
- **Who gave way:** same cast and structure, but in the faith run the key agent gave up her most important day,
  while in the control Natalie gave way for the key agent. This matches pork v2 (Aisyah does the sertu
  herself), Hindu bereavement (Karthik works at night) and the faith runs in scenarios 1 and 3. Two caveats.
  Aisyah's own reason was being new, not faith. And a wedding ceremony is a fixed event while "preparing" sounds
  movable, so wording may drive it, as it did in S47/S50. Single runs.
- Case-run spend about $28.

**Working tree (2026-11-08):** `main` was fast-forwarded to `807567c` (the research branch), at the user's request; no merge commit, nothing pushed. Everything after it is still uncommitted. `upstream/update-gpt-6-luna` (`81cd8f6`) is unrelated and was not merged. **Earlier (2026-11-06):** only `807567c` is committed. `373dbb1`, `bdbca79` and `3b65ab9` were
undone into uncommitted changes at the user's request, and run manifests still name them. Never push,
and commit only when asked. `check.py` holds a live API key and is not gitignored: do not stage it.

**Open:** with so few real arrangements, "given that a resolution happens" leaves little data in
S28. `tiny_person.py` line ~749 passes `emotions` as `attention`; left as is so S28 stays comparable.

Tests: add `tests/unit/test_s26_chope_priorities.py` and
`tests/unit/test_move_coding_and_label_probe.py` to the command below; 145 pass.

## Older handoff (2026-11-03), superseded by HANDOVER at the top

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
version of the chope (S04) scenario. (Superseded on 2026-11-05: S28 is now the candidate, see the
section above.) S25 is not ready for a
C0-C4 comparison: its agreements are thin or built on invented facts (see the S25 x5 section).
Read "Evaluator v2.6 and the S25 x5 batch" before doing anything else.

## Research constraints (from the user, 2026-11-03; the question and case-study aim in HANDOVER replace the ones here)

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
