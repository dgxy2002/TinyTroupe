"""S07: table availability and an unreturned tray."""

from .common import AgentPreset, ScenarioPreset, validate_scenario


SCENARIO = ScenarioPreset(
    scenario_id="S07",
    title="Table availability and an unreturned tray",
    environment="Hawker centre",
    initial_datetime="2026-10-29T14:00:00+08:00",
    source_status="Controlled extension of hawker-centre etiquette",
    initial_interaction_type="Potential low-intensity conflict",
    shared_setting=(
        "At a hawker centre after the lunch rush, one table is becoming free. Agent A has "
        "stood up, but A's used tray and plates remain on the tabletop. A tray-return station "
        "is visible elsewhere in the seating area."
    ),
    shared_trigger=(
        "Agent A turns to leave as Agent B approaches the table carrying food. Agent C is "
        "seated nearby. Agent D passes while carrying D's own used tray toward the return station."
    ),
    agents={
        "A": AgentPreset(
            age=39,
            role="Diner who has finished eating",
            immediate_priority="Leave promptly for the next commitment.",
            private_knowledge="Has not made a plan to take the tray to the return station.",
            initial_observation="Sees B approaching the table while turning away.",
        ),
        "B": AgentPreset(
            age=21,
            role="Incoming diner carrying food",
            immediate_priority="Use a clear surface and sit before the food cools.",
            private_knowledge="Does not know whether A intends to return for the tray.",
            initial_observation="Finds A standing up while the used tray remains on the table.",
        ),
        "C": AgentPreset(
            age=54,
            role="Nearby diner",
            immediate_priority="Continue the meal without becoming unnecessarily involved.",
            private_knowledge="Saw A finish eating and stand but cannot know A's next intention.",
            initial_observation="Sees B arrive with food as A turns away.",
        ),
        "D": AgentPreset(
            age=47,
            role="Diner returning a personal tray",
            immediate_priority="Return the personal tray and continue on the way.",
            private_knowledge="Has no staff role or authority over the other diners.",
            initial_observation="Passes the table carrying a separate used tray toward the station.",
        ),
    },
    observation_focus=(
        "Whether tray-return norms are mentioned and how responsibility is negotiated, without "
        "assigning authority to a bystander."
    ),
)

validate_scenario(SCENARIO)
