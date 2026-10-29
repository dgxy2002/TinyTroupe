"""S05: asking to share a hawker table during the lunch peak."""

from .common import AgentPreset, ScenarioPreset, validate_scenario


SCENARIO = ScenarioPreset(
    scenario_id="S05",
    title="Sharing a hawker table during lunch peak",
    environment="Hawker centre",
    initial_datetime="2026-10-29T12:45:00+08:00",
    source_status="Adapted from the 22 Oct presentation: table sharing",
    initial_interaction_type="Low-intensity interaction; conflict may not occur",
    shared_setting=(
        "A hawker centre during peak lunch. Only a few seats are free. A four-seat table "
        "has one diner, Agent A, whose bag occupies one extra chair and whose meal uses "
        "part of the tabletop. No sign says whether strangers must share tables."
    ),
    shared_trigger=(
        "Agent B approaches with a tray, pauses beside an unused chair, and asks Agent A, "
        "'Excuse me, is this seat free?' Agents C and D are close enough to observe the "
        "request while deciding where to sit."
    ),
    agents={
        "A": AgentPreset(
            age=30,
            role="Solo diner already seated",
            immediate_priority="Finish the meal in relative quiet.",
            private_knowledge="Placed a bag on one extra chair without considering incoming diners.",
            initial_observation="Hears B's question and sees B holding a tray beside the chair.",
        ),
        "B": AgentPreset(
            age=45,
            role="Diner searching for a seat",
            immediate_priority="Sit down before the meal becomes cold.",
            private_knowledge="Does not know whether A minds sharing with a stranger.",
            initial_observation="Sees one unused chair and another occupied by A's bag.",
        ),
        "C": AgentPreset(
            age=23,
            role="Nearby diner carrying a drink",
            immediate_priority="Find a seat but avoid unnecessary confrontation.",
            private_knowledge="Has not decided whether to approach the same table.",
            initial_observation="Hears B ask whether the seat is free.",
        ),
        "D": AgentPreset(
            age=61,
            role="Diner finishing at a neighbouring table",
            immediate_priority="Finish and leave soon.",
            private_knowledge="Has not offered the neighbouring place to anyone.",
            initial_observation="Can see A's table and hear B's request.",
        ),
    },
    observation_focus=(
        "Whether the request leads to accommodation, clarification, refusal, avoidance, "
        "or a conflict-free shared-table arrangement."
    ),
)

validate_scenario(SCENARIO)
