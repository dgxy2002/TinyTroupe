"""S09: competing but partly hidden priority-seat needs."""

from .common import AgentPreset, ScenarioPreset, validate_scenario


SCENARIO = ScenarioPreset(
    scenario_id="S09",
    title="Priority-seat expectations on the MRT",
    environment="Crowded MRT carriage",
    initial_datetime="2026-10-29T17:30:00+08:00",
    source_status="Adapted from the 22 Oct presentation: priority seats",
    initial_interaction_type="Potential conflict or silent accommodation",
    shared_setting=(
        "A crowded MRT carriage has one occupied priority seat and several standing passengers. "
        "The seated passenger has no visible mobility aid or outward sign of discomfort. An "
        "older commuter boards and stands near the seating area."
    ),
    shared_trigger=(
        "Agent B, the older commuter, takes hold of a nearby pole beside Agent A's priority seat. "
        "Agent C stands close enough to notice the arrangement. Agent D occupies an ordinary "
        "seat nearby and can observe what happens."
    ),
    agents={
        "A": AgentPreset(
            age=26,
            role="Passenger seated in a priority seat",
            immediate_priority="Remain seated long enough to recover from substantial fatigue.",
            private_knowledge=(
                "The fatigue is genuine but not visually obvious and has not been disclosed to anyone."
            ),
            initial_observation="Sees B board and stand nearby while holding the pole.",
        ),
        "B": AgentPreset(
            age=69,
            role="Older commuter who has just boarded",
            immediate_priority="Maintain a stable position during the journey.",
            private_knowledge="Has not asked anyone for a seat and does not know A's condition.",
            initial_observation="Sees A in the priority seat and D in an ordinary seat.",
        ),
        "C": AgentPreset(
            age=38,
            role="Standing commuter nearby",
            immediate_priority="Travel safely while deciding whether any response is warranted.",
            private_knowledge="Cannot know A's hidden fatigue or B's exact level of need.",
            initial_observation="Notices B standing beside A's priority seat.",
        ),
        "D": AgentPreset(
            age=48,
            role="Commuter seated in an ordinary seat",
            immediate_priority="Continue the journey, with the option to offer the seat voluntarily.",
            private_knowledge="Has no obligation or authority to direct A or B.",
            initial_observation="Can see A seated and B holding the nearby pole.",
        ),
    },
    observation_focus=(
        "Whether assumptions about need are voiced, a bystander intervenes, or accommodation "
        "occurs without confrontation."
    ),
    implementation_notes="Do not invent a diagnosis for Agent A or Agent B.",
)

validate_scenario(SCENARIO)
