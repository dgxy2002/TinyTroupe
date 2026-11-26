# Real public reactions, news stages 1-4 (classified 2026-11-26; for the user's review)

Data: `haze_ground_truth_stages1_4.csv` (30 reactions, one row each, with quote, source and whether the article was
read in full), built by `tools/build_haze_ground_truth.py`. Coverage check: `haze_ground_truth_coverage.md`.

**Rules used.** Each reaction is assigned to the news stage whose event triggered it, not its calendar date (the
mockery of the 10 October "oxygen" remark counts as stage 4, because that is when the agents receive it). Public side
only, because governments are silent before the cutoff in the simulation; each row is tagged ordinary people, NGO,
commentator or politician, since the simulated citizens are only ordinary people. "None stated" means the source gives
nothing, which is not the same as "no reaction".

## What reality looked like, stage by stage

| Stage (news) | Malaysian side | Indonesian side | Singaporean side |
|---|---|---|---|
| **1** (4 Sep: fires, Sarawak emergency, PSI above 100) | NGOs protest at the Indonesian embassy, demand disclosure and naming Malaysian firms, "not about blaming Indonesia"; residents cope (shorter trips); a columnist calls the haze an "infamous Indonesian export" | NGOs (Walhi, Pantau Gambut, Greenpeace) blame weak enforcement and companies; demand corporate accountability, permit revocation, restoration | nothing found |
| **2** (18 Sep: Malaysia's offer, 95 companies investigated) | nothing found | class action against Prabowo and officials (negligence; national emergency, healthcare, compensation); Jambi street protest ("demand stronger action") | fear and distaste online ("Feeling terrified, never seen such haze during night time before.") |
| **3** (9 Oct: Greenpeace list, schools shut, PSI 192 at F1) | boycott calls against Indonesian brands, which began from a football row (Kahf), with some dismissal ("waste of time") | an Indonesian in Johor writes to Prabowo, ashamed: "Enough is enough. People must come before profits." | F1 fans disappointed but turnout near record |
| **4** (13 Oct: "oxygen" remark, boycott call, no reply to aid offer) | mockery ("How do you quantify O2? But we can definitely quantify haze."); politicians demand an apology; frustration aimed at Indonesia's government; a boycott of Indonesian products ("If we don't teach them a lesson, they won't stop"); MP Syed Saddiq: treat Indonesia as an "outcast" | apology to neighbours and blame of own government ("We're truly sorry for the haze."); calls to declare a national disaster; "SEAblings" solidarity; NGOs reject the "nature" excuse ("disguise environmental and corporate crimes behind natural causes"); an ex-minister's nationalist pushback ("do not insult the entire nation") | disbelief at "oxygen" (a journalist); mask queues, worry |

## By dimension (what the simulation should be compared against)

| Dimension | Malaysian public | Indonesian public |
|---|---|---|
| Emotion | stage 4: mockery, sarcasm, indignation, anger, frustration; earlier: coping | shame and apology (stage 3-4), frustration (stage 2-4) |
| Blame | Indonesia's government and officials (stage 4); companies and secrecy (NGOs, stage 1) | own government (stages 2-4); companies and weak enforcement (NGOs, stage 1-4) |
| Stance to other countries | stage 1 NGOs solidary with Indonesians; stage 3-4 hostile to Indonesian brands and critical of Indonesia | solidary with Malaysians and Singaporeans (apology, "SEAblings"); one nationalist ex-politician |
| Public actions | embassy protest (stage 1), boycott of Indonesian brands and products (stages 3-4), online mockery (stage 4) | class action, street protest (stage 2), open letter (stage 3), viral video and online apologies (stage 4) |
| Demands | disclosure and naming firms (stage 1); an apology (stage 4) | national emergency, free healthcare, compensation, corporate accountability, outside pressure on Jakarta |
| Diversity of views | boycott vs "waste of time" | apologisers vs a nationalist ex-minister (ordinary nationalist voices: anecdotal only) |
| Framing | corporate accountability (NGOs); human cause vs "nature" excuse (stage 4); national rivalry (boycott) | companies vs individuals (NGOs); government incompetence; rejecting the "nature" excuse |

## Governments, windows W1-W4 (`haze_ground_truth_government_w1_4.csv`, 19 moves)

Assigned by date window (W1 4-17 Sep, W2 18 Sep-8 Oct, W3 9-12 Oct, W4 13-15 Oct), not by trigger, because in free play
the simulated governments are compared with what real governments did over the same dates. 11 of the 19 moves later
appear in the news we inject, so they are input to the agents as well as truth.

| Window | Singapore | Malaysia | Indonesia |
|---|---|---|---|
| W1 | advisories, Haze Task Force | Serian emergency; offer of firefighting assets, "shared responsibility" | 138 suspects named, companies probed (police) |
| W2 | community centres opened | Anwar phones Prabowo, asks for an ASEAN ministers' meeting | no-show at the class-action hearing; open to dialogue after the Jambi protest |
| W3 | "We stand ready to assist where we can." | says no reply to its offer | "this is truly nature ... we send oxygen"; 57 businesses identified; "maximum efforts" |
| W4 | legal action could follow; "keep options open" | formal protest "a last resort" | 223 people and 9 companies named; help approved in principle (never taken up) |

Pattern: Singapore and Malaysia stay restrained and cooperative (offers, calls, no protest); conflict comes from
Indonesia's side (the "oxygen" remark) and later Singapore's enforcement. Brunei's government: advisories only, not
tabulated.

## After stage 4 (`haze_ground_truth_later.csv`, started)

One row so far, from the article the user saved in `news_source/independentsg.md`: Indonesian writer Abdul Khalik
(Jakarta Post op-ed, 3 Nov) says Jakarta has returned to "an old political habit: blaming outsiders rather than
confronting failures at home", and that Prabowo treated criticism as an insult. It also reports Balakrishnan meeting
Prabowo on 28 Oct (our timeline has him meeting the foreign minister on 27 Oct; possibly both).

## Caveats for scoring

- **Who speaks.** Much of the real record is NGOs, commentators and politicians; the simulated citizens are ordinary
  people. Scoring should say which kind of real voice a match is to.
- **Gaps.** Malaysian public at stage 2 and the Singaporean public overall are thin; Brunei has nothing. Scored as
  "no data".
- **Boycott timing.** The Malaysian boycott began from a football row before the haze link (stage 3) and was reported
  as haze-driven on 26 October; it is assigned to stage 4 here as a reaction to the boycott call and the "oxygen"
  remark.
- **Two rows rest on search summaries of blocked articles** (Johor Pakatan Harapan; Singapore mask queues) and two on
  search summaries of readable sites; the rest were read in full.
- **Ground truth ambiguity found for the forecast test:** Indonesia approved foreign help in principle (about 15 Oct),
  said on 19 Oct it could handle the fires without foreign help, and had not taken up any offer by 21-23 Oct. Target G1
  ("Indonesia accepts help") is therefore ambiguous; the society's main "hit" on 13 October rests on it.
