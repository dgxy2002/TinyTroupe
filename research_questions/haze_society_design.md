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
