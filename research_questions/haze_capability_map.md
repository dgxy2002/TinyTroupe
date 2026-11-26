# Haze simulator: where it predicts and where it does not (draft, 2026-11-26)

Goal (user, 2026-11-26): not to predict everything, but to map where the simulator can predict and where it cannot.
This note tags every real event and every prediction from the first test (cutoff after 13 October), states the
patterns, and fixes hypotheses to test on the unseen cutoff after 21 October before any run. Everything here is hand
tagging by me from transcripts I read in full; no model calls. Tagging script: `tools/haze_capability_tags.py`.

## Tags

Adapted from CAMEO / PLOVER event coding (international relations), plus two classes this episode needs:

| Tag | Meaning | Examples |
|---|---|---|
| COOP-V | cooperation between countries, said | welcoming help, proposing a meeting, an apology |
| COOP-M | cooperation between countries, done | accepting aid, a joint task force, sending firefighters |
| CONF-V | conflict between countries or peoples, said (CAMEO: demand, criticise, reject, threaten) | a rebuke, summoning an ambassador, "do not lecture us", an energy threat, denying blame |
| CONF-M | conflict, done (CAMEO: protest, reduce relations, coerce) | a national boycott, the gas cut, a protest at an embassy |
| ENF-V | enforcement against companies, threatened or intended | "will not hesitate to act under the haze law", "open to a law" |
| ENF-M | enforcement against companies, done | legal notices served, suspects named, licences revoked, exchange queries |
| DOM | domestic protection | masks, school closures, relief packages, firefighting at home |

Also: actor (government or public) and specificity (S: a concrete act with a target or number; Gn: a general intent).
Target hits scored "partly" count as general. Limits: one tagger (me), tags chosen after seeing the 13 October results,
few real events per class.

## Cutoff after 13 October: what each method predicted (per forecast; baseline 10, society 3)

| Type | Baseline | Society | Real events (11 targets, total) |
|---|---|---|---|
| COOP-V | 2.9 | 2.3 | 1 |
| COOP-M | 0.7 | 1.7 | 1 |
| CONF-V | 3.0 | 0.7 | 3 |
| CONF-M | 1.1 | 0.7 | 1 |
| ENF-V | 1.6 | 2.0 | 2 |
| ENF-M | 3.9 | 1.3 | 3 |
| DOM | 3.9 | 2.0 | 0 (not targeted; masks and closures were real) |

- **Specific enforcement acts:** baseline 3.2 per forecast, society **0.0** (the society's enforcement is all intent:
  "will not hesitate to act", "pursuing legal action").
- **Between countries:** baseline 3.6 cooperation vs 4.1 conflict per forecast; society **4.0 vs 1.3**. Real targets:
  2 cooperation, 4 conflict.
- **Who starts the conflict:** baseline's conflict comes mostly from Malaysia's government (summoning Indonesia's
  ambassador in 9 of 10 forecasts; the real Malaysian government avoided criticism and ruled out protests); the
  society's only conflict is Singapore and Malaysia demanding Indonesia's list of companies. Real conflict came from
  Indonesia's government (denial of blame, Prabowo's rebuke, energy threat) and Malaysia's public (boycott) and
  Malaysia's denial of its firms' role.
- **Public action:** baseline 3.8 public actions per forecast (campaigns, protests, hashtags), society 1.3. The
  society's citizens mostly complain to their governments rather than act.
- **Invented (not found among real events):** baseline 9.2 per forecast, society 5.3. Society: 86% of its said
  cooperation invented (meetings, joint mechanisms), half its domestic moves invented (relief packages). Baseline:
  87% of its said conflict invented (ambassador summons, protest notes, rebukes by Malaysia and Singapore). "Invented"
  means not among events we found; some may have happened unreported.

**Ground-truth caveat found 2026-11-26:** target G1 (Indonesia accepts foreign help) is ambiguous. Indonesia approved
help in principle around 15 October, said on 19 October it could handle the fires without foreign help, and had taken
up no offer by 21-23 October. The society's main hit (G1 in R01 and F02) rests on it; rescore G1 as "partly real".

## Patterns, stated as hypotheses for the unseen cutoff (after 21 October)

Fixed 2026-11-26, before any run on that cutoff. Society = HS4 unchanged; baseline = same direct question.

- **H1, concrete enforcement:** the society predicts no specific enforcement act against companies; the baseline
  predicts at least one per forecast on average. Real acts in the window: NEA information requests to 10
  Singapore-registered firms (23 Oct), Singapore's haze-law amendment (4 Nov), 17 concessions revoked (announced 15 Nov).
- **H2, cooperation skew:** the society's between-country moves are mostly cooperation (at least 2 to 1), and it hits
  cooperation targets (task force, apology, Malaysia's diplomacy-first line) more often than conflict targets (energy
  threat, gas cut, "do not lecture us").
- **H3, conflict from the source country is missed:** neither method predicts Indonesia's material conflict (the gas
  cut, 24 Oct); the baseline again puts most predicted conflict on Malaysia's or Singapore's governments.
- **H4, passive public:** the society predicts fewer public actions than the baseline and no national hostility
  between publics (real: Malaysians mocking Prabowo's "not our fault" apology; the boycott of Indonesian products).
- **H5, invented cooperation:** more than half of the society's said cooperation is invented (meetings, protocols,
  relief packages).
- **H6, possible strength (exploratory):** the society predicts the joint task force to "follow the money" (27 Oct)
  more often than the baseline, because its governments already invented information sharing on companies at the
  13 October cutoff.

What would count against the map: the society predicting the gas cut or "do not lecture us"; the society naming a
specific enforcement act; the society's between-country moves being mostly conflict.

## Real events after 21 October (draft targets for the cutoff-6 test; tags; confirmation)

Free rounds after a cutoff at stage 6 are dated 26 Oct, 5 Nov, 16 Nov and 19 Nov (rounds 13-16), with physical facts
only. Long gaps between rounds: a caveat for this window.

| Date | Event | Tag | Confirmed by |
|---|---|---|---|
| 22 Oct | Prabowo vows to revoke licences of foreign firms linked to fires | ENF-V, G, S | Malay Mail 23 Oct; Bernama; Media Selangor |
| 22 Oct | Bahlil: reconsider energy exports to countries that do not respect Indonesia | CONF-V, G, S | Jakarta Post via ANN 27 Oct; Wikipedia |
| 23 Oct | NEA asks 10 Singapore-registered palm oil and forestry firms for information on Indonesian links | ENF-M, G, S | Straits Times via ANN (search summary); recheck |
| 23 Oct | Malaysians online: "We want to know!" the companies Prabowo threatens to expose | ENF-V, P, S | The Rakyat Post 23 Oct |
| 24 Oct | Indonesia cuts pipeline gas to Singapore (about 8-9% of exports) | CONF-M, G, S | Fortune 26 Oct; Wikipedia; Kompas |
| 25 Oct | Wong: Singapore expects all parties to honour commitments | CONF-V, G, S | sources doc (search summaries); recheck |
| 26 Oct | Bahlil: "Do not lecture us ... on honoring contracts"; alleges Singapore re-exports Indonesian LNG | CONF-V, G, S | Jakarta Post via ANN 27 Oct; Wikipedia |
| by 26 Oct | Malaysian boycott of Indonesian products continues | CONF-M, P, S | Straits Times via ANN 26 Oct; BBC |
| 27 Oct | Singapore-Indonesia joint task force to follow the money; ministerial hotlines | COOP-M, G, S | Jakarta Post editorial 30 Oct; Wikipedia |
| 27-28 Oct | Malaysia: no (conclusive) evidence Malaysian firms caused the fires | CONF-V, G, S | Malaysiakini; Borneo Post 28 Oct; Malay Mail 28 Oct |
| 2 Nov | Bahlil: no electricity exports to Singapore unless the price is right | CONF-V, G, S | ANN (search summary); recheck |
| 4 Nov | Singapore passes haze-law amendment; maximum fine S$20 million | ENF-M, G, S | eco-business (search summary); recheck |
| Nov | Malaysia keeps a diplomatic approach rather than legal action | COOP-V, G, Gn | NST Nov; Malaysiakini; Newswav |
| 15 Nov | Prabowo at the ASEAN Summit: apologises, "It is not our fault"; 17 concessions revoked, 104 companies investigated | COOP-V + ENF-M, G, S | Al Jazeera 16 Nov (read); Malay Mail; SCMP |
| after 15 Nov | Malaysiakini readers mock the apology ("what about next year's haze?") | CONF-V, P, S | found 2026-11-20; recheck |
| (Wikipedia only) | Pro-government Indonesians harass Malaysian influencers | CONF-V, P, S | Wikipedia only; do not score unless confirmed |

Not yet done: rechecking the items marked "recheck", writing yes / partly rules, and adding them to
`tools/haze_forecast_coder.py` as `TARGETS_CUTOFF_6`. No run on this cutoff without the user's go-ahead.
