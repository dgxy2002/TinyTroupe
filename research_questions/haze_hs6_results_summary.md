# HS6 results summary: five runs against what really happened (2026-11-27)

Five full-timeline runs of the same design (HS6: 13 agents, real news and real government statements fed in eight
stages from 4 Sep to 16 Nov 2026; governments also talk privately). Backbone Gemini 2.5 Pro via OpenRouter, no web
access. Runs: `outputs/society-hs6-e2e1` to `-e2e5`. Details in `haze_society_design.md` sections 14-16.

Results are given in seven simple dimensions: four for ordinary people (Feel, Blame, Others, Act) and three for
governments (Tone, Foresight, Moves).

## How to read the table

- **How close to real (0-1).** An outside LLM judge (Claude Sonnet 5.5, rubric `haze-similarity-v2`,
  `tools/haze_similarity_judge.py`) reads, for each run, stage and country, what the simulated citizens said aloud and
  the real reactions recorded for that stage and country, and rates each of its own dimensions: match 1, partly 0.5,
  mismatch 0, or no data (left out). Each judgement is made twice independently (the two passes agree
  85-95% of the time). Governments are judged the same way, comparing each government's private
  diplomatic talk with what it really did in the following days.
- **The seven dimensions** were set after the runs and are not separate judge scores. Each is the plain average of the
  judge's dimensions it covers, averaged over stages, countries and the five runs. The definition column lists those
  parts with their own scores and the exact wording the judge was given.
- **Moves** also contains two hand scores (government cooperation and conflict), which I scored from the transcripts,
  one per run. They are rougher than the judge scores.
- **Real** is real reactions by people and governments, from news reports and social media (`haze_ground_truth_*.csv`),
  not the news fed to the agents, which both sides share.
- **Coverage.** People rows cover Malaysia, Indonesia and Singapore (Brunei has no real record; Singapore's is thin).
- Quotes are examples; the numbers come from all stages. Rows are sorted by how close to real, highest first.

## Results

### People

| Dimension | Exact definition | Simulated | Real | How they compare | How close to real (0-1) |
|---|---|---|---|---|---|
| **Feel** | How upset are they, and what news sets them off?<br>*emotion* (0.51): the emotions and tone expressed (anger, mockery, shame, frustration, fear, solidarity, resignation...)<br>*triggers* (0.52): which events or statements they react to most (and which they ignore) | "Sending oxygen? Is that what you call this? I had a tour business. It's gone. ... This is our lives you're burning." (Lim Chee Keong, Malaysia, run 2, 13 Oct) | "Supply oxygen? Seriously?" and "How do you quantify O2? But we can definitely quantify haze." (Malaysian netizens, after the 10 Oct remark); "We're truly sorry for the haze." (Jakarta doctor, Threads) | Same anger and shame, at the same flashpoint (the "oxygen" remark). Real Malaysians also mocked; agents rarely did. | **0.52** |
| **Blame** | Who or what do they say caused it, including their own government?<br>*blame* (0.34): whom they hold responsible (Indonesian government, their own government, companies, nature, nobody)<br>*framing* (0.50): how they frame the crisis (nature vs human cause, companies vs governments, national pride, ordinary people suffer)<br>*division within a country* (0.29): whether they turn against their OWN government (blame it, distrust it, are ashamed of it) | "It's not 'nature', it's smoke from fires and it's making our families sick." (Kelvin Tan, Singapore, run 2); "Please don't think that our government speaks for us." (Dewi Lestari, Indonesia, run 2) | "They are trying to disguise environmental and corporate crimes behind natural causes" (Walhi, Indonesian NGO); "The Indonesian (government) needs to do the right thing" (Malaysian tour operator); "Haze & Prabowo's Regime = National Disaster." (Greenpeace activists, Jakarta) | Both say people and companies caused it, not nature. Real people named governments more, and real Indonesians protested against and sued their own government; agents were only embarrassed by one official. | **0.38** |
| **Others** | Are they friendly or hostile towards the other countries?<br>*stance between publics* (0.37): how they treat other countries' governments and people (hostile, critical, neutral, solidary) | "My anger is not with you, it is with the companies who are burning and the governments that let them get away with it, year after year." (Kelvin Tan, Singapore, to the Indonesians, run 3) | Friendly: Indonesians apologising, "SEAblings". Hostile: "If we don't teach them a lesson, they won't stop" (KL boycotter of Indonesian products); "treat them as an outcast in the region" (MP Syed Saddiq) | The friendly side matches; the hostile side (boycotting Indonesia, "outcast") never appears, and it is most of the real Malaysian record. | **0.37** |
| **Act** | What do they do, and what do they demand?<br>*public actions* (0.26): what they do or say they will do (boycott, protest, lawsuit, apology, online campaign, nothing)<br>*demands* (0.15): what they ask for (apology, naming companies, emergency, compensation, legal action, aid) | "A boycott will only hurt us, the small people, the most." (Budi Santoso, Indonesia, run 3); "We need financial assistance. What help is there for small businesses like mine?" (Lim Chee Keong, run 2) | Malaysians boycotted Indonesian brands; Indonesians protested and filed a class action in Pontianak; "Stop making excuses and apologise" (Johor Pakatan Harapan) | Agents only talk and ask for money (run 5 backed a boycott, then dropped it a week later over workers' jobs); real people boycotted, marched, sued and demanded apologies. | **0.20** |

### Governments

| Dimension | Exact definition | Simulated | Real | How they compare | How close to real (0-1) |
|---|---|---|---|---|---|
| **Tone** | Are they friendly or hostile towards each other?<br>*tone* (0.64): is the simulated government's stance towards the other governments (cooperative, defensive, confrontational) like the real one's? | "Talk is no longer sufficient. We demand immediate enforcement." (Singapore, run 3, 9 Oct) | "Do not lecture us, especially the energy ministry, on the importance of honoring contracts." (Indonesia's energy minister, 26 Oct) | Both mostly diplomatic, so this scores well. When real Indonesia turned hostile, the simulated one stayed polite; the sharpest simulated words came from Malaysia (run 5), whose real government stayed restrained. | **0.64** |
| **Foresight** | Does their talk point to what they really did next?<br>*anticipation* (0.38): does the simulated government signal, propose, plan or argue for any of its real next moves before they happen? | "we must express our serious concern regarding the legal notices issued to Indonesian companies by Singapore. This unilateral measure is not helpful" (Indonesia, run 2, 16 Oct) | 21 Oct, Indonesia rebukes countries that "like to insult" it: "Indonesia will not tolerate being continually provoked." | Right direction in 2 of 5 runs (Indonesia objects to Singapore); no run foresaw the energy threat or the gas cut. | **0.38** |
| **Moves** | What concrete steps do they take (help, push-back, measures)?<br>*specificity* (0.36): does the simulated government name concrete acts (notices, numbers, named measures) the way the real one does, or stay vague?<br>*government cooperation* (0.20, hand): hand-scored by me: 1 if simulated Indonesia did not take up help before mid-October, as in reality; 0 if it accepted early<br>*conflict* (0.20, hand): hand-scored by me: average of (a) Indonesia objects to Singapore's legal action in words, 1/0, and (b) it takes or threatens a concrete counter-measure such as the gas cut, 1/0 | "We propose to hold the technical meeting this Wednesday, 28 October, at 10:00 Jakarta time." (Indonesia, run 3); "Indonesia formally accepts Malaysia's generous offer of firefighting assets and personnel." (Indonesia, run 3, 18 Sep) | Indonesia held off on help until 15 Oct, then said on 19 Oct it could manage alone; energy-export threat (22 Oct); gas to Singapore cut by about 8% (24 Oct); Singapore's notices to 10 companies; 17 concessions revoked | Simulated governments act through meetings and dates. Indonesia accepted help early (4 of 5 runs) and pushed back only in words (2 of 5); no run produced the gas cut, fines or revoked licences. | **0.25** |

**Left out: how much people disagree.** The judge's "diversity of views" (whether people of one country disagree or all
say the same) scores 0.32. It is reported as a property of the simulator rather than a dimension: agents agree with
each other too much (18-25% of citizen lines open by agreeing, "Yes", "Exactly", "Same here"), while real
people argued, for example over whether to boycott.

**Overall closeness (judge's own 0-10 rating, 5-run mean):** people 3.54, governments 3.33.

## By country

How close to real (0-1) for each country, averaged over the five runs. In brackets: how many judge scores the average
rests on (one per dimension part and stage with real data, per run). Averages resting on fewer than 7 scores are
shaky. Brunei has no real record. Moves by country uses its judge part (specificity) only, because the hand scores were
not given by country.

**People**

| Dimension | Indonesia | Malaysia | Singapore | All five |
|---|---|---|---|---|
| Feel | 0.44 (70) | 0.46 (45) | 0.68 (50) | 0.52 |
| Blame | 0.37 (105) | 0.38 (59) | 0.37 (32) | 0.38 |
| Others | 0.55 (8) | 0.21 (25) | 0.90 (5) | 0.37 |
| Act | 0.13 (60) | 0.23 (50) | 0.23 (31) | 0.20 |

**Governments**

| Dimension | Indonesia | Malaysia | Singapore | All five |
|---|---|---|---|---|
| Tone | 0.44 (35) | 0.79 (35) | 0.68 (35) | 0.64 |
| Foresight | 0.35 (33) | 0.47 (33) | 0.33 (34) | 0.38 |
| Moves (specificity only) | 0.24 (35) | 0.45 (35) | 0.40 (35) | 0.36 |

## In one paragraph

Across five runs, the simulated society reproduces how people feel and what sets them off (Feel 0.52), and
partly whom they blame (0.38) and how they treat other countries (0.37, the friendly side
only). It does not reproduce what people did or demanded (Act 0.20: no boycott beyond talk, no protests, class
action or apology demands). Governments sound roughly right (Tone 0.64) because they are diplomatic most of
the time, real and simulated alike; their talk only sometimes points to what they did next (Foresight
0.38), and their moves are vague (Moves 0.25): Indonesia takes help too early and never
produces the real counter-measures (gas cut, energy threat). These are five runs of one design on one event.

## Appendix A: scores per run

"Real stage" is the how-close score used above. "Wrong stage" is a background check: the same agents compared with real
reactions from a different point in the crisis, which shows how much of a score would come anyway (for example,
governments sound diplomatic at any time). Moves shows only its judge part here, because the hand scores have no
wrong-stage version. Averaging each stage-country pair over the five runs, the judge's overall rating is higher at the
real stage in 13 of 17 people pairs (4 lower, 0 tied; sign test
p = 0.049) and in 15 of 21 government pairs (6 lower, 0 tied;
p = 0.078).

**People**

| | Feel | Blame | Others | Act | Overall (0-10) |
|---|---|---|---|---|---|
| Run 1, real stage | 0.48 | 0.37 | 0.36 | 0.20 | 3.24 |
| Run 1, wrong stage | 0.27 | 0.33 | 0.17 | 0.18 | 2.59 |
| Run 2, real stage | 0.52 | 0.36 | 0.39 | 0.22 | 3.50 |
| Run 2, wrong stage | 0.24 | 0.23 | 0.21 | 0.18 | 2.32 |
| Run 3, real stage | 0.54 | 0.43 | 0.38 | 0.19 | 3.65 |
| Run 3, wrong stage | 0.23 | 0.29 | 0.12 | 0.10 | 2.32 |
| Run 4, real stage | 0.55 | 0.40 | 0.36 | 0.22 | 3.71 |
| Run 4, wrong stage | 0.27 | 0.30 | 0.15 | 0.08 | 2.65 |
| Run 5, real stage | 0.50 | 0.34 | 0.39 | 0.19 | 3.59 |
| Run 5, wrong stage | 0.23 | 0.23 | 0.25 | 0.16 | 2.41 |
| **Mean, real stage** | **0.52** | **0.38** | **0.37** | **0.20** | **3.54** |
| Mean, wrong stage | 0.25 | 0.28 | 0.18 | 0.14 | 2.46 |

**Governments**

| | Tone | Foresight | Moves (specificity only) | Overall (0-10) |
|---|---|---|---|---|
| Run 1, real stage | 0.67 | 0.30 | 0.30 | 3.33 |
| Run 1, wrong stage | 0.57 | 0.25 | 0.33 | 2.69 |
| Run 2, real stage | 0.64 | 0.45 | 0.40 | 3.62 |
| Run 2, wrong stage | 0.56 | 0.28 | 0.39 | 2.75 |
| Run 3, real stage | 0.62 | 0.39 | 0.45 | 3.26 |
| Run 3, wrong stage | 0.61 | 0.28 | 0.44 | 2.90 |
| Run 4, real stage | 0.64 | 0.45 | 0.26 | 3.15 |
| Run 4, wrong stage | 0.58 | 0.22 | 0.40 | 2.38 |
| Run 5, real stage | 0.61 | 0.33 | 0.39 | 3.29 |
| Run 5, wrong stage | 0.50 | 0.24 | 0.37 | 2.67 |
| **Mean, real stage** | **0.64** | **0.38** | **0.36** | **3.33** |
| Mean, wrong stage | 0.56 | 0.25 | 0.39 | 2.68 |

## Appendix B: the judge's original dimensions

The scores the seven dimensions are built from (five-run means). Hand scores per run: government cooperation
0, 1, 0, 0, 0; conflict 0.5, 0.5, 0, 0, 0.

| Who | Old dimension | Real stage | Wrong stage | Goes into |
|---|---|---|---|---|
| People | triggers | 0.52 | 0.12 | Feel |
| People | emotion | 0.51 | 0.37 | Feel |
| People | framing | 0.50 | 0.34 | Blame |
| People | stance between publics | 0.37 | 0.18 | Others |
| People | blame | 0.34 | 0.18 | Blame |
| People | diversity of views | 0.32 | 0.30 | left out (simulator property) |
| People | division within a country | 0.29 | 0.31 | Blame |
| People | public actions | 0.26 | 0.17 | Act |
| People | demands | 0.15 | 0.11 | Act |
| Governments | tone | 0.64 | 0.56 | Tone |
| Governments | anticipation | 0.38 | 0.25 | Foresight |
| Governments | specificity | 0.36 | 0.39 | Moves |
| Governments | government cooperation | 0.20 | none (hand) | Moves |
| Governments | conflict | 0.20 | none (hand) | Moves |
