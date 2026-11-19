"""The 2026 Southeast Asian haze (S123-S124): four average citizens react to the real timeline.

First real-world-event scenario (Shaoyang's brief, 2026-11-16/17): each agent is an ordinary citizen of one
country, not a specific person in a made-up dispute, and the run is compared afterwards with what actually happened.
The episode is the most recent one, August to November 2026, which is after the simulator's training data (Gemini
2.5 Pro), so the agents cannot recite how it went; they still know earlier episodes (2013, 2015, 2019).

Design (user decisions 2026-11-19): one citizen per country, a staged timeline, built but not run.
- Countries: Singapore, Malaysia and Indonesia, the three at the centre of the 2026 dispute, plus Brunei, which was
  hit early (home-based learning on 2-3 September) and joined Malaysia's call for ASEAN action. The engine needs
  exactly four agents. Brunei has the least coverage to compare against (see haze_2026_sources.md).
- Each "average citizen" is facts only (age near the national median, the largest ethnic group, a common job, where
  most people live, household). Nothing tells them what to think about the haze, who to blame or how to behave.
- Setting: a public live audio room online where people from around the region talk about the haze; the same four
  keep turning up. Everyone's country is public (rule 4: the prompt tells agents not to infer a background).
- Timeline: each stage is a dated public news update, delivered to all four before odd rounds (3, 5, ... 15), so
  every stage has two rounds (the engine allows two spoken turns per round). Updates hold only what governments,
  officials, politicians, NGOs and the weather did, as reported. What ordinary people did (online apologies,
  boycotts, protests, lawsuits, harassment) is left out on purpose: it is what the run is compared against.
- S123 runs the whole timeline to Prabowo's apology (16 rounds). S124 stops the news at 21 October (12 rounds), so
  what the citizens say should happen next can be compared with what did (gas cut, task force, apology).
- No resolution goal. As in the case scenarios: conversation only, priced priority, setting pinned, no clock.

Sources, the full timeline and what counts as ground truth are in research_questions/haze_2026_sources.md.
"""

from __future__ import annotations

from .case_common import _REASON_RULE
from .common import AgentPreset, PROFILE_CONFIGURATIONS, ScenarioPreset, validate_scenario

_STYLE = "Plain and conversational, the way you would speak in a live online room with strangers from around the region."
_GUIDANCE = (
    "Reassess your immediate priority when observable facts change; do not keep defending a practical reason "
    "after it is no longer true." + _REASON_RULE
)

_SETTING = (
    "Since August 2026, smoke haze from forest and land fires has drifted across Southeast Asia. Four ordinary "
    "people, each from a different country, take part in a public live audio room online where people from "
    "around the region talk about the haze. They do not know each other offline; the room opens again when "
    "there is news, and the same four keep turning up. Agent A is from Singapore, Agent B is from Malaysia, "
    "Agent C is from Indonesia, and Agent D is from Brunei. Each lives in their own country and speaks from "
    "there, in English. None of them works for a government, a plantation or paper company, or an "
    "environmental group."
)

# Stage 1, round 1. Facts as at Friday 4 September 2026.
_TRIGGER = (
    "It is Friday 4 September 2026. This year has a strong El Nino, and fires on peat and forest land in Sumatra "
    "and Kalimantan in Indonesia have been burning since August; smaller fires have also burned in Sarawak and "
    "Johor in Malaysia. Today Sarawak declared an emergency in Serian district after air quality there reached "
    "hazardous levels, and hundreds of Sarawak schools have been closed at different times since mid-August. In "
    "Brunei, schools moved to home-based learning on 2 and 3 September. In Singapore, the 24-hour PSI went above "
    "100, the unhealthy range, on 3 September for the first time since 2023, and the National Environment Agency "
    "has started daily haze advisories. Schools in parts of the Philippines have suspended classes. Today a "
    "former Malaysian health minister called Indonesia a \"banana republic\" over the haze. The room has just "
    "opened."
)

_ROUND_OBSERVATIONS = {
    3: (
        "It is now Friday 18 September 2026. Air quality is unhealthy at half of Malaysia's 68 monitoring "
        "stations, and the haze reached southern Vietnam on 14 September. Malaysia has offered Indonesia one "
        "firefighting plane, three helicopters and 52 personnel. Japan has sent military helicopters to help "
        "Indonesia fight the fires. Indonesian police say 95 companies are being investigated over the fires, "
        "along with many individuals. The room has opened again."
    ),
    5: (
        "It is now Friday 9 October 2026. On 7 October Greenpeace Malaysia published a list of the 20 entities "
        "most linked to this year's fires in Indonesia; it includes Malaysian and Singaporean companies. All "
        "schools in Johor have been closed since 7 October, and today schools were also ordered closed in "
        "Melaka, Negeri Sembilan, Selangor, Kuala Lumpur and Putrajaya. In Singapore the 24-hour PSI reached 192 "
        "this evening, the highest this year, on the weekend of the Formula One Grand Prix, which is going ahead. "
        "Malaysia's Prime Minister Anwar Ibrahim said he had called Indonesia's President Prabowo Subianto, who "
        "agreed to take the necessary steps. The room has opened again."
    ),
    7: (
        "It is now Tuesday 13 October 2026. On 10 October the head of Indonesia's Government Communications "
        "Agency, Syahganda Nainggolan, said the fires were \"beyond human error; this is truly nature\" and "
        "added: \"We're not just sending over the haze. When there's no haze, we send oxygen. The oxygen from "
        "Singapore and Malaysia is from our forests, right?\" A video of the remark is being widely shared. "
        "Indonesia's disaster agency said ground personnel are preferred to aircraft from neighbours. On 11 "
        "October Malaysia said it had still had no reply to its offer of help. On 12 October President Prabowo "
        "ordered maximum efforts against the fires. Today a Malaysian MP told Parliament that Malaysians should "
        "boycott companies linked to the burning (\"We need to hit them where they hurt the most\") and that banks "
        "should stop financing them. Malaysia's Firefly airline has cancelled flights to Singapore because of the "
        "haze. The room has opened again."
    ),
    9: (
        "It is now Friday 16 October 2026. On 14 October fine-particle pollution in western Singapore reached "
        "its highest level since 2015; Singapore has opened haze shelters, is giving out N95 masks and some "
        "schools have stopped outdoor activities. Timor-Leste closed its schools. Indonesian police named 223 "
        "people and nine companies as suspects. On 15 October Indonesia's Foreign Minister said Indonesia would "
        "now accept foreign firefighting help, and Singapore's Prime Minister Lawrence Wong said Singapore was "
        "checking which companies were responsible and that legal action could follow. Today Singapore's "
        "Minister Grace Fu announced that notices had been sent to seven Indonesian companies under Singapore's "
        "Transboundary Haze Pollution Act; some lawyers said this could have diplomatic consequences. Singapore's "
        "24-hour PSI reached 229 today, the very unhealthy range, the 12th day in a row of unhealthy air. The "
        "haze has reached Jakarta. Malaysia's government said no Malaysian plantation companies were involved in "
        "the fires. The room has opened again."
    ),
    11: (
        "It is now Wednesday 21 October 2026. On 19 October Singapore's Minister K. Shanmugam said the Singapore "
        "Exchange was questioning seven Singapore-listed agriculture companies about links to the fires (Golden "
        "Agri-Resources, Bumitama Agri, First Resources, Wilmar International, Kencana Agri, Indofood Agri "
        "Resources and TSH Resources), that the government was also looking at Asia Pulp and Paper, and that "
        "notices had gone to three more Indonesian companies, ten in all. He said: \"We will pursue this matter "
        "for as long as it takes\" and \"The Indonesian public is suffering as well.\" The same day a former "
        "Indonesian trade minister, Muhammad Lutfi, said four of the seven Indonesian companies had Singapore ties "
        "and challenged Singapore to raid their offices. Today President Prabowo said there were indications that "
        "foreign companies were involved in the fires, and Malaysia's deputy environment minister said Malaysia "
        "was open to a haze law like Singapore's. The room has opened again."
    ),
    13: (
        "It is now Monday 26 October 2026. On 22 October Indonesia's energy minister, Bahlil Lahadalia, said "
        "Indonesia would reconsider energy exports to countries that do not respect it. On 24 October Indonesia "
        "cut its pipeline gas to Singapore by about 8 per cent of those exports, less than 2 per cent of "
        "Singapore's gas use, citing domestic needs. On 25 October Prime Minister Wong said Singapore expects all "
        "parties to honour their commitments. Today Bahlil said: \"Do not lecture us, especially the energy "
        "ministry, on the importance of honoring contracts.\" Singapore's air has been back in the moderate range "
        "since 22 October, after 18 days of unhealthy air, and the first rains have fallen on Sumatra and "
        "Kalimantan. The room has opened again."
    ),
    15: (
        "It is now Monday 16 November 2026. On 27 October Singapore's Foreign Minister Vivian Balakrishnan met "
        "Indonesia's Foreign Minister Arrmanatha Nasir in Jakarta; they agreed to set up a joint task force to "
        "trace the money and corporate links of companies behind the fires, and direct ministerial hotlines. "
        "Arrmanatha said: \"Smoke can cross borders, so can money.\" Rain put out most of the fires in late "
        "October, and Singapore ended its haze measures on 7 November. Singapore plans to push for an ASEAN "
        "coordinating centre on haze when it chairs ASEAN in 2027. Yesterday, at the ASEAN Summit in Manila, "
        "President Prabowo said: \"I would like to apologise to my neighbouring countries Malaysia and "
        "Singapore. It is not our fault, but once again we apologise. But we have done our best.\" He said 17 "
        "company concessions had been revoked, 104 companies were under police investigation, 71,000 "
        "firefighters had been deployed and 16 people had died fighting the fires. The room has opened again."
    ),
}

_AGENTS = {
    "A": AgentPreset(
        age=43,
        role="Singaporean, lives in Jurong West",
        immediate_priority="Keep your mother and children safe from the haze while getting on with work.",
        private_knowledge=(
            "You live in an HDB flat in Jurong West with your wife, your two children in primary school and your "
            "mother, who has asthma. You work as a logistics supervisor at a warehouse in Tuas, partly outdoors. "
            "You check the PSI on your phone several times a day. You remember the 2015 haze, when your mother "
            "was in and out of the clinic."
        ),
        initial_observation="Sees the PSI on your phone app showing the unhealthy range again this morning.",
        interaction_style=_STYLE,
        behavioral_guidance=_GUIDANCE,
    ),
    "B": AgentPreset(
        age=31,
        role="Malaysian, lives in Johor Bahru",
        immediate_priority="Keep your son safe and keep your job while the haze disrupts school and work.",
        private_knowledge=(
            "You live in Johor Bahru with your husband and your seven-year-old son, who is in primary school. "
            "You work as an administrative clerk at a factory in Pasir Gudang. When schools close, you have to "
            "find someone to look after your son or take leave. Your parents live in Batu Pahat."
        ),
        initial_observation="Sees a grey sky over Johor Bahru and smells smoke on the way to work.",
        interaction_style=_STYLE,
        behavioral_guidance=_GUIDANCE,
    ),
    "C": AgentPreset(
        age=30,
        role="Indonesian, lives in Bekasi near Jakarta",
        immediate_priority="Keep earning your daily income on the road and keep your sister's family safe.",
        private_knowledge=(
            "You live in Bekasi, near Jakarta, with your wife and your baby daughter. You work as a motorbike "
            "ride-hailing and delivery driver, outdoors all day; you are paid per trip. Your older sister lives "
            "with her family in Palangka Raya, Central Kalimantan, near the fires. She tells you the sky there "
            "has been yellow and orange for weeks and her children keep coughing."
        ),
        initial_observation="Sees a message from your sister with a photo of an orange sky over Palangka Raya.",
        interaction_style=_STYLE,
        behavioral_guidance=_GUIDANCE,
    ),
    "D": AgentPreset(
        age=32,
        role="Bruneian, lives in Brunei-Muara",
        immediate_priority="Keep your daughter healthy and daily life as normal as possible.",
        private_knowledge=(
            "You live in Brunei-Muara district with your husband and your five-year-old daughter, who goes to "
            "kindergarten. You work as an administrative officer in a government ministry office. Your "
            "daughter's kindergarten switched to home-based learning on 2 and 3 September because of the haze."
        ),
        initial_observation="Sees the haze over the river from your office window.",
        interaction_style=_STYLE,
        behavioral_guidance=_GUIDANCE,
    ),
}


def _haze(scenario_id: str, title: str, last_round: int) -> ScenarioPreset:
    case = ScenarioPreset(
        scenario_id=scenario_id,
        title=title,
        environment="Public live audio room online",
        initial_datetime="2026-09-04T20:00:00+08:00",
        source_status="Real event: 2026 Southeast Asian haze; facts and sources in haze_2026_sources.md",
        initial_interaction_type="Recurring public discussion of a regional crisis",
        shared_setting=_SETTING,
        shared_trigger=_TRIGGER,
        agents=_AGENTS,
        observation_focus=(
            "Who each citizen blames and when, what they ask for (apology, legal action, boycott, aid, "
            "cooperation), how they respond to each other and to each news stage, where they agree or stay "
            "apart, and how this compares with what citizens and governments actually did."
        ),
        implementation_notes=(
            "Staged timeline: one dated public update before each odd round. Updates hold official, political, "
            "NGO and weather events only; ordinary citizens' reactions are left out because they are the "
            "ground truth for comparison."
        ),
        round_observations={n: text for n, text in _ROUND_OBSERVATIONS.items() if n <= last_round},
        timing_free=True,
        conversation_only=True,
        priced_priority=True,
        pin_shared_setting=True,
    )
    validate_scenario(case)
    return case


HAZE_FULL = _haze("S123", "2026 Southeast Asian haze: four citizens, full timeline", last_round=15)
HAZE_OPEN_END = _haze("S124", "2026 Southeast Asian haze: four citizens, news stops on 21 October", last_round=11)
HAZE_SCENARIOS = {scenario.scenario_id: scenario for scenario in (HAZE_FULL, HAZE_OPEN_END)}

# Rounds each scenario is meant to run (two rounds per news stage). Pass with run_cases.py, e.g. S123:HZ1:v1:16.
HAZE_ROUNDS = {"S123": 16, "S124": 12}

# ---- Cast (profile cell) ----
# HZ1: one citizen per country, nationality as the background label, biographies with home language and faith as
# facts (the most common ones for each country), named after common names in each country.
PROFILE_CONFIGURATIONS.update(
    {
        "HZ1": {
            "backgrounds": {"A": "Singaporean", "B": "Malaysian", "C": "Indonesian", "D": "Bruneian"},
            "countries": {"A": "Singapore", "B": "Malaysia", "C": "Indonesia", "D": "Brunei"},
            "role_names": {"A": "Kelvin Tan", "B": "Farhana", "C": "Budi Santoso", "D": "Nur Aqilah"},
            "biography": "personal",
            "first_speaker": "A",
            "biography_overrides": {
                "A": "You are a Singaporean citizen of Chinese descent and grew up in an HDB flat. You speak "
                "Mandarin and English at home and went to local schools.",
                "B": "You are a Malaysian citizen, Malay, and grew up in Johor. You speak Malay at home and use "
                "English at work. You are Muslim.",
                "C": "You are an Indonesian citizen, Javanese, and grew up in Central Java before moving to the "
                "Jakarta area for work. You speak Indonesian and Javanese at home. You are Muslim.",
                "D": "You are a Bruneian citizen, Malay, and grew up in Bandar Seri Begawan. You speak Malay at "
                "home and use English at work. You are Muslim.",
            },
        }
    }
)
