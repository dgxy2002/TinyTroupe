"""Shared schemas and controlled cultural-background configurations.

Scenario modules deliberately do not contain a cultural-background field. The
field is added only when a C1-C4 run preset is materialized, and is omitted for
C0. This makes it straightforward to verify that background assignment is the
only configured difference between conditions.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime
from typing import Any, Mapping


AGENT_IDS = ("A", "B", "C", "D")
CULTURAL_BACKGROUNDS = (
    "Singaporean Chinese",
    "Singaporean Malay",
    "Singaporean Indian",
    "Singaporean Eurasian",
)

BACKGROUND_CONFIGURATIONS: dict[str, dict[str, str | None]] = {
    "C0": {agent_id: None for agent_id in AGENT_IDS},
    "C1": {
        "A": "Singaporean Chinese",
        "B": "Singaporean Malay",
        "C": "Singaporean Indian",
        "D": "Singaporean Eurasian",
    },
    "C2": {
        "A": "Singaporean Malay",
        "B": "Singaporean Indian",
        "C": "Singaporean Eurasian",
        "D": "Singaporean Chinese",
    },
    "C3": {
        "A": "Singaporean Indian",
        "B": "Singaporean Eurasian",
        "C": "Singaporean Chinese",
        "D": "Singaporean Malay",
    },
    "C4": {
        "A": "Singaporean Eurasian",
        "B": "Singaporean Chinese",
        "C": "Singaporean Malay",
        "D": "Singaporean Indian",
    },
}


@dataclass(frozen=True)
class AgentPreset:
    """Facts supplied only to one agent unless independently observable."""

    age: int
    role: str
    immediate_priority: str
    private_knowledge: str
    initial_observation: str
    interaction_style: str = (
        "Brief and conversational; speak only when directly involved or when adding useful information."
    )
    behavioral_guidance: str = (
        "Reassess your immediate priority when observable facts change; do not keep defending "
        "a practical reason after it is no longer true."
    )
    normative_position: str = (
        "Separate what you personally observed from what you think people ought to do."
    )
    negotiation_boundary: str = (
        "You may revise a position when its practical cost is addressed, but do not agree "
        "merely to end the conversation."
    )
    reconsideration_criteria: str = (
        "Change or soften your position only when a new observed fact, a relevant reason, or "
        "a concrete proposal addresses the basis for it; politeness and repetition alone are "
        "not reasons to agree."
    )


@dataclass(frozen=True)
class ScenarioPreset:
    """One background-neutral scenario shared across C0-C4."""

    scenario_id: str
    title: str
    environment: str
    initial_datetime: str
    source_status: str
    initial_interaction_type: str
    shared_setting: str
    shared_trigger: str
    agents: Mapping[str, AgentPreset]
    observation_focus: str
    implementation_notes: str = ""
    round_observations: Mapping[int, str] = field(default_factory=dict)


def validate_scenario(scenario: ScenarioPreset) -> None:
    """Fail fast when an editable scenario preset is structurally incomplete."""

    if set(scenario.agents) != set(AGENT_IDS):
        raise ValueError(
            f"{scenario.scenario_id} must define exactly agents {AGENT_IDS}."
        )
    if not scenario.scenario_id.startswith("S") or len(scenario.scenario_id) != 3:
        raise ValueError("scenario_id must use the S01-S99 form.")
    parsed_datetime = datetime.fromisoformat(scenario.initial_datetime)
    if parsed_datetime.tzinfo is None:
        raise ValueError("initial_datetime must include an explicit UTC offset.")
    for round_number, observation in scenario.round_observations.items():
        if round_number < 2 or not observation.strip():
            raise ValueError(
                "round_observations must contain non-empty updates for round 2 or later."
            )
    for agent_id, agent in scenario.agents.items():
        if agent.age < 18:
            raise ValueError(f"{scenario.scenario_id}-{agent_id} must be an adult.")
        for field_name, value in asdict(agent).items():
            if value is None or (isinstance(value, str) and not value.strip()):
                raise ValueError(
                    f"{scenario.scenario_id}-{agent_id}.{field_name} is empty."
                )


def materialize_configuration(
    scenario: ScenarioPreset, config_id: str
) -> dict[str, Any]:
    """Return a serializable run preset with the requested background rotation.

    C0 does not contain a ``cultural_background`` key. C1-C4 add exactly one
    background label to each agent without changing any other scenario field.
    """

    validate_scenario(scenario)
    try:
        assignments = BACKGROUND_CONFIGURATIONS[config_id]
    except KeyError as exc:
        expected = ", ".join(BACKGROUND_CONFIGURATIONS)
        raise KeyError(f"Unknown configuration {config_id!r}; expected {expected}.") from exc

    payload = asdict(scenario)
    payload["configuration_id"] = config_id
    for agent_id, cultural_background in assignments.items():
        if cultural_background is not None:
            payload["agents"][agent_id]["cultural_background"] = cultural_background
    return payload


def _validate_background_design() -> None:
    for config_id, assignments in BACKGROUND_CONFIGURATIONS.items():
        if set(assignments) != set(AGENT_IDS):
            raise ValueError(f"{config_id} does not assign all four agent slots.")
        values = tuple(assignments.values())
        if config_id == "C0" and any(value is not None for value in values):
            raise ValueError("C0 must omit all cultural-background labels.")
        if config_id != "C0" and set(values) != set(CULTURAL_BACKGROUNDS):
            raise ValueError(f"{config_id} must use each background exactly once.")

    for agent_id in AGENT_IDS:
        assigned = {
            BACKGROUND_CONFIGURATIONS[config_id][agent_id]
            for config_id in ("C1", "C2", "C3", "C4")
        }
        if assigned != set(CULTURAL_BACKGROUNDS):
            raise ValueError(f"Background rotation is not balanced for Agent {agent_id}.")


_validate_background_design()


__all__ = [
    "AGENT_IDS",
    "AgentPreset",
    "BACKGROUND_CONFIGURATIONS",
    "CULTURAL_BACKGROUNDS",
    "ScenarioPreset",
    "materialize_configuration",
    "validate_scenario",
]
