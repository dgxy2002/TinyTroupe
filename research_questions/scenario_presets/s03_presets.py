"""Scenario 3: fasting and the dinner rota (S51-S54), plus its casts FR1-FR4.

S51 Muslim (Ramadan), S52 Hindu (Purattasi), S53 Buddhist (vegetarian days), S54 control (a medical diet).
"""

from __future__ import annotations

from dataclasses import replace

from .case_common import _FAITH_WORDS, _REASON_RULE
from .common import _cast, PROFILE_CONFIGURATIONS, ScenarioPreset, validate_scenario
from .s30_flat import PORK_PAN


# Scenario 3 of scenarios.md: fasting and the dinner rota (S51 Muslim, S52 Hindu, S53 Buddhist, S54
# control), built with the fixes learned in scenario 1: no shared fund (each cook buys their own
# night's food), casts FR1-FR4 with no food rule outside Agent D, every need written as a personal
# rule, and a stake for every role that the change touches. Run at 12 rounds.
FR_BACKGROUNDS = {
    "FR1": {"A": "Eurasian", "B": "Chinese", "C": "Eurasian", "D": "Malay"},
    "FR2": {"A": "Eurasian", "B": "Chinese", "C": "Eurasian", "D": "Indian"},
    "FR3": {"A": "Eurasian", "B": "Eurasian", "C": "Eurasian", "D": "Chinese"},
    "FR4": {"A": "Eurasian", "B": "Chinese", "C": "Eurasian", "D": "Eurasian"},
}


def _rota_setting(backgrounds: dict[str, str]) -> str:
    faiths = {role: _FAITH_WORDS[background] for role, background in backgrounds.items()}
    return (
        "Four adults have shared a rented HDB flat for six months. On weeknights they keep a dinner "
        "rota: each takes one night from Monday to Thursday and cooks dinner for all four at 6.30 "
        "p.m., buying the food for their own night. You all know each other's faith and what each of "
        f"you eats: Agent A is {faiths['A']}, Agent B is {faiths['B']}, Agent C is {faiths['C']}, and "
        f"Agent D is {faiths['D']}. It is a weeknight evening and all four are in the kitchen and the "
        "living area next to it. All four will be living here for the rest of the lease."
    )


_ROTA_ROLES = {
    "A": dict(
        role="Flatmate who started the dinner rota",
        immediate_priority="Keep the rota working the way it does now.",
        private_knowledge=(
            "You started the rota, and the shared dinner is the only time the four of you spend "
            "together. You only know how to cook a few dishes, and all of them have meat."
        ),
        initial_observation="Sees Agent D waiting for an answer, and the rota stuck on the fridge.",
    ),
    "B": dict(
        role="Flatmate with an early shift",
        immediate_priority="Eat early enough to sleep before your early shift.",
        private_knowledge=(
            "You start work at 6 a.m., and you need to eat by 6.30 p.m. to be asleep by 9."
        ),
        initial_observation="Sees Agent D asking to change the rota.",
    ),
    "C": dict(
        role="Flatmate who dislikes cooking",
        immediate_priority="Not cook more than your one night a week.",
        private_knowledge=(
            "You dislike cooking and agreed to the rota only because it means one night a week."
        ),
        initial_observation="Sees the others turn to look at the rota on the fridge.",
    ),
    "D": dict(
        role="Newest flatmate",
        immediate_priority=(
            "Get through the coming month the way you need to, and stay part of the household dinners."
        ),
        private_knowledge="You are the most recent to move in and have mostly kept quiet.",
        initial_observation="Sees the others waiting for you to explain.",
    ),
}


def _rota_case(scenario_id: str, title: str, need: str, backgrounds: dict[str, str]) -> ScenarioPreset:
    agents = {}
    for agent_id, preset in PORK_PAN.agents.items():
        fields = dict(_ROTA_ROLES[agent_id])
        if agent_id == "D":
            fields["private_knowledge"] += f" {need}"
        agents[agent_id] = replace(
            preset, **fields, behavioral_guidance=preset.behavioral_guidance + _REASON_RULE
        )
    case = replace(
        PORK_PAN,
        scenario_id=scenario_id,
        title=f"Dinner rota: {title}",
        environment="Shared HDB flat, kitchen and living area",
        source_status="scenarios.md scenario 3, with the scenario 1 fixes",
        shared_setting=_rota_setting(backgrounds),
        shared_trigger=(
            "Agent D has just said that for the next month, Agent D cannot take part in the dinner "
            "rota the usual way, and has asked whether it could change for a while. Nobody has "
            "answered yet."
        ),
        agents=agents,
    )
    validate_scenario(case)
    return case


ROTA_MUSLIM = _rota_case(
    "S51",
    "Muslim",
    "You are Muslim, and Ramadan starts tomorrow. For you, that means fasting from dawn until "
    "sunset, at about 7.10 p.m., every day for the month.",
    FR_BACKGROUNDS["FR1"],
)
ROTA_HINDU = _rota_case(
    "S52",
    "Hindu",
    "You are Hindu, and the Tamil month of Purattasi starts tomorrow. For you, the whole month is "
    "vegetarian: no meat, fish or eggs, and nothing cooked in pots that have had meat in them this "
    "month.",
    FR_BACKGROUNDS["FR2"],
)
ROTA_BUDDHIST = _rota_case(
    "S53",
    "Buddhist",
    "You are Buddhist and have taken a vow to eat only vegetarian food for the coming month. For "
    "you, that means no meat, fish or eggs, and nothing cooked in pots that have had meat in them.",
    FR_BACKGROUNDS["FR3"],
)
ROTA_CONTROL = _rota_case(
    "S54",
    "medical diet (control)",
    "Your doctor has put you on a strict diet for the next month for a liver problem. For you, "
    "that means no meat, nothing fried, and meals only at fixed times.",
    FR_BACKGROUNDS["FR4"],
)


# ---- Casts (profile cells) for this scenario ----
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
