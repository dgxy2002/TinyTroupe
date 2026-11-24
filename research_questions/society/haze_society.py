"""The 2026 Southeast Asian haze as a small society (design note: research_questions/haze_society_design.md).

13 agents (citizens, business owners, a smallholder, an estate manager and four governments) in channels: a private
group for each of Singapore, Malaysia and Indonesia, a public regional feed, and a diplomatic channel for the
governments only. Real news is delivered stage by stage up to a cutoff; after it, everyone, governments included,
acts freely and only physical facts (air quality, rain) are still delivered. Then the free-play rounds are compared
with what really happened next.

Biographies are facts only (age, place, job, household, language, faith); nothing tells anyone what to think about
the haze. Governments speak for their government as a whole; no agent plays a real, named person (user decision
2026-11-24). Their private facts list the tools each government really had, stated as facts; this can prime the
real moves (e.g. Indonesia's gas exports) and is noted in the design note.
"""

from __future__ import annotations

import re
from dataclasses import asdict, dataclass, field

from ..scenario_presets.haze_presets import _ROUND_OBSERVATIONS, _TRIGGER


@dataclass(frozen=True)
class SocietyAgent:
    agent_id: str
    name: str
    country: str
    kind: str  # "citizen" or "government"
    role: str
    immediate_priority: str
    private_knowledge: str
    initial_observation: str
    biography: str = ""
    age: int | None = None


@dataclass(frozen=True)
class Channel:
    channel_id: str
    name: str
    description: str
    speakers: tuple[str, ...]
    readers: tuple[str, ...] = ()
    # Receive every line but are not named to the members (HS3: governments monitoring their national group).
    hidden_readers: tuple[str, ...] = ()
    # Extra sentence in the turn cue (HS4: says plainly whether the channel is public or private).
    cue_note: str = ""


@dataclass(frozen=True)
class Stage:
    number: int
    date: str
    news: str  # delivered when the stage is before or at the cutoff
    physical: str  # delivered instead after the cutoff: air, fires, rain only


@dataclass(frozen=True)
class SocietyPreset:
    preset_id: str
    title: str
    setting: str
    agents: dict[str, SocietyAgent]
    channels: tuple[Channel, ...]
    stages: tuple[Stage, ...]
    rounds_per_stage: int = 2
    # Recent episodic memories shown in each prompt (TinyTroupe default 20). Agents in several channels receive about
    # 15-20 messages a round, so 20 would cover only the last round; the news itself is also kept in the persona
    # ("news_so_far") so the real history never scrolls out before the cutoff.
    memory_lookback: int = 40
    # Fixes after pilot 1 (HS2 on, HS1 off so pilot 1's preset hash is unchanged):
    # every round without news starts with its date (free play had no sense of time: "'next week' for two months");
    # governments post first in the public feed (pilot 1: Singapore's government happened to post last in round 9
    # and citizens attacked its "silence").
    date_every_round: bool = False
    governments_post_first: bool = False
    style: str = (
        "Plain and conversational, the way people write in an online group or feed: short messages, "
        "in English."
    )
    government_style: str = (
        "The way a government communicates: public statements in the public feed are short and official; "
        "messages in the diplomatic channel are direct but diplomatic. In English."
    )
    notes: dict = field(default_factory=dict)


def _strip_room(text: str) -> str:
    """The pilots' news ended with a line about the audio room; the society has no room."""

    return re.sub(r"\s*The room has (?:just opened|opened again)\.\s*$", "", text).strip()


_NEWS = [_strip_room(_TRIGGER)] + [_strip_room(_ROUND_OBSERVATIONS[r]) for r in (3, 5, 7, 9, 11, 13, 15)]

# Physical facts only, for stages after the cutoff. From haze_2026_sources.md; stages 4 and 6 give no exact count
# because the sources disagree by a day on when Singapore's unhealthy run began (12th day on 16 Oct; 18 days in all).
_PHYSICAL = [
    _NEWS[0],
    "It is now Friday 18 September 2026. Air quality is unhealthy at half of Malaysia's 68 monitoring stations, "
    "and the haze reached southern Vietnam on 14 September.",
    "It is now Friday 9 October 2026. In Singapore the 24-hour PSI reached 192 this evening, the highest this year.",
    "It is now Tuesday 13 October 2026. The fires in Sumatra and Kalimantan are still burning, and Singapore's air "
    "has been in the unhealthy range every day since early October.",
    "It is now Friday 16 October 2026. On 14 October fine-particle pollution in western Singapore reached its "
    "highest level since 2015. Singapore's 24-hour PSI reached 229 today, the very unhealthy range, the 12th day in "
    "a row of unhealthy air. The haze has reached Jakarta.",
    "It is now Wednesday 21 October 2026. The fires are still burning, and Singapore's air has been in the "
    "unhealthy range every day for more than two weeks.",
    "It is now Monday 26 October 2026. Singapore's air has been back in the moderate range since 22 October, after "
    "18 days of unhealthy air, and the first rains have fallen on Sumatra and Kalimantan.",
    "It is now Monday 16 November 2026. Rain put out most of the fires in late October, and the haze has cleared "
    "across the region.",
]
_DATES = ["2026-09-04", "2026-09-18", "2026-10-09", "2026-10-13", "2026-10-16", "2026-10-21", "2026-10-26", "2026-11-16"]
STAGES = tuple(Stage(i + 1, _DATES[i], _NEWS[i], _PHYSICAL[i]) for i in range(8))

SETTING = (
    "Since August 2026, smoke haze from forest and land fires has drifted across Southeast Asia. This is a "
    "simulated online society of people and governments in Singapore, Malaysia, Indonesia and Brunei. People talk "
    "in the online spaces they belong to: a private group for each of Singapore, Malaysia and Indonesia, and a "
    "public regional feed that everyone can read. Each government can read its own country's group and the public "
    "feed, can post public statements in the public feed, and can talk privately with the other governments in a "
    "diplomatic channel. Everyone sees the same news. Everyone writes in English."
)

_ASEAN = (
    "Singapore, Malaysia, Indonesia and Brunei are all members of ASEAN and parties to the ASEAN Agreement on "
    "Transboundary Haze Pollution."
)

AGENTS = {
    # ---- Singapore ----
    "SG1": SocietyAgent(
        "SG1", "Kelvin Tan", "Singapore", "citizen", "Singaporean, lives in Jurong West",
        "Keep your mother and children safe from the haze while getting on with work.",
        "You live in an HDB flat in Jurong West with your wife, your two children in primary school and your "
        "mother, who has asthma. You work as a logistics supervisor at a warehouse in Tuas, partly outdoors. You "
        "check the PSI on your phone several times a day. You remember the 2015 haze, when your mother was in and "
        "out of the clinic. You are in the Singapore group and you read and post in the public regional feed.",
        "Sees the PSI on your phone app showing the unhealthy range again this morning.",
        "You are a Singaporean citizen of Chinese descent and grew up in an HDB flat. You speak Mandarin and English "
        "at home and went to local schools.",
        43,
    ),
    "SG2": SocietyAgent(
        "SG2", "Ahmad Faizal", "Singapore", "citizen", "Singaporean, runs a small business, lives in Bedok",
        "Keep your business going and your family healthy through the haze.",
        "You run a small company with six staff that organises outdoor events and team-building activities. When "
        "the PSI is in the unhealthy range, clients cancel outdoor bookings. You live in Bedok with your wife and "
        "your two young children. You are in the Singapore group and you read and post in the public regional feed.",
        "Sees two clients asking whether next week's outdoor events will go ahead.",
        "You are a Singaporean citizen, Malay, and grew up in Bedok. You speak Malay and English at home. You are "
        "Muslim.",
        38,
    ),
    "SG-G": SocietyAgent(
        "SG-G", "Government of Singapore", "Singapore", "government", "The Government of Singapore",
        "Protect Singapore's people and interests during the haze.",
        "You speak for the Government of Singapore as a whole. Singapore has no large fires of its own; the haze "
        "comes from fires elsewhere. Singapore's Transboundary Haze Pollution Act (2014) allows action against "
        "companies, in Singapore or abroad, that cause or contribute to haze pollution in Singapore. Several large "
        "palm-oil and paper groups with plantations in Indonesia are listed on the Singapore Exchange. Singapore "
        "imports part of its natural gas by pipeline from Indonesia. " + _ASEAN + " You read the Singapore group "
        "and the public regional feed, you can post public statements in the public feed, and you can talk "
        "privately with the other governments in the diplomatic channel.",
        "Sees the National Environment Agency's air-quality readings rising into the unhealthy range.",
    ),
    # ---- Malaysia ----
    "MY1": SocietyAgent(
        "MY1", "Farhana", "Malaysia", "citizen", "Malaysian, lives in Johor Bahru",
        "Keep your son safe and keep your job while the haze disrupts school and work.",
        "You live in Johor Bahru with your husband and your seven-year-old son, who is in primary school. You work "
        "as an administrative clerk at a factory in Pasir Gudang. When schools close, you have to find someone to "
        "look after your son or take leave. Your parents live in Batu Pahat. You are in the Malaysia group and you "
        "read and post in the public regional feed.",
        "Sees a grey sky over Johor Bahru and smells smoke on the way to work.",
        "You are a Malaysian citizen, Malay, and grew up in Johor. You speak Malay at home and use English at work. "
        "You are Muslim.",
        31,
    ),
    "MY2": SocietyAgent(
        "MY2", "Lim Chee Keong", "Malaysia", "citizen", "Malaysian, runs a small tour agency in Selangor",
        "Keep your tour business going through the haze.",
        "You run a small tour agency with four staff that takes tourists to Batu Caves and around Kuala Lumpur. "
        "Bookings have dropped since the haze began. You live in Gombak with your wife and your two teenage "
        "children. You are in the Malaysia group and you read and post in the public regional feed.",
        "Sees three tour bookings for next week cancelled this morning.",
        "You are a Malaysian citizen of Chinese descent and grew up in Selangor. You speak Cantonese at home and "
        "Malay and English at work. You are Buddhist.",
        47,
    ),
    "MY-G": SocietyAgent(
        "MY-G", "Government of Malaysia", "Malaysia", "government", "The Government of Malaysia",
        "Protect Malaysia's people and interests during the haze.",
        "You speak for the Government of Malaysia as a whole. Most of the haze comes from fires in Indonesia, but "
        "Malaysia also has smaller fires of its own this year, in Sarawak and Johor. Malaysia has firefighting "
        "aircraft and personnel. Some Malaysian palm-oil groups have plantations in Indonesia. Malaysia has no law "
        "like Singapore's Transboundary Haze Pollution Act. " + _ASEAN + " You read the Malaysia group and the "
        "public regional feed, you can post public statements in the public feed, and you can talk privately with "
        "the other governments in the diplomatic channel.",
        "Sees reports of school closures and hazardous air in Sarawak.",
    ),
    # ---- Indonesia ----
    "ID1": SocietyAgent(
        "ID1", "Budi Santoso", "Indonesia", "citizen", "Indonesian, lives in Bekasi near Jakarta",
        "Keep earning your daily income on the road and keep your sister's family safe.",
        "You live in Bekasi, near Jakarta, with your wife and your baby daughter. You work as a motorbike "
        "ride-hailing and delivery driver, outdoors all day; you are paid per trip. Your older sister lives with her "
        "family in Palangka Raya, Central Kalimantan, near the fires. She tells you the sky there has been yellow "
        "and orange for weeks and her children keep coughing. You are in the Indonesia group and you read and post "
        "in the public regional feed.",
        "Sees a message from your sister with a photo of an orange sky over Palangka Raya.",
        "You are an Indonesian citizen, Javanese, and grew up in Central Java before moving to the Jakarta area for "
        "work. You speak Indonesian and Javanese at home. You are Muslim.",
        30,
    ),
    "ID2": SocietyAgent(
        "ID2", "Dewi Lestari", "Indonesia", "citizen", "Indonesian, a teacher in Pontianak, West Kalimantan",
        "Keep your children healthy and keep teaching when the smoke allows.",
        "You are a primary-school teacher in Pontianak, West Kalimantan, where the smoke is thick. Your school has "
        "closed several times since August. You live with your husband and your two children, who have been "
        "coughing for weeks. You are in the Indonesia group and you read and post in the public regional feed.",
        "Sees the sky outside the school yellow with smoke and hears children coughing in class.",
        "You are an Indonesian citizen, Malay, and grew up in Pontianak. You speak Indonesian and Pontianak Malay "
        "at home. You are Muslim.",
        36,
    ),
    "ID3": SocietyAgent(
        "ID3", "Sutrisno", "Indonesia", "citizen", "Indonesian, an oil-palm smallholder in South Sumatra",
        "Keep your farm earning and your family provided for.",
        "You own four hectares of oil palm in Ogan Komering Ilir, South Sumatra, and farm them with your family. "
        "Your income comes from selling fresh fruit bunches to a nearby mill. To clear land for replanting, burning "
        "costs a small part of what renting machinery costs. Burning land is illegal in Indonesia. You live with "
        "your wife; your two grown children work in Palembang. You are in the Indonesia group. You do not use the "
        "public regional feed, though you can see what is posted there.",
        "Sees smoke over the peat land across the river from your plot.",
        "You are an Indonesian citizen, Javanese; your parents moved to South Sumatra from Central Java. You speak "
        "Javanese and Indonesian at home. You are Muslim.",
        48,
    ),
    "ID4": SocietyAgent(
        "ID4", "Andreas Wijaya", "Indonesia", "citizen", "Indonesian, an estate manager for a palm-oil group in Riau",
        "Keep your estate running and your workers safe.",
        "You manage one estate in Riau for a large palm-oil group whose parent company is listed on the Singapore "
        "Exchange; the estate has several hundred workers. The group has a no-burning policy. Fires on or near a "
        "company's land can lead to investigations of the company. You live on the estate with your wife; your "
        "children are at school in Pekanbaru. You are in the Indonesia group. You do not post in the public regional "
        "feed, though you can see what is posted there.",
        "Sees the morning fire-watch report listing hotspots near the estate boundary.",
        "You are an Indonesian citizen of Chinese descent and grew up in Medan. You speak Indonesian at home. You "
        "are Catholic.",
        44,
    ),
    "ID-G": SocietyAgent(
        "ID-G", "Government of Indonesia", "Indonesia", "government", "The Government of Indonesia",
        "Protect Indonesia's people and interests during the haze.",
        "You speak for the Government of Indonesia as a whole. Most of the fires are on peat and forest land in "
        "Sumatra and Kalimantan. Fire control, the police, plantation permits (concessions) and energy exports are "
        "the government's responsibility. Indonesia exports natural gas by pipeline to Singapore. Millions of "
        "Indonesians depend on palm oil and on pulp and paper for jobs. " + _ASEAN + " You read the Indonesia group "
        "and the public regional feed, you can post public statements in the public feed, and you can talk "
        "privately with the other governments in the diplomatic channel.",
        "Sees the daily hotspot count for Sumatra and Kalimantan.",
    ),
    # ---- Brunei ----
    "BN1": SocietyAgent(
        "BN1", "Nur Aqilah", "Brunei", "citizen", "Bruneian, lives in Brunei-Muara",
        "Keep your daughter healthy and daily life as normal as possible.",
        "You live in Brunei-Muara district with your husband and your five-year-old daughter, who goes to "
        "kindergarten. You work as a receptionist at a private clinic. Your daughter's kindergarten switched to "
        "home-based learning on 2 and 3 September because of the haze. You read and post in the public regional "
        "feed.",
        "Sees the haze over the river on the way to work.",
        "You are a Bruneian citizen, Malay, and grew up in Bandar Seri Begawan. You speak Malay at home and use "
        "English at work. You are Muslim.",
        32,
    ),
    "BN-G": SocietyAgent(
        "BN-G", "Government of Brunei", "Brunei", "government", "The Government of Brunei",
        "Protect Brunei's people and interests during the haze.",
        "You speak for the Government of Brunei as a whole. Brunei has little burning of its own; the haze reaches it "
        "from fires elsewhere. " + _ASEAN + " You read the public regional feed, you can post public statements in "
        "the public feed, and you can talk privately with the other governments in the diplomatic channel.",
        "Sees the air-quality readings in Brunei-Muara rising.",
    ),
}

GOVERNMENTS = ("SG-G", "MY-G", "ID-G", "BN-G")

CHANNELS = (
    Channel("sg_group", "Singapore group", "a private online group of Singaporeans", ("SG1", "SG2"), ("SG-G",)),
    Channel("my_group", "Malaysia group", "a private online group of Malaysians", ("MY1", "MY2"), ("MY-G",)),
    Channel(
        "id_group", "Indonesia group", "a private online group of Indonesians", ("ID1", "ID2", "ID3", "ID4"), ("ID-G",)
    ),
    Channel(
        "public_feed",
        "public regional feed",
        "a public online feed that everyone in the region can read",
        ("SG1", "SG2", "MY1", "MY2", "ID1", "ID2", "BN1") + GOVERNMENTS,
        ("ID3", "ID4"),
    ),
    Channel("diplomatic", "diplomatic channel", "a private channel between the four governments", GOVERNMENTS),
)

HAZE_SOCIETY = SocietyPreset(
    preset_id="HS1",
    title="2026 Southeast Asian haze: a society of 13 agents in channels",
    setting=SETTING,
    agents=AGENTS,
    channels=CHANNELS,
    stages=STAGES,
)

# ---- HS2: governments given their known interests and history (user approved the approach 2026-11-24) ----
# Pilot 1 (HS1) governments had only their legal tools and fell back on cooperative, identical PR statements. HS2
# adds, for every government under the same headings (economic stakes, relations with neighbours, past episodes),
# facts known before August 2026, each sourced in haze_society_design.md section 9. No instructions on how to act,
# nothing from 2026. Wording is a draft for the user's review; not run.
_GOVERNMENT_FACTS = {
    "SG-G": (
        "Past episodes: in June 2013 Singapore's PSI reached a record 401. In 2014 Singapore passed the "
        "Transboundary Haze Pollution Act, and in 2015 it served notices under the Act on Indonesian companies and "
        "asked a Singapore-listed paper group for information about its suppliers' land. Relations: Singapore has "
        "been the largest source of foreign investment in Indonesia for about a decade."
    ),
    "MY-G": (
        "Past episodes: in June 2013 a haze emergency was declared in Muar and Ledang, Johor, after the air "
        "pollutant index passed 700. Nearly 7,000 Malaysian schools were closed at the worst point of the 2015 "
        "haze, and more than 1,000 in 2019."
    ),
    "ID-G": (
        "Economic stakes: Indonesia is the world's largest palm-oil producer. Millions of Indonesians in Sumatra and "
        "Kalimantan live in the smoke themselves. Relations: Singapore has been the largest source of foreign "
        "investment in Indonesia for about a decade. Past episodes: Indonesia was the last ASEAN member to ratify "
        "the ASEAN haze agreement, in 2014. In June 2013 the Indonesian minister coordinating the haze response "
        "publicly criticised Singapore's complaints about the haze, and Singapore's prime minister declined to "
        "answer in kind."
    ),
    "BN-G": (
        "Economic stakes: Brunei's economy rests on oil and gas. Past episodes: in September 2019 haze from fires in "
        "Kalimantan reached Brunei, and in the 1990s Brunei closed schools because of haze."
    ),
}


def _with_facts(agent: SocietyAgent) -> SocietyAgent:
    facts = _GOVERNMENT_FACTS.get(agent.agent_id)
    if not facts:
        return agent
    # Inserted before the closing sentence about which channels the government reads and writes.
    head, sep, tail = agent.private_knowledge.partition(" You read ")
    return SocietyAgent(**{**asdict(agent), "private_knowledge": f"{head} {facts}{sep}{tail}"})


HAZE_SOCIETY_V2 = SocietyPreset(
    preset_id="HS2",
    title="2026 Southeast Asian haze: 13 agents in channels, governments with known interests and history",
    setting=SETTING,
    agents={aid: _with_facts(a) for aid, a in AGENTS.items()},
    channels=CHANNELS,
    stages=STAGES,
    date_every_round=True,
    governments_post_first=True,
)

SOCIETY_PRESETS = {p.preset_id: p for p in (HAZE_SOCIETY, HAZE_SOCIETY_V2)}


# ---- HS3: HS2 with governments monitoring their national groups silently (user approved 2026-11-25) ----
# HS2 history pilot: citizens were told their government reads their group, but governments cannot speak before the
# cutoff, so "@Government of Singapore ... still no reply" became a main grievance. In HS3 the governments still
# receive their group's messages, but the setting, the turn cue and the citizens' contact lists no longer say so.
SETTING_V3 = SETTING.replace(
    "Each government can read its own country's group and the public feed, can post public statements in the public "
    "feed, and can talk privately with the other governments in a diplomatic channel.",
    "Each government can post public statements in the public feed and can talk privately with the other "
    "governments in a diplomatic channel.",
)
assert SETTING_V3 != SETTING


def _monitors(agent: SocietyAgent) -> SocietyAgent:
    if agent.kind != "government":
        return agent
    text = re.sub(
        r"You read the (Singapore|Malaysia|Indonesia) group and the public regional feed",
        lambda m: f"You monitor the {m.group(1)} group (its members are not told this) and you read the public "
        "regional feed",
        agent.private_knowledge,
    )
    return SocietyAgent(**{**asdict(agent), "private_knowledge": text})


CHANNELS_V3 = tuple(
    Channel(c.channel_id, c.name, c.description, c.speakers, (), c.readers) if c.channel_id.endswith("_group") else c
    for c in CHANNELS
)

HAZE_SOCIETY_V3 = SocietyPreset(
    preset_id="HS3",
    title="2026 Southeast Asian haze: 13 agents in channels, governments with known interests, monitoring silently",
    setting=SETTING_V3,
    agents={aid: _monitors(a) for aid, a in HAZE_SOCIETY_V2.agents.items()},
    channels=CHANNELS_V3,
    stages=STAGES,
    date_every_round=True,
    governments_post_first=True,
)

SOCIETY_PRESETS[HAZE_SOCIETY_V3.preset_id] = HAZE_SOCIETY_V3


# ---- HS4: HS3 plus a plain public/private line in the turn cue (mechanical fix, user approved 2026-11-25) ----
# HS3 test: Singapore's government wrote a message addressed "to diplomatic channel" while in the public feed (round 9;
# governments post in the feed right after the diplomatic channel). Each turn cue now says who can read the channel.
_CUE_NOTES = {
    "public_feed": "This is public: anyone in the region can read it, including people and governments of other "
    "countries.",
    "diplomatic": "This is private: only the four governments can read it; the public cannot.",
}
CHANNELS_V4 = tuple(
    Channel(c.channel_id, c.name, c.description, c.speakers, c.readers, c.hidden_readers, _CUE_NOTES.get(c.channel_id, ""))
    for c in CHANNELS_V3
)

HAZE_SOCIETY_V4 = SocietyPreset(
    preset_id="HS4",
    title="2026 Southeast Asian haze: 13 agents in channels, governments monitoring silently, public/private cue",
    setting=SETTING_V3,
    agents=HAZE_SOCIETY_V3.agents,
    channels=CHANNELS_V4,
    stages=STAGES,
    date_every_round=True,
    governments_post_first=True,
)

SOCIETY_PRESETS[HAZE_SOCIETY_V4.preset_id] = HAZE_SOCIETY_V4
