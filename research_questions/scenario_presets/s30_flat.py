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


# S36 and S37 are the pan-only pair, for the K1 cell. The smell and stove disputes are gone, so the
# pan is the one problem in the room, and it is the only pan in the flat, so nobody can sidestep it.
# Everyone knows each other's faith, stated as fact, because the prompt tells agents not to infer
# a background. Each agent is asked to give reasons when refusing, in S17's words. Only the
# residue in the pan and Agent D's need differ between the two, and that need is a supplied fact,
# so a case here is not "unprompted": Agent D still decides whether to raise it, how to explain
# it and what to accept. S37 is the control: a need with no faith behind it. Neither states a
# resolution goal or tells anyone how to react.
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
K1_BACKGROUNDS = {"A": "Indian", "B": "Eurasian", "C": "Chinese", "D": "Malay"}
K2_BACKGROUNDS = {"A": "Eurasian", "B": "Chinese", "C": "Malay", "D": "Indian"}


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
K3_BACKGROUNDS = {"A": "Malay", "B": "Indian", "C": "Eurasian", "D": "Chinese"}


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


# Scenario 1 of scenarios.md: housewarming drinks. S42 Muslim (K1), S43 Buddhist (K3), S44 Hindu
# (K2), S45 control (K4, sober after alcohol dependence). The trigger and roles A-C are identical;
# only the faith line's order (set by the cast) and Agent D's key fact differ. No resolution goal.
K4_BACKGROUNDS = {"A": "Chinese", "B": "Malay", "C": "Indian", "D": "Eurasian"}


def _housewarming_setting(backgrounds: dict[str, str]) -> str:
    faiths = {role: _FAITH_WORDS[background] for role, background in backgrounds.items()}
    return (
        "Four adults moved into a rented HDB flat together a month ago. Last week they agreed to "
        "hold a housewarming in the flat this Saturday, and each has invited friends. You all know "
        f"each other's faith and what each of you eats: Agent A is {faiths['A']}, Agent B is "
        f"{faiths['B']}, Agent C is {faiths['C']}, and Agent D is {faiths['D']}. It is a weeknight "
        "and all four are in the living room. All four will be living here together for the rest "
        "of the lease."
    )


_HOUSEWARMING_ROLES = {
    "A": dict(
        role="Flatmate who organised the housewarming",
        immediate_priority="Have the party as planned.",
        private_knowledge=(
            "You topped up the house fund with your own money to buy the drinks, and the shop does "
            "not take returns."
        ),
        initial_observation="Sees the others looking at the drinks you have just put away.",
    ),
    "B": dict(
        role="Flatmate with guests from work",
        immediate_priority="Not embarrass yourself in front of your guests.",
        private_knowledge=(
            "You invited your manager and two colleagues, and you told them there would be drinks."
        ),
        initial_observation="Sees Agent A putting the drinks in the fridge.",
    ),
    "C": dict(
        role="Flatmate who keeps track of the house fund",
        immediate_priority="Keep costs fair.",
        private_knowledge=(
            "Your budget is tight this month, and you have nothing more to put into the house fund."
        ),
        initial_observation="Sees the receipt for the drinks on the table.",
    ),
    "D": dict(
        role="Newest flatmate",
        immediate_priority=(
            "Feel at home at your own housewarming, and not be overlooked as the newest person here."
        ),
        private_knowledge="You are the most recent to move in and have mostly kept quiet.",
        initial_observation="Sees the beer and wine in the fridge next to your food.",
    ),
}


def _housewarming_case(
    scenario_id: str, title: str, need: str, backgrounds: dict[str, str]
) -> ScenarioPreset:
    agents = {}
    for agent_id, preset in PORK_PAN.agents.items():
        fields = dict(_HOUSEWARMING_ROLES[agent_id])
        if agent_id == "D":
            fields["private_knowledge"] += f" {need}"
        agents[agent_id] = replace(
            preset, **fields, behavioral_guidance=preset.behavioral_guidance + _REASON_RULE
        )
    case = replace(
        PORK_PAN,
        scenario_id=scenario_id,
        title=f"Housewarming drinks: {title}",
        environment="Shared HDB flat, living room",
        source_status="scenarios.md scenario 1, at S36's information level",
        shared_setting=_housewarming_setting(backgrounds),
        shared_trigger=(
            "Agent A has just come home with two cartons of beer and three bottles of wine for "
            "Saturday, bought with the shared house fund, and has put them in the fridge. Agent A "
            "has said the drinks are sorted. Agent D is looking at them. Agents B and C are in the "
            "living room too. Nobody has said anything else yet."
        ),
        agents=agents,
    )
    validate_scenario(case)
    return case


HOUSEWARMING_MUSLIM = _housewarming_case(
    "S42",
    "Muslim",
    "You are Muslim. For you, alcohol is haram: you do not drink it, and you are not comfortable "
    "hosting a party in your own home where it is served.",
    K1_BACKGROUNDS,
)
HOUSEWARMING_BUDDHIST = _housewarming_case(
    "S43",
    "Buddhist",
    "You are Buddhist and keep the five precepts, one of which is to avoid intoxicants. For you, "
    "serving alcohol at a party you are hosting goes against them.",
    K3_BACKGROUNDS,
)
HOUSEWARMING_HINDU = _housewarming_case(
    "S44",
    "Hindu",
    "You are Hindu and do not drink. Your parents are coming to the housewarming, and for your "
    "family, alcohol at a gathering with elders present would be disrespectful.",
    K2_BACKGROUNDS,
)
HOUSEWARMING_CONTROL = _housewarming_case(
    "S45",
    "sober flatmate (control)",
    "You have been sober for a year after alcohol dependence. For you, a party with alcohol in "
    "your own home is a real risk of relapse.",
    K4_BACKGROUNDS,
)


# Scenario 1, version 2 (S46-S49), after the first runs: Agent A paid with their own money, so
# there is no shared-fund dispute, and Agent C's stake is no longer about money. Run with HW1-HW4,
# whose non-key agents have no faith rule about alcohol. S42-S45 are left as they were run.
HW_BACKGROUNDS = {
    "HW1": {"A": "Eurasian", "B": "Chinese", "C": "Indian", "D": "Malay"},
    "HW2": {"A": "Eurasian", "B": "Chinese", "C": "Eurasian", "D": "Indian"},
    "HW3": {"A": "Eurasian", "B": "Indian", "C": "Eurasian", "D": "Chinese"},
    "HW4": {"A": "Eurasian", "B": "Chinese", "C": "Indian", "D": "Eurasian"},
}
_HOUSEWARMING_V2_ROLES = {
    **_HOUSEWARMING_ROLES,
    "A": dict(
        _HOUSEWARMING_ROLES["A"],
        private_knowledge=(
            "You paid for the drinks with your own money, and the shop does not take returns."
        ),
    ),
    "C": dict(
        role="Flatmate whose last flatshare fell apart",
        immediate_priority="Not go through another flatshare falling apart.",
        private_knowledge=(
            "Your last flatshare broke up after a fight over a party, and you had to find a new "
            "place at short notice."
        ),
        initial_observation="Sees Agent D go quiet, looking at the fridge.",
    ),
}


def _housewarming_v2_case(
    scenario_id: str, title: str, need: str, backgrounds: dict[str, str]
) -> ScenarioPreset:
    agents = {}
    for agent_id, preset in PORK_PAN.agents.items():
        fields = dict(_HOUSEWARMING_V2_ROLES[agent_id])
        if agent_id == "D":
            fields["private_knowledge"] += f" {need}"
        agents[agent_id] = replace(
            preset, **fields, behavioral_guidance=preset.behavioral_guidance + _REASON_RULE
        )
    case = replace(
        HOUSEWARMING_MUSLIM,
        scenario_id=scenario_id,
        title=f"Housewarming drinks v2: {title}",
        source_status="scenarios.md scenario 1, version 2: no shared-fund dispute, own casts",
        shared_setting=_housewarming_setting(backgrounds),
        shared_trigger=HOUSEWARMING_MUSLIM.shared_trigger.replace(
            "bought with the shared house fund", "bought with Agent A's own money"
        ),
        agents=agents,
    )
    validate_scenario(case)
    return case


HOUSEWARMING_V2_MUSLIM = _housewarming_v2_case(
    "S46", "Muslim", HOUSEWARMING_MUSLIM.agents["D"].private_knowledge.split("kept quiet. ")[1], HW_BACKGROUNDS["HW1"]
)
HOUSEWARMING_V2_HINDU = _housewarming_v2_case(
    "S47", "Hindu", HOUSEWARMING_HINDU.agents["D"].private_knowledge.split("kept quiet. ")[1], HW_BACKGROUNDS["HW2"]
)
HOUSEWARMING_V2_BUDDHIST = _housewarming_v2_case(
    "S48", "Buddhist", HOUSEWARMING_BUDDHIST.agents["D"].private_knowledge.split("kept quiet. ")[1], HW_BACKGROUNDS["HW3"]
)
HOUSEWARMING_V2_CONTROL = _housewarming_v2_case(
    "S49",
    "sober flatmate (control)",
    HOUSEWARMING_CONTROL.agents["D"].private_knowledge.split("kept quiet. ")[1],
    HW_BACKGROUNDS["HW4"],
)


# S50: S47 with the Hindu need written as a personal rule, like the Muslim and Buddhist variants. In
# S44 and S47 the need was the family's view ("for your family ... would be disrespectful") and the
# Hindu agent let the alcohol stay both times; S50 tests whether that came from the weaker wording.
HOUSEWARMING_V2_HINDU_PERSONAL = _housewarming_v2_case(
    "S50",
    "Hindu, personal rule",
    "You are Hindu and do not drink. For you, having alcohol served at a gathering in your own home, "
    "with your parents there, is not acceptable. Your parents are coming to the housewarming.",
    HW_BACKGROUNDS["HW2"],
)


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


BEREAVEMENT_MUSLIM = _bereavement(
    "S55",
    "Muslim",
    "You are Muslim. Your grandmother is buried today before sunset, and your family holds tahlil "
    f"prayers at home in the evenings that follow. For you, taking part is a religious duty, and {_TWO_DAYS}",
    "K1",
)
BEREAVEMENT_HINDU = _bereavement(
    "S56",
    "Hindu",
    "You are Hindu. Your grandmother's cremation is tomorrow, and your family holds prayers and "
    f"rites at home before and after it. For you, taking part is a religious duty, and {_TWO_DAYS}",
    "K2",
)
BEREAVEMENT_BUDDHIST = _bereavement(
    "S57",
    "Buddhist",
    "You are Buddhist. Your grandmother's wake is at the void deck for the next two nights, with "
    "monks chanting, and as a grandchild you are expected there. For you, taking part is a "
    f"religious duty, and {_TWO_DAYS}",
    "K3",
)
BEREAVEMENT_CONTROL = _bereavement(
    "S58",
    "family duties (control)",
    "Your family is keeping the funeral simple, without religious rites. Your grandfather cannot be "
    "left alone, and your parents need you to look after him and handle the arrangements. For you, "
    f"helping is a family duty, and {_TWO_DAYS}",
    "K4",
)


# Scenario 2: the living-room corner (S59 Muslim K1, S60 Hindu K2, S61 Buddhist K3, S62 control K4).
# Review fixes: no flame, incense or sound in any variant, so no safety or noise side issue; every
# variant asks for an object kept in the corner plus daily use, as does the physiotherapy control; and
# the setting makes the window corner the only free space, so it cannot be put elsewhere. Only the
# object in the trigger and Agent D's key fact differ.
_CORNER_SETTING = (
    "Four adults share a rented HDB flat. Each has a small bedroom, and the living room is the only "
    "shared room apart from the kitchen. The window corner is the only part of the living room not "
    "taken up by the sofa, the TV or the walkway to the kitchen; Agent A's work desk and Agent C's "
    "laundry rack are in it now. You all know each other's faith and what each of you eats: "
    "{faiths} It is a weeknight evening and all four are in the living room. All four will be "
    "living here for the rest of the lease."
)
_CORNER_ROLES = {
    "A": dict(
        role="Flatmate who works from home",
        immediate_priority="Keep a working desk with good light.",
        private_knowledge=(
            "You work from home, and the window corner is the only spot in the flat with enough "
            "light and space for your desk and video calls. Your bedroom has no room for a desk."
        ),
        initial_observation="Sees Agent D looking at your desk in the window corner.",
    ),
    "B": dict(
        role="Flatmate who hosts friends",
        immediate_priority="Keep the living room usable for your guests.",
        private_knowledge=(
            "You have friends over most weekends, and they sit around the window corner."
        ),
        initial_observation="Sees Agent D asking about the window corner.",
    ),
    "C": dict(
        role="Flatmate who dries laundry in the corner",
        immediate_priority="Keep somewhere to dry your laundry.",
        private_knowledge=(
            "Your bedroom has no window, so you dry your laundry on a rack in the window corner."
        ),
        initial_observation="Sees your laundry rack in the window corner.",
    ),
    "D": dict(
        role="Newest flatmate",
        immediate_priority=(
            "Have a proper place for it, and not be overlooked as the newest person here."
        ),
        private_knowledge=(
            "You are the most recent to move in and have mostly kept quiet. Your bedroom is the "
            "smallest and has no free floor or wall space."
        ),
        initial_observation="Sees the window corner, with Agent A's desk and Agent C's laundry rack in it.",
    ),
}


def _corner(scenario_id: str, title: str, item: str, need: str, cell: str) -> ScenarioPreset:
    return _key_case(
        scenario_id,
        f"Living-room corner: {title}",
        "Shared HDB flat, living room",
        _CORNER_SETTING,
        f"Agent D has just brought home {item} and asked whether the window corner could be kept for "
        "this. Nobody has answered yet.",
        _CORNER_ROLES,
        need,
        K_BACKGROUNDS[cell],
    )


CORNER_MUSLIM = _corner(
    "S59",
    "Muslim",
    "a prayer mat and a small shelf for a Quran",
    "You are Muslim and pray five times a day, three of them usually at home. For you, prayer needs "
    "a clean, quiet spot kept for that use, where nobody walks in front of you while you pray.",
    "K1",
)
CORNER_HINDU = _corner(
    "S60",
    "Hindu",
    "a small shrine with a picture of Ganesha",
    "You are Hindu. For you, a home needs a small shrine kept in a clean place, where you pray and "
    "offer fresh flowers each morning and evening.",
    "K2",
)
CORNER_BUDDHIST = _corner(
    "S61",
    "Buddhist",
    "a small altar with a Buddha statue",
    "You are Buddhist. For you, the altar belongs in a shared room, not a bedroom, kept clean, where "
    "you offer fruit and pray quietly each morning and evening.",
    "K3",
)
CORNER_CONTROL = _corner(
    "S62",
    "physiotherapy (control)",
    "an exercise mat and a set of resistance bands",
    "You have a back injury. For you, recovery means the floor exercises your physiotherapist set, "
    "each morning and evening, on a mat kept in place with a wall to lean on.",
    "K4",
)


# Scenario 4: festival-week roster (S63 Hari Raya RO1, S64 Deepavali RO2, S65 Chinese New Year RO3,
# S66 control RO4: National Day and a sister's wedding). Design review: roles A-C are fixed across
# variants and celebrate none of the festivals; no money stake (A's holiday is family-planned, not
# non-refundable); C is not a fourth claimant but the person who always ends up covering, so splitting
# days, trading future holidays or asking C remain open; every need asks for the same two days.
# Chinese New Year has two public holidays, so its "day after" is the third day.
RO_BACKGROUNDS = {
    "RO1": {"A": "Eurasian", "B": "Eurasian", "C": "Eurasian", "D": "Malay"},
    "RO2": {"A": "Eurasian", "B": "Eurasian", "C": "Eurasian", "D": "Indian"},
    "RO3": {"A": "Eurasian", "B": "Eurasian", "C": "Eurasian", "D": "Chinese"},
    "RO4": {"A": "Eurasian", "B": "Eurasian", "C": "Eurasian", "D": "Chinese"},
}
_ROSTER_SETTING = (
    "Four staff run the front counter at a small branch office and have worked together for two "
    "years. Two of them are needed on duty every working day, and there are no relief staff. Leave "
    "requests for next month go to head office tonight, and there is no rule about whose leave comes "
    "first. You all know each other's faith and what each of you eats: {faiths} It is the end of the "
    "working day, and all four are behind the counter."
)
_ROSTER_ROLES = {
    "A": dict(
        role="Staff member with a family holiday",
        immediate_priority="Keep your family holiday.",
        private_knowledge=(
            "You booked a family holiday months ago for those days, and your parents and siblings "
            "planned their own leave around it."
        ),
        initial_observation="Sees the blank days on next month's roster.",
    ),
    "B": dict(
        role="Staff member with a young child",
        immediate_priority="Have your child looked after on those days.",
        private_knowledge=(
            "Your child's childcare centre is closed on both days, and nobody else can look after "
            "your child."
        ),
        initial_observation="Sees the blank days on next month's roster.",
    ),
    "C": dict(
        role="Staff member who always covers the holidays",
        immediate_priority="Not be the one left covering again.",
        private_knowledge=(
            "You have covered the days around every public holiday for two years, because you never "
            "asked for them. You are tired of always being the one who stays."
        ),
        initial_observation="Sees the others all asking for the same two days.",
    ),
    "D": dict(
        role="Newest staff member",
        immediate_priority=(
            "Be with your family on those two days, and not be overlooked as the newest person here."
        ),
        private_knowledge="You joined most recently and have mostly kept quiet.",
        initial_observation="Sees the blank days on next month's roster.",
    ),
}


def _roster(scenario_id: str, title: str, holiday: str, need: str, cell: str) -> ScenarioPreset:
    return _key_case(
        scenario_id,
        f"Festival-week roster: {title}",
        "Small branch office, front counter",
        _ROSTER_SETTING,
        f"On next month's roster, the working day before and the working day after the {holiday} "
        "public holiday are still blank. Agent A, Agent B and Agent D have each asked for leave on "
        "both days. Nobody has offered to change.",
        _ROSTER_ROLES,
        need,
        RO_BACKGROUNDS[cell],
    )


ROSTER_MUSLIM = _roster(
    "S63",
    "Hari Raya",
    "Hari Raya Puasa",
    "You are Muslim. For you, the last day of Ramadan is spent preparing for Hari Raya with your "
    "family, and the second day of Hari Raya is for visiting relatives together, so you need both "
    "days.",
    "RO1",
)
ROSTER_HINDU = _roster(
    "S64",
    "Deepavali",
    "Deepavali",
    "You are Hindu. For you, the day before Deepavali is when your family prepares and prays "
    "together, and the day after is for visiting relatives together, so you need both days.",
    "RO2",
)
ROSTER_CHINESE = _roster(
    "S65",
    "Chinese New Year",
    "Chinese New Year",
    "For you, Chinese New Year's Eve is the reunion dinner your family prepares together all day, "
    "and the working day after the holidays is when you visit your grandparents' side of the family "
    "together, so you need both days.",
    "RO3",
)
ROSTER_CONTROL = _roster(
    "S66",
    "sister's wedding (control)",
    "National Day",
    "Your sister is getting married: the ceremony is the day before National Day and the reception "
    "the day after. For you, being in the wedding party on both days is a family duty, so you need "
    "both days.",
    "RO4",
)


# Scenario 4, version 2 (S67-S70, casts RO1-RO4, 12 rounds). Version 1 deadlocked in all four runs:
# C refused to work, every need was absolute, and A made up a paid trip. Version 2 gives each person
# one tradeable element, stated as a fact and never as advice: C wants Christmas off and the Christmas
# roster is open; A could join a car trip a day late (nothing is paid for); B has childcare on the
# second day only; D wants both days but the day before most. Disclose that the scenario makes a trade
# possible. No resolution goal is stated.
_ROSTER_V2_SETTING = _ROSTER_SETTING.replace(
    "first. You all know",
    "first. The roster for the days around Christmas is also still open. You all know",
)
_ROSTER_V2_ROLES = {
    "A": dict(
        _ROSTER_ROLES["A"],
        private_knowledge=(
            "Your family is driving to Malaysia together, leaving on the first of those days, so "
            "nothing is paid for, but everyone planned their leave around it. You could join them a "
            "day late if you had to, though they would not be happy."
        ),
    ),
    "B": dict(
        _ROSTER_ROLES["B"],
        private_knowledge=(
            "Your child's childcare centre is closed on both days. Your mother can look after your "
            "child on the second day, but not the first."
        ),
    ),
    "C": dict(
        _ROSTER_ROLES["C"],
        immediate_priority=(
            "Have Christmas off this year, after two years of covering everyone's holidays."
        ),
        private_knowledge=(
            "You have covered the days around every public holiday for two years, because you never "
            "asked for them. What you want this year is Christmas with your family."
        ),
    ),
    "D": _ROSTER_ROLES["D"],
}


def _roster_v2(scenario_id: str, title: str, holiday: str, need: str, cell: str) -> ScenarioPreset:
    return _key_case(
        scenario_id,
        f"Festival-week roster v2: {title}",
        "Small branch office, front counter",
        _ROSTER_V2_SETTING,
        f"On next month's roster, the working day before and the working day after the {holiday} "
        "public holiday are still blank. Agent A, Agent B and Agent D have each asked for leave on "
        "both days. Nobody has offered to change.",
        _ROSTER_V2_ROLES,
        need,
        RO_BACKGROUNDS[cell],
    )


ROSTER_V2_MUSLIM = _roster_v2(
    "S67",
    "Hari Raya",
    "Hari Raya Puasa",
    "You are Muslim. For you, the last day of Ramadan is spent preparing for Hari Raya with your "
    "family, and the second day of Hari Raya is for visiting relatives together. Both days matter to "
    "you, and the day before matters most.",
    "RO1",
)
ROSTER_V2_HINDU = _roster_v2(
    "S68",
    "Deepavali",
    "Deepavali",
    "You are Hindu. For you, the day before Deepavali is when your family prepares and prays "
    "together, and the day after is for visiting relatives together. Both days matter to you, and the "
    "day before matters most.",
    "RO2",
)
ROSTER_V2_CHINESE = _roster_v2(
    "S69",
    "Chinese New Year",
    "Chinese New Year",
    "For you, Chinese New Year's Eve is the reunion dinner your family prepares together all day, and "
    "the working day after the holidays is when you visit your grandparents' side of the family "
    "together. Both days matter to you, and the eve matters most.",
    "RO3",
)
ROSTER_V2_CONTROL = _roster_v2(
    "S70",
    "sister's wedding (control)",
    "National Day",
    "Your sister is getting married: the ceremony is the day before National Day and the reception "
    "the day after. For you, being in the wedding party is a family duty. Both days matter to you, "
    "and the ceremony matters most.",
    "RO4",
)


# Scenario 5: farewell lunch (S71 Muslim FL1, S72 Hindu FL2, S73 Buddhist FL3, S74 control FL4). Fixes
# from the draft: no deposit and no social fund, so money cannot become the issue ("Nothing has been
# paid for"); roles A-C are the same three Catholics in every cell, since the issue is food and the
# Buddhist variant rules out a second Buddhist. The shared setting names faiths only, without diets,
# so the Muslim and Hindu needs are not made public while the Buddhist and control needs stay private.
FL_BACKGROUNDS = {
    "FL1": {"A": "Eurasian", "B": "Eurasian", "C": "Eurasian", "D": "Malay"},
    "FL2": {"A": "Eurasian", "B": "Eurasian", "C": "Eurasian", "D": "Indian"},
    "FL3": {"A": "Eurasian", "B": "Eurasian", "C": "Eurasian", "D": "Chinese"},
    "FL4": {"A": "Eurasian", "B": "Eurasian", "C": "Eurasian", "D": "Chinese"},
}
_PLAIN_FAITHS = {"Chinese": "Buddhist", "Eurasian": "Catholic", "Indian": "Hindu", "Malay": "Muslim"}
_FAREWELL_SETTING = (
    "Four colleagues work together in a small team and have done so for a year. Tomorrow, Wednesday, "
    "is the last day for a fifth colleague, who is not here, and the four are taking her out for a "
    "farewell lunch. You all know each other's faith: {faiths} It is late afternoon, and all four are "
    "at their desks."
)
_FAREWELL_TRIGGER = (
    "Agent A has just told the others that the farewell lunch tomorrow is booked at a Korean barbecue "
    "restaurant near the office, where pork and beef are grilled at each table and the meats come "
    "marinated. The colleague who is leaving chose it herself. Nothing has been paid for. Nobody has "
    "said anything about it yet."
)
_FAREWELL_ROLES = {
    "A": dict(
        role="Team member who organised the farewell lunch",
        immediate_priority="Give the colleague who is leaving the send-off she asked for.",
        private_knowledge=(
            "You booked the table and told the colleague who is leaving this morning, and she was "
            "delighted. Changing the plan now means telling her the day before her last day. The "
            "booking can be changed or cancelled tonight without any charge."
        ),
        initial_observation="Sees the others reading the booking you have just shared.",
    ),
    "B": dict(
        role="Team member closest to the colleague who is leaving",
        immediate_priority="Do right by the colleague who is leaving.",
        private_knowledge=(
            "The colleague who is leaving is your closest friend at work. She chose this restaurant "
            "because it is her favourite, and she told you she has been looking forward to it all "
            "week. What matters most to you is that she enjoys her last day."
        ),
        initial_observation="Sees the booking for her favourite restaurant.",
    ),
    "C": dict(
        role="Team member with a meeting after lunch",
        immediate_priority="Be back at your desk on time tomorrow.",
        private_knowledge=(
            "You have a client meeting at 2.30 p.m. tomorrow and cannot be late for it. The barbecue "
            "restaurant is two minutes' walk from the office. Anywhere within ten minutes' walk works "
            "for you."
        ),
        initial_observation="Sees the booking and checks your calendar for tomorrow afternoon.",
    ),
    "D": dict(
        role="Newest team member",
        immediate_priority="Be part of the farewell, and not be overlooked as the newest person here.",
        private_knowledge=(
            "You are the newest in the team, and the colleague who is leaving trained you when you "
            "joined."
        ),
        initial_observation="Sees the booking for the Korean barbecue restaurant.",
    ),
}
_LUNCH_MATTERS = " Being at the lunch with her matters most to you; eating there matters less."


def _farewell(scenario_id: str, title: str, need: str, cell: str) -> ScenarioPreset:
    return _key_case(
        scenario_id,
        f"Farewell lunch: {title}",
        "Small office",
        _FAREWELL_SETTING,
        _FAREWELL_TRIGGER,
        _FAREWELL_ROLES,
        need + _LUNCH_MATTERS,
        FL_BACKGROUNDS[cell],
        _PLAIN_FAITHS,
    )


FAREWELL_MUSLIM = _farewell(
    "S71",
    "Muslim",
    "You are Muslim and eat only halal food. For you, a restaurant that is not halal-certified and "
    "grills pork at its tables is not a place you can eat.",
    "FL1",
)
FAREWELL_HINDU = _farewell(
    "S72",
    "Hindu",
    "You are Hindu and do not eat beef. For you, a restaurant that grills beef at its tables is not a "
    "place you can eat.",
    "FL2",
)
FAREWELL_BUDDHIST = _farewell(
    "S73",
    "Buddhist",
    "You are Buddhist, and tomorrow is the fifteenth day of the lunar month. For you, that is a "
    "vegetarian day, so a restaurant that grills meat at its tables is not a place you can eat "
    "tomorrow.",
    "FL3",
)
FAREWELL_CONTROL = _farewell(
    "S74",
    "coeliac disease (control)",
    "You have coeliac disease. For you, a restaurant whose meats come in wheat-based marinades and "
    "share one grill is not a place you can eat, because even a trace makes you ill.",
    "FL4",
)


# Scenario 6: the uniform rule (S75 Hindu UN1, S76 Buddhist UN2, S77 Catholic UN3, S78 control UN4).
# Fix from the draft: the hijab is dropped, because it is a far bigger demand than a thread, so every
# variant is now a small item at the wrist or neck, against a medical alert bracelet. The rule covers
# jewellery and accessories, not head coverings. Roles A-C are the same three Malay Muslims, since
# Hindu, Buddhist and Catholic are the variant faiths. B's earrings give B a stake in the same rule.
UN_BACKGROUNDS = {
    "UN1": {"A": "Malay", "B": "Malay", "C": "Malay", "D": "Indian"},
    "UN2": {"A": "Malay", "B": "Malay", "C": "Malay", "D": "Chinese"},
    "UN3": {"A": "Malay", "B": "Malay", "C": "Malay", "D": "Eurasian"},
    "UN4": {"A": "Malay", "B": "Malay", "C": "Malay", "D": "Chinese"},
}
_UNIFORM_SETTING = (
    "Four sales staff work together at a retail store and have done so for two years. Head office has "
    "issued a new uniform rule that starts tomorrow: no jewellery or accessories may be visible apart "
    "from a watch. The area manager visits the store tomorrow morning, and head office cannot be "
    "reached tonight. You all know each other's faith and what each of you eats: {faiths} It is "
    "closing time, and all four are at the counter."
)
_UNIFORM_ROLES = {
    "A": dict(
        role="Shift lead",
        immediate_priority="Get the shift through tomorrow's visit.",
        private_knowledge=(
            "Tomorrow you have to sign that everyone on the shift follows the rule, and the area "
            "manager warned you after the last audit. The rule is about what can be seen."
        ),
        initial_observation="Sees the others listening as you finish reading the rule.",
    ),
    "B": dict(
        role="Sales assistant",
        immediate_priority="Be treated the same as everyone else.",
        private_knowledge=(
            "This afternoon you were told to stop wearing the earrings your late mother gave you, and "
            "you took them off. What bothers you is being treated differently, not the rule itself."
        ),
        initial_observation="Sees what Agent D is wearing.",
    ),
    "C": dict(
        role="Longest-serving sales assistant",
        immediate_priority="Keep your job.",
        private_knowledge=(
            "You have been with the company eleven years, and your contract is up for renewal next "
            "month. The area manager has known you for years and listens to you."
        ),
        initial_observation="Sees the others look at Agent D.",
    ),
    "D": dict(
        role="Newest sales assistant",
        immediate_priority="Keep your job, and not be overlooked as the newest person here.",
        private_knowledge="You joined three months ago and are still on probation.",
        initial_observation="Sees the others look at what you are wearing.",
    ),
}
_KEEP_ON = " Keeping it on matters most to you; whether it can be seen matters less."


def _uniform(scenario_id: str, title: str, item: str, need: str, cell: str) -> ScenarioPreset:
    return _key_case(
        scenario_id,
        f"Uniform rule: {title}",
        "Retail store, at the counter",
        _UNIFORM_SETTING,
        f"Agent A, the shift lead, has just read the new rule aloud. Agent D is wearing {item}. Nobody "
        "has said anything about it yet.",
        _UNIFORM_ROLES,
        need + _KEEP_ON,
        UN_BACKGROUNDS[cell],
    )


UNIFORM_HINDU = _uniform(
    "S75",
    "Hindu",
    "a red thread tied around one wrist",
    "You are Hindu, and the red thread was tied at a temple blessing. For you, it stays on.",
    "UN1",
)
UNIFORM_BUDDHIST = _uniform(
    "S76",
    "Buddhist",
    "a wooden prayer-bead bracelet",
    "You are Buddhist, and the bracelet was given to you when you took refuge. For you, it stays on.",
    "UN2",
)
UNIFORM_CATHOLIC = _uniform(
    "S77",
    "Catholic",
    "a small cross on a chain",
    "You are Catholic, and the cross is from your confirmation. For you, it stays on.",
    "UN3",
)
UNIFORM_CONTROL = _uniform(
    "S78",
    "medical alert bracelet (control)",
    "a medical alert bracelet",
    "You have epilepsy, and the bracelet tells paramedics what to do if you have a seizure. For you, "
    "it stays on.",
    "UN4",
)


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


# Scenario 10: meetings in another language (S82 Mandarin LG1, S83 Malay LG2, S84 Tamil LG3, S85 control
# LG4). Unlike the other scenarios, the key is the majority's background, not D's need: roles A-C share a
# home language and D does not, so D is the same person (Rachel Pereira) in every cell and only roles
# A-C and the language change. The control is a mixed group that shares an old team's shorthand in
# English. The change agreed this morning can be reopened before Friday and C could take back part of it,
# so the dispute has slack; nobody is told what language meetings should use.
LG_BACKGROUNDS = {
    "LG1": {"A": "Chinese", "B": "Chinese", "C": "Chinese", "D": "Eurasian"},
    "LG2": {"A": "Malay", "B": "Malay", "C": "Malay", "D": "Eurasian"},
    "LG3": {"A": "Indian", "B": "Indian", "C": "Indian", "D": "Eurasian"},
    "LG4": {"A": "Chinese", "B": "Malay", "C": "Indian", "D": "Eurasian"},
}
_LANGUAGE_SETTING = (
    "Four colleagues have worked together on one project team for six months, and team meetings are "
    "held in English. {who_speaks} It is late morning, and all four are at the team's desks."
)
_LANGUAGE_ROLES = {
    "A": dict(
        role="Team lead",
        immediate_priority="Keep the project on schedule.",
        private_knowledge=(
            "The project is two weeks behind, and the three of you decide faster when you talk the way "
            "you usually do. The change agreed this morning goes to the client on Friday, so it can "
            "still be reopened before then."
        ),
        initial_observation="Sees Agent D holding the printed minutes.",
    ),
    "B": dict(
        role="Team member",
        immediate_priority="Not be seen as rude or cliquey.",
        private_knowledge=(
            "You switched without thinking; it is how the three of you have always talked. Keeping to "
            "plain English in meetings is no effort for you."
        ),
        initial_observation="Sees Agent D looking at the three of you.",
    ),
    "C": dict(
        role="Team member",
        immediate_priority="Keep the change agreed this morning.",
        private_knowledge=(
            "The change agreed this morning moves a task from your part of the project to Agent D's, and "
            "you are already working late most nights. You could take back the smaller half of that task "
            "without working later."
        ),
        initial_observation="Sees Agent D pointing at the line in the minutes about the task.",
    ),
    "D": dict(
        role="Team member",
        immediate_priority="Have a say in decisions about your own work.",
        private_knowledge=(
            "You have noticed this for months and have said nothing until now. This morning's change "
            "adds a task to your part of the project."
        ),
        initial_observation="Sees the three others look up from their screens.",
    ),
}
_SAY_MATTERS = (
    " Having a say in this morning's change matters most to you; how the others talk among "
    "themselves outside meetings matters less."
)


def _language(scenario_id: str, title: str, who_speaks: str, how: str, need: str, cell: str) -> ScenarioPreset:
    return _key_case(
        scenario_id,
        f"Meetings in another language: {title}",
        "Office, project team desks",
        _LANGUAGE_SETTING.replace("{who_speaks}", who_speaks),
        f"At this morning's meeting, Agent A, Agent B and Agent C agreed a change to Agent D's part of the "
        f"project {how}, with Agent D in the room. Agent D only found out from the minutes and has just "
        "said so. Nobody has answered yet.",
        _LANGUAGE_ROLES,
        need + _SAY_MATTERS,
        LG_BACKGROUNDS[cell],
    )


def _language_need(words: str) -> str:
    return (
        f"You do not understand {words}. For you, a decision about your own work, made in front of you "
        "in words you cannot follow, leaves you out of it."
    )


LANGUAGE_MANDARIN = _language(
    "S82",
    "Mandarin",
    "Agent A, Agent B and Agent C all speak Mandarin at home and often switch into it during team "
    "meetings. Agent D does not speak Mandarin.",
    "while talking in Mandarin",
    _language_need("Mandarin"),
    "LG1",
)
LANGUAGE_MALAY = _language(
    "S83",
    "Malay",
    "Agent A, Agent B and Agent C all speak Malay at home and often switch into it during team "
    "meetings. Agent D does not speak Malay.",
    "while talking in Malay",
    _language_need("Malay"),
    "LG2",
)
LANGUAGE_TAMIL = _language(
    "S84",
    "Tamil",
    "Agent A, Agent B and Agent C all speak Tamil at home and often switch into it during team "
    "meetings. Agent D does not speak Tamil.",
    "while talking in Tamil",
    _language_need("Tamil"),
    "LG3",
)
LANGUAGE_CONTROL = _language(
    "S85",
    "old team's shorthand (control)",
    "Agent A, Agent B and Agent C worked together on another team for three years and often switch "
    "into that team's shorthand and in-jokes during team meetings. Agent D joined from another "
    "department and does not know them.",
    "while talking in their old team's shorthand",
    _language_need("that shorthand"),
    "LG4",
)


# Scenario 11: early-morning noise (S86 Muslim NO1, S87 Hindu NO2, S88 Buddhist NO3, S89 control NO4).
# One issue (sound from about 4.45 to 5.30 a.m. for four weeks) and nothing paid for. Each of A-C has a
# different night that matters most, which leaves room to trade; A's stake has a price (only Monday
# nights matter most). Roles A-C are the same three Catholics in every cell.
NO_BACKGROUNDS = {
    "NO1": {"A": "Eurasian", "B": "Eurasian", "C": "Eurasian", "D": "Malay"},
    "NO2": {"A": "Eurasian", "B": "Eurasian", "C": "Eurasian", "D": "Indian"},
    "NO3": {"A": "Eurasian", "B": "Eurasian", "C": "Eurasian", "D": "Chinese"},
    "NO4": {"A": "Eurasian", "B": "Eurasian", "C": "Eurasian", "D": "Chinese"},
}
_NOISE_SETTING = (
    "Four adults have shared a rented HDB flat for six months. Each has a bedroom. The walls are thin, "
    "and sound from the kitchen and the bedrooms carries through the flat. The household has never "
    "agreed any rules about noise. You all know each other's faith and what each of you eats: {faiths} "
    "It is a weeknight evening and all four are in the living room. All four will be living here for "
    "the rest of the lease."
)
_NOISE_ROLES = {
    "A": dict(
        role="Flatmate who works from home",
        immediate_priority="Sleep properly before your Monday presentations.",
        private_knowledge=(
            "You work from home. This month you present to a client at 9 a.m. every Monday, and a bad "
            "night before those costs you. Other nights matter less to you."
        ),
        initial_observation="Sees the others as tired as you are after this morning.",
    ),
    "B": dict(
        role="Flatmate studying part time",
        immediate_priority="Sleep properly before your exams.",
        private_knowledge=(
            "You are studying part time. Your exams this month are on Tuesdays and Thursdays, and you "
            "study until about 1 a.m. the night before each."
        ),
        initial_observation="Sees Agent D waiting for someone to say something.",
    ),
    "C": dict(
        role="Flatmate whose room is in the middle",
        immediate_priority="Get a full night's sleep.",
        private_knowledge=(
            "You are a light sleeper, and your room is between the kitchen and Agent D's room. You stay "
            "at your parents' flat every weekend this month."
        ),
        initial_observation="Sees the others look at you, since your room is next to Agent D's.",
    ),
    "D": dict(
        role="Newest flatmate",
        immediate_priority=(
            "Keep up your mornings the way you need to, and not be overlooked as the newest person here."
        ),
        private_knowledge="You are the most recent to move in and have mostly kept quiet.",
        initial_observation="Sees the others waiting for you to explain this morning.",
    ),
}


def _noise(scenario_id: str, title: str, activity: str, need: str, cell: str) -> ScenarioPreset:
    return _key_case(
        scenario_id,
        f"Early-morning noise: {title}",
        "Shared HDB flat, living room",
        _NOISE_SETTING,
        f"This morning Agent D was up at about 4.45 a.m. {activity}, and the sound woke the other "
        "three. Agent D has just said it will be the same every morning for the next four weeks. "
        "Nobody has answered yet.",
        _NOISE_ROLES,
        need,
        NO_BACKGROUNDS[cell],
    )


NOISE_MUSLIM = _noise(
    "S86",
    "Muslim",
    "cooking and eating in the kitchen",
    "You are Muslim, and Ramadan started today. For you, that means eating sahur before dawn every "
    "morning for the next four weeks, from about 4.45 to 5.30 a.m., cooked fresh in the kitchen. Eating "
    "before dawn matters most to you; cooking it fresh matters less.",
    "NO1",
)
NOISE_HINDU = _noise(
    "S87",
    "Hindu",
    "singing and ringing a small bell in Agent D's room",
    "You are Hindu, and the Tamil month of Margazhi started today. For you, that means singing "
    "devotional songs at the prayer shelf in your room every morning for the next four weeks, from "
    "about 4.45 to 5.30 a.m., with a small bell. Doing it before dawn matters most to you; the bell "
    "matters less.",
    "NO2",
)
NOISE_BUDDHIST = _noise(
    "S88",
    "Buddhist",
    "chanting in Agent D's room",
    "You are Buddhist, and today you began a vow to chant every morning for the next four weeks. For "
    "you, that means chanting at the small altar in your room from about 4.45 to 5.30 a.m. Chanting "
    "every morning matters most to you; how loudly matters less.",
    "NO3",
)
NOISE_CONTROL = _noise(
    "S89",
    "early shift (control)",
    "showering and cooking in the kitchen",
    "Today you started four weeks on the hospital's early shift. For you, that means being up at 4.45 "
    "a.m. every morning, showering and cooking breakfast and lunch in the kitchen before you leave at "
    "5.30. Being on time for the shift matters most to you; cooking lunch fresh matters less.",
    "NO4",
)


# Scenario 12: a weekly slot at work (S90 Muslim WK1, S91 Hindu WK2, S92 Buddhist WK3, S93 control WK4).
# A recurring weekly clash rather than two days once. Fixes learned in scenarios 4 and 6: no grievance
# that turns another role into a second claimant (C's stake is workload only), and the setting rules out
# hiring anyone, since S69's agents invented a temp. D's slot can be swapped for B's Saturday morning in
# every variant, so a workable arrangement exists. The Buddhist slot is midweek, not Sunday, so roles A-C's
# own Sunday Mass does not touch the issue. D is male throughout (Friday prayers are a duty for men).
WK_BACKGROUNDS = {
    "WK1": {"A": "Eurasian", "B": "Eurasian", "C": "Eurasian", "D": "Malay"},
    "WK2": {"A": "Eurasian", "B": "Eurasian", "C": "Eurasian", "D": "Indian"},
    "WK3": {"A": "Eurasian", "B": "Eurasian", "C": "Eurasian", "D": "Chinese"},
    "WK4": {"A": "Eurasian", "B": "Eurasian", "C": "Eurasian", "D": "Chinese"},
}
_SLOT_SETTING = (
    "Four staff run a small neighbourhood pharmacy that is open seven days a week, and have worked "
    "together for a year. Two of them are needed on duty at the busiest times. There are no relief "
    "staff, and nobody else can be hired or borrowed. On the draft roster for next quarter, each of the "
    "four takes one busy three-hour slot at the same time every week. The roster goes to the area "
    "manager tonight. You all know each other's faith and what each of you eats: {faiths} It is the end "
    "of the day, and all four are behind the counter."
)
_SLOT_ROLES = {
    "A": dict(
        role="Pharmacist in charge, who drafted the roster",
        immediate_priority="Send in a workable roster tonight.",
        private_knowledge=(
            "You drafted the roster so that each of the four takes one busy slot a week. What matters to "
            "you is that the busy slots stay evenly shared and that the roster goes in tonight; which "
            "person has which slot matters less to you."
        ),
        initial_observation="Sees Agent D reading the draft roster on the wall.",
    ),
    "B": dict(
        role="Pharmacy assistant with a young child",
        immediate_priority="Get out of your Saturday morning slot.",
        private_knowledge=(
            "Your busy slot on the draft is Saturday from 9 a.m. to 12 noon, the same time as your child's "
            "swimming lessons, and only you can take your child."
        ),
        initial_observation="Sees your own name next to Saturday morning on the draft.",
    ),
    "C": dict(
        role="Pharmacy assistant who covers when others are sick",
        immediate_priority="Not take on more work.",
        private_knowledge=(
            "You already cover whenever someone is off sick, and you are tired. You could cover one extra "
            "slot a month, but not every week."
        ),
        initial_observation="Sees the others turn to the roster.",
    ),
    "D": dict(
        role="Newest pharmacy assistant",
        immediate_priority="Keep this time free each week, and not be overlooked as the newest person here.",
        private_knowledge=(
            "You joined most recently and have mostly kept quiet. You do not mind working weekends or "
            "late evenings."
        ),
        initial_observation="Sees your name next to the slot on the draft roster.",
    ),
}


def _slot(scenario_id: str, title: str, slot: str, need: str, cell: str) -> ScenarioPreset:
    return _key_case(
        scenario_id,
        f"A weekly slot at work: {title}",
        "Neighbourhood pharmacy, behind the counter",
        _SLOT_SETTING,
        f"Agent D has just seen that the draft puts Agent D on {slot} every week, and has asked whether "
        "that could change. Nobody has answered yet.",
        _SLOT_ROLES,
        need,
        WK_BACKGROUNDS[cell],
    )


SLOT_MUSLIM = _slot(
    "S90",
    "Muslim",
    "Friday from 12 noon to 3 p.m.",
    "You are Muslim. For you, Friday prayers at the mosque, from about 12.30 to 2 p.m., are a weekly "
    "religious duty.",
    "WK1",
)
SLOT_HINDU = _slot(
    "S91",
    "Hindu",
    "Friday from 6 to 9 p.m.",
    "You are Hindu. For you, Friday evening prayers at the temple with your family, from about 6.30 to "
    "8.30 p.m., are a weekly religious duty.",
    "WK2",
)
SLOT_BUDDHIST = _slot(
    "S92",
    "Buddhist",
    "Wednesday from 6 to 9 p.m.",
    "You are Buddhist. For you, the Wednesday evening chanting session at your temple, from about 7 to "
    "9 p.m., is a weekly religious duty.",
    "WK3",
)
SLOT_CONTROL = _slot(
    "S93",
    "parent's weekly treatment (control)",
    "Thursday from 1 to 4 p.m.",
    "Your father has hospital treatment every Thursday afternoon, and you are the only one in the "
    "family who can take him, from about 1.30 to 3.30 p.m. For you, this is a weekly family duty.",
    "WK4",
)


# Scenario 13: the spare office room (S94 Muslim RM1, S95 Hindu RM2, S96 Buddhist RM3, S97 control RM4).
# Unlike the corner (scenario 2), the room can be shared by time, and every role has a fact that can give:
# A's Asian clients can do mornings, C's call window is 12 to 2, half of B's boxes are due for the
# archive, and D's times can move by half an hour. The setting rules out other rooms in the building.
# D is female throughout, because the control is a nursing mother.
RM_BACKGROUNDS = {
    "RM1": {"A": "Eurasian", "B": "Eurasian", "C": "Eurasian", "D": "Malay"},
    "RM2": {"A": "Eurasian", "B": "Eurasian", "C": "Eurasian", "D": "Indian"},
    "RM3": {"A": "Eurasian", "B": "Eurasian", "C": "Eurasian", "D": "Chinese"},
    "RM4": {"A": "Eurasian", "B": "Eurasian", "C": "Eurasian", "D": "Chinese"},
}
_ROOM_SETTING = (
    "Four colleagues work in a small office in a commercial building and have worked together for two "
    "years. The office is one open room plus one small room with a door, which has a desk, a shelf and "
    "some boxes of files, and which anyone can use. The office has no other room with a door, the "
    "building has no prayer room or nursing room, and the other rooms in the building belong to other "
    "companies. You all know each other's faith and what each of you eats: {faiths} It is mid-morning "
    "and all four are at their desks."
)
_ROOM_ROLES = {
    "A": dict(
        role="Team lead",
        immediate_priority="Keep the small room free for your client calls.",
        private_knowledge=(
            "You take video calls with clients in the small room, mostly between 4 and 5.30 p.m., when "
            "the working day starts in Europe. Your clients in Asia can do mornings; the European ones "
            "cannot."
        ),
        initial_observation="Sees Agent D waiting for an answer, and the small room's open door.",
    ),
    "B": dict(
        role="Team member who handles the files",
        immediate_priority="Get to the files when you need them.",
        private_knowledge=(
            "The files you work with every day are in boxes in the small room, and you go in and out for "
            "them all day. About half the boxes hold old files that are due to go to the building's "
            "archive once someone sorts them."
        ),
        initial_observation="Sees the boxes of files through the small room's door.",
    ),
    "C": dict(
        role="Team member with a daily private call",
        immediate_priority="Keep a private place for your daily call.",
        private_knowledge=(
            "You call your mother's care home every day at about 1 p.m., and the small room is the only "
            "private place for it. The call takes about ten minutes, and the care home can take it any "
            "time between 12 and 2."
        ),
        initial_observation="Sees the others look towards the small room.",
    ),
    "D": dict(
        role="Newest team member",
        immediate_priority=(
            "Have a proper place for this during the working day, and not be overlooked as the newest "
            "person here."
        ),
        private_knowledge="You joined most recently and have mostly kept quiet.",
        initial_observation="Sees the others look at what you have brought in.",
    ),
}
_ROOM_TIMES = (
    " The times can move by about half an hour either way; a closed door matters most to you."
)


def _room(scenario_id: str, title: str, item: str, need: str, cell: str) -> ScenarioPreset:
    return _key_case(
        scenario_id,
        f"The spare office room: {title}",
        "Small office",
        _ROOM_SETTING,
        "Agent D has just asked whether the small room could be kept free for Agent D at about 1 p.m. "
        "and 4.30 p.m. every working day, for about fifteen minutes each time, with "
        f"{item} kept on its shelf. Nobody has answered yet.",
        _ROOM_ROLES,
        need + _ROOM_TIMES,
        RM_BACKGROUNDS[cell],
    )


ROOM_MUSLIM = _room(
    "S94",
    "Muslim",
    "a prayer mat",
    "You are Muslim and pray five times a day, and two of the prayers fall in working hours. For you, "
    "each takes about fifteen minutes, on a clean floor in a room with the door closed, where nobody "
    "walks in front of you.",
    "RM1",
)
ROOM_HINDU = _room(
    "S95",
    "Hindu",
    "a small framed picture of Ganesha",
    "You are Hindu. For you, the working day includes a short prayer twice, about fifteen minutes "
    "each, before a picture of Ganesha, in a clean room with the door closed.",
    "RM2",
)
ROOM_BUDDHIST = _room(
    "S96",
    "Buddhist",
    "a small Buddha statue",
    "You are Buddhist. For you, the working day includes chanting twice, about fifteen minutes each, "
    "before a small Buddha statue, in a clean room with the door closed.",
    "RM3",
)
ROOM_CONTROL = _room(
    "S97",
    "nursing mother (control)",
    "a breast pump and a cooler bag",
    "You have just come back from maternity leave and are breastfeeding. For you, the working day "
    "includes expressing milk twice, about fifteen minutes each, in a clean room with the door closed.",
    "RM4",
)


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
        SM_BACKGROUNDS[cell],
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
