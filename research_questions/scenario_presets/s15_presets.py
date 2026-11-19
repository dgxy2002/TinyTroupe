"""Scenario 15: cooking smells in a shared flat, with no religion (S98-S110), plus the casts SM1-SM4 and MJxy.

S98 Malay, S99 Indian, S100 Chinese, S101 control (a heart diet), cells SM1-SM4. S102-S110 are the majority
and minority rooms (2026-11-18), cells MJ + majority initial + minority initial, e.g. MJCM; rooms with a
Eurasian majority are S98-S100 run with SM1-SM3.
"""

from __future__ import annotations

from typing import Any

from .case_common import _key_case
from .common import _cast, _MAJORITY_CASTS, MINORITY_NAMES, _NOISE_FIXED, PROFILE_CONFIGURATIONS, ScenarioPreset


# Scenario 15: cooking smells in a shared flat (S98 Malay SM1, S99 Indian SM2, S100 Chinese SM3, S101 control
# SM4). The first case scenario with no religion in it: the key need is a family dish whose smell fills the
# flat, and the setting states backgrounds, not faiths (`_BACKGROUND_WORDS`). The SM casts give every role a
# biography without a faith line. Roles A-C are the same three Eurasians in every cell, and their stakes are
# hours and places, so none of them cooks anything the rule would touch. D is female throughout. Every role has
# a fact that can give: A is out most Saturdays and A's calls end at about 7 p.m., a shut door and an open
# window keep B's room clear, C does laundry only three evenings a week, and D's evenings and frequency can move.
_BACKGROUND_WORDS = {"Chinese": "Chinese", "Eurasian": "Eurasian", "Indian": "Indian", "Malay": "Malay"}
_SMELL_SETTING = (
    "Four adults have shared a rented HDB flat for six months. Each has a bedroom, and all four cook in the "
    "one kitchen, which opens onto the living room and onto the service yard where everyone hangs laundry to "
    "dry. The kitchen has a window and a weak cooker hood, and the landlord does not allow any changes to the "
    "kitchen. Cooking in the common corridor is not allowed, and there is nowhere else in the flat to cook. "
    "None of the four wants to spend money on this. The household has never agreed any rules about cooking. "
    "You all know each other's backgrounds: {faiths} It is a weekday evening and all four are in the living "
    "room. All four will be living here for the rest of the lease."
)
_SMELL_ROLES = {
    "A": dict(
        role="Housemate who works from home",
        immediate_priority="Keep strong cooking smells out of the living room.",
        private_knowledge=(
            "You work from home at the dining table in the living room and are on video calls with clients "
            "until about 7 p.m. on weekdays. A strong cooking smell stays in the living room for hours. You "
            "are out most Saturdays."
        ),
        initial_observation="Sees the dining table where you work, a few steps from the kitchen.",
    ),
    "B": dict(
        role="Housemate whose room is next to the kitchen",
        immediate_priority="Keep cooking smells out of your room and your clothes.",
        private_knowledge=(
            "Your bedroom is next to the kitchen, and smells get into your clothes and bedding. When your door "
            "is shut and your window is open, the smell stays out of your room."
        ),
        initial_observation="Can still smell last night's cooking in your room.",
    ),
    "C": dict(
        role="Housemate who dries laundry in the service yard",
        immediate_priority="Keep your laundry from smelling of cooking.",
        private_knowledge=(
            "You hang your laundry in the service yard off the kitchen, because there is nowhere else to dry "
            "it, and it takes in the smell of anything cooked nearby. You do your laundry on Monday, "
            "Wednesday and Friday evenings."
        ),
        initial_observation="Sees your laundry hanging in the service yard.",
    ),
    "D": dict(
        role="Newest housemate",
        immediate_priority=(
            "Keep cooking what matters to you at home, and not be overlooked as the newest person here."
        ),
        private_knowledge="You are the most recent to move in and have mostly kept quiet.",
        initial_observation="Sees the others look towards the kitchen.",
    ),
}
_SMELL_TIMES = " Cooking it at home matters most to you; which evenings, and how often, matters less."
SM_BACKGROUNDS = {
    "SM1": {"A": "Eurasian", "B": "Eurasian", "C": "Eurasian", "D": "Malay"},
    "SM2": {"A": "Eurasian", "B": "Eurasian", "C": "Eurasian", "D": "Indian"},
    "SM3": {"A": "Eurasian", "B": "Eurasian", "C": "Eurasian", "D": "Chinese"},
    "SM4": {"A": "Eurasian", "B": "Eurasian", "C": "Eurasian", "D": "Chinese"},
}


def _smell(scenario_id: str, title: str, dish: str, need: str, cell: str) -> ScenarioPreset:
    return _smell_in_room(scenario_id, title, dish, need, SM_BACKGROUNDS[cell])


def _smell_in_room(
    scenario_id: str, title: str, dish: str, need: str, backgrounds: dict[str, str]
) -> ScenarioPreset:
    return _key_case(
        scenario_id,
        f"Cooking smells: {title}",
        "Shared HDB flat",
        _SMELL_SETTING,
        f"Last night Agent D cooked {dish} in the kitchen, and the smell filled the flat and the laundry in the "
        "service yard. Agent D cooks it about twice a week. Agent A has just "
        "asked that nobody cook strong-smelling food in the flat from now on. Nobody has answered yet.",
        _SMELL_ROLES,
        need + _SMELL_TIMES,
        backgrounds,
        _BACKGROUND_WORDS,
    )


_FAMILY_DISH = (
    "{dish} is in almost every meal your family has made since you were small, and you cook it the way "
    "your mother taught you. For you, cooking it in your own kitchen, about twice a week in the evening, is "
    "part of keeping your family's {culture} cooking alive."
)
SMELL_MALAY = _smell(
    "S98",
    "Malay",
    "sambal belacan",
    _FAMILY_DISH.format(dish="Sambal belacan", culture="Malay"),
    "SM1",
)
SMELL_INDIAN = _smell(
    "S99",
    "Indian",
    "fish curry",
    _FAMILY_DISH.format(dish="Fish curry", culture="Indian"),
    "SM2",
)
SMELL_CHINESE = _smell(
    "S100",
    "Chinese",
    "fried salted fish",
    _FAMILY_DISH.format(dish="Fried salted fish", culture="Chinese"),
    "SM3",
)
SMELL_CONTROL = _smell(
    "S101",
    "heart diet (control)",
    "grilled mackerel",
    "After a heart scare last year, your doctor put you on a diet built around oily fish. For you, cooking "
    "grilled mackerel in your own kitchen, about twice a week in the evening, is part of keeping your heart "
    "healthy.",
    "SM4",
)


# Scenario 15, majority and minority rooms (S102-S110, cells MJxy, 2026-11-18). Same setting, trigger, roles and
# need wording as S98-S100; only the room changes: roles A-C share one background (the majority) and Agent D,
# who holds the need, has another (the minority). The variant follows D, who cooks her own family's dish. Rooms
# with a Eurasian majority are S98-S100 run with SM1-SM3; the Eurasian D (devil curry) is new here.
_FAMILY_DISHES = {
    "Chinese": "fried salted fish",
    "Eurasian": "devil curry",
    "Indian": "fish curry",
    "Malay": "sambal belacan",
}


def _smell_room(scenario_id: str, majority: str, minority: str) -> ScenarioPreset:
    dish = _FAMILY_DISHES[minority]
    return _smell_in_room(
        scenario_id,
        f"{minority} housemate among three {majority} housemates",
        dish,
        _FAMILY_DISH.format(dish=dish[0].upper() + dish[1:], culture=minority),
        {"A": majority, "B": majority, "C": majority, "D": minority},
    )


# (scenario ID, majority, minority D); the profile cell for each is MJ + the two initials, e.g. MJCM.
SMELL_ROOM_PLAN = (
    ("S102", "Chinese", "Malay"),
    ("S103", "Indian", "Malay"),
    ("S104", "Chinese", "Indian"),
    ("S105", "Malay", "Indian"),
    ("S106", "Malay", "Chinese"),
    ("S107", "Indian", "Chinese"),
    ("S108", "Chinese", "Eurasian"),
    ("S109", "Malay", "Eurasian"),
    ("S110", "Indian", "Eurasian"),
)
SMELL_ROOMS = {
    scenario_id: _smell_room(scenario_id, majority, minority)
    for scenario_id, majority, minority in SMELL_ROOM_PLAN
}


# ---- Casts (profile cells) for this scenario ----
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
# MJxy: scenario 15 majority and minority rooms (S102-S110). x is the majority of roles A-C, y is Agent D. Each
# majority keeps the same three people in every room (A male, B and C female, as in the NO cast), and each D keeps
# one name in every room (the SM names, plus Sarah Fernandez for the Eurasian D). The user decided (2026-11-18) to
# treat names as having no effect in this experiment. Rooms with a Eurasian majority use SM1-SM3.
PROFILE_CONFIGURATIONS.update(
    {
        f"MJ{majority[0]}{minority[0]}": _secular_cast({**cast, "D": (minority, MINORITY_NAMES[minority])})
        for majority, cast in _MAJORITY_CASTS.items()
        for minority in MINORITY_NAMES
        if minority != majority
    }
)
