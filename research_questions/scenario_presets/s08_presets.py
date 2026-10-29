"""S08: audible phone video on an MRT train."""

from .common import AgentPreset, ScenarioPreset, validate_scenario


SCENARIO = ScenarioPreset(
    scenario_id="S08",
    title="Loud video audio on an MRT train",
    environment="MRT carriage",
    initial_datetime="2026-10-29T15:00:00+08:00",
    source_status="Adapted from the 22 Oct presentation: audio without headphones",
    initial_interaction_type="Potential conflict",
    shared_setting=(
        "An MRT carriage during a weekday afternoon journey. Passengers are seated and "
        "standing close together. A phone video is clearly audible to the nearby passengers "
        "but does not drown out ordinary speech or train announcements."
    ),
    shared_trigger=(
        "Agent A watches the video through the phone speaker. Agent B is seated nearby with "
        "reading material. Agent C stands between the seating areas, and Agent D travels with A."
    ),
    agents={
        "A": AgentPreset(
            age=24,
            role="Passenger watching a video",
            immediate_priority="Stay entertained during the commute.",
            private_knowledge="Does not know whether any nearby passenger is bothered.",
            initial_observation="Can hear the video and sees B reading nearby.",
        ),
        "B": AgentPreset(
            age=36,
            role="Passenger trying to read",
            immediate_priority="Have a sufficiently quiet journey to continue reading.",
            private_knowledge="Has not decided whether to address A or take another action.",
            initial_observation="Can clearly hear A's video from the nearby seat.",
        ),
        "C": AgentPreset(
            age=55,
            role="Standing commuter",
            immediate_priority="Travel without unnecessary disruption.",
            private_knowledge="Does not know whether B will react or whether A has headphones.",
            initial_observation="Can hear the video while positioned near both A and B.",
        ),
        "D": AgentPreset(
            age=27,
            role="Passenger travelling with Agent A",
            immediate_priority="Have an uneventful journey.",
            private_knowledge="Knows A socially but is not responsible for A's choices.",
            initial_observation="Can hear the video and see the nearby passengers.",
        ),
    },
    observation_focus=(
        "Whether annoyance becomes an expressed disagreement, indirect accommodation, or no conflict."
    ),
)

validate_scenario(SCENARIO)
