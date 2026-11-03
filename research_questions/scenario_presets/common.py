"""Shared schemas and controlled cultural-background configurations.

Scenario modules deliberately do not contain a cultural-background field. The
materializer controls background labels and display names for both the standard
C0-C4 rotations and the exploratory factorial screen.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime
import re
from typing import Any, Mapping


AGENT_IDS = ("A", "B", "C", "D")
AGENT_DISPLAY_NAMES = {
    "A": "Alex",
    "B": "Jamie",
    "C": "Casey",
    "D": "Robin",
}
CULTURAL_DISPLAY_NAMES = {
    "Singaporean Chinese": "John",
    "Singaporean Malay": "Fatimah",
    "Singaporean Indian": "Arjun",
    "Singaporean Eurasian": "Michelle",
}
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

# Two-by-two exploratory treatment using the C1 role/background allocation.
# The first bit controls explicit cultural-background fields; the second controls
# culturally associated display names.
FACTORIAL_CONFIGURATIONS = {
    "F00": {"background_labels": False, "cultural_names": False},
    "F10": {"background_labels": True, "cultural_names": False},
    "F01": {"background_labels": False, "cultural_names": True},
    "F11": {"background_labels": True, "cultural_names": True},
}
MATERIALIZATION_CONFIGURATION_IDS = (
    *BACKGROUND_CONFIGURATIONS,
    *FACTORIAL_CONFIGURATIONS,
)


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
    # Empty means free resolution: agents are told no agreement is required. Non-empty
    # text is shown identically to every agent and replaces that sentence. Resolution-
    # expected scenarios must not be pooled with free-resolution ones.
    resolution_expectation: str = ""
    # True removes timing cues from the shared prompt (the clock line, the "five minutes"
    # example, and the time-estimate guidance). Scenario text must be timing-free too.
    timing_free: bool = False
    # True makes the interaction speech-only in the shared prompt: physical-action wording
    # is dropped and spoken commitments count. Combined with a resolution expectation it
    # also replaces the 'priority is a hard constraint' rule with a priced-preference rule.
    conversation_only: bool = False


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

    C0 does not contain a ``cultural_background`` key and uses neutral names.
    C1-C4 add one background label and its associated name to each agent. The
    Fxx cells independently switch labels and associated names using C1 roles.
    """

    validate_scenario(scenario)
    if config_id in BACKGROUND_CONFIGURATIONS:
        assignments = BACKGROUND_CONFIGURATIONS[config_id]
        name_assignments = assignments
        factorial_treatment = None
    elif config_id in FACTORIAL_CONFIGURATIONS:
        factorial_treatment = FACTORIAL_CONFIGURATIONS[config_id]
        c1_assignments = BACKGROUND_CONFIGURATIONS["C1"]
        assignments = (
            c1_assignments
            if factorial_treatment["background_labels"]
            else BACKGROUND_CONFIGURATIONS["C0"]
        )
        name_assignments = (
            c1_assignments
            if factorial_treatment["cultural_names"]
            else BACKGROUND_CONFIGURATIONS["C0"]
        )
    else:
        expected = ", ".join(MATERIALIZATION_CONFIGURATION_IDS)
        raise KeyError(f"Unknown configuration {config_id!r}; expected {expected}.")

    display_names = {
        agent_id: (
            AGENT_DISPLAY_NAMES[agent_id]
            if cultural_background is None
            else CULTURAL_DISPLAY_NAMES[cultural_background]
        )
        for agent_id, cultural_background in name_assignments.items()
    }
    payload = _render_agent_display_names(asdict(scenario), display_names)
    payload["configuration_id"] = config_id
    if factorial_treatment is not None:
        payload["factorial_treatment"] = {
            **factorial_treatment,
            "background_rotation": "C1",
        }
    for agent_id, cultural_background in assignments.items():
        payload["agents"][agent_id]["display_name"] = display_names[agent_id]
        if cultural_background is not None:
            payload["agents"][agent_id]["cultural_background"] = cultural_background
    return payload


def _render_agent_display_names(
    value: Any, display_names: Mapping[str, str]
) -> Any:
    """Replace explicit role labels while preserving A-D analysis keys.

    Bare ``A`` is ambiguous with the English article, so scenario prose must use
    ``Agent A`` (or ``Agents A and D``) when it means a participant.
    """

    if isinstance(value, str):
        rendered = value
        plural_pattern = re.compile(r"\bAgents ([A-D]) and ([A-D])\b")
        rendered = plural_pattern.sub(
            lambda match: (
                f"{display_names[match.group(1)]} and "
                f"{display_names[match.group(2)]}"
            ),
            rendered,
        )
        for agent_id, display_name in display_names.items():
            rendered = rendered.replace(f"Agent {agent_id}", display_name)
        return rendered
    if isinstance(value, dict):
        return {
            key: _render_agent_display_names(item, display_names)
            for key, item in value.items()
        }
    if isinstance(value, list):
        return [_render_agent_display_names(item, display_names) for item in value]
    if isinstance(value, tuple):
        return tuple(
            _render_agent_display_names(item, display_names) for item in value
        )
    return value


def _validate_background_design() -> None:
    if set(CULTURAL_DISPLAY_NAMES) != set(CULTURAL_BACKGROUNDS):
        raise ValueError("Every cultural background must have one associated display name.")
    if len(set(CULTURAL_DISPLAY_NAMES.values())) != len(CULTURAL_DISPLAY_NAMES):
        raise ValueError("Cultural display names must be unique.")
    if set(FACTORIAL_CONFIGURATIONS) != {"F00", "F10", "F01", "F11"}:
        raise ValueError("Factorial configurations must define the complete two-by-two design.")

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
    "AGENT_DISPLAY_NAMES",
    "AgentPreset",
    "BACKGROUND_CONFIGURATIONS",
    "CULTURAL_DISPLAY_NAMES",
    "FACTORIAL_CONFIGURATIONS",
    "MATERIALIZATION_CONFIGURATION_IDS",
    "CULTURAL_BACKGROUNDS",
    "ScenarioPreset",
    "materialize_configuration",
    "validate_scenario",
]
