"""Shared schemas and controlled cultural-background configurations.

Scenario modules deliberately do not contain a cultural-background field. The
materializer controls background labels and display names for both the standard
C0-C4 rotations and the exploratory factorial screen.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime
import re
from typing import Any, Mapping


AGENT_IDS = ("A", "B", "C", "D")
AGENT_DISPLAY_NAMES = {
    "A": "Alex",
    "B": "Jamie",
    "C": "Casey",
    "D": "Robin",
}
CULTURAL_DISPLAY_NAMES = {
    "Singaporean Chinese": "John",
    "Singaporean Malay": "Fatimah",
    "Singaporean Indian": "Arjun",
    "Singaporean Eurasian": "Michelle",
}
CULTURAL_BACKGROUNDS = (
    "Singaporean Chinese",
    "Singaporean Malay",
    "Singaporean Indian",
    "Singaporean Eurasian",
)

BACKGROUND_CONFIGURATIONS: dict[str, dict[str, str | None]] = {
    "C0": {agent_id: None for agent_id in AGENT_IDS},
    "C1": {
        "A": "Singaporean Chinese",
        "B": "Singaporean Malay",
        "C": "Singaporean Indian",
        "D": "Singaporean Eurasian",
    },
    "C2": {
        "A": "Singaporean Malay",
        "B": "Singaporean Indian",
        "C": "Singaporean Eurasian",
        "D": "Singaporean Chinese",
    },
    "C3": {
        "A": "Singaporean Indian",
        "B": "Singaporean Eurasian",
        "C": "Singaporean Chinese",
        "D": "Singaporean Malay",
    },
    "C4": {
        "A": "Singaporean Eurasian",
        "B": "Singaporean Chinese",
        "C": "Singaporean Malay",
        "D": "Singaporean Indian",
    },
}

# Two-by-two exploratory treatment using the C1 role/background allocation.
# The first bit controls explicit cultural-background fields; the second controls
# culturally associated display names.
FACTORIAL_CONFIGURATIONS = {
    "F00": {"background_labels": False, "cultural_names": False},
    "F10": {"background_labels": True, "cultural_names": False},
    "F01": {"background_labels": False, "cultural_names": True},
    "F11": {"background_labels": True, "cultural_names": True},
}
# Profile screen: does anything richer than a bare label change behaviour? All cells keep
# neutral names, so a difference cannot come from the name. Biographies share one sentence
# frame and state facts only, never conduct. They describe a plausible person, not a group;
# none of these details holds for everyone with that background.
_BIOGRAPHY_FRAME = (
    "Grew up in an HDB flat in Singapore and went to local schools. The family speaks "
    "{languages} at home and is {faith}. Goes home for {festival} every year."
)
BIOGRAPHIES = {
    "Singaporean Chinese": _BIOGRAPHY_FRAME.format(
        languages="Mandarin and English", faith="Buddhist", festival="Chinese New Year"
    ),
    "Singaporean Malay": _BIOGRAPHY_FRAME.format(
        languages="Malay and English", faith="Muslim", festival="Hari Raya"
    ),
    "Singaporean Indian": _BIOGRAPHY_FRAME.format(
        languages="Tamil and English", faith="Hindu", festival="Deepavali"
    ),
    "Singaporean Eurasian": _BIOGRAPHY_FRAME.format(
        languages="English", faith="Catholic", festival="Christmas"
    ),
}
# Used by the K1 cell: the faith is the agent's own, not the family's. These are one plausible
# person each, not claims about a group.
_PERSONAL_BIOGRAPHY_FRAME = (
    "You grew up in an HDB flat in Singapore and went to local schools. You speak {languages} at "
    "home. {faith} You go home for {festival} every year."
)
PERSONAL_BIOGRAPHIES = {
    "Singaporean Chinese": _PERSONAL_BIOGRAPHY_FRAME.format(
        languages="Mandarin and English", faith="You are Buddhist.", festival="Chinese New Year"
    ),
    "Singaporean Malay": _PERSONAL_BIOGRAPHY_FRAME.format(
        languages="Malay and English", faith="You are Muslim and eat halal.", festival="Hari Raya"
    ),
    "Singaporean Indian": _PERSONAL_BIOGRAPHY_FRAME.format(
        languages="Tamil and English",
        faith="You are Hindu and do not eat beef.",
        festival="Deepavali",
    ),
    "Singaporean Eurasian": _PERSONAL_BIOGRAPHY_FRAME.format(
        languages="English", faith="You are Catholic.", festival="Christmas"
    ),
}
VALUE_ORIENTATIONS = {
    "harmony": (
        "You care most about keeping things peaceful with the people around you, and you "
        "would rather not embarrass anyone in front of others."
    ),
    "direct": (
        "You care most about saying plainly what you think and want, and you expect others "
        "to do the same."
    ),
}
# L: label only. B: label plus biography, same rotations as L. V: values with no label; the
# four cells give each role each value twice.
PROFILE_CONFIGURATIONS: dict[str, dict[str, Any]] = {
    **{f"L{n}": {"rotation": f"C{n}"} for n in (1, 2, 3)},
    **{f"B{n}": {"rotation": f"C{n}", "biography": True} for n in (1, 2, 3)},
    # P: same rotations as L, with "Malay" in place of "Singaporean Malay". The setting stays
    # in Singapore, and so does the agent's country of residence.
    **{f"P{n}": {"rotation": f"C{n}", "plain_label": True} for n in (1, 2, 3)},
    "V1": {"harmony_roles": ("A", "B")},
    "V2": {"harmony_roles": ("C", "D")},
    "V3": {"harmony_roles": ("A", "C")},
    "V4": {"harmony_roles": ("B", "D")},
    # W: the V cells with a set first speaker. Each role opens twice, once with each value,
    # so an effect of speaking first cannot pass for an effect of the value.
    "W1": {"harmony_roles": ("A", "B"), "first_speaker": "A"},
    "W2": {"harmony_roles": ("A", "B"), "first_speaker": "C"},
    "W3": {"harmony_roles": ("C", "D"), "first_speaker": "D"},
    "W4": {"harmony_roles": ("C", "D"), "first_speaker": "B"},
    "W5": {"harmony_roles": ("A", "C"), "first_speaker": "C"},
    "W6": {"harmony_roles": ("A", "C"), "first_speaker": "D"},
    "W7": {"harmony_roles": ("B", "D"), "first_speaker": "B"},
    "W8": {"harmony_roles": ("B", "D"), "first_speaker": "A"},
}
# Named culture screen. Several names per background, so an effect of one name or of gender
# is not read as an effect of culture. Labels are plain ("Malay"), as the user specified.
BACKGROUND_NAMES = {
    "Singaporean Chinese": {"male": ("Wei Ming", "Jun Jie"), "female": ("Hui Min", "Xin Yi")},
    "Singaporean Malay": {"male": ("Hafiz", "Irfan"), "female": ("Nurul", "Aisyah")},
    "Singaporean Indian": {"male": ("Karthik", "Suresh"), "female": ("Priya", "Kavitha")},
    "Singaporean Eurasian": {
        "male": ("Daniel Pereira", "Marcus de Souza"),
        "female": ("Rachel Pereira", "Natalie Rodrigues"),
    },
}
# Rotation, male-named backgrounds, and opening background for each run, found by search:
# every background has 5 male and 5 female names, every run has 2 of each, and openers are
# spread across backgrounds (2-3), roles (2-3), and gender (5 each).
_NAMED_SCHEDULE = (
    ("C1", ("Indian", "Eurasian"), "Eurasian"),
    ("C2", ("Malay", "Eurasian"), "Indian"),
    ("C3", ("Indian", "Eurasian"), "Indian"),
    ("C4", ("Chinese", "Indian"), "Malay"),
    ("C1", ("Chinese", "Malay"), "Eurasian"),
    ("C2", ("Chinese", "Eurasian"), "Chinese"),
    ("C3", ("Malay", "Indian"), "Chinese"),
    ("C4", ("Chinese", "Indian"), "Eurasian"),
    ("C1", ("Chinese", "Malay"), "Malay"),
    ("C2", ("Malay", "Eurasian"), "Malay"),
)


def _named_cells() -> dict[str, dict[str, Any]]:
    """Expand the schedule, cycling each background's names within each gender."""

    used: dict[tuple[str, str], int] = {}
    cells: dict[str, dict[str, Any]] = {}
    for number, (rotation, male, opener) in enumerate(_NAMED_SCHEDULE, start=1):
        names: dict[str, str] = {}
        genders: dict[str, str] = {}
        for background, options in BACKGROUND_NAMES.items():
            gender = "male" if background.removeprefix("Singaporean ") in male else "female"
            count = used.get((background, gender), 0)
            used[(background, gender)] = count + 1
            names[background] = options[gender][count % 2]
            genders[background] = gender
        assignment = BACKGROUND_CONFIGURATIONS[rotation]
        cells[f"N{number:02d}"] = {
            "rotation": rotation,
            "plain_label": True,
            "names": names,
            "name_genders": genders,
            "first_speaker": next(
                role
                for role, background in assignment.items()
                if background == f"Singaporean {opener}"
            ),
        }
    return cells


PROFILE_CONFIGURATIONS.update(_named_cells())
# M: the named cells plus biography. M1-M4 put each background in each role once.
PROFILE_CONFIGURATIONS.update(
    {
        f"M{number}": {**PROFILE_CONFIGURATIONS[f"N{number:02d}"], "biography": True}
        for number in range(1, 11)
    }
)
# K1: M3's placement (Suresh, Daniel Pereira, Hui Min, Aisyah) with first-person biographies, for
# S36 and S37, whose shared setting states these same faiths.
PROFILE_CONFIGURATIONS["K1"] = {**PROFILE_CONFIGURATIONS["M3"], "biography": "personal"}
# K4: M1's placement (Hui Min, Nurul, Karthik, Daniel Pereira), Agent A opening. Used for
# controls, where Agent D's Catholic faith has nothing to do with the issue.
PROFILE_CONFIGURATIONS["K4"] = {
    **PROFILE_CONFIGURATIONS["M1"],
    "biography": "personal",
    "first_speaker": "A",
}
# HW1-HW4: casts for scenario 1 (housewarming drinks). Alcohol needs casts of its own: no non-key
# agent may hold a faith that rules alcohol out, so the only Muslim is the key agent, and the
# buyer (Agent A) is the same Catholic, Natalie Rodrigues, in every cell. Backgrounds may repeat. HW1 and HW4 differ
# only in Agent D. Plain labels, first-person biographies, Agent A opens.
def _cast(roles: dict[str, tuple[str, str]]) -> dict[str, Any]:
    return {
        "backgrounds": {role: f"Singaporean {background}" for role, (background, _) in roles.items()},
        "role_names": {role: name for role, (_, name) in roles.items()},
        "plain_label": True,
        "biography": "personal",
        "first_speaker": "A",
    }


PROFILE_CONFIGURATIONS.update(
    {
        "HW1": _cast({"A": ("Eurasian", "Natalie Rodrigues"), "B": ("Chinese", "Jun Jie"), "C": ("Indian", "Suresh"), "D": ("Malay", "Aisyah")}),
        "HW2": _cast({"A": ("Eurasian", "Natalie Rodrigues"), "B": ("Chinese", "Jun Jie"), "C": ("Eurasian", "Marcus de Souza"), "D": ("Indian", "Karthik")}),
        "HW3": _cast({"A": ("Eurasian", "Natalie Rodrigues"), "B": ("Indian", "Suresh"), "C": ("Eurasian", "Marcus de Souza"), "D": ("Chinese", "Xin Yi")}),
        "HW4": _cast({"A": ("Eurasian", "Natalie Rodrigues"), "B": ("Chinese", "Jun Jie"), "C": ("Indian", "Suresh"), "D": ("Eurasian", "Daniel Pereira")}),
    }
)
# FR1-FR4: casts for scenario 3 (fasting and the dinner rota). The issue is food, so no non-key
# agent holds a faith with a food rule; in FR3 the other Buddhist is swapped for a Catholic.
# FR1, FR2 and FR4 differ only in Agent D.
PROFILE_CONFIGURATIONS.update(
    {
        "FR1": _cast({"A": ("Eurasian", "Natalie Rodrigues"), "B": ("Chinese", "Jun Jie"), "C": ("Eurasian", "Marcus de Souza"), "D": ("Malay", "Aisyah")}),
        "FR2": _cast({"A": ("Eurasian", "Natalie Rodrigues"), "B": ("Chinese", "Jun Jie"), "C": ("Eurasian", "Marcus de Souza"), "D": ("Indian", "Karthik")}),
        "FR3": _cast({"A": ("Eurasian", "Natalie Rodrigues"), "B": ("Eurasian", "Rachel Pereira"), "C": ("Eurasian", "Marcus de Souza"), "D": ("Chinese", "Xin Yi")}),
        "FR4": _cast({"A": ("Eurasian", "Natalie Rodrigues"), "B": ("Chinese", "Jun Jie"), "C": ("Eurasian", "Marcus de Souza"), "D": ("Eurasian", "Daniel Pereira")}),
    }
)
# RO1-RO4: casts for scenario 4 (festival-week roster). Roles A-C are fixed in every cell and
# celebrate none of the variant festivals; only Agent D changes.
_RO_FIXED = {"A": ("Eurasian", "Natalie Rodrigues"), "B": ("Eurasian", "Marcus de Souza"), "C": ("Eurasian", "Rachel Pereira")}
PROFILE_CONFIGURATIONS.update(
    {
        "RO1": _cast({**_RO_FIXED, "D": ("Malay", "Aisyah")}),
        "RO2": _cast({**_RO_FIXED, "D": ("Indian", "Karthik")}),
        "RO3": _cast({**_RO_FIXED, "D": ("Chinese", "Xin Yi")}),
        "RO4": _cast({**_RO_FIXED, "D": ("Chinese", "Jun Jie")}),
    }
)
# FL1-FL4: casts for scenario 5 (farewell lunch). The issue is food, so roles A-C are the same three
# Catholics in every cell (no second Buddhist in the Buddhist variant). D is male throughout. The
# control D is Chinese, as in RO4, so D is never of the same background as A-C.
PROFILE_CONFIGURATIONS.update(
    {
        "FL1": _cast({**_RO_FIXED, "D": ("Malay", "Hafiz")}),
        "FL2": _cast({**_RO_FIXED, "D": ("Indian", "Karthik")}),
        "FL3": _cast({**_RO_FIXED, "D": ("Chinese", "Wei Ming")}),
        "FL4": _cast({**_RO_FIXED, "D": ("Chinese", "Jun Jie")}),
    }
)
# UN1-UN4 (scenario 6, uniform rule) and VD1-VD3 (scenario 8, void deck wake): the variant faiths
# include Hindu, Buddhist and Catholic, so roles A-C are the same three Malay Muslims. UN D is male
# throughout and VD D female throughout; neither D shares a background with A-C.
_MALAY_FIXED = {"A": ("Malay", "Hafiz"), "B": ("Malay", "Nurul"), "C": ("Malay", "Irfan")}
PROFILE_CONFIGURATIONS.update(
    {
        "UN1": _cast({**_MALAY_FIXED, "D": ("Indian", "Karthik")}),
        "UN2": _cast({**_MALAY_FIXED, "D": ("Chinese", "Wei Ming")}),
        "UN3": _cast({**_MALAY_FIXED, "D": ("Eurasian", "Daniel Pereira")}),
        "UN4": _cast({**_MALAY_FIXED, "D": ("Chinese", "Jun Jie")}),
        "VD1": _cast({**_MALAY_FIXED, "D": ("Chinese", "Xin Yi")}),
        "VD2": _cast({**_MALAY_FIXED, "D": ("Eurasian", "Rachel Pereira")}),
        "VD3": _cast({**_MALAY_FIXED, "D": ("Indian", "Priya")}),
    }
)
# LG1-LG4: scenario 10 (meetings in another language). The key is the majority, so roles A-C share a
# background (Chinese, Malay, Indian) and D is the same English-only Eurasian in every cell; LG4 is the
# mixed control. A-C are male, female, male in every cell.
_LANGUAGE_D = ("Eurasian", "Rachel Pereira")
PROFILE_CONFIGURATIONS.update(
    {
        "LG1": _cast({"A": ("Chinese", "Wei Ming"), "B": ("Chinese", "Hui Min"), "C": ("Chinese", "Jun Jie"), "D": _LANGUAGE_D}),
        "LG2": _cast({"A": ("Malay", "Hafiz"), "B": ("Malay", "Nurul"), "C": ("Malay", "Irfan"), "D": _LANGUAGE_D}),
        "LG3": _cast({"A": ("Indian", "Karthik"), "B": ("Indian", "Priya"), "C": ("Indian", "Suresh"), "D": _LANGUAGE_D}),
        "LG4": _cast({"A": ("Chinese", "Wei Ming"), "B": ("Malay", "Nurul"), "C": ("Indian", "Suresh"), "D": _LANGUAGE_D}),
    }
)
# NO1-NO4 (scenario 11, early-morning noise), WK1-WK4 (scenario 12, weekly slot) and RM1-RM4 (scenario 13,
# spare office room): the variant faiths are Muslim, Hindu and Buddhist, so roles A-C are three Catholics,
# the same people in every cell of a scenario. NO and RM have a female D throughout, WK a male D (Friday
# prayers at the mosque). The control D is Chinese, so D never shares a background with A-C.
_NOISE_FIXED = {"A": ("Eurasian", "Marcus de Souza"), "B": ("Eurasian", "Rachel Pereira"), "C": ("Eurasian", "Natalie Rodrigues")}
_OFFICE_FIXED = {"A": ("Eurasian", "Natalie Rodrigues"), "B": ("Eurasian", "Marcus de Souza"), "C": ("Eurasian", "Rachel Pereira")}
PROFILE_CONFIGURATIONS.update(
    {
        "NO1": _cast({**_NOISE_FIXED, "D": ("Malay", "Aisyah")}),
        "NO2": _cast({**_NOISE_FIXED, "D": ("Indian", "Priya")}),
        "NO3": _cast({**_NOISE_FIXED, "D": ("Chinese", "Xin Yi")}),
        "NO4": _cast({**_NOISE_FIXED, "D": ("Chinese", "Hui Min")}),
        "WK1": _cast({**_OFFICE_FIXED, "D": ("Malay", "Hafiz")}),
        "WK2": _cast({**_OFFICE_FIXED, "D": ("Indian", "Karthik")}),
        "WK3": _cast({**_OFFICE_FIXED, "D": ("Chinese", "Wei Ming")}),
        "WK4": _cast({**_OFFICE_FIXED, "D": ("Chinese", "Jun Jie")}),
        "RM1": _cast({**_OFFICE_FIXED, "D": ("Malay", "Nurul")}),
        "RM2": _cast({**_OFFICE_FIXED, "D": ("Indian", "Kavitha")}),
        "RM3": _cast({**_OFFICE_FIXED, "D": ("Chinese", "Xin Yi")}),
        "RM4": _cast({**_OFFICE_FIXED, "D": ("Chinese", "Hui Min")}),
    }
)
# HX1-HX2: race-versus-religion test on scenario 1 (S46, housewarming, Muslim need). HW1 with only Agent D
# changed: the same Muslim faith and need, held by an Indian Muslim (HX1) or a Chinese Muslim (HX2) instead
# of a Malay. The shared setting still says D "is Muslim and eats halal", so only D's name, label, and home
# language change. Everyone else is the HW1 cast.
_MUSLIM_BIOGRAPHY = (
    "You grew up in an HDB flat in Singapore and went to local schools. You speak {languages} at home. "
    "You are Muslim and eat halal. You go home for Hari Raya every year."
)
_HW1_FIXED = {"A": ("Eurasian", "Natalie Rodrigues"), "B": ("Chinese", "Jun Jie"), "C": ("Indian", "Suresh")}
PROFILE_CONFIGURATIONS.update(
    {
        "HX1": {
            **_cast({**_HW1_FIXED, "D": ("Indian", "Fathima")}),
            "biography_overrides": {"D": _MUSLIM_BIOGRAPHY.format(languages="Tamil and English")},
        },
        "HX2": {
            **_cast({**_HW1_FIXED, "D": ("Chinese", "Mei Ling")}),
            "biography_overrides": {"D": _MUSLIM_BIOGRAPHY.format(languages="Mandarin and English")},
        },
        # Crossed cells, to separate the name others see from D's own label: HX3 keeps the name Aisyah with
        # a Chinese label and Mandarin at home; HX4 keeps the Malay label and biography with the name Mei Ling.
        "HX3": {
            **_cast({**_HW1_FIXED, "D": ("Chinese", "Aisyah")}),
            "biography_overrides": {"D": _MUSLIM_BIOGRAPHY.format(languages="Mandarin and English")},
        },
        "HX4": _cast({**_HW1_FIXED, "D": ("Malay", "Mei Ling")}),
    }
)
# SM1-SM4: scenario 15 (cooking smells), the first case scenario with no religion in it. Every role gets a
# biography without a faith line, and the shared setting states backgrounds, not faiths. Roles A-C are the NO
# cast; D is female, with the same names as the NO cells.
_SECULAR_BIOGRAPHY = (
    "You grew up in an HDB flat in Singapore and went to local schools. You speak {languages} at home."
)
_SECULAR_LANGUAGES = {"Chinese": "Mandarin and English", "Eurasian": "English", "Indian": "Tamil and English", "Malay": "Malay and English"}


def _secular_cast(roles: dict[str, tuple[str, str]]) -> dict[str, Any]:
    return {
        **_cast(roles),
        "biography_overrides": {
            role: _SECULAR_BIOGRAPHY.format(languages=_SECULAR_LANGUAGES[background])
            for role, (background, _) in roles.items()
        },
    }


PROFILE_CONFIGURATIONS.update(
    {
        "SM1": _secular_cast({**_NOISE_FIXED, "D": ("Malay", "Aisyah")}),
        "SM2": _secular_cast({**_NOISE_FIXED, "D": ("Indian", "Priya")}),
        "SM3": _secular_cast({**_NOISE_FIXED, "D": ("Chinese", "Xin Yi")}),
        "SM4": _secular_cast({**_NOISE_FIXED, "D": ("Chinese", "Hui Min")}),
    }
)
# K3: M2's placement (Hafiz, Priya, Marcus de Souza, Xin Yi) for S40 and S41, Agent A opening.
PROFILE_CONFIGURATIONS["K3"] = {
    **PROFILE_CONFIGURATIONS["M2"],
    "biography": "personal",
    "first_speaker": "A",
}
# K2: M4's placement (Rachel Pereira, Wei Ming, Nurul, Karthik) for S38 and S39, with Agent A
# opening as in K1 (M4 itself opens with Agent C).
PROFILE_CONFIGURATIONS["K2"] = {
    **PROFILE_CONFIGURATIONS["M4"],
    "biography": "personal",
    "first_speaker": "A",
}
# Languages an agent thinks in for the H cells. Agents still speak English.
HOME_LANGUAGES = {
    "Singaporean Chinese": "Mandarin",
    "Singaporean Malay": "Malay",
    "Singaporean Indian": "Tamil",
    "Singaporean Eurasian": "English",
}
# H: M1-M4 thinking privately in a home language. E: M1-M4 told to act on typical cultural
# values, with the prompt's rule against that removed, as an upper bound. E is a behavioural
# instruction on purpose, so it must never be pooled with cells that have no such instruction.
PROFILE_CONFIGURATIONS.update(
    {
        **{
            f"H{number}": {**PROFILE_CONFIGURATIONS[f"M{number}"], "home_language_thinking": True}
            for number in range(1, 5)
        },
        **{
            f"E{number}": {**PROFILE_CONFIGURATIONS[f"M{number}"], "explicit_culture": True}
            for number in range(1, 5)
        },
    }
)
_SAME_CULTURE_GENDERS = (
    ("male", "female", "male", "female"),
    ("female", "male", "female", "male"),
    ("male", "male", "female", "female"),
    ("female", "female", "male", "male"),
)


def _same_culture_cells() -> dict[str, dict[str, Any]]:
    """G: four agents from one background, a baseline for differences within a culture."""

    cells: dict[str, dict[str, Any]] = {}
    for number, (background, options) in enumerate(BACKGROUND_NAMES.items(), start=1):
        used = {"male": 0, "female": 0}
        role_names: dict[str, str] = {}
        role_genders: dict[str, str] = {}
        for role, gender in zip(AGENT_IDS, _SAME_CULTURE_GENDERS[number - 1]):
            role_names[role] = options[gender][used[gender]]
            role_genders[role] = gender
            used[gender] += 1
        cells[f"G{number}"] = {
            "same_background": background,
            "plain_label": True,
            "biography": True,
            "role_names": role_names,
            "role_genders": role_genders,
            "first_speaker": AGENT_IDS[number - 1],
        }
    return cells


PROFILE_CONFIGURATIONS.update(_same_culture_cells())

MATERIALIZATION_CONFIGURATION_IDS = (
    *BACKGROUND_CONFIGURATIONS,
    *FACTORIAL_CONFIGURATIONS,
    *PROFILE_CONFIGURATIONS,
)


@dataclass(frozen=True)
class AgentPreset:
    """Facts supplied only to one agent unless independently observable."""

    age: int
    role: str
    immediate_priority: str
    private_knowledge: str
    initial_observation: str
    interaction_style: str = (
        "Brief and conversational; speak only when directly involved or when adding useful information."
    )
    behavioral_guidance: str = (
        "Reassess your immediate priority when observable facts change; do not keep defending "
        "a practical reason after it is no longer true."
    )
    normative_position: str = (
        "Separate what you personally observed from what you think people ought to do."
    )
    negotiation_boundary: str = (
        "You may revise a position when its practical cost is addressed, but do not agree "
        "merely to end the conversation."
    )
    reconsideration_criteria: str = (
        "Change or soften your position only when a new observed fact, a relevant reason, or "
        "a concrete proposal addresses the basis for it; politeness and repetition alone are "
        "not reasons to agree."
    )


@dataclass(frozen=True)
class ScenarioPreset:
    """One background-neutral scenario shared across C0-C4."""

    scenario_id: str
    title: str
    environment: str
    initial_datetime: str
    source_status: str
    initial_interaction_type: str
    shared_setting: str
    shared_trigger: str
    agents: Mapping[str, AgentPreset]
    observation_focus: str
    implementation_notes: str = ""
    round_observations: Mapping[int, str] = field(default_factory=dict)
    # Empty means free resolution: agents are told no agreement is required. Non-empty
    # text is shown identically to every agent and replaces that sentence. Resolution-
    # expected scenarios must not be pooled with free-resolution ones.
    resolution_expectation: str = ""
    # True removes timing cues from the shared prompt (the clock line, the "five minutes"
    # example, and the time-estimate guidance). Scenario text must be timing-free too.
    timing_free: bool = False
    # True makes the interaction speech-only in the shared prompt: physical-action wording
    # is dropped and spoken commitments count. Combined with a resolution expectation it
    # also replaces the 'priority is a hard constraint' rule with a priced-preference rule.
    conversation_only: bool = False
    # True applies the priced-preference rule to a conversation-only scenario that has no
    # resolution expectation, so a with/without-notice pair differs only in the notice.
    priced_priority: bool = False
    # True keeps the shared setting in every prompt and stores the opening event in episodic
    # memory. Otherwise both live only in the agent's context, which the model's own summary
    # replaces after each turn, so they fade. Use only when the setting cannot go stale.
    pin_shared_setting: bool = False


def validate_scenario(scenario: ScenarioPreset) -> None:
    """Fail fast when an editable scenario preset is structurally incomplete."""

    if set(scenario.agents) != set(AGENT_IDS):
        raise ValueError(
            f"{scenario.scenario_id} must define exactly agents {AGENT_IDS}."
        )
    if not (scenario.scenario_id.startswith("S") and scenario.scenario_id[1:].isdigit() and len(scenario.scenario_id) in (3, 4)):
        raise ValueError("scenario_id must use the S01-S999 form.")
    parsed_datetime = datetime.fromisoformat(scenario.initial_datetime)
    if parsed_datetime.tzinfo is None:
        raise ValueError("initial_datetime must include an explicit UTC offset.")
    for round_number, observation in scenario.round_observations.items():
        if round_number < 2 or not observation.strip():
            raise ValueError(
                "round_observations must contain non-empty updates for round 2 or later."
            )
    for agent_id, agent in scenario.agents.items():
        if agent.age < 18:
            raise ValueError(f"{scenario.scenario_id}-{agent_id} must be an adult.")
        for field_name, value in asdict(agent).items():
            if value is None or (isinstance(value, str) and not value.strip()):
                raise ValueError(
                    f"{scenario.scenario_id}-{agent_id}.{field_name} is empty."
                )


def materialize_configuration(
    scenario: ScenarioPreset, config_id: str
) -> dict[str, Any]:
    """Return a serializable run preset with the requested background rotation.

    C0 does not contain a ``cultural_background`` key and uses neutral names.
    C1-C4 add one background label and its associated name to each agent. The
    Fxx cells independently switch labels and associated names using C1 roles.
    """

    validate_scenario(scenario)
    profile = PROFILE_CONFIGURATIONS.get(config_id)
    if config_id in BACKGROUND_CONFIGURATIONS:
        assignments = BACKGROUND_CONFIGURATIONS[config_id]
        name_assignments = assignments
        factorial_treatment = None
    elif profile is not None:
        if "backgrounds" in profile:
            assignments = dict(profile["backgrounds"])
        elif "same_background" in profile:
            assignments = {agent_id: profile["same_background"] for agent_id in AGENT_IDS}
        else:
            assignments = BACKGROUND_CONFIGURATIONS[profile.get("rotation", "C0")]
        name_assignments = BACKGROUND_CONFIGURATIONS["C0"]
        factorial_treatment = None
    elif config_id in FACTORIAL_CONFIGURATIONS:
        factorial_treatment = FACTORIAL_CONFIGURATIONS[config_id]
        c1_assignments = BACKGROUND_CONFIGURATIONS["C1"]
        assignments = (
            c1_assignments
            if factorial_treatment["background_labels"]
            else BACKGROUND_CONFIGURATIONS["C0"]
        )
        name_assignments = (
            c1_assignments
            if factorial_treatment["cultural_names"]
            else BACKGROUND_CONFIGURATIONS["C0"]
        )
    else:
        expected = ", ".join(MATERIALIZATION_CONFIGURATION_IDS)
        raise KeyError(f"Unknown configuration {config_id!r}; expected {expected}.")

    display_names = {
        agent_id: (
            AGENT_DISPLAY_NAMES[agent_id]
            if cultural_background is None
            else CULTURAL_DISPLAY_NAMES[cultural_background]
        )
        for agent_id, cultural_background in name_assignments.items()
    }
    if profile and "names" in profile:
        display_names = {
            agent_id: profile["names"][background]
            for agent_id, background in assignments.items()
        }
    if profile and "role_names" in profile:
        display_names = dict(profile["role_names"])
    payload = _render_agent_display_names(asdict(scenario), display_names)
    payload["configuration_id"] = config_id
    if factorial_treatment is not None:
        payload["factorial_treatment"] = {
            **factorial_treatment,
            "background_rotation": "C1",
        }
    for agent_id, cultural_background in assignments.items():
        payload["agents"][agent_id]["display_name"] = display_names[agent_id]
        if cultural_background is not None:
            payload["agents"][agent_id]["cultural_background"] = (
                cultural_background.removeprefix("Singaporean ")
                if profile and profile.get("plain_label")
                else cultural_background
            )
        if profile and profile.get("biography"):
            override = (profile.get("biography_overrides") or {}).get(agent_id)
            payload["agents"][agent_id]["biography"] = override or (
                PERSONAL_BIOGRAPHIES if profile["biography"] == "personal" else BIOGRAPHIES
            )[cultural_background]
        if profile and profile.get("home_language_thinking"):
            payload["agents"][agent_id]["thinking_language"] = HOME_LANGUAGES[cultural_background]
        if profile and profile.get("explicit_culture"):
            payload["agents"][agent_id]["explicit_culture"] = cultural_background.removeprefix(
                "Singaporean "
            )
        if profile and "harmony_roles" in profile:
            orientation = "harmony" if agent_id in profile["harmony_roles"] else "direct"
            payload["agents"][agent_id]["personal_values"] = VALUE_ORIENTATIONS[orientation]
    if profile is not None:
        payload["profile_treatment"] = dict(profile)
    return payload


def _render_agent_display_names(
    value: Any, display_names: Mapping[str, str]
) -> Any:
    """Replace explicit role labels while preserving A-D analysis keys.

    Bare ``A`` is ambiguous with the English article, so scenario prose must use
    ``Agent A`` (or ``Agents A and D``) when it means a participant.
    """

    if isinstance(value, str):
        rendered = value
        plural_pattern = re.compile(r"\bAgents ([A-D]) and ([A-D])\b")
        rendered = plural_pattern.sub(
            lambda match: (
                f"{display_names[match.group(1)]} and "
                f"{display_names[match.group(2)]}"
            ),
            rendered,
        )
        for agent_id, display_name in display_names.items():
            rendered = rendered.replace(f"Agent {agent_id}", display_name)
        return rendered
    if isinstance(value, dict):
        return {
            key: _render_agent_display_names(item, display_names)
            for key, item in value.items()
        }
    if isinstance(value, list):
        return [_render_agent_display_names(item, display_names) for item in value]
    if isinstance(value, tuple):
        return tuple(
            _render_agent_display_names(item, display_names) for item in value
        )
    return value


def _validate_background_design() -> None:
    if set(CULTURAL_DISPLAY_NAMES) != set(CULTURAL_BACKGROUNDS):
        raise ValueError("Every cultural background must have one associated display name.")
    if len(set(CULTURAL_DISPLAY_NAMES.values())) != len(CULTURAL_DISPLAY_NAMES):
        raise ValueError("Cultural display names must be unique.")
    if set(FACTORIAL_CONFIGURATIONS) != {"F00", "F10", "F01", "F11"}:
        raise ValueError("Factorial configurations must define the complete two-by-two design.")

    for config_id, assignments in BACKGROUND_CONFIGURATIONS.items():
        if set(assignments) != set(AGENT_IDS):
            raise ValueError(f"{config_id} does not assign all four agent slots.")
        values = tuple(assignments.values())
        if config_id == "C0" and any(value is not None for value in values):
            raise ValueError("C0 must omit all cultural-background labels.")
        if config_id != "C0" and set(values) != set(CULTURAL_BACKGROUNDS):
            raise ValueError(f"{config_id} must use each background exactly once.")

    for agent_id in AGENT_IDS:
        assigned = {
            BACKGROUND_CONFIGURATIONS[config_id][agent_id]
            for config_id in ("C1", "C2", "C3", "C4")
        }
        if assigned != set(CULTURAL_BACKGROUNDS):
            raise ValueError(f"Background rotation is not balanced for Agent {agent_id}.")


_validate_background_design()


__all__ = [
    "AGENT_IDS",
    "AGENT_DISPLAY_NAMES",
    "AgentPreset",
    "BACKGROUND_CONFIGURATIONS",
    "BACKGROUND_NAMES",
    "BIOGRAPHIES",
    "PERSONAL_BIOGRAPHIES",
    "HOME_LANGUAGES",
    "PROFILE_CONFIGURATIONS",
    "VALUE_ORIENTATIONS",
    "CULTURAL_DISPLAY_NAMES",
    "FACTORIAL_CONFIGURATIONS",
    "MATERIALIZATION_CONFIGURATION_IDS",
    "CULTURAL_BACKGROUNDS",
    "ScenarioPreset",
    "materialize_configuration",
    "validate_scenario",
]
