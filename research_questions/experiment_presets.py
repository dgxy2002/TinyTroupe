"""Experiment-level presets for runs, repetitions, and round horizons.

Scenario content belongs in ``scenario_presets/``. This module controls only
which scenario/configuration pairs run, how often they repeat, how many timed
intervals each run receives, and which conversation controller is used.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterator

from .scenario_presets import BACKGROUND_CONFIGURATIONS, SCENARIOS


ALL_SCENARIO_IDS = tuple(SCENARIOS)
ALL_CONFIGURATION_IDS = tuple(BACKGROUND_CONFIGURATIONS)
DEFAULT_ROUNDS_PER_RUN = 10


@dataclass(frozen=True)
class ExperimentPreset:
    """A reproducible selection of scenario runs."""

    name: str
    scenario_ids: tuple[str, ...]
    configuration_ids: tuple[str, ...]
    repetitions_per_configuration: int
    rounds_per_run: int = DEFAULT_ROUNDS_PER_RUN
    stop_on_resolution: bool = False
    evaluate_after_run: bool = True
    randomize_agent_order: bool = False
    parallelize_agent_actions: bool = False
    conversation_mode: str = "fixed_round_robin"
    description: str = ""

    @property
    def total_runs(self) -> int:
        return (
            len(self.scenario_ids)
            * len(self.configuration_ids)
            * self.repetitions_per_configuration
        )

    @property
    def total_simulation_rounds(self) -> int:
        return self.total_runs * self.rounds_per_run


@dataclass(frozen=True)
class RunSpec:
    """One independent simulation run generated from an experiment preset."""

    run_id: str
    experiment_name: str
    scenario_id: str
    configuration_id: str
    repetition: int
    rounds: int
    stop_on_resolution: bool
    evaluate_after_run: bool
    randomize_agent_order: bool
    parallelize_agent_actions: bool
    conversation_mode: str = "fixed_round_robin"


CALIBRATION_S04_PRESET = ExperimentPreset(
    name="calibration-s04",
    scenario_ids=("S04",),
    configuration_ids=("C0",),
    repetitions_per_configuration=1,
    rounds_per_run=6,
    description=(
        "Calibration run for scenario grounding, natural dialogue, and the "
        "peak-versus-remaining conflict evaluator. Not confirmatory research data."
    ),
)

CALIBRATION_S04_LONG_PRESET = ExperimentPreset(
    name="calibration-s04-long",
    scenario_ids=("S04",),
    configuration_ids=("C0",),
    repetitions_per_configuration=1,
    rounds_per_run=10,
    description=(
        "Ten-round S04 horizon diagnostic with no additional scripted events after "
        "round 6. Tests whether extra interaction produces insight or merely repetition."
    ),
)

CALIBRATION_S04_HYBRID_PRESET = ExperimentPreset(
    name="calibration-s04-hybrid",
    scenario_ids=("S04",),
    configuration_ids=("C0",),
    repetitions_per_configuration=1,
    rounds_per_run=6,
    conversation_mode="hybrid_self_selection",
    description=(
        "Six-interval S04 calibration using direct-reply priority and deterministic "
        "self-selection instead of a mandatory four-agent round robin."
    ),
)

CALIBRATION_S02_S06_PRESET = ExperimentPreset(
    name="calibration-s02-s06",
    scenario_ids=("S02", "S06"),
    configuration_ids=("C0",),
    repetitions_per_configuration=1,
    rounds_per_run=6,
    description=(
        "Six-round C0 calibration for the stateful shared-kitchen and ambiguous-order "
        "scenarios. Not confirmatory research data."
    ),
)

CALIBRATION_S02_PRESET = ExperimentPreset(
    name="calibration-s02",
    scenario_ids=("S02",),
    configuration_ids=("C0",),
    repetitions_per_configuration=1,
    rounds_per_run=6,
    description="Six-round stateful C0 shared-kitchen calibration.",
)

CALIBRATION_S06_PRESET = ExperimentPreset(
    name="calibration-s06",
    scenario_ids=("S06",),
    configuration_ids=("C0",),
    repetitions_per_configuration=1,
    rounds_per_run=4,
    description="Four-round stateful C0 ambiguous-order calibration.",
)

SMOKE_PRESET = ExperimentPreset(
    name="smoke",
    scenario_ids=("S04",),
    configuration_ids=("C0",),
    repetitions_per_configuration=1,
    rounds_per_run=1,
    description=(
        "Non-research structural check for agent construction, transcript capture, "
        "and evaluator wiring."
    ),
)

FOCUSED_PILOT_PRESET = ExperimentPreset(
    name="focused-pilot",
    scenario_ids=("S02", "S04", "S06"),
    configuration_ids=ALL_CONFIGURATION_IDS,
    repetitions_per_configuration=3,
    rounds_per_run=10,
    description=(
        "Initial 45-run pilot covering a multi-issue case, a local-norm case, "
        "and a controlled misunderstanding case."
    ),
)

FULL_PILOT_PRESET = ExperimentPreset(
    name="full-pilot",
    scenario_ids=ALL_SCENARIO_IDS,
    configuration_ids=ALL_CONFIGURATION_IDS,
    repetitions_per_configuration=3,
    rounds_per_run=10,
    description="All 10 scenarios × 5 configurations × 3 repetitions = 150 runs.",
)

EXPANDED_PRESET = ExperimentPreset(
    name="expanded",
    scenario_ids=ALL_SCENARIO_IDS,
    configuration_ids=ALL_CONFIGURATION_IDS,
    repetitions_per_configuration=5,
    rounds_per_run=10,
    description="All 10 scenarios × 5 configurations × 5 repetitions = 250 runs.",
)

EXPERIMENT_PRESETS = {
    preset.name: preset
    for preset in (
        CALIBRATION_S04_PRESET,
        CALIBRATION_S04_LONG_PRESET,
        CALIBRATION_S04_HYBRID_PRESET,
        CALIBRATION_S02_S06_PRESET,
        CALIBRATION_S02_PRESET,
        CALIBRATION_S06_PRESET,
        SMOKE_PRESET,
        FOCUSED_PILOT_PRESET,
        FULL_PILOT_PRESET,
        EXPANDED_PRESET,
    )
}


def validate_experiment_preset(preset: ExperimentPreset) -> None:
    """Validate selections and the fixed-horizon post-run evaluation design."""

    unknown_scenarios = set(preset.scenario_ids) - set(SCENARIOS)
    if unknown_scenarios:
        raise ValueError(f"Unknown scenarios: {sorted(unknown_scenarios)}")

    unknown_configs = set(preset.configuration_ids) - set(
        BACKGROUND_CONFIGURATIONS
    )
    if unknown_configs:
        raise ValueError(f"Unknown configurations: {sorted(unknown_configs)}")

    if len(set(preset.scenario_ids)) != len(preset.scenario_ids):
        raise ValueError("scenario_ids must not contain duplicates.")
    if len(set(preset.configuration_ids)) != len(preset.configuration_ids):
        raise ValueError("configuration_ids must not contain duplicates.")
    if preset.repetitions_per_configuration < 1:
        raise ValueError("repetitions_per_configuration must be positive.")
    if preset.rounds_per_run < 1:
        raise ValueError("rounds_per_run must be positive.")
    if preset.stop_on_resolution:
        raise ValueError("This protocol must not stop when conflict resolves.")
    if not preset.evaluate_after_run:
        raise ValueError("This protocol evaluates each transcript after its run.")
    if preset.conversation_mode not in {
        "fixed_round_robin",
        "hybrid_self_selection",
    }:
        raise ValueError(f"Unknown conversation_mode: {preset.conversation_mode}")


def iter_run_specs(preset: ExperimentPreset) -> Iterator[RunSpec]:
    """Yield stable Sxx-Cx-Rxx run specifications in scenario-major order."""

    validate_experiment_preset(preset)
    width = max(2, len(str(preset.repetitions_per_configuration)))
    for scenario_id in preset.scenario_ids:
        for configuration_id in preset.configuration_ids:
            for repetition in range(1, preset.repetitions_per_configuration + 1):
                yield RunSpec(
                    run_id=(
                        f"{scenario_id}-{configuration_id}-"
                        f"R{repetition:0{width}d}"
                    ),
                    experiment_name=preset.name,
                    scenario_id=scenario_id,
                    configuration_id=configuration_id,
                    repetition=repetition,
                    rounds=preset.rounds_per_run,
                    stop_on_resolution=preset.stop_on_resolution,
                    evaluate_after_run=preset.evaluate_after_run,
                    randomize_agent_order=preset.randomize_agent_order,
                    parallelize_agent_actions=preset.parallelize_agent_actions,
                    conversation_mode=preset.conversation_mode,
                )


def get_experiment_preset(name: str) -> ExperimentPreset:
    """Return one named experiment preset."""

    try:
        return EXPERIMENT_PRESETS[name.lower()]
    except KeyError as exc:
        expected = ", ".join(EXPERIMENT_PRESETS)
        raise KeyError(f"Unknown experiment preset {name!r}; expected {expected}.") from exc


for _preset in EXPERIMENT_PRESETS.values():
    validate_experiment_preset(_preset)


__all__ = [
    "ALL_CONFIGURATION_IDS",
    "ALL_SCENARIO_IDS",
    "CALIBRATION_S04_PRESET",
    "CALIBRATION_S04_LONG_PRESET",
    "CALIBRATION_S04_HYBRID_PRESET",
    "CALIBRATION_S02_S06_PRESET",
    "CALIBRATION_S02_PRESET",
    "CALIBRATION_S06_PRESET",
    "DEFAULT_ROUNDS_PER_RUN",
    "EXPERIMENT_PRESETS",
    "EXPANDED_PRESET",
    "ExperimentPreset",
    "FOCUSED_PILOT_PRESET",
    "FULL_PILOT_PRESET",
    "RunSpec",
    "SMOKE_PRESET",
    "get_experiment_preset",
    "iter_run_specs",
    "validate_experiment_preset",
]
