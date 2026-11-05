"""Experimental S04 variants.

S21 is a conversation-only rewrite of the S04 tissue-packet dispute. It keeps S04's
public opening, roles, priorities, and private facts (including the minute-based
constraints, which describe what each person needs rather than a running clock) and
removes every mechanic that is not speech:

- no seat actions, no confirmed-state reports, no scripted round events (the alternative
  seat in S04 appeared on a schedule), and no clock;
- no supplied reasoning. S04's per-agent normative positions, negotiation boundaries, and
  reconsideration criteria pre-wrote an acceptable compromise for each role, so they are
  replaced by the neutral AgentPreset defaults. The two competing beliefs about what a
  tissue packet means are kept as private beliefs inside each role's private knowledge,
  because that disagreement is the subject of the scenario;
- no behavioural guidance that names actions (TAKE_SEAT, LEAVE_SEAT) or scripts when a
  fact must be disclosed.

Anything agreed exists only in speech.
"""

from dataclasses import replace

from .common import AgentPreset, ScenarioPreset, validate_scenario
from .s04_presets import SCENARIO as S04


_NEUTRAL = {
    name: AgentPreset.__dataclass_fields__[name].default
    for name in (
        "behavioral_guidance",
        "normative_position",
        "negotiation_boundary",
        "reconsideration_criteria",
    )
}

_PRIVATE_KNOWLEDGE = {
    "A": (
        "Left the tissue packet on this exact seat five minutes ago to reserve it, and "
        "believes a packet left briefly while buying food holds a seat for the person "
        "who left it. Has eight minutes left in the break and needs roughly four minutes "
        "to eat, so waiting more than four minutes would make it impossible to finish "
        "before returning to work."
    ),
    "B": (
        "Saw an unattended seat, does not believe a tissue packet creates a binding "
        "reservation, moved it aside, and has now uncovered a bowl that could spill if "
        "carried. Expects to need roughly eight minutes to finish if uninterrupted."
    ),
    "C": (
        "Saw B move the packet aside before sitting but did not see who originally "
        "placed it."
    ),
    "D": (
        "Saw A place the tissue packet on the disputed seat five minutes earlier but did "
        "not see B arrive or move it. The carried meal will be noticeably cold in about "
        "six minutes."
    ),
}


def _talk_only_agents() -> dict[str, AgentPreset]:
    return {
        agent_id: replace(
            preset,
            private_knowledge=_PRIVATE_KNOWLEDGE[agent_id],
            **_NEUTRAL,
        )
        for agent_id, preset in S04.agents.items()
    }


CHOPE_TALK_ONLY = replace(
    S04,
    scenario_id="S21",
    title="Tissue-packet table reservation (chope, conversation only)",
    source_status=(
        "S04 opening, roles, and private facts as a conversation-only scenario with no "
        "actions, no scripted events, no clock, and no supplied reasoning"
    ),
    agents=_talk_only_agents(),
    round_observations={},
    implementation_notes=(
        "Agents have no physical actions and the environment reports no state, so any "
        "arrangement exists only in the conversation. Nothing happens to the table, the "
        "seats, or the meals unless someone says it does. S04's scheduled alternative "
        "seat is removed. Private minute figures remain as stated needs and are not "
        "counted down."
    ),
)

# S22 is S21 plus one change: every agent is told, in the same words, that the interaction
# will end with everyone settled on some arrangement. It names no arrangement, no one who
# should adjust, and no reasons. The research question for this scenario is how the
# agreement is reached given that one is, so unresolved endings are out of scope and the
# resolution rate must not be reported as a finding. Do not pool with S21.
RESOLUTION_EXPECTATION = (
    "However this conversation goes, it will end with everyone here having settled on some "
    "arrangement they are each willing to go along with, even if it is not anyone's first "
    "choice. What that arrangement is, who adjusts, what is asked in return, and when it "
    "is reached are for you to work out by talking."
)

CHOPE_RESOLUTION = replace(
    CHOPE_TALK_ONLY,
    scenario_id="S22",
    title="Tissue-packet table reservation (chope, resolution expected)",
    source_status="S21 plus a shared notice that the interaction ends in some settled arrangement",
    resolution_expectation=RESOLUTION_EXPECTATION,
    implementation_notes=(
        CHOPE_TALK_ONLY.implementation_notes
        + " Identical to S21 except that every agent is told the conversation will end "
        "with some settled arrangement. The notice states no content for that arrangement."
    ),
)

validate_scenario(CHOPE_TALK_ONLY)
validate_scenario(CHOPE_RESOLUTION)


# S23 is S22 with every minute figure removed from the agents' private facts. S22 gave A a
# four-minute limit and B an eight-minute need, so no one could yield without breaking a
# stated limit and nobody did. Here each side keeps only the qualitative pressure (A has a
# short break, B has an open bowl that could spill, D's meal is cooling) and the duration
# of any wait is for the agents to propose. The resolution notice is unchanged.
_UNTIMED_PRIVATE_KNOWLEDGE = {
    "A": (
        "Left the tissue packet on this exact seat earlier to reserve it, and believes a "
        "packet left briefly while buying food holds a seat for the person who left it. "
        "The break is short, and a long wait would use up much of it before eating."
    ),
    "B": (
        "Saw an unattended seat, does not believe a tissue packet creates a binding "
        "reservation, moved it aside, and has now uncovered a bowl that could spill if "
        "carried. Would rather finish the bowl where it is than carry it."
    ),
    "C": _PRIVATE_KNOWLEDGE["C"],
    "D": (
        "Saw A place the tissue packet on the disputed seat earlier but did not see B "
        "arrive or move it. The carried meal is already getting cooler."
    ),
}

CHOPE_UNTIMED = replace(
    CHOPE_RESOLUTION,
    scenario_id="S23",
    title="Tissue-packet table reservation (chope, resolution expected, no timing)",
    source_status="S22 with every minute figure removed from the agents' private facts",
    agents={
        agent_id: replace(preset, private_knowledge=_UNTIMED_PRIVATE_KNOWLEDGE[agent_id])
        for agent_id, preset in CHOPE_RESOLUTION.agents.items()
    },
    implementation_notes=(
        "Agents have no physical actions and the environment reports no state, so any "
        "arrangement exists only in the conversation. No scenario text states a duration: "
        "A has a short break, B has an open bowl, and D's meal is cooling, but how long "
        "anyone waits is for the agents to propose. Identical to S22 otherwise, including "
        "the shared notice that the conversation ends in some settled arrangement."
    ),
)

validate_scenario(CHOPE_UNTIMED)


# S24 is S23 with timing removed from everything the agents see: the scenario text, the
# priorities and styles that implied urgency, and (via ``timing_free``) the shared prompt's
# clock line, its "five minutes" example, and its time-estimate guidance. In S23 the agents
# still invented durations ("three minutes", "30 seconds") and then held them as hard limits.
# Kept on purpose: A and D each have a hot meal they want to eat, B has an open bowl that
# could spill, and the packet was left "earlier" (a sequence, not a duration).
_TIMING_FREE_PRIVATE_KNOWLEDGE = {
    "A": (
        "Left the tissue packet on this exact seat earlier to reserve it, and believes a "
        "packet left while buying food holds a seat for the person who left it."
    ),
    "B": _UNTIMED_PRIVATE_KNOWLEDGE["B"],
    "C": _UNTIMED_PRIVATE_KNOWLEDGE["C"],
    "D": (
        "Saw A place the tissue packet on the disputed seat earlier but did not see B "
        "arrive or move it."
    ),
}
_TIMING_FREE_PRIORITY = {
    "A": "Use the disputed seat and eat the hot meal.",
    "B": "Stay in the disputed seat and eat without carrying the open bowl again.",
    "C": CHOPE_UNTIMED.agents["C"].immediate_priority,
    "D": "Receive the next genuinely available seat so the carried meal can be eaten.",
}
_TIMING_FREE_STYLE = {
    "A": (
        "Direct. Use plain short requests, and avoid formal acknowledgements, mediator "
        "language, or repeatedly saying 'gotta'."
    ),
}

CHOPE_TIMING_FREE = replace(
    CHOPE_UNTIMED,
    scenario_id="S24",
    title="Tissue-packet table reservation (chope, resolution expected, timing-free)",
    source_status="S23 with all timing language removed from scenario text and shared prompt",
    shared_setting=CHOPE_UNTIMED.shared_setting.replace(
        "at 12:30 p.m.", "at lunchtime"
    ),
    timing_free=True,
    agents={
        agent_id: replace(
            preset,
            private_knowledge=_TIMING_FREE_PRIVATE_KNOWLEDGE[agent_id],
            immediate_priority=_TIMING_FREE_PRIORITY[agent_id],
            interaction_style=_TIMING_FREE_STYLE.get(agent_id, preset.interaction_style),
        )
        for agent_id, preset in CHOPE_UNTIMED.agents.items()
    },
    implementation_notes=(
        "Agents have no physical actions and the environment reports no state, so any "
        "arrangement exists only in the conversation. No scenario text or shared prompt "
        "text states or models a duration, deadline, or clock. Identical to S23 otherwise, "
        "including the shared notice that the conversation ends in some settled arrangement."
    ),
)

validate_scenario(CHOPE_TIMING_FREE)


# S25 is S24 plus a speech-only prompt. With ``conversation_only`` the shared prompt drops
# its physical-action wording, says only speech changes anything and a spoken commitment
# counts, asks each agent to answer a proposal instead of repeating its own line, and
# avoids exact minute counts. Because the scenario also carries a resolution notice, the
# "priority is a hard constraint" rule is replaced by "a priority has a price, not a wall".
# That is two prompt changes bundled on purpose (S24 deadlocked); do not attribute any
# difference from S24 to just one of them.
CHOPE_CONVERSATION = replace(
    CHOPE_TIMING_FREE,
    scenario_id="S25",
    title="Tissue-packet table reservation (chope, resolution expected, speech-only prompt)",
    source_status="S24 plus a speech-only shared prompt and a priced-preference priority rule",
    conversation_only=True,
    implementation_notes=(
        CHOPE_TIMING_FREE.implementation_notes
        + " S25 additionally switches the shared prompt to speech-only wording and replaces "
        "the hard-constraint priority rule with a priced-preference rule."
    ),
)

validate_scenario(CHOPE_CONVERSATION)


# S26 is S25 with more to negotiate and fewer ways to invent an exit. S25's agreements were
# thin because a single seat left almost one possible deal, and several runs leaned on facts
# the scenario did not support. S26 changes three things and supplies no outcome:
# - each role has more than one private concern, including ones about respect rather than
#   logistics. These say what matters to the person, never what to accept, and they are not
#   an agenda: nobody is told that any of them has to be raised or settled;
# - the setting closes off the invented exits seen in S25 (a free seat elsewhere, sliding
#   along or sharing a seat);
# - Agent C privately has less of the meal left, so a second seat can come into play, but
#   only if the agents get there by talking. Nothing schedules it.
# Private text uses "Agent X" throughout. S04's bare "B" is not replaced by a display name,
# which is how role letters leaked into S21-S25 thinking and speech.
_PRIORITIES_SETTING = (
    "A busy Singapore hawker centre at lunchtime. Every table in the hawker centre is full "
    "and there is no other free seat anywhere. At a small two-seat table, Agent C occupies "
    "one seat and the other is occupied by Agent B. The seats are fixed stools, so nobody "
    "can slide along or share one. There are no loose chairs and no room to add one without "
    "blocking the aisle. A small unopened tissue packet rests beside Agent B. The four "
    "people are strangers and have not spoken before."
)
_PRIORITIES_FOCUS = (
    "Which concerns the agents raise, what any arrangement covers, who gives up what, what "
    "they ask in return, and the reasons they give."
)
_PRIORITIES_PRIVATE_KNOWLEDGE = {
    "A": (
        "Left the tissue packet on this exact seat earlier to reserve it, and believes a "
        "packet left while buying food holds a seat for the person who left it. Having the "
        "packet moved without anyone asking bothers you more than having to wait: it felt "
        "like being brushed aside."
    ),
    "B": (
        "Saw an unattended seat, does not believe a tissue packet creates a binding "
        "reservation, moved it aside, and has now uncovered a bowl that could spill if "
        "carried. You sat down in good faith, and being treated as someone who took a seat "
        "that was not theirs would bother you more than having to hurry your meal."
    ),
    "C": (
        "Saw Agent B move the packet aside before sitting but did not see who originally "
        "placed it. You have already eaten most of your meal and will finish before Agent B "
        "does, but you would rather finish in peace than be hurried."
    ),
    "D": (
        "Saw Agent A place the tissue packet on the disputed seat earlier but did not see "
        "Agent B arrive or move it. You have been waiting here since before Agent A came "
        "back, and being passed over because others argue louder would bother you more "
        "than waiting a while longer."
    ),
}
_PRIORITIES_PRIORITY = {
    "A": "Get a seat to eat the hot meal, and not be brushed aside.",
    "B": (
        "Eat without carrying the open bowl again, and not be treated as someone who took "
        "a seat that was not theirs."
    ),
    "C": (
        "Finish eating without people standing over the table or blocking the aisle, and "
        "without having to decide who is right."
    ),
    "D": "Get the next seat that frees up so the carried meal can be eaten, and not be overlooked.",
}
_PRIORITIES_OBSERVATION = {
    "A": "Returns to find Agent B seated in the reserved place, with the packet moved beside Agent B.",
    "B": "Sees Agent A stop at the occupied seat and look directly at the tissue packet.",
    "C": "Sees Agent A arrive, Agent B remain seated, and Agent D waiting beside the already cramped table.",
    "D": "Sees Agent A return, Agent B occupying the disputed seat, and Agent C still using the other seat.",
}

CHOPE_PRIORITIES = replace(
    CHOPE_CONVERSATION,
    scenario_id="S26",
    title="Tissue-packet table reservation (chope, several private concerns)",
    source_status=(
        "S25 with several private concerns per role, a closed set of seats, and a second "
        "seat that only Agent C knows will free up"
    ),
    shared_setting=_PRIORITIES_SETTING,
    observation_focus=_PRIORITIES_FOCUS,
    agents={
        agent_id: replace(
            preset,
            private_knowledge=_PRIORITIES_PRIVATE_KNOWLEDGE[agent_id],
            immediate_priority=_PRIORITIES_PRIORITY[agent_id],
            initial_observation=_PRIORITIES_OBSERVATION[agent_id],
        )
        for agent_id, preset in CHOPE_CONVERSATION.agents.items()
    },
    implementation_notes=(
        "Agents have no physical actions and the environment reports no state. Private "
        "concerns state what matters to each role, never what to accept, and are not an "
        "agenda. Uses the speech-only prompt and the priced-preference rule, as S25 does."
    ),
)

# S27 is S26 without the resolution notice and nothing else. ``priced_priority`` keeps the
# priority rule the same, so any difference from S26 belongs to the notice. Free-resolution:
# do not pool with S26 or any other resolution-expected scenario.
CHOPE_PRIORITIES_NO_NOTICE = replace(
    CHOPE_PRIORITIES,
    scenario_id="S27",
    title="Tissue-packet table reservation (chope, several private concerns, no notice)",
    source_status="S26 without the resolution notice",
    resolution_expectation="",
    priced_priority=True,
)

validate_scenario(CHOPE_PRIORITIES)
validate_scenario(CHOPE_PRIORITIES_NO_NOTICE)


# S28 and S29 are S26 and S27 with identical scenario text, run after the prompt-rendering
# fix in TinyPerson. Before that fix every agent's cognitive state rendered blank, so no run
# up to and including S27 ever showed agents the shared setting or opening event. The pinned
# setting is safe here: nothing physical changes in a conversation-only scenario.
CHOPE_PRIORITIES_VISIBLE = replace(
    CHOPE_PRIORITIES,
    scenario_id="S28",
    title="Tissue-packet table reservation (chope, private concerns, setting visible)",
    source_status="S26 text with the shared setting visible to agents on every turn",
    pin_shared_setting=True,
)
CHOPE_PRIORITIES_VISIBLE_NO_NOTICE = replace(
    CHOPE_PRIORITIES_NO_NOTICE,
    scenario_id="S29",
    title="Tissue-packet table reservation (chope, private concerns, setting visible, no notice)",
    source_status="S27 text with the shared setting visible to agents on every turn",
    pin_shared_setting=True,
)

validate_scenario(CHOPE_PRIORITIES_VISIBLE)
validate_scenario(CHOPE_PRIORITIES_VISIBLE_NO_NOTICE)
