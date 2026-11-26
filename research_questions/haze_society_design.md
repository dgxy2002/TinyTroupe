# Haze society simulator: design note (draft, 2026-11-24)

Status: draft for the user to review; nothing built except the stage coder. Background, timeline and ground truth
are in `haze_2026_sources.md`; the two four-citizen pilots (S123, `outputs/s123-case-v1-hz1`, `-v2-hz1`) are
described in `CLAUDE.md`.

## 1. Goal

Build a simulator of the 2026 Southeast Asian haze that can **predict next actions**: given the real events up to a
date, what do citizens, businesses and governments do next, and how often does the real next step appear across
runs? (User, 2026-11-24, after the Prof's feedback.)

Prof's requirements: the agents cannot search or browse (checked: no tools, no web plugin, only THINK/TALK/DONE);
results are frequencies across runs, never one run; per-agent, per-stage variables (anger, blame, actions); main
figure = per-country curves over the news stages, averaged across runs, with the real events marked; a "society"
with citizens and governments where some people can talk to some others and not to everyone.

Why a society and not one room: both pilots were polite consensus rooms (four parents, one civil audio room). The
real hostility (the boycott, mockery of the "oxygen" remark) happened in public, anonymous, cross-border online
spaces, and the real clashes of interest (smallholders and plantations against those breathing the smoke) were
missing from the cast.

## 2. Cast: 13 agents

Biographies are facts only (age, place, job, household, language, faith), as in the pilots. Nothing tells anyone
what to think about the haze. Government agents speak for their government as a whole ("the Government of
Singapore"); no agent plays a real, named person. Real officials appear only in the injected news.

| ID | Country | Who | Facts that give them a stake |
|---|---|---|---|
| SG1 | Singapore | Kelvin Tan, 43, Jurong West (from the pilots) | Logistics supervisor, partly outdoors; mother with asthma; two children in primary school |
| SG2 | Singapore | Ahmad Faizal, 38, Bedok | Runs a small outdoor-events and team-building company; bookings cancel when the PSI is unhealthy |
| SG-G | Singapore | Government of Singapore | Responsible for public health and the Transboundary Haze Pollution Act |
| MY1 | Malaysia | Farhana, 31, Johor Bahru (from the pilots) | Factory clerk; seven-year-old son whose school closes |
| MY2 | Malaysia | Lim Chee Keong, 47, Selangor | Runs a small tour agency near Batu Caves; tourist bookings have dropped |
| MY-G | Malaysia | Government of Malaysia | Offered firefighting help; its own states (Sarawak, Johor) also had fires |
| ID1 | Indonesia | Budi Santoso, 30, Bekasi (from the pilots) | Ride-hailing driver, outdoors all day; sister in Central Kalimantan |
| ID2 | Indonesia | Dewi Lestari, 36, Pontianak, West Kalimantan | Primary-school teacher in the smoke; school closures; her own children cough |
| ID3 | Indonesia | Sutrisno, 48, Ogan Komering Ilir, South Sumatra | Oil-palm smallholder, 4 hectares; clearing by burning costs far less than machinery; burning is illegal |
| ID4 | Indonesia | Andreas Wijaya, 44, Riau | Estate manager for a palm-oil group listed on the Singapore Exchange (company not named) |
| ID-G | Indonesia | Government of Indonesia | Responsible for fire control, the police investigations and energy exports |
| BN1 | Brunei | Nur Aqilah, 32, Brunei-Muara (from the pilots) | Now a receptionist at a private clinic, not a ministry officer; daughter of five in kindergarten |
| BN-G | Brunei | Government of Brunei | Moved schools to home-based learning; joined Malaysia's call for ASEAN action |

Brunei has almost no ground truth for citizens; its codes are reported but not scored against reality.

## 3. Who can talk to whom

| Channel | Members who speak | Who also reads it | Visible to |
|---|---|---|---|
| National group, one each for Singapore, Malaysia, Indonesia | That country's citizens and business owners (SG1-2; MY1-2; ID1-4) | Own government | Members only |
| Public regional feed | SG1, SG2, MY1, MY2, ID1, ID2, BN1; governments post public statements | Everyone | Everyone |
| Diplomatic channel | The four governments | | Governments only |

- Brunei has no national group (one citizen); BN1 speaks in the public feed and reads her government's statements.
- The smallholder (ID3) and the estate manager (ID4) are not in the public feed: they talk only in the Indonesian
  group, so whatever reaches the region from them goes through other Indonesians.
- Every agent is told, each turn, which channel they are speaking in and who can see it.

## 4. How a run works: rolling forecast

1. **Real history up to a cutoff stage.** The eight dated news updates (`haze_2026_sources.md`) are delivered as
   before, two rounds per stage. Governments do not speak in this part: their real decisions and statements are in
   the news. Citizens and businesses talk freely in their channels.
2. **Free play after the cutoff: 4 rounds.** Every agent, governments included, acts freely. Only physical facts
   are still injected on their real dates (air quality, rain, fires going out); no decisions by anyone.
3. **Compare with what happened next.** A forecast coder marks, for each real next step, whether it appeared
   (proposed, threatened or done, and by whom).

| Cutoff after | Real next steps to look for |
|---|---|
| Stage 4 (13 Oct: "oxygen" remark, boycott call) | Indonesia accepts foreign help; Singapore sends legal notices; the Malaysian boycott spreads; Indonesian citizens apologise to neighbours |
| Stage 5 (16 Oct) | Singapore Exchange questions listed firms; Indonesia blames foreign companies; Malaysia considers a haze law |
| Stage 6 (21 Oct) | Indonesia threatens energy exports and cuts gas to Singapore; "do not lecture us" |
| Stage 7 (26 Oct) | Joint task force to follow the money; Indonesian apology framed as "not our fault"; ASEAN action |

**Tuning rule.** The design is adjusted only on what happens up to stage 4. The pilot runs real history for stages
1-3 and then free play, so it tests both modes without touching stages 5-8, which are the test.
**Correction (2026-11-25):** a cutoff-3 pilot with 4 free rounds runs to 18 October and receives stage 5's
physical facts in round 9, so it overlaps the first test window (stage 5, 16 October). The pilots are not test data,
but behaviour seen in their rounds 9-10 should not be used to tune the design.

## 5. Measurement

- **Stage coder** (`tools/haze_stage_coder.py`, rubric `haze-stage-coding-v2`, Sonnet 5.5, two passes): for every
  agent at every stage, speech and private thought coded separately: anger 1-5; blame (Indonesian, Malaysian,
  Singapore or Brunei government; Indonesian, Singapore- or Malaysia-linked or unspecified companies;
  smallholders; nature); actions proposed and actions rejected (boycott, legal action, demand an apology,
  apologise, accept or offer help, regional cooperation, trade or energy measures, protest, accountability,
  demand government action); stance towards other countries; defending own country; recall of past episodes. For
  the society runs it will also record the channel.
  Checked on the two pilots (2026-11-24, $0.78 for four passes): v1 missed a boycott proposed and withdrawn in the
  same stage and used "legal action" for vague accountability; v2 fixed both. v2 passes agree on anger 92%,
  stance 93%, Indonesian-government blame 17 of 17, boycott rejected 7 of 7; weakest label "companies,
  unspecified" (5 of 10). Codes match the transcripts (e.g. pilot 2 stage 4: Farhana proposes then drops a
  boycott, Budi argues against it).
- **Forecast coder** (to build): per run and cutoff, each real next step marked yes / partly / no with a quote.
- **Main figure:** per country, mean anger and the share of runs blaming each target or proposing each action, over
  the stages, real events marked; forecast hit rates per cutoff beside it.
- The conflict evaluator from the culture work is not used (its "resolved" does not apply here).

## 6. Cost (estimates)

Basis: pilot 2 cost $1.38 for 64 calls (one per agent turn, about 10,300 input and 1,270 output tokens each, $0.022
per call). The society has 15 turns per round before the cutoff and 23 after (governments join), with longer prompts
(40 recent memories, news so far in the persona), so about $0.03 per turn. Pilot: 6 x 15 + 4 x 23 = 182 turns.

| Item | Runs | Estimate |
|---|---|---|
| Pilot: stages 1-3 real, then 4 rounds free play; read in full | 1 | $5-6 |
| Lean: 2 cutoffs (after stages 4 and 6) x 5 runs | 10 | $60-90 |
| Medium: 2 cutoffs x 10 runs | 20 | $120-180 |
| Full: 4 cutoffs x 10 runs | 40 | $240-360 |
| Stage coding | per run | about $0.20-0.30 (pilots: $0.10 per pass with 4 agents) |

Saving to test: run the real history once, save a checkpoint, and start several free-play forecasts from it. Only
the free-play part is paid per forecast. Forecasts from one history vary less, so use 2-3 histories per cutoff.

## 7. Engine (built 2026-11-24, not yet run)

A separate module, so no older scenario, cast or prompt hash changes (all 223 older tests still pass):

- `society/haze_society.py`: preset HS1 (13 agents, 5 channels, 8 stages with full news and physical-only
  versions). The full news reuses the S123 texts word for word, minus the audio-room sentence.
- `society/engine.py`: `ChannelWorld` sends each spoken line only to the channel's speakers and readers (logged in
  `deliveries`); before each turn the agent is told which channel it is in and who can read it. Each round: news to
  everyone, then the Singapore, Malaysia and Indonesia groups, the public feed and the diplomatic channel, each
  speaker offered one turn, order rotating by round; governments only after the cutoff. Checkpoint after every
  round; `<run>-cutoff.json` is kept for forks, which start free play from it (a fork's cost counts only its own
  calls; the history's cost is recorded separately).
- Memory: each prompt shows the first 10 and the last 40 memories (TinyTroupe default 20, which in a multi-channel
  round would cover only the last round), and every news update is also kept in the persona as `news_so_far`, so the
  real history stays in every prompt at the cutoff.
- Prompt: `prompts/tiny_person_society.mustache`, a byte-for-byte copy of the pilots' template with one line changed
  ("ordinary face-to-face interaction" to "ordinary online communication").
- `tools/run_society.py`: command line (see its docstring). `tests/unit/test_haze_society.py`: 6 offline tests
  (routing, government silence before the cutoff, news vs physical facts, 15 then 23 turns per round, cutoff
  checkpoint, fork, the coder reading the transcript).
- Stage coder rubric v3: same as v2 except the opening sentence allows governments and explains the channel tag.

## 8. Open questions

None left before the pilot. Decided (user, 2026-11-24): all agents speak English; one simulator model for everyone
(Gemini 2.5 Pro); government agents are "the Government of X", not named officials; batch size (lean, medium or
full) is chosen after the pilot, from its real cost and whether the design works.

## 9. HS2: government facts and the two fixes (drafted 2026-11-24, approved by the user 2026-11-25)

After pilot 1 (`outputs/society-hs1-pilot1`, $4.14): governments were identical, cooperative PR voices that only
answered their own citizens; time was vague in free play; turn order created a fake grievance. HS2 = HS1 plus:

- **Dated rounds:** every round without news opens with its date ("It is now Wednesday 14 October 2026"), halfway
  between the stage's date and the next stage's.
- **Governments post first** in the public feed after the cutoff (rotating among themselves), then the citizens.
- **Government facts**, added to each government's private knowledge. Rules: only facts known before August 2026;
  same headings for every government (economic stakes, relations, past episodes); facts, not instructions; nothing
  from 2026. Lines I could only state as interpretation ("foreign criticism plays badly at home") were dropped.

| Government | Added text | Source |
|---|---|---|
| Singapore | In June 2013 Singapore's PSI reached a record 401. | Widely reported (2013 haze); recheck before citing |
| Singapore | In 2014 Singapore passed the Transboundary Haze Pollution Act, and in 2015 it served notices under the Act on Indonesian companies and asked a Singapore-listed paper group for information about its suppliers' land. | NAS archive, MEWR/NEA press release 2 Oct 2015: https://www.nas.gov.sg/archivesonline/data/pdfdoc/20151002005.htm |
| Singapore, Indonesia | Singapore has been the largest source of foreign investment in Indonesia for about a decade. | Databoks (Indonesian investment ministry data): https://databoks.katadata.co.id/en/economics-macro/statistics/6ae03bf1844d7/singapore-the-largest-source-of-foreign-investment-in-indonesia-over-the-last-15-years |
| Malaysia | In June 2013 a haze emergency was declared in Muar and Ledang, Johor, after the air pollutant index passed 700. | The Star, 23-24 Jun 2013 (API 746): https://www.thestar.com.my/News/Nation/2013/06/23/Haze-API-in-Muar-spikes-at-746/ |
| Malaysia | Nearly 7,000 Malaysian schools were closed at the worst point of the 2015 haze, and more than 1,000 in 2019. | 2015: The Malaysian Insight (via search summary); 2019: AFP about 1,500, Malaysiakini about 2,400 (https://www.aljazeera.com/news/2019/9/19/malaysia-indonesia-shut-thousands-of-schools-as-haze-worsens), so "more than 1,000" |
| Indonesia | Indonesia is the world's largest palm-oil producer. Millions of Indonesians in Sumatra and Kalimantan live in the smoke themselves. | General knowledge; recheck the first before citing |
| Indonesia | Indonesia was the last ASEAN member to ratify the ASEAN haze agreement, in 2014. | Jakarta Post 17 Sep 2014; Mongabay: https://news.mongabay.com/2014/09/after-12-years-indonesia-finally-ratifies-transboundary-haze-agreement/ (instrument deposited Jan 2015) |
| Indonesia | **Flagged:** In June 2013 the Indonesian minister coordinating the haze response publicly criticised Singapore's complaints about the haze, and Singapore's prime minister declined to answer in kind. | Agung Laksono, 20 Jun 2013, "behaving like a child": https://www.rappler.com/world/31753-indonesia-singapore-behaving-like-a-child-over-haze |
| Brunei | Brunei's economy rests on oil and gas. In September 2019 haze from fires in Kalimantan reached Brunei, and in the 1990s Brunei closed schools because of haze. | 2019: Wikipedia "2019 Southeast Asian haze"; 1990s: Borneo Bulletin (via search summary); recheck before citing |

Flag on the Indonesia 2013 line: it is a real pre-2026 fact and a real Indonesian government would know it, but it is
the closest thing to the 2026 "oxygen" remark (Laksono also said in 2013 the fires were "because of nature"; that
part is deliberately left out). Keeping it raises the chance the Indonesian government turns defensive because we
told it about its own past; dropping it leaves Indonesia without any "relations" history. **User decision 2026-11-25: keep it**, and say so in any write-up.

Unchanged from HS1: Singapore's line that it imports pipeline gas from Indonesia and Indonesia's line that it exports
it (both were already in HS1; they bear on the real 24 October gas cut, which falls in the stage 6 to 7 test window). **User decision 2026-11-25: keep both.**

Code: `HAZE_SOCIETY_V2` in `society/haze_society.py`; switches `date_every_round` and `governments_post_first` (off in
HS1, and left out of the preset hash while off, so HS1 keeps the hash pilot 1 recorded; a test pins it). 232 tests
pass.

## 10. HS3 and HS4 (2026-11-25)

- **HS3** = HS2 with governments monitoring their national groups silently: they still receive every line, but the
  shared setting, the turn cue and the citizens' contact lists no longer mention them (`Channel.hidden_readers`), and
  each government's facts say "its members are not told this". Why: in the HS2 history pilot citizens knew the
  government read their group, but governments cannot speak before the cutoff, so "still no reply" became a main
  grievance. Tested in `outputs/society-hs3-pilot1` ($4.16).
- **HS4** = HS3 plus one sentence in each turn cue (`Channel.cue_note`): the public feed "This is public: anyone in the
  region can read it, including people and governments of other countries."; the diplomatic channel "This is private:
  only the four governments can read it; the public cannot." Why: in the HS3 test Singapore's government wrote a
  message addressed "to diplomatic channel" while in the public feed. Mechanical only; not yet run.
- **Tuning stopped after HS4** (my recommendation): the cutoff-3 pilots overlap the first test window (section 4
  correction), so further behavioural changes would partly use test data. HS4 is the candidate frozen design for the
  batch, which awaits the user.

## 11. Forecast targets for the cutoff after stage 4 (fixed 2026-11-26, before any forecast was scored)

Window: 14-23 October 2026 (free-play rounds 9-12 are dated 16, 18, 21 and 23 October). Re-researched 2026-11-26;
each target confirmed by at least one report beyond our original timeline. Rules (yes / partly / no) are in
`tools/haze_forecast_coder.py` (`TARGETS_CUTOFF_4`, rubric `haze-forecast-coding-v1`). Primary targets are government
moves and decide go / no-go; secondary targets are public reactions.

| ID | Real event | Date | Sources |
|---|---|---|---|
| G1 | Indonesia approves foreign firefighting help in principle (offers had gone unanswered; later reports say none taken up yet) | about 15 Oct | Reuters via Business Recorder; Mothership "Indonesia's Prabowo approves foreign assistance" |
| G2 | Police name 223 people and 9 companies as suspects | reported 14 Oct | Tempo; Business Today 14 Oct; Xinhua 15 Oct; The Online Citizen 16 Oct |
| G3 | Singapore serves haze-law notices on 7 Indonesian firms (Grace Fu, 16 Oct), 3 more on 19 Oct | 16-19 Oct | The Star, Bernama, NST, SCMP, Jakarta Post 16-18 Oct; AP 19 Oct |
| G4 | Singapore says the Singapore Exchange is questioning 7 listed agriculture firms (Shanmugam) | 19-20 Oct | Mothership; AsiaOne; CNBC 20 Oct |
| G5 | Malaysia's cabinet told no Malaysian plantation firms involved | 16 Oct | Bernama; Malaysiakini; Media Selangor |
| G6 | Malaysia open to a Singapore-style haze law (deputy minister Syed Ibrahim) | 21 Oct | The Star 21 Oct; The Malaysian Reserve 21 Oct; Malaysiakini |
| G7 | Prabowo: foreign companies involved, threatens to expose them; vows to revoke foreign firms' licences | 21-22 Oct | Kompas 21 Oct; Mothership; Malay Mail 21 and 23 Oct; Bernama; Tempo |
| G8 | Prabowo rebukes "certain countries that like to insult the Indonesian nation" | 21 Oct | Kompas 21 Oct; Mothership; Malay Mail 21 Oct |
| G9 | Bahlil: reconsider energy exports to countries that do not respect Indonesia | 22 Oct | Jakarta Post via ANN 27 Oct; Fortune 26 Oct; Wikipedia |
| C1 | Malaysians boycott Indonesian products (Indocafe, Sosro, Kara), after the MP's 13 Oct call | from 13 Oct, reported 26 Oct | Straits Times via ANN; BBC; Red Hot Singapore |
| C2 | Indonesians apologise online and urge neighbours to pressure Jakarta | from 12 Oct, reported 22 Oct | Jakarta Post 22 Oct; ANN |

Changes from the draft list: the Indonesian citizens' apology is secondary (its quoted example is from 12 October, before
the cutoff); the energy threat stays (22 Oct, inside the window) but the gas cut (24 Oct) is "real later"; G8 is new
(Prabowo's rebuke was missing from our timeline); C1 is now a boycott of Indonesian products, as reported. Also real in
the window, and so not false alarms: Wong's "legal action could follow" (15 Oct), shelters and N95 masks, Lutfi's
challenge, Shanmugam's "every legal and regulatory lever", 97 companies identified, NEA queries to 10
Singapore-registered firms (23 Oct), Malaysia avoiding criticism. Note for reading results: real Malaysian and
Singaporean leaders largely refrained from criticising Indonesia; the friction came from Indonesia's side.

Baseline: `tools/haze_baseline_forecast.py` gives Gemini 2.5 Pro the same four news updates and asks for a ten-day
forecast. Decision rule (agreed 2026-11-24): a batch only if the society gets several primary targets in at least 2 of
3 forecasts and does at least as well as the baseline.

## 12. First prediction test, cutoff after stage 4 (2026-11-26; user: "do a test ... never do a batch yet")

- **Baseline:** `outputs/haze-baseline-c4-v1` (10 direct forecasts from Gemini 2.5 Pro given the same 4 news updates;
  $0.39). **Society:** `outputs/society-hs4-c4-test1` (HS4; R01 history to 13 Oct plus 4 free rounds, $4.74; F01 and
  F02 forked from R01's cutoff, $2.08 each). All read in full.
- **Scoring:** `tools/haze_forecast_coder.py`, rubric v2 (v1 gave "yes" for a boycott of listed companies; v2 requires
  the quote to show what makes it "yes"; changed before any society forecast was scored). Two passes each: baseline
  agree 109/110, society 32/33; disagreements settled by the written rules (B03 G6 partly, F01 G7 partly). Outputs
  `haze-forecast-v2-baseline-c4` (+ `-b`), `haze-forecast-v2-society-hs4-c4-a`/`-b`.
- **Result (per forecast, primary = 9 government targets):** baseline 2.1 clear hits + 2.1 partly, 9.2 false alarms
  (major actions that did not happen); society 0.7 clear hits + 2.0 partly, 5.3 false alarms. Per target, baseline
  (10) vs society (3): accept help G1 4y2p vs 2y1p; arrests/suspects G2 8y1p vs 0y1p; Singapore legal notices G3
  4y1p vs 0y2p; Singapore Exchange G4 4y4p vs 0; Malaysia denial G5 0y3p vs 0; Malaysia haze law G6 0y4p vs 0y1p;
  foreign companies G7 1y5p vs 0y1p; Prabowo's rebuke G8 0y1p vs 0; energy threat G9 0 vs 0. Public reactions:
  boycott C1 1y9p vs 0y2p; Indonesian apologies C2 0y10p vs 0y1p.
- **Decision rule (agreed 2026-11-24): no-go.** The society got at most one clear hit per forecast and did worse than
  the baseline. Its governments stay vague and cooperative (statements, meetings, relief packages), so they rarely
  name a concrete real move; the baseline names many concrete moves, right and wrong. Neither predicted Indonesia's
  escalation (Prabowo's rebuke, the energy threat). Fewer false alarms in the society mostly reflect fewer concrete
  predictions overall.
- **Caveats:** 3 society forecasts from one history (forks share it); the baseline was asked directly for concrete
  predictions, the society agents were not asked to predict anything; free play is 4 rounds; the judge is an LLM, its
  hits were checked by hand. The public/private slip persisted in HS4 (governments posted messages addressed "to
  diplomatic channel" in the public feed in all three forecasts), so the cue did not fix it.
- **Test-data caveat:** the cutoff-4 window has now been looked at. Any design change made after this test must not
  be judged on cutoff 4 again; the cutoff after stage 6 (21 Oct; gas cut, "do not lecture us", task force) is still
  unseen.
- **Cost of the test:** $10.60 (coder check $0.07, baseline $0.39, baseline scoring $1.02 incl. the discarded v1,
  society $8.90, society scoring $0.22).

## 13. First full-timeline run with option B, and the similarity evaluation (2026-11-26)

Run `outputs/society-hs5-e2e1` (HS5, cutoff 8, 16 rounds, 240 calls, $5.35, no failures; read in full). Evaluation:
similarity judge `tools/haze_similarity_judge.py` (rubric haze-similarity-v1; passes `haze-similarity-v1-hs5-e2e1-a`
and `-b2`; pass `-b` crashed on a malformed reply after about 35 calls and was discarded; a retry for malformed
replies was added, scoring instructions unchanged) and stage coder v3 (`haze-coding-v3-hs5-e2e1-a`/`-b`).
Evaluation cost about $1.85 incl. the discarded pass; total about $7.20.

- **Reliability:** judge passes agree on 88% of dimension scores (287), overall scores differ by 0.17 on average;
  coder passes agree on anger 89% (within one point 100%), stance 92%.
- **Similarity to real public reactions (0-10, mean of two passes):** matched stages 3.65 vs wrong-stage control 2.69;
  matched higher in 12 of 17 stage-country pairs, lower in 4, tied in 1 (sign test p = 0.08; one run). Highest:
  Malaysia and Singapore at stage 4 ("oxygen", 6.5), Malaysia at stage 8 (apology, 5.5), Singapore at stage 5 (5.0),
  Indonesia at stage 4 (5.0). Lowest: Indonesia stages 1-2 and Malaysia stage 3 (below the control), where the real
  record is NGOs' enforcement demands and a football-born boycott.
- **By dimension (match = 1, partly = 0.5; matched vs control):** emotion 0.58 vs 0.39, framing 0.58 vs 0.39,
  diversity 0.48 vs 0.25, blame 0.38 vs 0.29, stance 0.33 vs 0.20 (only 6 cells with data), actions 0.27 vs 0.15,
  **demands 0.20 vs 0.20** (no better than the wrong stage). Indonesian public actions 0.08: real protests, class action
  and banners never appear; simulated citizens talk, worry and pray.
- **Stage coder curves (spoken anger, 1-5):** every country peaks at stage 4 (the "oxygen" remark); Indonesia then
  falls back to 1.0 by stage 7; Singapore rises again at stages 7-8 (gas cut 3.0, apology 3.0); Malaysia stays at 2.5
  from stage 6 on. Blame of Indonesia's government by all eight citizens at stage 4 (Indonesians included), by
  Singaporeans and Malaysians again at stages 7-8; Malaysians blame their own government at stages 5-6 (its denial
  that Malaysian firms were involved). No Indonesian citizen apologises to neighbours; one boycott mention.
- **Reading:** the simulation reproduces how ordinary people feel and frame the big moments (mockery at "oxygen",
  scorn at "not our fault", shame among Indonesians) but not what real publics did or asked for (boycott of Indonesian
  products, protests, lawsuits, an emergency declaration, an apology). Caveats: one run; the judge is an LLM; much of
  the real record is NGOs, commentators and politicians; absolute scores are low partly for that reason.

## 14. HS6: governments talk privately, public words stay scripted (2026-11-26)

User: "let government talk but the factual news of what government say should still be injected. then see if theres any
more improvements then run 1 run only and score it". HS6 = HS5 plus a turn for each government in the diplomatic channel
every round (citizens never see it); each government is also told its own scripted posts. One full-timeline run,
`outputs/society-hs6-e2e1`: 304 calls, $6.83, no failures, all 66 government TALK lines in the diplomatic channel. Read in
full. Scoring $2.34 (judge v2 public + government, two passes; stage coder v3, two passes). HS5 rescored on v2 for the
comparison ($0.97).

**Scores (judge `haze-similarity-v2`, 0-10 overall, mean of two passes; one run each, so describe, do not count):**

| | HS5 public | HS6 public | HS6 governments |
|---|---|---|---|
| Passes agree exactly | 90% | 85% | 90% |
| Matched vs wrong-stage control | 3.53 vs 2.60 | 3.24 vs 2.58 | 3.33 vs 2.69 |
| Higher / lower / tied | 9 / 3 / 5 (p = 0.15) | 10 / 5 / 2 (p = 0.30) | 11 / 6 / 4 (p = 0.33) |

Public dimensions, HS6 matched vs control: triggers 0.46 vs 0.14, emotion 0.50 vs 0.40, framing 0.45 vs 0.42, stance 0.36
vs 0.17, blame 0.37 vs 0.26, demands 0.16 vs 0.12, actions 0.23 vs 0.25 (Indonesia 0.00), division 0.30 vs 0.29.
Government dimensions: tone 0.67 vs 0.57, anticipation 0.30 vs 0.25, specificity 0.30 vs 0.33.

**What the governments did in private.** Round 1: identical "deeply concerned" notes (Singapore sent the same text to
each government separately). Round 2 (11 Sep): Malaysia offered help and Indonesia accepted at once (really: no reply
until 15 Oct). Round 3: Singapore described a C-130 for cloud seeding, an SCDF team and satellite hotspot data, none of
which is in its persona or the news; this matches Singapore's 2015 offer, so it is probably recall. Rounds 6-11: all four
agreed to a joint statement (never real), set 24-hour deadlines, and Indonesia stalled. Round 12 (23 Oct): Indonesia
blocked it: "Unilateral actions, such as the legal notices issued by Singapore, complicate the spirit of a collective
ASEAN response." Rounds 13-14: Indonesia demanded sovereignty and non-interference wording and called Singapore's law
"extraterritorial"; Malaysia mediated; Brunei proposed strengthening the ASEAN haze agreement instead; all agreed. This is
the first Indonesian pushback any run generated, in the direction of the real 21-26 Oct rebuke, but it came after the
Prabowo and Lutfi news was delivered and named no concrete measure (no energy lever, no licence revocations); the judge
scored Indonesia 2.5-3. Governments twice addressed "the public regional feed" from inside the diplomatic channel
(routed privately; nothing reached citizens). Brunei acted as the broker throughout.

**Citizens (same inputs as HS5, so a second replicate).** Anger by country and stage correlates 0.77 with HS5 (32 cells,
mean gap 0.39); peak at stage 3-4 again. Same patterns: anger at the "oxygen" remark in every country, Budi and Dewi
embarrassed by their own government, "we are all victims" at the Greenpeace list (Budi first turned it on Malaysians and
Singaporeans: "your own companies"), the gas cut dismissed as "politicians fighting", the apology as "just words". New
here: no boycott backed (Andreas: boycotts "hurt ordinary workers"; HS5 had 3 boycott codes); Farhana caught her
government's "no Malaysian companies" line against the Greenpeace list; an Indonesian split at stage 8 (revoked
concessions vs investors and jobs; Sutrisno on fruit-bunch prices). Still never: protests, class action, Indonesian
apology. Both business owners close their businesses twice (continuity error). Properties: echo 23% (HS5 24%),
parroting 0% (2%), recall codes all "every few years" except Kelvin's biographical 2015.

**Reading.** Letting governments talk did not raise public similarity (citizens cannot see it; the difference from HS5
is run-to-run noise). Government talk is closer in tone than a wrong window but not in what they actually did:
specificity equals the control. It shows one more failure mode: governments invent a consensus project (the joint
statement) and spend the episode negotiating it.

## 15. HS6 replicates: three runs compared (2026-11-26; user: "ok run the 2 runs")

Two more HS6 full-timeline runs, unchanged design, scored like run 1 (judge v2 public and government, two passes; stage
coder, two passes; properties). `outputs/society-hs6-e2e2` ($6.71 run, $2.30 scoring) and `society-hs6-e2e3` ($6.61,
$2.18); $17.80 in all against an estimate of $18.40. Both transcripts read in full, government talk included. The
tables below come from a session script (judge and coder CSVs only, no model calls).

**Scores.**

| | run 1 | run 2 | run 3 | pooled |
|---|---|---|---|---|
| Public: matched vs control | 3.24 vs 2.59 | 3.50 vs 2.32 | 3.65 vs 2.32 | 3.46 vs 2.41 |
| Public: higher / lower / tied (p) | 10/5/2 (0.30) | 12/2/3 (0.01) | 11/1/5 (0.01) | 13/4/0 of 17 pairs averaged over runs (0.049) |
| Government: matched vs control | 3.33 vs 2.69 | 3.62 vs 2.75 | 3.26 vs 2.90 | 3.40 vs 2.78 |
| Government: higher / lower / tied (p) | 11/6/4 (0.33) | 11/3/6 (0.06) | 11/5/5 (0.21) | 13/5/3 of 21 pairs averaged (0.10) |
| Passes agree (public / government) | 85% / 90% | 88% / 92% | 85% / 95% | |

Only 8 of 17 public pairs (7 of 20 government) beat the control in every run, so single pairs are noisy; the direction is
stable once runs are averaged. Pooling the 51 run-pairs as independent gives p < 0.01, but the pairs share ground truth,
so the averaged test is the one to cite.

Dimensions (matched, mean of three runs, range in brackets; control mean): triggers 0.50 (0.46-0.54; 0.12), emotion 0.52
(0.50-0.56; 0.36), framing 0.52 (0.45-0.59; 0.34), stance 0.37 (0.36-0.39; 0.17), blame 0.34 (0.28-0.37; 0.20), diversity
0.34, division 0.30 (control 0.30), actions 0.24 (Indonesia 0.08), demands 0.16 (control 0.13). Government: tone 0.64
(control 0.58), anticipation 0.38 (0.30-0.45; control 0.27), specificity 0.38 (control 0.39). Every dimension moved
by 0.15 or less between runs; the ordering (triggers, emotion, framing well above control; demands, actions,
specificity at control) held in all three.

**Anger curves** (citizens, says, country x stage, mean of the two coder passes): correlations between runs 0.46-0.71
among the three HS6 runs, 0.65-0.77 with HS5 (mean absolute gaps 0.39-0.72 on the 1-5 scale). Peak at stage 3 or 4 (PSI
192 and the Greenpeace list, or the "oxygen" remark) in every country and run. Brunei's curve rests on one citizen.

**Events, out of 3 runs.**

| Event | Count | Notes |
|---|---|---|
| Indonesia privately disowns the "oxygen" remark | 3 | |
| Singapore and Malaysia promise to investigate their own listed firms after the Greenpeace list | 3 | real Malaysia said none were involved |
| Governments invent process (meetings, contact points, working groups, frameworks) | 3 | the main diplomatic content in every run |
| Indonesia pushes back on Singapore's legal notices | 2 | run 1 from 23 Oct; run 2 from 16 Oct ("unilateral", two tracks, sovereignty); run 3 never, even after the gas cut |
| Indonesia accepts help early (before 15 Oct) | 2 | runs 1 and 3; run 2 hedged ("liaise to coordinate") |
| Invented joint statement | 1 | run 1 |
| Any government raises the gas cut in private | 0 | |
| Indonesia takes or threatens a concrete measure | 0 | |
| Citizens back a boycott | 0 | Indonesians reject it in all 3 ("hurts the small people"); HS5 had 3 boycott codes |
| Indonesians distance themselves from their government at "oxygen" | 3 | |
| Explicit Indonesian apology to neighbours | 1 | run 3: "as an Indonesian, I'm just so sorry and embarrassed" |
| Citizens notice the gas cut | 3 | "just politics"; Indonesians: "our government is picking fights" |
| "Not our fault" apology mocked | 2 | runs 2 and 3; run 1 "just words" |
| Protests, petitions, class action | 0 | |

**Run differences.** Run 2: citizens turned their demands on their own governments (17 and 16 "demand government
action" codes vs 5-6 in runs 1 and 3: Ahmad, Farhana, Lim, Nur Aqilah asking for relief), and the governments answered "to
public regional feed" from the diplomatic channel 8 times (Malaysian relief package "launched", Brunei N95 handout); none of
it reached citizens (checked: channel `diplomatic`), so Nur Aqilah later said her government "never even answered us".
Run 1 did this twice, run 3 never. Run 3: governments fully unanimous; Indonesia named an invented official, "Mr. Hassan
Wirajuda" (the name of a former Indonesian foreign minister). Continuity: business owners closed twice in run 1 only.

**Properties.** Echo 23% / 20% / 18%; parroting 0% / 1% / 1%; recall codes 19 / 0 / 3, the only years recalled are
Kelvin's biographical 2015 (run 1) and the "since 2015" in the stage-5 news (run 3). No leak.

**Reading.** The public result holds up across replicates: in each run the matched stage beats the wrong stage, and
averaged over three runs 13 of 17 stage-country pairs do (p = 0.049). What is reproduced is stable: what triggers
reactions, how angry people are and how they frame it. What is not reproduced is also stable: demands, public actions
(Indonesian protests and class action never appear) and the boycott (backed in no HS6 run). Government talk is somewhat
closer than chance in what comes next (anticipation 0.38 vs 0.27) but not in what governments actually did
(specificity at control); whether Indonesia turns on Singapore varies from run to run (2 of 3), and no run produced the
energy lever. One run is not enough to judge a design: run 1 alone looked like noise (p = 0.30).

## 16. HS6 replicates 4 and 5: five runs compared (2026-11-27; user: "can you run 2 more, then update the values")

Runs `outputs/society-hs6-e2e4` ($6.38, 304 calls) and `-e2e5` ($6.73), each scored with judge v2 public and government
(two passes) and the stage coder (two passes): $8.55 and $9.01 in all, $17.56 for both (estimate about $18). Both read in
full, government talk included. Summary regenerated in `haze_hs6_results_summary.md` by `tools/haze_hs6_summary.py` (hand scores in
`haze_hs6_hand_scores.json`); per-run tables by `tools/haze_hs6_compare.py`.

- **Scores, five runs:** public real stage 3.54 vs wrong stage 2.46; pairs averaged over runs 13 of 17 higher, 4 lower
  (p = 0.049, unchanged). Government 3.33 vs 2.68; 15 of 21 higher, 6 lower (p = 0.078). Runs 4 and 5 public 3.71 and 3.59
  (control 2.65, 2.41); government 3.15 and 3.29 (2.38, 2.67). Dimensions moved at most 0.03 from the three-run values.
- **Seven simple dimensions** (user, 2026-11-27; equal-weight averages of the judge dimensions, no new judge calls;
  diversity dropped and kept as a simulator property): Feel 0.52 (emotion, triggers), Blame 0.38 (blame, framing,
  division), Others 0.37 (stance), Act 0.20 (actions, demands), Tone 0.64, Moves 0.25 (specificity, plus hand-scored
  cooperation and conflict), Foresight 0.38 (anticipation).
- **Hand scores** (same rules): cooperation 0, 0 (Indonesia accepted help on 11 Sep in both); conflict 0, 0 (no
  objection to Singapore's legal action, no counter-measure). Five-run means 0.20 and 0.20.
- **Run 4:** unanimous; Indonesia disowns "oxygen"; Singapore and Malaysia promise to investigate their own listed firms;
  process drift (ministerial meeting, technical meeting, joint working group); Singapore's C-130 / SCDF / satellite
  package again (as run 1). Only friction: Malaysia asks Indonesia to explain its "ground personnel" preference. Citizens:
  no boycott discussed; Indonesians call the remark "embarrassing"; the gas cut noticed and called a distraction; "not
  our fault" apology mocked.
- **Run 5:** the sharpest governments so far, but Malaysia against Indonesia (real Malaysia was restrained): "Frankly, it
  is not sufficient. The comments were a grave insult"; "Our patience is exhausted". Indonesia stalls on a deployment
  schedule and claims a "productive" meeting; no word on Singapore's notices; at the end it resists a binding framework
  ("strengthen ... the existing ASEAN Agreement"). Invented: Brunei financial assistance. Citizens: all six public-feed
  speakers backed a boycott at the "oxygen" stage, Indonesians included (first in HS6); a week later Andreas and Sutrisno
  raised workers' jobs and every one withdrew ("I didn't think about the workers"); Malaysians distrusted their
  government's "no Malaysian companies" line. One garbled line (Sutrisno, Chinese characters and broken pinyin).
- **Properties:** echo 23% and 25%, parroting 1% and 1%, recall codes only "earlier" (5 and 2), no year leaked.
- **Out of 5:** Indonesia accepts help early 4; objects to Singapore's notices 2; gas cut raised by any government 0;
  boycott backed by citizens 1 (then dropped); Indonesians distance from own government at "oxygen" 5.
