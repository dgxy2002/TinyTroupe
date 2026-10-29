"""S10: constrained access to an MRT doorway before an interchange stop."""

from .common import AgentPreset, ScenarioPreset, validate_scenario


SCENARIO = ScenarioPreset(
    scenario_id="S10",
    title="Access to an MRT doorway with shopping bags",
    environment="MRT carriage approaching an interchange",
    initial_datetime="2026-10-29T17:45:00+08:00",
    source_status="Redesigned extension of public-transport space etiquette",
    initial_interaction_type="Coordination problem; conflict may not occur",
    shared_setting=(
        "A moderately crowded MRT train is a few minutes from a busy interchange. Several "
        "passengers are preparing to alight. Shopping bags on the floor near one doorway "
        "narrow the route but do not fully block it. The doors are still closed, leaving time "
        "for passengers to coordinate before arrival."
    ),
    shared_trigger=(
        "Agent B moves toward the doorway and pauses where Agent D's shopping bags narrow the "
        "path. Agent A is standing beside the door. Agent C is nearby and can see the available "
        "space. All four can speak normally before the train reaches the station."
    ),
    agents={
        "A": AgentPreset(
            age=31,
            role="Passenger standing beside the doorway",
            immediate_priority="Remain on the train while keeping a stable standing position.",
            private_knowledge="Is not sure which nearby passengers intend to alight.",
            initial_observation="Sees B pause near D's bags while the train remains in motion.",
        ),
        "B": AgentPreset(
            age=44,
            role="Passenger preparing to alight",
            immediate_priority="Reach the doorway before the interchange without stepping on anything.",
            private_knowledge="Must leave at the next stop but has not yet said so.",
            initial_observation="Finds the route narrowed by D's bags and A's standing position.",
        ),
        "C": AgentPreset(
            age=20,
            role="Passenger standing near the seating area",
            immediate_priority="Maintain personal space and avoid obstructing anyone who must alight.",
            private_knowledge="Does not know whether A, B, or D will leave at the next stop.",
            initial_observation="Can see B pause and the limited space around the doorway.",
        ),
        "D": AgentPreset(
            age=57,
            role="Passenger travelling with several shopping bags",
            immediate_priority="Keep the bags secure and remain stable while the train is moving.",
            private_knowledge=(
                "Will remain on the train after the interchange and has limited safe places to "
                "move the bags before arrival."
            ),
            initial_observation="Sees B pause near the bags and A standing by the door.",
        ),
    },
    observation_focus=(
        "Whether passengers coordinate space cooperatively, make competing requests, or develop "
        "a disagreement before the stop. A conflict-free adjustment is valid."
    ),
    implementation_notes=(
        "The interaction occurs before arrival; do not hold open train doors for ten rounds or "
        "invent an emergency."
    ),
)

validate_scenario(SCENARIO)
