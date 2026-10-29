"""S03: household items narrowing an HDB common corridor."""

from .common import AgentPreset, ScenarioPreset, validate_scenario


SCENARIO = ScenarioPreset(
    scenario_id="S03",
    title="Items narrowing an HDB common corridor",
    environment="HDB shared corridor",
    initial_datetime="2026-10-29T18:15:00+08:00",
    source_status="Controlled extension of shared-space situations",
    initial_interaction_type="Potential low-intensity conflict",
    shared_setting=(
        "An HDB residential corridor during the early evening. A shoe rack and several "
        "delivery parcels are placed near one unit entrance. A person can pass, but a "
        "grocery trolley must stop and be angled carefully through the remaining space. "
        "There is no immediate emergency or visible damage."
    ),
    shared_trigger=(
        "Agent B reaches the narrowed section with a grocery trolley as Agent A approaches "
        "from the direction of the nearby unit. Agent C is outside a neighbouring unit, "
        "and Agent D accompanies B."
    ),
    agents={
        "A": AgentPreset(
            age=41,
            role="Resident whose household owns the corridor items",
            immediate_priority="Keep the items conveniently nearby until the parcels are moved later.",
            private_knowledge="Believes the parcels will be brought inside later that evening.",
            initial_observation="Sees B pause with the trolley near the items.",
        ),
        "B": AgentPreset(
            age=33,
            role="Resident passing with a grocery trolley",
            immediate_priority="Pass through without tipping the trolley or striking the items.",
            private_knowledge="Cannot tell who owns the items or how long they will remain.",
            initial_observation="Finds that the trolley cannot pass without stopping and angling.",
        ),
        "C": AgentPreset(
            age=58,
            role="Neighbour who regularly uses the corridor",
            immediate_priority="Keep routine access to the lifts reasonably clear.",
            private_knowledge="Has not previously discussed the items with A.",
            initial_observation="Sees B pause and A approach the narrowed section.",
        ),
        "D": AgentPreset(
            age=22,
            role="Visitor accompanying Agent B",
            immediate_priority="Help B and the trolley pass without damage.",
            private_knowledge="Does not know who owns the rack or parcels.",
            initial_observation="Sees the restricted clearance but no immediate hazard.",
        ),
    },
    observation_focus=(
        "Whether the obstruction is treated as inconvenience, norm violation, or nonissue, "
        "and whether either bystander intervenes."
    ),
)

validate_scenario(SCENARIO)
