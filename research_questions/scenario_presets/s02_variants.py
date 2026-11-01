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


for _scenario in (MINIMAL, STAKES, CLEAN, CLEAN_STAKES):
    validate_scenario(_scenario)


__all__ = ["CLEAN", "CLEAN_STAKES", "MINIMAL", "STAKES"]
