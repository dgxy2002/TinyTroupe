# Ground-truth coverage check for the haze dimensions (2026-11-26)

Purpose: before scoring the simulation against reality, check which of the 12 dimensions (see
`haze_capability_map.md` and the conversation of 2026-11-26) real sources cover, for which actor and which news stage.
Done with web searches plus full reads of the articles marked "read". No model calls. Nothing here is scored yet.

Stages: 1 = 4 Sep, 2 = 18 Sep, 3 = 9 Oct, 4 = 13 Oct ("oxygen" remark), 5 = 16 Oct, 6 = 21 Oct, 7 = 26 Oct, 8 = 16 Nov.
Rating: **good** = several dated, sourced reactions; **thin** = one or two, or opinion pieces only; **none** = nothing found.

## Coverage by actor

| Actor | Coverage | Stages with data | What exists |
|---|---|---|---|
| Malaysian public | **good** | 1 (thin), 3-8 | online mockery of "oxygen" (The Star 12 Oct, read: "How do you quantify O2? But we can definitely quantify haze."); frustration (France 24 16 Oct); boycott of Indonesian brands, first from a football row (Malaysiakini 10 Oct, read), then haze-linked (Straits Times via ANN 26 Oct); civil-society march to the Indonesian embassy and parliament (Greenpeace Malaysia); demands to name companies (The Rakyat Post 23 Oct); sarcasm at the apology (Malaysiakini column, Nov); Khairy's "banana republic" and "we should sue Indonesia" (ex-minister, Sept) |
| Indonesian public | **good for criticism of own government; thin for nationalism** | 2-5, thin after | class action against Prabowo and officials (filed 19 Sep; hearings 7 and 21 Oct; demands: national emergency, free respiratory care, compensation); Jambi protest (about 8 Oct); online apologies and appeals for foreign pressure (Jakarta Post 22 Oct, blocked; ANN reprint read 2026-11-19); NGOs reject the "nature" framing (ANN ?p=308705, read: Walhi "disguise environmental and corporate crimes behind natural causes"); nationalist pushback only anecdotal (actor Boy Hamzah on the boycott; harassment of Malaysian influencers: Wikipedia only) |
| Singaporean public | **thin** | 1-5 | residents' complaints on social media (The Star 29 Sep); mask queues (Malay Mail 18 Oct, blocked); hawkers hit (The Star 19 Oct); F1 near-record turnout despite haze; journalist Bertha Henson on "oxygen"; "public outrage mounted" (Jakarta Post editorial). Little on blame, stance, demands or actions |
| Bruneian public | **none** | none | only government advisories and a complaints hotline |
| Singapore government | **good** | 1-8 | advisories, offers of help, notices, Singapore Exchange queries, Shanmugam ("disappointing", Mothership 19 Oct, read), Wong on gas contracts, task force, haze-law amendment |
| Malaysian government | **good** | 2-8 | aid offer, Anwar's calls, foreign minister: formal protest "a last resort" (ANN, read), denial of Malaysian firms' role, openness to a haze law, diplomacy-first |
| Indonesian government | **good** | 1-8 | "oxygen" remark, police suspects, accepting help, Prabowo's rebuke and licence threats, energy threat and gas cut, "do not lecture us", apology "not our fault" |
| Brunei government | **thin** | 1-2 | health advisories, school measures; no diplomatic statements found |

## Coverage by dimension (who it can be scored for)

| # | Dimension | Verdict | Scoreable for | Notes |
|---|---|---|---|---|
| 1 | Emotional reaction | keep | MY public (good), ID public (good), SG public (thin) | richest at stage 4 ("oxygen") and stage 8 (apology) |
| 2 | Blame direction | keep | MY public, ID public | ID public blames own government and companies; MY public blames Indonesian government and companies |
| 3 | Stance between publics | keep | MY public (hostility: boycott, mockery), ID public (apology vs nationalism, nationalist side thin) | |
| 4 | Public actions | keep | MY public, ID public | boycott, march, class action, protest, online apologies |
| 5 | Demands | keep | MY public, ID public | apology (Johor PH 12 Oct), name the companies, sue Indonesia, stronger laws; national emergency, healthcare, compensation |
| 6 | Diversity of views within a country | keep, flagged | ID public (apologisers vs nationalists; nationalist side thin), MY public (boycott vs "waste of time"; economists against) | weakest of the public dimensions |
| 7 | Government cooperation | keep | SG, MY, ID governments | |
| 8 | Government conflict / escalation | keep | SG, MY, ID governments | |
| 9 | Specificity of government action | keep | SG, MY, ID governments | |
| 10 | Division within a country | keep | ID (public vs government, clear); MY (activists vs government over Malaysian firms) | |
| 11 | Which news triggers a reaction | keep, restricted | stages 3, 4 and 8 for publics; all stages for governments | for many triggers (notices, gas cut) we have no public reaction: score "no data", not "no reaction" |
| 12 | Framing | keep | ID public and NGOs (nature vs human cause; nationalism deflecting blame: Jakarta Post 30 Oct lede), MY public (country vs companies), governments | |

Conclusion: all 12 dimensions survive, but **public dimensions can be scored only for the Malaysian and Indonesian
publics** (Singaporean public: emotion only, thinly; Bruneian public: nothing). Stages 1-2 have little public data;
stages 3-5 and 8 are the richest.

## Access

- **Readable by automated fetch:** The Star (incl. its Asia News Network reprints of Straits Times and Jakarta Post
  pieces), Malaysiakini, Mothership, asianews.network, Bernama, Fortune, Al Jazeera, Business Today, Tempo, Xinhua.
- **Blocked (HTTP 403 or paywall):** Jakarta Post, Malay Mail, The Independent SG; earlier also Straits Times, CNA,
  SCMP, The Guardian.
- **Workarounds without scraping:** read the Asia News Network or The Star reprint of a blocked Straits Times or
  Jakarta Post article; Yahoo Singapore reprints; or the user pastes articles they can open.
- **Scraping blocked sites** (a headless browser that gets past the 403) would get around the sites' own blocking and
  paywalls; it may breach their terms of use. Not done; a decision for the user, and reprints cover most needs.
