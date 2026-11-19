"""Helpers shared by the case scenarios (scenarios 0-15): faith wording, the reasons line, the K seating plans
and the generic case builder _key_case, in which roles A-C are identical across variants and only Agent D's
need changes. Every case builds on S31's PORK_PAN agents (s30_flat.py).
"""

from __future__ import annotations

from dataclasses import replace

from .common import _cast, ScenarioPreset, validate_scenario
from .s30_flat import PORK_PAN


# The reasons line every case scenario appends to behavioural guidance (S17's words).
_REASON_RULE = (
    " When you refuse a request or make a counter-proposal, say briefly why, in your own words."
)
# Faith wording per background, matching PERSONAL_BIOGRAPHIES in common.py.
_FAITH_WORDS = {
    "Chinese": "Buddhist",
    "Eurasian": "Catholic",
    "Indian": "Hindu and does not eat beef",
    "Malay": "Muslim and eats halal",
}
# Seating plans of the rotating K casts (cells K1-K4 in common.py). K1: S36, S37, S42, S55, S59. K2: S38, S39,
# S44, S56, S60. K3: S40, S41, S43, S57, S61. K4: S45, S58, S62 (controls).
K1_BACKGROUNDS = {"A": "Indian", "B": "Eurasian", "C": "Chinese", "D": "Malay"}
K2_BACKGROUNDS = {"A": "Eurasian", "B": "Chinese", "C": "Malay", "D": "Indian"}
K3_BACKGROUNDS = {"A": "Malay", "B": "Indian", "C": "Eurasian", "D": "Chinese"}
K4_BACKGROUNDS = {"A": "Chinese", "B": "Malay", "C": "Indian", "D": "Eurasian"}


# Scenarios 7 and 2 of scenarios.md, after a design review. Shared helpers: the faith sentence and a
# case builder in which roles A-C are identical across variants and only Agent D's key fact (and, where
# the cause must be visible, one phrase of the trigger) differs. Run with K1-K4 at 12 rounds.
K_BACKGROUNDS = {"K1": K1_BACKGROUNDS, "K2": K2_BACKGROUNDS, "K3": K3_BACKGROUNDS, "K4": K4_BACKGROUNDS}


def _faith_sentence(backgrounds: dict[str, str], faith_words: dict[str, str] = _FAITH_WORDS) -> str:
    faiths = {role: faith_words[background] for role, background in backgrounds.items()}
    return (
        f"Agent A is {faiths['A']}, Agent B is {faiths['B']}, Agent C is {faiths['C']}, and "
        f"Agent D is {faiths['D']}."
    )


# One-of-each rotation rooms (2026-11-20, user request): every room has one agent of each culture and the
# need moves to whoever is Agent D. Seats follow a Latin square, so across a scenario's four variants each
# culture sits in each role once (role A, the most opposed role, is not tied to one culture).
ROTATION_SEATS = {
    "Malay": ("Chinese", "Indian", "Eurasian"),
    "Indian": ("Eurasian", "Malay", "Chinese"),
    "Chinese": ("Indian", "Eurasian", "Malay"),
    "Eurasian": ("Malay", "Chinese", "Indian"),
}


def rotation_backgrounds(d_culture: str) -> dict[str, str]:
    a, b, c = ROTATION_SEATS[d_culture]
    return {"A": a, "B": b, "C": c, "D": d_culture}


def rotation_cell(people: dict[str, str], d_culture: str, cast=_cast) -> dict:
    """Profile cell for a rotation room: one fixed person per culture, seated by ROTATION_SEATS."""
    return cast({role: (culture, people[culture]) for role, culture in rotation_backgrounds(d_culture).items()})


def rotated_case(
    base: ScenarioPreset,
    scenario_id: str,
    setting_template: str,
    d_culture: str,
    faith_words: dict[str, str] = _FAITH_WORDS,
) -> ScenarioPreset:
    """The existing variant ``base`` with only the room changed: the setting's faith sentence is rewritten
    for a one-of-each room. Roles, trigger and Agent D's need stay word for word as in the original runs."""

    case = replace(
        base,
        scenario_id=scenario_id,
        title=f"{base.title}, one of each culture",
        source_status=f"{base.scenario_id} with a one-of-each room (rotation, 2026-11-20)",
        shared_setting=setting_template.replace(
            "{faiths}", _faith_sentence(rotation_backgrounds(d_culture), faith_words)
        ),
    )
    validate_scenario(case)
    return case


def _key_case(
    scenario_id: str,
    title: str,
    environment: str,
    setting: str,
    trigger: str,
    roles: dict[str, dict[str, str]],
    need: str,
    backgrounds: dict[str, str],
    faith_words: dict[str, str] = _FAITH_WORDS,
) -> ScenarioPreset:
    agents = {}
    for agent_id, preset in PORK_PAN.agents.items():
        fields = dict(roles[agent_id])
        if agent_id == "D":
            fields["private_knowledge"] += f" {need}"
        agents[agent_id] = replace(
            preset, **fields, behavioral_guidance=preset.behavioral_guidance + _REASON_RULE
        )
    case = replace(
        PORK_PAN,
        scenario_id=scenario_id,
        title=title,
        environment=environment,
        source_status="scenarios.md, after the design review of 2026-11-08",
        shared_setting=setting.replace("{faiths}", _faith_sentence(backgrounds, faith_words)),
        shared_trigger=trigger,
        agents=agents,
    )
    validate_scenario(case)
    return case

