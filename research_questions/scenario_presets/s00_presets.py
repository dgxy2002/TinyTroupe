"""Scenario 0: the shared pan and the incense (S36-S41), the first type 3 case scenarios.

S36 pork in the only pan, Muslim D needs sertu; S37 control, shellfish oil and an allergy (cell K1). S38 a pan
that touched beef, Hindu D; S39 control, peanut allergy (K2). S40 incense for a grandmother's death
anniversary, Buddhist D; S41 control, medicated steam (K3). The K casts rotate, so they live in common.py.
"""

from __future__ import annotations

from dataclasses import replace

from .case_common import _FAITH_WORDS, K1_BACKGROUNDS, K2_BACKGROUNDS, K3_BACKGROUNDS, _REASON_RULE
from .common import ScenarioPreset, validate_scenario
from .s30_flat import PORK_PAN


# S36 and S37 are the pan-only pair, for the K1 cell. The smell and stove disputes are gone, so the
# pan is the one problem in the room, and it is the only pan in the flat, so nobody can sidestep it.
# Everyone knows each other's faith, stated as fact, because the prompt tells agents not to infer
# a background. Each agent is asked to give reasons when refusing, in S17's words. Only the
# residue in the pan and Agent D's need differ between the two, and that need is a supplied fact,
# so a case here is not "unprompted": Agent D still decides whether to raise it, how to explain
# it and what to accept. S37 is the control: a need with no faith behind it. Neither states a
# resolution goal or tells anyone how to react.


def _pan_setting(backgrounds: dict[str, str]) -> str:
    faiths = {role: _FAITH_WORDS[background] for role, background in backgrounds.items()}
    return (
        "Four adults have shared a rented HDB flat for eight months. There is one kitchen with "
        "one stove, and all four people cook there. The household has never agreed any rules "
        "about the kitchen. After eight months, you all know each other's faith and what each of "
        f"you eats: Agent A is {faiths['A']}, Agent B is {faiths['B']}, Agent C is {faiths['C']}, "
        f"and Agent D is {faiths['D']}. It is a weeknight evening and all four are in the kitchen "
        "and the living area next to it. All four will be living here and using this kitchen "
        "again tomorrow, and for the rest of the lease."
    )


_PAN_OBSERVATIONS = {
    "A": "Sees Agent C pointing at the pan and the others looking at you, because you cook most nights.",
    "B": "Sees the argument about the pan starting just as you were about to go to bed.",
    "C": "Sees the unwashed pan in the sink and nobody moving to wash it.",
    "D": "Sees the stove free and the only pan unwashed in the sink.",
}
_PAN_PRIORITIES = {
    "A": PORK_PAN.agents["A"].immediate_priority,
    "B": "Get to bed before your early shift, without being made to clean up after other people.",
    "C": PORK_PAN.agents["C"].immediate_priority,
    "D": "Cook your dinner tonight, and not be overlooked as the newest person here.",
}
_PAN_PRIVATE_KNOWLEDGE = {
    "A": PORK_PAN.agents["A"].private_knowledge,
    "B": (
        "You start work at dawn and try to sleep early. You rarely use the kitchen, so you have "
        "not cleaned it in weeks, which you know the others could bring up."
    ),
    "C": (
        "You have cleaned the kitchen nearly every weekend since moving in, and nobody asked you "
        "to. You are tired of it."
    ),
    "D": PORK_PAN.agents["D"].private_knowledge,
}


def _pan_case(
    scenario_id: str, title: str, residue: str, need: str, backgrounds: dict[str, str]
) -> ScenarioPreset:
    agents = {
        agent_id: replace(
            preset,
            immediate_priority=_PAN_PRIORITIES[agent_id],
            private_knowledge=(
                _PAN_PRIVATE_KNOWLEDGE[agent_id] + (f" {need}" if agent_id == "D" else "")
            ),
            initial_observation=_PAN_OBSERVATIONS[agent_id],
            behavioral_guidance=preset.behavioral_guidance + _REASON_RULE,
        )
        for agent_id, preset in PORK_PAN.agents.items()
    }
    case = replace(
        PORK_PAN,
        scenario_id=scenario_id,
        title=f"Shared flat, pan only: {title}",
        source_status="S31 reduced to the pan, with faiths public and one supplied need",
        shared_setting=_pan_setting(backgrounds),
        shared_trigger=(
            "Agent C has found last night's shared pan still unwashed in the sink and has said "
            f"so. There is {residue} left in it, and all four housemates cook with this pan, the "
            "only one in the flat. Nobody has said who used it. Agent D has just got home and "
            "wants to use the pan to cook dinner. Agents A and B are in the kitchen too. Nobody "
            "has offered anything yet."
        ),
        agents=agents,
    )
    validate_scenario(case)
    return case


FAITH_PAN = _pan_case(
    "S36",
    "pork and a faith need",
    "pork fat",
    "You are Muslim. For you, a pan that has touched pork needs sertu, a ritual cleansing, "
    "before you can use it.",
    K1_BACKGROUNDS,
)
SHELLFISH_PAN = _pan_case(
    "S37",
    "shellfish and an allergy (control)",
    "shellfish oil",
    "You have a severe shellfish allergy. For you, a pan that has touched shellfish needs a deep "
    "clean before you can use it.",
    K1_BACKGROUNDS,
)

# S38 and S39 repeat the pan-only pair for a Hindu agent in role D, run with K2. The need is one
# plausible person's practice, not a claim about Hindus: some keep cookware that has touched beef
# away from their food for good. It is stronger than S36's, since washing cannot fix it, and S39's
# control has the same structure with an allergy.
BEEF_PAN = _pan_case(
    "S38",
    "beef and a faith need",
    "beef fat",
    "You are Hindu. For you, a pan that has had beef in it cannot be used for your food again, "
    "however well it is washed.",
    K2_BACKGROUNDS,
)
PEANUT_PAN = _pan_case(
    "S39",
    "peanut and an allergy (control)",
    "peanut oil",
    "You have a severe peanut allergy. For you, a pan that has had peanut oil in it cannot be "
    "used for your food again, however well it is washed.",
    K2_BACKGROUNDS,
)


# S40 and S41 are the incense pair, for the K3 cell, at the same information level as S36: faiths
# personal and public, one supplied practice for Agent D, the reasons line, one issue, and no
# resolution goal. Here Agent D's practice causes the problem rather than being blocked by it. The
# kitchen is gone, so roles are rewritten around the shared space; ages and names stay. The
# practice is one plausible person's, not a claim about Buddhists. S41 is the control: a medical
# need with a strong smell. Only the source of the smell and Agent D's need differ.


def _shared_space_setting(backgrounds: dict[str, str]) -> str:
    faiths = {role: _FAITH_WORDS[background] for role, background in backgrounds.items()}
    return (
        "Four adults have shared a rented HDB flat for eight months. Each has a bedroom, and they "
        "share the living room. The household has never agreed any rules about the shared space. "
        "After eight months, you all know each other's faith and what each of you eats: Agent A "
        f"is {faiths['A']}, Agent B is {faiths['B']}, Agent C is {faiths['C']}, and Agent D is "
        f"{faiths['D']}. It is a weeknight evening and all four are in the living room and the "
        "corridor to the bedrooms. All four will be living here tomorrow, and for the rest of the "
        "lease."
    )


_SPACE_ROLES = {
    "A": dict(
        role="Flatmate who works from home",
        immediate_priority=(
            "Keep the living room usable for your work, without being dragged into taking sides."
        ),
        private_knowledge=(
            "You work from home, and the living room is where you spend most of your day."
        ),
        initial_observation=(
            "Sees Agent B come out of their room annoyed, and the smell drifting into the living "
            "room."
        ),
    ),
    "B": dict(
        role="Flatmate with an early shift",
        immediate_priority="Get to sleep before your early shift.",
        private_knowledge=(
            "You start work at dawn and try to sleep early. The smell has got into your room and "
            "your work clothes, and you cannot sleep with it."
        ),
        initial_observation="Smells it in your room just as you were trying to sleep.",
    ),
    "C": dict(
        role="Flatmate who usually sorts out household problems",
        immediate_priority=(
            "Stop being the one who sorts out every household problem, without becoming the "
            "household nag."
        ),
        private_knowledge=(
            "You have sorted out nearly every household problem since moving in, and nobody asked "
            "you to. You are tired of it."
        ),
        initial_observation=(
            "Sees Agent B heading for Agent D's door, and the others looking at you to sort it out."
        ),
    ),
    "D": dict(
        role="Newest flatmate",
        immediate_priority=(
            "Get through this evening the way you need to, and not be overlooked as the newest "
            "person here."
        ),
        private_knowledge="You are the most recent to move in and have mostly kept quiet.",
        initial_observation="Sees Agent B at your door, upset about the smell.",
    ),
}


def _shared_space_case(
    scenario_id: str, title: str, source: str, need: str, backgrounds: dict[str, str]
) -> ScenarioPreset:
    agents = {}
    for agent_id, preset in PORK_PAN.agents.items():
        fields = dict(_SPACE_ROLES[agent_id])
        if agent_id == "D":
            fields["private_knowledge"] += f" {need}"
        agents[agent_id] = replace(
            preset, **fields, behavioral_guidance=preset.behavioral_guidance + _REASON_RULE
        )
    case = replace(
        PORK_PAN,
        scenario_id=scenario_id,
        title=f"Shared flat, shared space: {title}",
        environment="Shared HDB flat, living room and bedrooms",
        source_status="S36's information level, with a practice in Agent D's room as the one issue",
        shared_setting=_shared_space_setting(backgrounds),
        shared_trigger=(
            f"{source} in Agent D's room, and its smell has reached the living room and Agent B's "
            "room. Agent B has come out and said so at Agent D's door. Agents A and C are in the "
            "living room too. Nobody has offered anything yet."
        ),
        agents=agents,
    )
    validate_scenario(case)
    return case


INCENSE_PRACTICE = _shared_space_case(
    "S40",
    "incense and a faith practice",
    "Incense is burning at a small altar",
    "You are Buddhist. Today is the anniversary of your grandmother's death. You keep a small "
    "altar for her in your room, and on this day you burn incense there for her through the "
    "evening.",
    K3_BACKGROUNDS,
)
MEDICATED_STEAM = _shared_space_case(
    "S41",
    "medicated steam and a health need (control)",
    "A bowl of strong-smelling medicated oil is steaming",
    "You have a chest infection. Your doctor told you to breathe steam from a bowl of "
    "strong-smelling medicated oil in your room through the evening.",
    K3_BACKGROUNDS,
)
