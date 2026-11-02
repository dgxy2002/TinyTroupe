"""Experimental S02 ablation variants.

The frozen S02 preset remains the structured reference condition. These variants
share its public opening, state mechanics, and agent priorities so differences
can be attributed to a small number of declared changes:

- S12 removes supplied moral interpretations, compromise ranges, reconsideration
  logic, and reasoning scripts. Physical-action guidance is retained.
- S13 starts from S12 and adds genuinely private stakes (disclosure is the
  agent's choice) so that no ventilation option is free, and lets the stove timer
  count down instead of the environment declaring the dish finished at round 2.
"""

from dataclasses import replace

from .common import AgentPreset, ScenarioPreset, validate_scenario
from .s02_presets import SCENARIO as S02


def _minimal_agents() -> dict[str, AgentPreset]:
    """S02 facts and priorities without supplied reasoning or outcome boundaries."""

    base = S02.agents
    return {
        "A": AgentPreset(
            age=base["A"].age,
            role=base["A"].role,
            immediate_priority=base["A"].immediate_priority,
            private_knowledge=base["A"].private_knowledge,
            initial_observation=base["A"].initial_observation,
            interaction_style="Practical and direct.",
            behavioral_guidance=(
                "When the meal is ready, physically release the stove. If you take a "
                "concrete ventilation step, perform the available action rather than "
                "only promising it."
            ),
        ),
        "B": AgentPreset(
            age=base["B"].age,
            role=base["B"].role,
            immediate_priority=base["B"].immediate_priority,
            private_knowledge=base["B"].private_knowledge,
            initial_observation=base["B"].initial_observation,
            interaction_style="Direct and unembellished.",
            behavioral_guidance=(
                "If you choose an available ventilation action, perform it; do not imply "
                "that a window or extractor was used until confirmed."
            ),
        ),
        "C": AgentPreset(
            age=base["C"].age,
            role=base["C"].role,
            immediate_priority=base["C"].immediate_priority,
            private_knowledge=base["C"].private_knowledge,
            initial_observation=base["C"].initial_observation,
            interaction_style="Precise and reserved.",
            behavioral_guidance=(
                "If you move your rack, use the available action rather than claiming it happened."
            ),
        ),
        "D": AgentPreset(
            age=base["D"].age,
            role=base["D"].role,
            immediate_priority=base["D"].immediate_priority,
            private_knowledge=base["D"].private_knowledge,
            initial_observation=base["D"].initial_observation,
            interaction_style="Brief and time-conscious.",
            behavioral_guidance=(
                "Take the stove only after the environment confirms it is free, using "
                "TAKE_STOVE."
            ),
        ),
    }


MINIMAL = replace(
    S02,
    scenario_id="S12",
    title="Cooking odour, ventilation responsibility, and stove access (minimal facts)",
    source_status="S02 ablation: supplied reasoning and outcome boundaries removed",
    agents=_minimal_agents(),
    implementation_notes=(
        "Frozen-S02 public opening, state mechanics, and priorities. Agent "
        "normative_position, negotiation_boundary, reconsideration_criteria, and "
        "reasoning scripts use the neutral AgentPreset defaults."
    ),
)


def _stakes_agents() -> dict[str, AgentPreset]:
    minimal = _minimal_agents()
    private = {
        "A": (
            "Agent B first raised the odour concern moments ago. The dish is slow-cooked "
            "for a guest arriving in about fifteen minutes; taking it off the heat "
            "early would ruin it. Nobody else in the flat knows about the guest."
        ),
        "B": (
            "This is the first time Agent B has raised the lingering-odour concern with "
            "Agent A. Strong cooking smells give Agent B headaches, which Agent B has "
            "never mentioned to the flatmates."
        ),
        "C": (
            "The rack can be moved to a sheltered spot, but doing so takes effort and "
            "temporarily uses part of the preparation area. Agent C has an online "
            "tutoring session starting in about six minutes in the common area and "
            "needs it quiet; the extractor hum is audible there. The clothes on the "
            "rack are needed dry tomorrow."
        ),
        "D": (
            "Arrived moments ago and did not observe the earlier cooking, but directly "
            "heard Agent A reject Agent D's request to release the stove within two "
            "minutes. Agent D must leave for a night shift in about fifteen minutes and "
            "needs to eat first, which takes about ten minutes at the stove."
        ),
    }
    return {
        agent_id: replace(preset, private_knowledge=private[agent_id])
        for agent_id, preset in minimal.items()
    }


STAKES = replace(
    MINIMAL,
    scenario_id="S13",
    title="Cooking odour, ventilation responsibility, and stove access (private stakes)",
    source_status="S12 plus private stakes and a stove timer the agents control",
    agents=_stakes_agents(),
    implementation_notes=(
        "S12 plus private stakes for every role. No ventilation option is free: "
        "the extractor disturbs C's session, the window needs C's rack moved, and "
        "A's dish needs about ten minutes. The environment reports the remaining "
        "cooking time rather than declaring the dish finished at round 2."
    ),
)


def _clean_agents(with_stakes: bool) -> dict[str, AgentPreset]:
    """Neutral personas whose private facts are practical, not interpretive.

    S02's hints about what each agent would accept are dropped from private
    knowledge. With ``with_stakes`` each role also gets one genuinely private,
    time-bound stake; whether and when to disclose it is the agent's choice.
    """

    facts = {
        "A": "Agent B first raised the odour concern moments ago.",
        "B": (
            "This is the first time Agent B has raised the lingering-odour concern "
            "with Agent A; Agent A explicitly rejected the demand moments ago."
        ),
        "C": (
            "The rack can be moved to a sheltered spot, but doing so takes effort "
            "and temporarily uses part of the preparation area."
        ),
        "D": S02.agents["D"].private_knowledge,
    }
    stakes = {
        "A": (
            " The dish is slow-cooked for a guest arriving in about fifteen minutes; "
            "taking it off the heat early would ruin it. Nobody else knows about the guest."
        ),
        "B": (
            " Strong cooking smells give Agent B headaches, which Agent B has never "
            "mentioned to the flatmates."
        ),
        "C": (
            " Agent C has an online tutoring session starting in about six minutes in "
            "the common area and needs it quiet; the extractor hum is audible there. "
            "The clothes on the rack are needed dry tomorrow."
        ),
        "D": (
            " Agent D must leave for a night shift in about fifteen minutes and needs "
            "to eat first, which takes about ten minutes at the stove."
        ),
    }
    return {
        agent_id: replace(
            preset,
            private_knowledge=facts[agent_id]
            + (stakes[agent_id] if with_stakes else ""),
        )
        for agent_id, preset in _minimal_agents().items()
    }


CLEAN = replace(
    S02,
    scenario_id="S14",
    title="Cooking odour, ventilation responsibility, and stove access (clean)",
    source_status=(
        "S02 opening with no supplied reasoning, no scripted relief, and an "
        "owner-only laundry action"
    ),
    agents=_clean_agents(with_stakes=False),
    round_observations={},
    implementation_notes=(
        "Same public opening as S02. Neutral persona defaults replace supplied "
        "normative positions, boundaries, and reconsideration criteria. The "
        "environment reports only elapsed time and confirmed state: it never "
        "announces that the dish is ready and never narrates the odour fading. "
        "Only the laundry owner can move the rack."
    ),
)

CLEAN_STAKES = replace(
    CLEAN,
    scenario_id="S15",
    title="Cooking odour, ventilation responsibility, and stove access (clean, private stakes)",
    source_status="S14 plus one private time-bound stake per role",
    agents=_clean_agents(with_stakes=True),
    implementation_notes=(
        "S14 plus private stakes: A's guest, B's headaches, C's tutoring session, "
        "and D's shift. Neither ventilating nor not ventilating is free."
    ),
)


# S16 changes exactly one thing relative to S14: each role's ``interaction_style`` is
# replaced by a fuller personality. Traits describe manner of speaking and what the
# person cares about. They are fixed per role, identical in every cultural
# configuration, and deliberately avoid conflict-handling dispositions (no
# "stubborn" or "conciliatory"), though any personality text can still shade outcomes.
PERSONALITIES = {
    "A": (
        "Practical and self-reliant; takes pride in cooking properly and dislikes being "
        "hurried. Explains things through concrete consequences rather than principles. "
        "Gets terse when a request sounds like an order."
    ),
    "B": (
        "Observant and plain-spoken; notices smells, noise and mess quickly and says so "
        "without dressing it up. Cares about shared spaces being comfortable for everyone. "
        "Remembers what people said earlier in the conversation and refers back to it."
    ),
    "C": (
        "Reserved and careful with words; speaks up when something touches their own "
        "things, then says it precisely. Values being asked before anyone handles their "
        "belongings. Dislikes being discussed as if absent."
    ),
    "D": (
        "Busy and time-conscious; asks for specific times and numbers. Friendly but "
        "impatient with open-ended talk when waiting on something. Thinks in terms of "
        "who needs what, and when."
    ),
}

PERSONALITY = replace(
    CLEAN,
    scenario_id="S16",
    title="Cooking odour, ventilation responsibility, and stove access (clean, fuller personality)",
    source_status="S14 with role-fixed personality text in place of the short style",
    agents={
        agent_id: replace(preset, interaction_style=PERSONALITIES[agent_id])
        for agent_id, preset in CLEAN.agents.items()
    },
    implementation_notes=(
        "Identical to S14 except interaction_style. Personality is fixed per role and "
        "must never vary with cultural configuration."
    ),
)


# S17 changes exactly one thing relative to S14: one identical sentence is appended to
# every role's behavioral_guidance. It asks for a stated reason when refusing or
# countering and prescribes no content, position, or outcome. It sits in the scenario
# data, not the shared prompt template, so the agent-prompt hash is unchanged.
REASON_RULE = (
    " When you refuse a request or make a counter-proposal, say briefly why, in "
    "your own words."
)

REASONS = replace(
    CLEAN,
    scenario_id="S17",
    title="Cooking odour, ventilation responsibility, and stove access (clean, brief reasons)",
    source_status="S14 plus one sentence asking for a brief reason when refusing or countering",
    agents={
        agent_id: replace(
            preset, behavioral_guidance=preset.behavioral_guidance + REASON_RULE
        )
        for agent_id, preset in CLEAN.agents.items()
    },
    implementation_notes=(
        "Identical to S14 except one sentence appended to every agent's "
        "behavioral_guidance. The sentence is the same for all roles and all "
        "cultural configurations."
    ),
)


# S18 changes exactly one thing relative to S14: the shared setting states publicly
# that the next cook's dish will smell strongly too, so the odour situation will recur
# within minutes. This gives deferring the ventilation question a practical cost
# without stating any rule, position, or outcome. Nothing in the agents' personas or
# the environment mechanics changes.
RECURRENCE_FACT = (
    " Agent D plans to cook a strongly scented dish on the same stove as soon as it "
    "is free, so the same odour situation will recur within minutes."
)

RECURRENCE = replace(
    CLEAN,
    scenario_id="S18",
    title="Cooking odour, ventilation responsibility, and stove access (clean, recurring odour)",
    source_status="S14 plus a public fact that the next cook's dish will also smell strongly",
    shared_setting=CLEAN.shared_setting + RECURRENCE_FACT,
    implementation_notes=(
        "Identical to S14 except one public sentence appended to the shared setting. "
        "It makes the odour situation recur, so deferring the question has a cost. It "
        "states no rule, position, or outcome."
    ),
)


# S20 = S18 (public recurrence fact) + private stakes for A, B, and C only. D keeps the
# S14 private knowledge, because S15's D stake (night shift needing ten minutes at the
# stove) collided with A's cook time and made "unresolved" partly a timing artifact.
# Each stake is private: whether and when to disclose it is the agent's choice.
_STAKE_AGENTS = _clean_agents(with_stakes=True)

RECURRENCE_STAKES = replace(
    RECURRENCE,
    scenario_id="S20",
    title="Cooking odour, ventilation responsibility, and stove access (recurring odour, private stakes)",
    source_status="S18 plus private stakes for A, B, and C; D unchanged",
    agents={
        "A": _STAKE_AGENTS["A"],
        "B": _STAKE_AGENTS["B"],
        "C": _STAKE_AGENTS["C"],
        "D": CLEAN.agents["D"],
    },
    implementation_notes=(
        "S18 (public fact that the next cook's dish will also smell strongly) plus private "
        "stakes: A's guest, B's headaches, C's tutoring session and the extractor hum. D has "
        "no private stake, to avoid S15's stove-time collision."
    ),
)


# S19 keeps S14's public opening, roles, priorities, and private facts, but removes
# every physical mechanic: no kitchen actions, no confirmed-state reports, and no
# advancing clock. Any settlement therefore has to be reached, and stay, purely in
# conversation. Guidance that names actions (RELEASE_STOVE, extractor, and so on) is
# replaced by the neutral AgentPreset default.
_NEUTRAL_GUIDANCE = AgentPreset.__dataclass_fields__["behavioral_guidance"].default

CONVERSATION_ONLY = replace(
    CLEAN,
    scenario_id="S19",
    title="Cooking odour, ventilation responsibility, and stove access (conversation only)",
    source_status=(
        "S14 opening with no physical actions, no state reports, and no advancing clock"
    ),
    agents={
        agent_id: replace(preset, behavioral_guidance=_NEUTRAL_GUIDANCE)
        for agent_id, preset in CLEAN.agents.items()
    },
    implementation_notes=(
        "Same opening, roles, priorities, and private facts as S14. Agents have no "
        "physical actions, the environment reports no state, and simulated time does "
        "not advance, so anything agreed exists only in the conversation. The shared "
        "prompt's 'a proposed action is not completed unless a later observation "
        "confirms it' still applies and may make agents hedge about their own promises."
    ),
)


for _scenario in (
    MINIMAL,
    STAKES,
    CLEAN,
    CLEAN_STAKES,
    PERSONALITY,
    REASONS,
    RECURRENCE,
    RECURRENCE_STAKES,
    CONVERSATION_ONLY,
):
    validate_scenario(_scenario)


__all__ = [
    "CLEAN",
    "CLEAN_STAKES",
    "CONVERSATION_ONLY",
    "MINIMAL",
    "PERSONALITY",
    "REASONS",
    "RECURRENCE",
    "RECURRENCE_STAKES",
    "STAKES",
]
