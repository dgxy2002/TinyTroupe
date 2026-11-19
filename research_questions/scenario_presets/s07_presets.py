"""Scenario 7: bereavement before a deadline (S55-S58 and S111-S122), plus the casts BRxy.

S55 Muslim (K1), S56 Hindu (K2), S57 Buddhist (K3), S58 control (K4): the rotating K casts, a known flaw (rule
6). S111-S122 are the majority and minority rooms (2026-11-18): roles A-C share one culture and faith, Agent D
has another and holds the need; cells BR + majority initial + minority initial, e.g. BRCM.
"""

from __future__ import annotations

from .case_common import K_BACKGROUNDS, _key_case
from .common import _cast, _MAJORITY_CASTS, MINORITY_NAMES, _NOISE_FIXED, PROFILE_CONFIGURATIONS, ScenarioPreset


# Scenario 7: bereavement before a deadline (S55 Muslim K1, S56 Hindu K2, S57 Buddhist K3, S58 control
# K4). Review fixes: every variant asks for the same thing (two days away from work), the control has
# the same death with non-religious family duties instead of a living grandmother in intensive care,
# and nobody outside the team can help.
_BEREAVEMENT_SETTING = (
    "Four colleagues work as a small team in an office and have worked together for two years. "
    "You all know each other's faith and what each of you eats: {faiths} A client pitch is due on "
    "Thursday at 9 a.m., two days from now. Each of the four owns one section of it, and Agent D's "
    "analysis section is about half done. Nobody outside the four knows the work well enough to "
    "help before Thursday. It is Tuesday morning and all four are in the team room."
)
_BEREAVEMENT_TRIGGER = (
    "Agent D has just told the team that their grandmother died this morning. Nobody has said "
    "anything about the deadline yet."
)
_BEREAVEMENT_ROLES = {
    "A": dict(
        role="Pitch lead",
        immediate_priority="Deliver the pitch on time.",
        private_knowledge=(
            "You promised the client this date, and moving it could lose the account."
        ),
        initial_observation="Sees Agent D's half-done section open on the shared screen.",
    ),
    "B": dict(
        role="Team member already covering for a colleague",
        immediate_priority="Not take on more work.",
        private_knowledge=(
            "You are already covering for a colleague on leave and have worked late every night "
            "this week."
        ),
        initial_observation="Sees Agent D trying to hold it together.",
    ),
    "C": dict(
        role="Junior team member",
        immediate_priority="Not be blamed for weak work.",
        private_knowledge=(
            "You have never done this kind of analysis, and your own section is behind."
        ),
        initial_observation="Sees the pitch deadline written on the whiteboard.",
    ),
    "D": dict(
        role="Newest team member",
        immediate_priority="Do what your family needs, and keep your place in the team.",
        private_knowledge="You are the newest member of the team, and this is your first big pitch.",
        initial_observation="Sees the others look at you, then at the deadline on the whiteboard.",
    ),
}
_TWO_DAYS = "it means being with your family, not at work, for the next two days."


def _bereavement(scenario_id: str, title: str, need: str, cell: str) -> ScenarioPreset:
    return _key_case(
        scenario_id,
        f"Bereavement before a deadline: {title}",
        "Office team room",
        _BEREAVEMENT_SETTING,
        _BEREAVEMENT_TRIGGER,
        _BEREAVEMENT_ROLES,
        need,
        K_BACKGROUNDS[cell],
    )


# D's need by D's background (the bundle Malay/Muslim, Indian/Hindu, Chinese/Buddhist, Eurasian/Catholic). The
# Catholic need is new for the majority/minority rooms below; it follows the Hindu one (a rite tonight, the funeral
# tomorrow) so that it fits the same two days and never reaches Thursday's pitch.
_BEREAVEMENT_NEEDS = {
    "Malay": "You are Muslim. Your grandmother is buried today before sunset, and your family holds tahlil "
    f"prayers at home in the evenings that follow. For you, taking part is a religious duty, and {_TWO_DAYS}",
    "Indian": "You are Hindu. Your grandmother's cremation is tomorrow, and your family holds prayers and "
    f"rites at home before and after it. For you, taking part is a religious duty, and {_TWO_DAYS}",
    "Chinese": "You are Buddhist. Your grandmother's wake is at the void deck for the next two nights, with "
    "monks chanting, and as a grandchild you are expected there. For you, taking part is a "
    f"religious duty, and {_TWO_DAYS}",
    "Eurasian": "You are Catholic. Your family prays the rosary for your grandmother at her wake tonight, and her "
    f"funeral Mass and burial are tomorrow. For you, taking part is a religious duty, and {_TWO_DAYS}",
}
BEREAVEMENT_MUSLIM = _bereavement("S55", "Muslim", _BEREAVEMENT_NEEDS["Malay"], "K1")
BEREAVEMENT_HINDU = _bereavement("S56", "Hindu", _BEREAVEMENT_NEEDS["Indian"], "K2")
BEREAVEMENT_BUDDHIST = _bereavement("S57", "Buddhist", _BEREAVEMENT_NEEDS["Chinese"], "K3")
BEREAVEMENT_CONTROL = _bereavement(
    "S58",
    "family duties (control)",
    "Your family is keeping the funeral simple, without religious rites. Your grandfather cannot be "
    "left alone, and your parents need you to look after him and handle the arrangements. For you, "
    f"helping is a family duty, and {_TWO_DAYS}",
    "K4",
)


# Scenario 7, majority and minority rooms (S111-S122, cells BRxy, 2026-11-18). The S55-S57 setting, trigger and
# roles, unchanged; roles A-C share one background and faith (the majority) and Agent D, whose grandmother died,
# has another (the minority). The need follows D's faith. Covering work touches no one's faith, so any majority
# fits any D. Fixed casts per majority (BRxy in common.py), with faith in every biography.
def _bereavement_room(scenario_id: str, majority: str, minority: str) -> ScenarioPreset:
    return _key_case(
        scenario_id,
        f"Bereavement before a deadline: {minority} colleague among three {majority} colleagues",
        "Office team room",
        _BEREAVEMENT_SETTING,
        _BEREAVEMENT_TRIGGER,
        _BEREAVEMENT_ROLES,
        _BEREAVEMENT_NEEDS[minority],
        {"A": majority, "B": majority, "C": majority, "D": minority},
    )


# (scenario ID, majority, minority D); the profile cell for each is BR + the two initials, e.g. BRCM.
BEREAVEMENT_ROOM_PLAN = (
    ("S111", "Chinese", "Malay"),
    ("S112", "Indian", "Malay"),
    ("S113", "Eurasian", "Malay"),
    ("S114", "Chinese", "Indian"),
    ("S115", "Malay", "Indian"),
    ("S116", "Eurasian", "Indian"),
    ("S117", "Malay", "Chinese"),
    ("S118", "Indian", "Chinese"),
    ("S119", "Eurasian", "Chinese"),
    ("S120", "Chinese", "Eurasian"),
    ("S121", "Malay", "Eurasian"),
    ("S122", "Indian", "Eurasian"),
)
BEREAVEMENT_ROOMS = {
    scenario_id: _bereavement_room(scenario_id, majority, minority)
    for scenario_id, majority, minority in BEREAVEMENT_ROOM_PLAN
}


# ---- Casts (profile cells) for this scenario ----
# BRxy: scenario 7 majority and minority rooms (S111-S122). The same fixed people as the MJ cells (the Eurasian
# majority is the SM cast), but with first-person biographies that state each faith.
_BEREAVEMENT_CASTS = {**_MAJORITY_CASTS, "Eurasian": _NOISE_FIXED}
PROFILE_CONFIGURATIONS.update(
    {
        f"BR{majority[0]}{minority[0]}": _cast({**cast, "D": (minority, MINORITY_NAMES[minority])})
        for majority, cast in _BEREAVEMENT_CASTS.items()
        for minority in MINORITY_NAMES
        if minority != majority
    }
)
