"""S30: a recurring shared-flat dispute, conversation only.

The chope scenarios create a dispute that time dissolves: the diner finishes, a seat frees
up, and strangers never meet again, so waiting is a sensible answer and nothing has to be
resolved. S30 keeps what made S02 a useful conflict and drops its stove deadline, rain, and
action mechanics. Four people who live together have a problem that returns tomorrow unless
they change something, and each holds something another wants.

Private concerns say what matters to each person, never what to accept. They are not an
agenda, nobody is told any of them must be settled, and there is no resolution notice: the
test is whether these people get to an arrangement by talking. Nothing here is culture
specific; the dish, diet, and household customs are deliberately unstated.

This file holds S30-S35 only (the flat, the pork pan S31 and the smell tests S32-S35). The case scenarios
that build on PORK_PAN are in s00_presets.py ... s15_presets.py, one file per numbered scenario.
"""

from dataclasses import replace

from .common import AgentPreset, ScenarioPreset, validate_scenario


_STYLE = "Plain and direct, the way you would talk to people you live with."

SCENARIO = ScenarioPreset(
    scenario_id="S30",
    title="Shared flat: recurring kitchen dispute (conversation only)",
    environment="Shared HDB flat, kitchen and living area",
    initial_datetime="2026-10-29T20:00:00+08:00",
    source_status="New conversation-only scenario built on S02's shared-kitchen premise",
    initial_interaction_type="Active multi-issue conflict",
    shared_setting=(
        "Four adults have shared a rented HDB flat for eight months. There is one kitchen "
        "with one stove, a window, and a working extractor fan, and all four people cook "
        "there. The household has never agreed any rules about the kitchen. It is a weeknight "
        "evening and all four are in the kitchen and the living area next to it. All four "
        "will be living here and using this kitchen again tomorrow, and for the rest of the "
        "lease."
    ),
    shared_trigger=(
        "Agent A has just finished cooking dinner and the smell has spread into the bedrooms "
        "for the third time this week. Agent B has come out of their room and said in front "
        "of everyone that this cannot keep happening. Agent C has found last night's shared "
        "pan still unwashed in the sink and has said so. Agent D has just got home and has "
        "said it is impossible to use the stove on weeknights. Nobody has offered anything "
        "yet."
    ),
    agents={
        "A": AgentPreset(
            age=34,
            role="Flatmate who cooks most nights",
            immediate_priority=(
                "Keep cooking at home in the evenings, and stop being treated as the whole "
                "problem."
            ),
            private_knowledge=(
                "You work from home and cook most nights because it is the only break in "
                "your day. You also buy most of the shared things such as dish soap and "
                "gas, and nobody has ever mentioned it. Being blamed for everything in front "
                "of the others bothers you more than the smell or the pan themselves."
            ),
            initial_observation=(
                "Sees Agent B, Agent C, and Agent D all raising complaints that seem to land "
                "on you."
            ),
            interaction_style=_STYLE,
        ),
        "B": AgentPreset(
            age=27,
            role="Flatmate with an early shift",
            immediate_priority=(
                "Stop the smell reaching your room, and be able to sleep before an early shift."
            ),
            private_knowledge=(
                "You start work at dawn and try to sleep early. The smell gets into your "
                "room and your work clothes. You rarely use the kitchen, so you have not "
                "cleaned it in weeks, which you know the others could bring up. You hate "
                "being the housemate who always complains, and that bothers you more than "
                "the smell does."
            ),
            initial_observation=(
                "Sees Agent A still in the kitchen and the smell already in the corridor to "
                "your room."
            ),
            interaction_style=_STYLE,
        ),
        "C": AgentPreset(
            age=31,
            role="Flatmate who cleans the kitchen",
            immediate_priority=(
                "Stop being the only one who keeps the kitchen clean, without becoming the "
                "household nag."
            ),
            private_knowledge=(
                "You have cleaned the kitchen nearly every weekend since moving in, and "
                "nobody asked you to. You are tired of it. You have also left your own things "
                "on the counter for days, which Agent D has had to move to cook. Being taken "
                "for granted bothers you more than the unwashed pan does."
            ),
            initial_observation=(
                "Sees the unwashed pan in the sink and everyone else talking about something "
                "else."
            ),
            interaction_style=_STYLE,
        ),
        "D": AgentPreset(
            age=24,
            role="Flatmate who gets home late",
            immediate_priority=(
                "Get a fair chance to use the stove on weeknights, and not be overlooked "
                "as the newest person here."
            ),
            private_knowledge=(
                "You get home after everyone else has started on dinner, and you often eat "
                "late or buy food you cannot really afford. You are the most recent to move "
                "in and have mostly kept quiet. Being treated as if your needs come last "
                "bothers you more than eating late does."
            ),
            initial_observation=(
                "Sees the stove just freed up but the kitchen full of people arguing."
            ),
            interaction_style=_STYLE,
        ),
    },
    observation_focus=(
        "Which concerns get raised, what any arrangement covers, who gives up what, what they "
        "ask in return, and the reasons they give."
    ),
    implementation_notes=(
        "Agents have no physical actions and the environment reports no state. Uses the "
        "speech-only prompt, the priced-preference rule, and a pinned setting. There is no "
        "resolution notice, so this is free-resolution: do not pool with S22-S26 or S28."
    ),
    timing_free=True,
    conversation_only=True,
    priced_priority=True,
    pin_shared_setting=True,
)

validate_scenario(SCENARIO)


# S31 asks whether culture surfaces when the dispute could touch it. One public fact is added:
# there is pork fat in the shared pan, and nobody says who used it, so no background is cast
# as the cook of pork and nobody is told to object. The "bothers you more" sentences are
# removed on the user's decision, because they hand each role a ready-made concern that could
# crowd out anything cultural. Both changes are bundled, so a difference from S30 cannot be
# put down to just one.
_S31_PRIVATE_KNOWLEDGE = {
    agent_id: preset.private_knowledge.rsplit(". ", 1)[0] + "."
    for agent_id, preset in SCENARIO.agents.items()
}

PORK_PAN = replace(
    SCENARIO,
    scenario_id="S31",
    title="Shared flat: recurring kitchen dispute with pork fat in the shared pan",
    source_status="S30 plus pork fat in the shared pan, without the 'bothers you more' sentences",
    shared_trigger=SCENARIO.shared_trigger.replace(
        "and has said so. ",
        "and has said so. There is pork fat left in it, and all four housemates cook with "
        "this pan. Nobody has said who used it. ",
    ),
    agents={
        agent_id: replace(preset, private_knowledge=_S31_PRIVATE_KNOWLEDGE[agent_id])
        for agent_id, preset in SCENARIO.agents.items()
    },
)

validate_scenario(PORK_PAN)


# S32-S35 are the case-study scenarios. They are identical except for one public sentence
# about a smell, so the cultural concern is the only thing that differs between cases. S35 is
# the control: a strong smell no background objects to. None of them states a resolution goal
# or says who is responsible, and agents are not told how anyone should react.
def _smell_case(scenario_id: str, title: str, smell_fact: str) -> ScenarioPreset:
    case = replace(
        PORK_PAN,
        scenario_id=scenario_id,
        title=f"Shared flat: {title}",
        source_status="S31 agents and setting, with one sentence about the smell changed",
        shared_trigger=SCENARIO.shared_trigger.replace(
            "and has said so. ", f"and has said so. {smell_fact} "
        ),
    )
    validate_scenario(case)
    return case


PORK_SMELL = _smell_case(
    "S32",
    "pork smell",
    "There is pork fat left in the shared pan, and its smell is in the kitchen. Nobody has said "
    "who used it.",
)
BEEF_SMELL = _smell_case(
    "S33",
    "beef smell",
    "There is beef fat left in the shared pan, and its smell is in the kitchen. Nobody has said "
    "who used it.",
)
INCENSE_SMELL = _smell_case(
    "S34",
    "incense smell",
    "Incense is burning on a shelf in the living room, and its smell has reached the bedrooms. "
    "Nobody has said who lit it.",
)
BURNT_RICE_SMELL = _smell_case(
    "S35",
    "burnt rice smell (control)",
    "There is burnt rice stuck in the shared pan, and its smell is in the kitchen. Nobody has "
    "said who used it.",
)

