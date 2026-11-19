# 2026 Southeast Asian haze: sources, timeline and ground truth

Background for `scenario_presets/haze_presets.py` (S123, S124, cast HZ1). Compiled 2026-11-19 from web research.
Many news sites (CNA, Straits Times, Guardian, SCMP, Jakarta Post direct) blocked automated reading, so several
facts rest on the Wikipedia article plus search-result summaries and the pages that could be read. The
"checked" column says how each fact was confirmed. Re-check anything marked "Wikipedia only" before citing it.

## Why this episode

- It is the most recent episode (August to November 2026; user's choice) and the largest since 2015: Singapore's
  longest run of unhealthy air since 2015 (18 days), estimated cost to Singapore S$2.32 billion, Malaysian schools
  closed across several states, Sarawak emergency, haze reaching Brunei, the Philippines, Timor-Leste and Vietnam.
- It happened after the simulator's training data (Gemini 2.5 Pro), so the agents cannot recite how it went. They
  do know the 2013, 2015 and 2019 episodes, so similarities may still come from memory of earlier ones.
- It has a clear dispute with turning points: an Indonesian official's "we send oxygen" remark, Singapore's legal
  notices to Indonesian firms and questions to Singapore-listed firms, Indonesia's gas cut to Singapore, a joint
  task force, and Prabowo's apology that the haze was "not our fault".

## Countries simulated

| Agent | Country | Why | Ground truth available |
|---|---|---|---|
| A | Singapore | Hit hardest in mid-October; government took legal action | Officials well covered; ordinary Singaporeans barely quoted |
| B | Malaysia | Hit from August (Sarawak, then the peninsula); loudest public anger; boycott | Good: news quotes, boycott coverage |
| C | Indonesia | Source of most fires; citizens both apologised and defended | Good: citizens quoted, protests, class action |
| D | Brunei | Hit early; joined Malaysia's call for ASEAN action | Almost none found |

Brunei fills the fourth slot the engine needs. Alternatives if the Prof prefers: the Philippines (classes
suspended in Metro Manila and Cebu) or a second Indonesian from a burning province (Kalimantan), which would show the
split inside Indonesia. Note the room is three affected countries against the source country, like the 3 + 1 rooms.

## Timeline given to the agents (inputs)

Inputs are what governments, officials, politicians, NGOs, airlines and the weather did, as reported. Ordinary
citizens' reactions are left out because they are what the simulation is compared against.

| Stage (round) | Date | Facts in the update | Checked |
|---|---|---|---|
| 1 (1) | Fri 4 Sep | El Nino; fires in Sumatra and Kalimantan since August, smaller ones in Sarawak and Johor; Sarawak emergency in Serian (4 Sep); Sarawak schools closed; Brunei home-based learning 2-3 Sep; Singapore PSI above 100 on 3 Sep, first since 2023, daily advisories; Philippine classes suspended; ex-Malaysian health minister calls Indonesia a "banana republic" (4 Sep) | Reuters and Straits Times headlines (Sarawak, PSI 101), FMT headline (Khairy), Philstar; details Wikipedia |
| 2 (3) | Fri 18 Sep | Half of Malaysia's 68 stations unhealthy; haze in southern Vietnam (14 Sep); Malaysia offers 1 plane, 3 helicopters, 52 personnel; Japan sends helicopters; Indonesian police investigating 95 companies | Star and RRI headlines; "95 corporations" confirmed by AFP 14 Oct; offer details Wikipedia only |
| 3 (5) | Fri 9 Oct | Greenpeace Malaysia list of top 20 entities includes Malaysian and Singaporean firms (7 Oct); Johor schools closed from 7 Oct, more states 9 Oct; Singapore PSI 192 on F1 weekend; Anwar says Prabowo agreed to take necessary steps | Bernama/Star 9 Oct (read); Greenpeace and CNA headlines |
| 4 (7) | Tue 13 Oct | Syahganda Nainggolan (10 Oct): "beyond human error; this is truly nature... we send oxygen" (video viral); disaster agency prefers ground crews; Malaysia: no reply to offer (11 Oct); Prabowo orders maximum efforts (12 Oct); MP Syed Saddiq urges boycott of linked companies, "hit them where they hurt the most" (13 Oct); Firefly cancels Singapore flights | Mothership 11 Oct (read), France 24 16 Oct (read), Straits Times 26 Oct via ANN (read), Al Jazeera headline |
| 5 (9) | Fri 16 Oct | West Singapore PM2.5 highest since 2015 (14 Oct), shelters, N95 masks; Timor-Leste schools shut; Indonesia names 223 suspects and 9 companies; Indonesia accepts foreign help (15 Oct); PM Wong: legal action could follow (15 Oct); Grace Fu: notices to 7 Indonesian companies under the Transboundary Haze Pollution Act (16 Oct); PSI 229, 12th unhealthy day; haze reaches Jakarta; Malaysia: no Malaysian firms involved | CNA/ST headlines; Mothership 19 Oct (read) confirms the 7 and 10 total but calls them "preventive measure notices"; Jakarta Post editorial (read) says notices "under the Transboundary Haze Pollution Act"; Jakarta haze Wikipedia only |
| 6 (11) | Wed 21 Oct | Shanmugam (19 Oct): SGX questioning 7 Singapore-listed firms (named), APP examined, 10 Indonesian firms noticed, "for as long as it takes", "The Indonesian public is suffering as well"; ex-trade minister Lutfi: 4 of the 7 have Singapore ties, raid their offices (19 Oct); Prabowo: indications of foreign companies (21-22 Oct); Malaysian deputy minister open to a Singapore-style law (21 Oct) | Mothership 19 Oct (read); ST via ANN 26 Oct (read); CNBC Indonesia headlines |
| 7 (13) | Mon 26 Oct | Bahlil: reconsider energy exports to countries that do not respect Indonesia (22 Oct); gas cut to Singapore 31 MMSCFD, about 8% of pipeline exports, under 2% of Singapore's use (24 Oct); Wong: honour commitments (25 Oct); Bahlil: "Do not lecture us..." (26 Oct); Singapore air moderate from 22 Oct; first rains | Jakarta Post via ANN 27 Oct (read); search summaries of SCMP, Star, Mothership |
| 8 (15) | Mon 16 Nov | Balakrishnan in Jakarta, joint task force to follow the money, hotlines (27 Oct); "Smoke can cross borders, so can money"; rains end fires; Singapore ends measures 7 Nov; ASEAN coordinating centre push for 2027; Prabowo at ASEAN Summit, Manila (15 Nov): apology, "It is not our fault... we have done our best", 17 concessions revoked, 104 companies investigated, 71,000 firefighters, 16 died | Al Jazeera 16 Nov (read); Jakarta Post editorial 30 Oct (read); search summaries |

S124 stops after stage 6 (21 October), so what the citizens expect or ask for next can be compared with stages 7
and 8.

Left out on purpose: statements by Indonesian officials not confirmed beyond Wikipedia (Zulkifli Hasan, Dudung,
Jonan), the football rivalry behind part of the boycott, influencer harassment, and censorship claims.

## Ground truth: what ordinary citizens did

| Country | What happened | Source |
|---|---|---|
| Malaysia | Frustration and anger; "The Indonesian (government) needs to do the right thing" (tour operator, Batu Caves) | France 24, 16 Oct |
| Malaysia | The "oxygen" video "prompted furious responses"; mockery of it online | France 24; SCMP headline "Malaysians mock Indonesian officials' 'we send oxygen' haze defence" |
| Malaysia | Consumer boycott of Indonesian brands (Indocafe, Sosro, Kara coconut milk), lists of local alternatives; "If we don't teach them a lesson, they won't stop" (NGO head, 67); partly started from a football rivalry; economists doubt it works | Straits Times 26 Oct via ANN; Malaysiakini headline |
| Indonesia | Citizens apologised to neighbours online ("We're truly sorry for the haze", Jakarta doctor, 12 Oct), blamed "the incompetence of our own government", asked "SEAblings" abroad to pressure or even sue Jakarta | Jakarta Post 23 Oct via ANN; SCMP headline |
| Indonesia | Protest in Jambi (8 Oct, water cannons); class action against Prabowo and officials in Pontianak demanding a national emergency, free care, compensation, accountability for firms ("This has already happened in 2015... 2019... 2026") | Bernama 9 Oct; AFP 14 Oct |
| Indonesia | Pro-government counter-reaction: harassment and death threats against Malaysian influencers; claims of shadowbanning | Wikipedia only |
| Singapore | "Public outrage mounted" as smoke reached hazardous levels; no ordinary Singaporean quoted in sources read | Jakarta Post editorial 30 Oct |
| Brunei | Nothing found | |
| Polls | None found for 2026. 2019 Ipsos (Malaysia): 84% blamed Indonesian authorities, 75% land owners, 80% thought suing companies would work; Malaysians were 87% of online haze talk, Singapore 7%, Indonesia 6% | Malay Mail via Yahoo, 25 Sep 2019 |

Government track for comparison: escalation (legal notices, SGX questions, "foreign actors", gas cut, "do not
lecture us") followed by de-escalation (task force, hotlines, apology with "not our fault"). No regional
settlement among citizens; the boycott and the class action continued.

## What to compare (proposal for the meeting)

1. **Blame:** whom each citizen blames at each stage (Indonesian government, companies including Singapore- and
   Malaysia-linked ones, smallholders, nature or El Nino), against the ground truth above.
2. **Emotion and tone:** anger after the "oxygen" remark; shame or apology from the Indonesian; defensiveness.
3. **Demands:** apology, legal action, boycott, aid, national emergency, ASEAN action.
4. **Cross-border dynamics:** solidarity (apology, "SEAblings") versus hostility (mockery, boycott, nationalism).
5. **Prediction (S124):** what the citizens expect next, compared with the gas cut, task force and apology.
6. **Failure modes:** too polite or agreeable; missing anger; stereotyped national views; the Indonesian agent
   defending or apologising for the government in a way real citizens did not; knowledge leaking from 2015.

Scoring could reuse the pair agreement scorer (start, end, who moved) plus a new stage-by-stage coder for blame,
emotion and demands. Not built yet.

## Running it (not yet run)

`python research_questions/tools/run_cases.py S123:HZ1:v1:16 S124:HZ1:v1:12`. Estimated cost about $1.0-1.5 for S123
(16 rounds, longer context than the 12-round case runs at about $0.72) and $0.8-1.0 for S124. Pilot one run and read
it in full first.

## Main sources

- Wikipedia, "2026 Southeast Asian haze" (revision 1386440193): https://en.wikipedia.org/wiki/2026_Southeast_Asian_haze
- NEA haze updates 23 and 26 Oct 2026: https://www.nea.gov.sg/media/news/advisories/index/haze-situation-update-23-october-2026
- Mothership, 11 Oct ("send oxygen"): https://mothership.sg/2026/10/indonesia-communications-head-when-no-smoke-send-oxygen/
- Mothership, 19 Oct (Shanmugam, SGX firms): https://mothership.sg/2026/10/singapore-govt-haze-companies-act/
- France 24 / AFP, 16 Oct: https://www.france24.com/en/live-news/20261016-in-malaysia-frustration-grows-over-indonesia-haze
- Jakarta Post via ANN, 23 Oct ("I'm sorry"): https://asianews.network/?p=309924
- Straits Times via ANN, 26 Oct (boycott): https://asianews.network/?p=310285
- Jakarta Post via ANN, 27 Oct (gas row): https://asianews.network/?p=310802
- Jakarta Post editorial via ANN, 30 Oct: https://asianews.network/?p=311565
- Bernama via The Star, 9 Oct (Jambi protest, class action): https://www.thestar.com.my/aseanplus/aseanplus-news/2026/10/09/indonesia-forest-fires-fuel-public-frustration-and-regional-concern
- AFP via The Star, 14 Oct (class action): https://www.thestar.com.my/aseanplus/aseanplus-news/2026/10/14/indonesians-on-fire-ravaged-island-sue-state-for-clean-air
- Al Jazeera, 16 Nov (apology): https://www.aljazeera.com/news/2026/11/16/indonesian-president-apologises-to-singapore-malaysia-for-wildfire-haze
- Search summaries: SCMP and Star on the gas cut, Singapore-Indonesia task force reports, apology coverage
  (Star, Bernama, Malay Mail, Mothership).
- Malay Mail via Yahoo, 25 Sep 2019 (Ipsos): https://sg.news.yahoo.com/pollster-complaints-haze-online-mostly-132034026.html
