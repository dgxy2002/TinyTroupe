"""Scenario 8: the void deck wake (S79-S81), plus its casts VD1-VD3.

S79 Buddhist, S80 Catholic, S81 control (a wake without religious rites). Roles A-C are three Malay Muslims.
"""

from __future__ import annotations

from .case_common import _key_case, rotated_case, rotation_cell
from .common import _cast, _MALAY_FIXED, PROFILE_CONFIGURATIONS, ScenarioPreset


# Scenario 8: the void deck wake (S79 Buddhist VD1, S80 Catholic VD2, S81 control VD3). Fix from the
# draft: every variant is a wake for Agent D's grandfather, so celebration versus mourning is no longer
# a difference; the control is the same wake without religious rites. Only two faith variants: a Muslim
# void-deck wake is not usual, and a Hindu one could not be checked. Roles A-C are the same three Malay
# Muslims. Each neighbour's stake comes with a time or place that could give.
VD_BACKGROUNDS = {
    "VD1": {"A": "Malay", "B": "Malay", "C": "Malay", "D": "Chinese"},
    "VD2": {"A": "Malay", "B": "Malay", "C": "Malay", "D": "Eurasian"},
    "VD3": {"A": "Malay", "B": "Malay", "C": "Malay", "D": "Indian"},
}
_VOID_DECK_SETTING = (
    "Four neighbours live in the same HDB block and know each other from the block's chat group, "
    "which they have used for two years. You all know each other's faith and what each of you eats: "
    "{faiths} Events at the void deck need a town council permit, and Agent D's family has one for a "
    "wake from tonight, Friday, until Sunday night. It is early evening, and all four are at the void "
    "deck."
)
_VOID_DECK_ROLES = {
    "A": dict(
        role="Neighbour whose mother uses a wheelchair",
        immediate_priority="Keep the path to the lift clear for your mother.",
        private_knowledge=(
            "Your mother uses a wheelchair, and the tent narrows the only path to the lift lobby. "
            "Every day she goes out at about 8 a.m. and comes back at about noon, and those are the "
            "times she needs the path."
        ),
        initial_observation="Sees the tent going up across the path to the lift lobby.",
    ),
    "B": dict(
        role="Neighbour who works night shifts",
        immediate_priority="Sleep before your night shifts.",
        private_knowledge=(
            "You are a nurse on night shifts this week, and you sleep from about 6 to 10.30 p.m. "
            "before work. Your bedroom window faces the void deck. You have Saturday night off."
        ),
        initial_observation="Sees the tent and the chairs going up under your window.",
    ),
    "C": dict(
        role="Neighbour who leads a morning exercise group",
        immediate_priority="Keep your morning group going.",
        private_knowledge=(
            "You lead a tai chi group of older residents at the void deck at 7 every morning, in the "
            "space the tent now takes. The open area by the playground nearby has room, but no shade."
        ),
        initial_observation="Sees the tent filling the space your group uses.",
    ),
    "D": dict(
        role="Newer resident",
        immediate_priority=(
            "Do right by your family, and keep good relations with your neighbours, without being "
            "overlooked as one of the newer residents."
        ),
        private_knowledge="You are one of the newer residents on the block.",
        initial_observation="Sees three neighbours coming over while your family sets up.",
    ),
}
_EVENINGS_MATTER = (
    " Holding the evenings in full matters most to you; how the tent is laid out matters less."
)


def _void_deck(scenario_id: str, title: str, rites: str, need: str, cell: str) -> ScenarioPreset:
    return _key_case(
        scenario_id,
        f"Void deck wake: {title}",
        "HDB void deck",
        _VOID_DECK_SETTING,
        "Agent D's grandfather died yesterday. Agent D's family is setting up a tent for his wake at "
        f"the void deck, with {rites} each evening until about 10.30 p.m. Agent A, Agent B and Agent C "
        "have come down to talk to Agent D about it. Nobody has proposed anything yet.",
        _VOID_DECK_ROLES,
        need + _EVENINGS_MATTER,
        VD_BACKGROUNDS[cell],
    )


VOID_DECK_BUDDHIST = _void_deck(
    "S79",
    "Buddhist",
    "monks chanting, with gongs,",
    "You are Buddhist. For you, the chanting each evening at the wake is a religious duty, and it runs "
    "for the three nights until the funeral on Monday.",
    "VD1",
)
VOID_DECK_CATHOLIC = _void_deck(
    "S80",
    "Catholic",
    "a rosary and hymns",
    "You are Catholic. For you, the rosary and hymns each evening at the wake are a religious duty, and "
    "they run for the three nights until the funeral Mass on Monday.",
    "VD2",
)
VOID_DECK_CONTROL = _void_deck(
    "S81",
    "wake without religious rites (control)",
    "family and friends gathering, with his favourite songs playing,",
    "Your family is holding the wake without religious rites. For you, the evening gatherings at the "
    "wake are a family duty, and they run for the three nights until the cremation on Monday.",
    "VD3",
)


# ---- Casts (profile cells) for this scenario ----
# VD1-VD3: casts for scenario 8 (void deck wake). The variant faiths are Buddhist and Catholic, so roles A-C
# are the same three Malay Muslims (_MALAY_FIXED in common.py, shared with scenario 6). D is female throughout
# and never shares a background with A-C.
PROFILE_CONFIGURATIONS.update(
    {
        "VD1": _cast({**_MALAY_FIXED, "D": ("Chinese", "Xin Yi")}),
        "VD2": _cast({**_MALAY_FIXED, "D": ("Eurasian", "Rachel Pereira")}),
        "VD3": _cast({**_MALAY_FIXED, "D": ("Indian", "Priya")}),
    }
)


# ---- One-of-each rotation rooms (2026-11-20) ----
# Only Buddhist and Catholic rites exist (a Muslim void-deck wake is not usual; a Hindu one could not be
# checked), so the Malay and the Indian D both hold the wake without religious rites (the control). D female.
_ROTATION_PEOPLE = {'Chinese': 'Xin Yi', 'Malay': 'Aisyah', 'Indian': 'Priya', 'Eurasian': 'Rachel Pereira'}
VOID_DECK_ROTATION = {
    'S134': rotated_case(VOID_DECK_CONTROL, 'S134', _VOID_DECK_SETTING, 'Malay'),
    'S135': rotated_case(VOID_DECK_CONTROL, 'S135', _VOID_DECK_SETTING, 'Indian'),
    'S136': rotated_case(VOID_DECK_BUDDHIST, 'S136', _VOID_DECK_SETTING, 'Chinese'),
    'S137': rotated_case(VOID_DECK_CATHOLIC, 'S137', _VOID_DECK_SETTING, 'Eurasian'),
}
VOID_DECK_ROTATION_CELLS = {
    'S134': "VDRM",
    'S135': "VDRI",
    'S136': "VDRC",
    'S137': "VDRE",
}
PROFILE_CONFIGURATIONS.update(
    {"VDRM": rotation_cell(_ROTATION_PEOPLE, 'Malay'), "VDRI": rotation_cell(_ROTATION_PEOPLE, 'Indian'), "VDRC": rotation_cell(_ROTATION_PEOPLE, 'Chinese'), "VDRE": rotation_cell(_ROTATION_PEOPLE, 'Eurasian')}
)
