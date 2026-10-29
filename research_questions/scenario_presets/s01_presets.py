"""S01: late-night audio outside neighbouring HDB units."""

from .common import AgentPreset, ScenarioPreset, validate_scenario


SCENARIO = ScenarioPreset(
    scenario_id="S01",
    title="Late-night noise outside HDB units",
    environment="HDB shared corridor",
    initial_datetime="2026-10-29T22:45:00+08:00",
    source_status="Adapted from the 22 Oct presentation: late-night noise",
    initial_interaction_type="Potential conflict",
    shared_setting=(
        "An HDB corridor at 10:45 p.m. Two neighbouring households are close "
        "enough that sound from one open doorway is clearly audible in the "
        "corridor, although it does not prevent ordinary conversation. Everyone "
        "is physically present in or near the corridor. No property manager or "
        "authority figure is present."
    ),
    shared_trigger=(
        "Agent A is beside the open doorway with a game or video playing through "
        "a speaker. Agent B steps into the corridor and approaches the doorway. "
        "Agents C and D are close enough to see and hear the encounter from that "
        "point onward."
    ),
    agents={
        "A": AgentPreset(
            age=29,
            role="Resident listening to audio after a late shift",
            immediate_priority="Have some downtime before resting.",
            private_knowledge="Does not know how far the audio carries beyond the doorway.",
            initial_observation="Sees B approach while the audio continues playing.",
        ),
        "B": AgentPreset(
            age=43,
            role="Neighbour preparing for an early start",
            immediate_priority="Get uninterrupted rest before the next morning.",
            private_knowledge="Is unsure whether A realizes the audio is audible nearby.",
            initial_observation="Can clearly hear A's audio from near B's own doorway.",
        ),
        "C": AgentPreset(
            age=37,
            role="Another resident in the same corridor",
            immediate_priority="Avoid becoming involved unless intervention seems necessary.",
            private_knowledge="Has heard the audio intermittently during the evening.",
            initial_observation="Notices B approach A's open doorway.",
        ),
        "D": AgentPreset(
            age=25,
            role="Housemate of Agent A",
            immediate_priority="Wind down and go to bed soon.",
            private_knowledge=(
                "Knows A had a tiring shift but cannot know how the sound is experienced "
                "inside B's unit."
            ),
            initial_observation="Is near A's doorway and sees B approach.",
        ),
    },
    observation_focus=(
        "Whether a request is made; directness, acknowledgement, withdrawal, and "
        "possible follow-up."
    ),
)

validate_scenario(SCENARIO)
