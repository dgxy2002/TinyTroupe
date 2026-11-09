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


def _faith_sentence(backgrounds: dict[str, str]) -> str:
    faiths = {role: _FAITH_WORDS[background] for role, background in backgrounds.items()}
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
        shared_setting=setting.replace("{faiths}", _faith_sentence(backgrounds)),
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
