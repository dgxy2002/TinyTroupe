"""Experiment-level presets for runs, repetitions, and round horizons.

Scenario content belongs in ``scenario_presets/``. This module controls only
which scenario/configuration pairs run, how often they repeat, how many timed
intervals each run receives, and which conversation controller is used.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterator

from .scenario_presets import (
    BACKGROUND_CONFIGURATIONS,
    FACTORIAL_CONFIGURATIONS,
    MATERIALIZATION_CONFIGURATION_IDS,
    RUNNABLE_SCENARIOS,
    SCENARIOS,
)


ALL_SCENARIO_IDS = tuple(SCENARIOS)
ALL_CONFIGURATION_IDS = tuple(BACKGROUND_CONFIGURATIONS)
FACTORIAL_CONFIGURATION_IDS = tuple(FACTORIAL_CONFIGURATIONS)
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
    # True adds a private per-agent debrief after evaluation. Stored separately; neither
    # the agents nor the evaluator ever see it.
    debrief_after_run: bool = False

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

CALIBRATION_S04_CULTURAL_PRESET = ExperimentPreset(
    name="calibration-s04-cultural",
    scenario_ids=("S04",),
    configuration_ids=ALL_CONFIGURATION_IDS,
    repetitions_per_configuration=1,
    rounds_per_run=6,
    conversation_mode="hybrid_self_selection",
    description=(
        "Exploratory S04 batch across C0-C4 using neutral C0 names and "
        "background-associated C1-C4 names, the same six timed intervals, and the "
        "deterministic hybrid controller."
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

CALIBRATION_S02_EXPLICIT_PRESET = ExperimentPreset(
    name="calibration-s02-explicit",
    scenario_ids=("S02",),
    configuration_ids=("C0",),
    repetitions_per_configuration=1,
    rounds_per_run=6,
    conversation_mode="hybrid_self_selection",
    description=(
        "One six-interval C0 diagnostic beginning from an explicit, already-active "
        "shared-kitchen conflict."
    ),
)

CALIBRATION_S02_MINIMAL_PRESET = ExperimentPreset(
    name="calibration-s02-minimal",
    scenario_ids=("S12",),
    configuration_ids=("C0",),
    repetitions_per_configuration=1,
    rounds_per_run=6,
    conversation_mode="hybrid_self_selection",
    description=(
        "S02 ablation with supplied normative positions, negotiation boundaries, and "
        "reconsideration criteria removed. Calibration only."
    ),
)

CALIBRATION_S02_STAKES_PRESET = ExperimentPreset(
    name="calibration-s02-stakes",
    scenario_ids=("S13",),
    configuration_ids=("C0",),
    repetitions_per_configuration=1,
    rounds_per_run=6,
    conversation_mode="hybrid_self_selection",
    description=(
        "Minimal-facts S02 plus private stakes. Calibration only."
    ),
)

CALIBRATION_S02_CLEAN_PRESET = ExperimentPreset(
    name="calibration-s02-clean",
    scenario_ids=("S14",),
    configuration_ids=ALL_CONFIGURATION_IDS,
    repetitions_per_configuration=1,
    rounds_per_run=6,
    conversation_mode="hybrid_self_selection",
    description=(
        "Clean S02 variant (no supplied reasoning or scripted relief, owner-only laundry "
        "action) across C0-C4. One screening run per configuration; calibration only."
    ),
)

CALIBRATION_S02_CLEAN_STAKES_PRESET = ExperimentPreset(
    name="calibration-s02-clean-stakes",
    scenario_ids=("S15",),
    configuration_ids=ALL_CONFIGURATION_IDS,
    repetitions_per_configuration=1,
    rounds_per_run=6,
    conversation_mode="hybrid_self_selection",
    description=(
        "Clean S02 variant plus private time-bound stakes across C0-C4. One screening "
        "run per configuration; calibration only."
    ),
)

CALIBRATION_S02_PERSONALITY_PRESET = ExperimentPreset(
    name="calibration-s02-personality",
    scenario_ids=("S16",),
    configuration_ids=("C0",),
    repetitions_per_configuration=5,
    rounds_per_run=6,
    conversation_mode="hybrid_self_selection",
    description=(
        "S14 with role-fixed fuller personality text as the only change, C0 only, five "
        "repetitions. Compare against calibration-s02-clean at C0. Calibration only."
    ),
)

CALIBRATION_S02_REASONS_PRESET = ExperimentPreset(
    name="calibration-s02-reasons",
    scenario_ids=("S17",),
    configuration_ids=("C0",),
    repetitions_per_configuration=5,
    rounds_per_run=6,
    conversation_mode="hybrid_self_selection",
    description=(
        "S14 plus one sentence asking for a brief reason when refusing or countering, "
        "C0 only, five repetitions. Compare against calibration-s02-clean at C0. "
        "Calibration only."
    ),
)

CALIBRATION_S02_RECURRENCE_PRESET = ExperimentPreset(
    name="calibration-s02-recurrence",
    scenario_ids=("S18",),
    configuration_ids=("C0",),
    repetitions_per_configuration=5,
    rounds_per_run=6,
    conversation_mode="hybrid_self_selection",
    description=(
        "S14 plus a public fact that the next cook's dish will also smell strongly, "
        "C0 only, five repetitions. Compare against calibration-s02-clean at C0. "
        "Calibration only."
    ),
)

CALIBRATION_S02_CONVERSATION_PRESET = ExperimentPreset(
    name="calibration-s02-conversation",
    scenario_ids=("S19",),
    configuration_ids=("C0",),
    repetitions_per_configuration=5,
    rounds_per_run=6,
    conversation_mode="hybrid_self_selection",
    description=(
        "S14 opening with no physical actions and no state reports, "
        "C0 only, five repetitions. Compare against calibration-s02-clean at "
        "C0. Calibration only."
    ),
)

CALIBRATION_S21_PRESET = ExperimentPreset(
    name="calibration-s21-chope-talk-only",
    scenario_ids=("S21",),
    configuration_ids=("C0",),
    repetitions_per_configuration=1,
    rounds_per_run=6,
    conversation_mode="hybrid_self_selection",
    description=(
        "Conversation-only chope dispute (S04 opening, no actions, no scripted events, "
        "no clock) with the shared conversational-strategy prompt. C0 only; calibration only."
    ),
)

CALIBRATION_S22_PRESET = ExperimentPreset(
    name="calibration-s22-chope-resolution",
    scenario_ids=("S22",),
    configuration_ids=("C0",),
    repetitions_per_configuration=1,
    rounds_per_run=8,
    conversation_mode="hybrid_self_selection",
    description=(
        "S21 plus a shared notice that the interaction ends in some settled arrangement. "
        "Resolution-expected: do not pool with free-resolution scenarios. C0 only; "
        "calibration only."
    ),
)

CALIBRATION_S23_PRESET = ExperimentPreset(
    name="calibration-s23-chope-untimed",
    scenario_ids=("S23",),
    configuration_ids=("C0",),
    repetitions_per_configuration=1,
    rounds_per_run=8,
    conversation_mode="hybrid_self_selection",
    description=(
        "S22 with every minute figure removed from the agents' private facts. "
        "Resolution-expected: do not pool with free-resolution scenarios. C0 only; "
        "calibration only."
    ),
)

CALIBRATION_S24_PRESET = ExperimentPreset(
    name="calibration-s24-chope-timing-free",
    scenario_ids=("S24",),
    configuration_ids=("C0",),
    repetitions_per_configuration=1,
    rounds_per_run=8,
    conversation_mode="hybrid_self_selection",
    description=(
        "S23 with all timing language removed from the scenario and the shared prompt. "
        "Resolution-expected: do not pool with free-resolution scenarios. C0 only; "
        "calibration only."
    ),
)

CALIBRATION_S25_PRESET = ExperimentPreset(
    name="calibration-s25-chope-conversation",
    scenario_ids=("S25",),
    configuration_ids=("C0",),
    repetitions_per_configuration=1,
    rounds_per_run=8,
    conversation_mode="hybrid_self_selection",
    description=(
        "S24 plus a speech-only shared prompt and a priced-preference priority rule. "
        "Resolution-expected: do not pool with free-resolution scenarios. C0 only; "
        "calibration only."
    ),
)

CALIBRATION_S26_PRESET = ExperimentPreset(
    name="calibration-s26-chope-priorities",
    scenario_ids=("S26",),
    configuration_ids=("C0",),
    repetitions_per_configuration=5,
    rounds_per_run=8,
    conversation_mode="hybrid_self_selection",
    debrief_after_run=True,
    description=(
        "S25 with several private concerns per role, a closed set of seats, and a second "
        "seat that only Casey knows will free up. Resolution-expected: do not pool with "
        "free-resolution scenarios. C0 only; calibration only."
    ),
)

CALIBRATION_S27_PRESET = ExperimentPreset(
    name="calibration-s27-chope-no-notice",
    scenario_ids=("S27",),
    configuration_ids=("C0",),
    repetitions_per_configuration=5,
    rounds_per_run=8,
    conversation_mode="hybrid_self_selection",
    debrief_after_run=True,
    description=(
        "S26 without the resolution notice; the only difference from S26. Free-resolution: "
        "do not pool with resolution-expected scenarios. C0 only; calibration only."
    ),
)

CALIBRATION_S28_PRESET = ExperimentPreset(
    name="calibration-s28-chope-visible",
    scenario_ids=("S28",),
    configuration_ids=("C0",),
    repetitions_per_configuration=5,
    rounds_per_run=8,
    conversation_mode="hybrid_self_selection",
    debrief_after_run=True,
    description=(
        "S26 text with the setting visible to agents. Do not compare with runs made before "
        "the prompt-rendering fix. Resolution-expected. C0 only; calibration only."
    ),
)

CALIBRATION_S29_PRESET = ExperimentPreset(
    name="calibration-s29-chope-visible-no-notice",
    scenario_ids=("S29",),
    configuration_ids=("C0",),
    repetitions_per_configuration=5,
    rounds_per_run=8,
    conversation_mode="hybrid_self_selection",
    debrief_after_run=True,
    description=(
        "S28 without the resolution notice. Free-resolution: do not pool with S28. Do not "
        "compare with runs made before the prompt-rendering fix. C0 only; calibration only."
    ),
)

CALIBRATION_S30_PRESET = ExperimentPreset(
    name="calibration-s30-flat",
    scenario_ids=("S30",),
    configuration_ids=("C0",),
    repetitions_per_configuration=3,
    rounds_per_run=6,
    conversation_mode="hybrid_self_selection",
    debrief_after_run=True,
    description=(
        "Recurring shared-flat dispute, conversation only, no resolution notice. "
        "Free-resolution: do not pool with resolution-expected scenarios. C0 only; a small "
        "check of whether this scenario produces real resolution."
    ),
)

CALIBRATION_S30_PROFILES_PRESET = ExperimentPreset(
    name="calibration-s30-profiles",
    scenario_ids=("S30",),
    configuration_ids=("L1", "L2", "L3", "B1", "B2", "B3", "V1", "V2", "V3", "V4"),
    repetitions_per_configuration=1,
    rounds_per_run=6,
    conversation_mode="hybrid_self_selection",
    debrief_after_run=True,
    description=(
        "Does anything richer than a bare label change S30? Label only, label plus biography, "
        "and values with no label, all with neutral names. One run per cell: a screen, not a test."
    ),
)

CALIBRATION_S30_PLAIN_PRESET = ExperimentPreset(
    name="calibration-s30-plain-labels",
    scenario_ids=("S30",),
    configuration_ids=("P1", "P2", "P3"),
    repetitions_per_configuration=1,
    rounds_per_run=6,
    conversation_mode="hybrid_self_selection",
    debrief_after_run=True,
    description=(
        "S30 with 'Malay' in place of 'Singaporean Malay', same rotations as L1-L3, neutral "
        "names. One run per cell: a screen, not a test."
    ),
)

CALIBRATION_S30_MODEL_CHECK_PRESET = ExperimentPreset(
    name="calibration-s30-model-check",
    scenario_ids=("S30",),
    configuration_ids=("P1", "V1", "V2"),
    repetitions_per_configuration=1,
    rounds_per_run=6,
    conversation_mode="hybrid_self_selection",
    debrief_after_run=True,
    description=(
        "A few S30 cells for a second simulation model, to see whether the same-deal pattern "
        "is specific to gpt-5-mini. One run per cell: a screen, not a test."
    ),
)

CALIBRATION_S30_VALUES_PRESET = ExperimentPreset(
    name="calibration-s30-values",
    scenario_ids=("S30",),
    configuration_ids=("W1", "W2", "W3", "W4", "W5", "W6", "W7", "W8"),
    repetitions_per_configuration=1,
    rounds_per_run=6,
    conversation_mode="hybrid_self_selection",
    debrief_after_run=True,
    description=(
        "Can this setup detect a difference at all? Harmony versus direct values, no labels, "
        "first speaker balanced by role and value. Fixed before data: compare harmony and "
        "direct speakers on words per line, uses_right, uses_interest, and concedes."
    ),
)

CALIBRATION_S30_NAMED_PRESET = ExperimentPreset(
    name="calibration-s30-named-cultures",
    scenario_ids=("S30",),
    configuration_ids=tuple(f"N{number:02d}" for number in range(1, 11)),
    repetitions_per_configuration=1,
    rounds_per_run=6,
    conversation_mode="hybrid_self_selection",
    debrief_after_run=True,
    description=(
        "First look at culture with names: plain labels, names rotated within gender, gender "
        "and first speaker balanced. Too small for a firm answer. Fixed before data: per-agent "
        "means of uses_right, blame language, concedes, and words, across the four cultures, "
        "and separately across name gender, permuted within runs."
    ),
)

CALIBRATION_S31_PORK_PRESET = ExperimentPreset(
    name="calibration-s31-pork-check",
    scenario_ids=("S31",),
    configuration_ids=("M1", "M2", "M3", "M4"),
    repetitions_per_configuration=1,
    rounds_per_run=6,
    conversation_mode="hybrid_self_selection",
    debrief_after_run=True,
    description=(
        "Does culture come up when the dispute could touch it? Pork fat in the shared pan, "
        "names, plain labels, and biographies. A small look, not a test."
    ),
)

def _s31_preset(name: str, cells: tuple[str, ...], description: str) -> ExperimentPreset:
    return ExperimentPreset(
        name=name,
        scenario_ids=("S31",),
        configuration_ids=cells,
        repetitions_per_configuration=1,
        rounds_per_run=6,
        conversation_mode="hybrid_self_selection",
        debrief_after_run=True,
        description=description,
    )


CALIBRATION_S31_PORK_REST_PRESET = _s31_preset(
    "calibration-s31-pork-rest",
    ("M5", "M6", "M7", "M8", "M9", "M10"),
    "The rest of the pork schedule, after M1-M4. A small look, not a test.",
)
CALIBRATION_S31_LANGUAGE_PRESET = _s31_preset(
    "calibration-s31-home-language",
    ("H1", "H2", "H3", "H4"),
    "M1-M4 with private thoughts in a home language and speech in English. A small look.",
)
CALIBRATION_S31_EXPLICIT_PRESET = _s31_preset(
    "calibration-s31-explicit-culture",
    ("E1", "E2", "E3", "E4"),
    "M1-M4 told to act on typical cultural values, an upper bound. This is a behavioural "
    "instruction: never pool with other cells. A small look.",
)
CALIBRATION_S31_SAME_CULTURE_PRESET = _s31_preset(
    "calibration-s31-same-culture",
    ("G1", "G2", "G3", "G4"),
    "Four agents from one background in each run, a baseline for within-culture differences.",
)

CASE_STUDY_SMELL_PRESET = ExperimentPreset(
    name="case-study-smell",
    scenario_ids=("S32",),
    configuration_ids=("M5",),
    repetitions_per_configuration=1,
    rounds_per_run=8,
    conversation_mode="hybrid_self_selection",
    debrief_after_run=True,
    description=(
        "One attempt at a smell case study, run with --scenario and --configuration. Stop a "
        "cultural case at the first run meeting definition B, at most 5 attempts, and report "
        "every attempt. The S35 control runs a fixed 3 times."
    ),
)

CALIBRATION_S02_RECURRENCE_STAKES_PRESET = ExperimentPreset(
    name="calibration-s02-recurrence-stakes",
    scenario_ids=("S20",),
    configuration_ids=("C0",),
    repetitions_per_configuration=5,
    rounds_per_run=6,
    conversation_mode="hybrid_self_selection",
    description=(
        "S18 plus private stakes for three roles, C0 only, five repetitions. Compare "
        "against calibration-s02-recurrence at C0. Calibration only."
    ),
)

CALIBRATION_S02_CULTURAL_PRESET = ExperimentPreset(
    name="calibration-s02-cultural",
    scenario_ids=("S02",),
    configuration_ids=ALL_CONFIGURATION_IDS,
    repetitions_per_configuration=1,
    rounds_per_run=6,
    conversation_mode="hybrid_self_selection",
    description=(
        "Exploratory shared-kitchen batch across C0-C4 using neutral C0 names and "
        "background-associated C1-C4 names with the deterministic hybrid controller."
    ),
)

CALIBRATION_S02_FACTORIAL_PRESET = ExperimentPreset(
    name="calibration-s02-factorial",
    scenario_ids=("S02",),
    configuration_ids=FACTORIAL_CONFIGURATION_IDS,
    repetitions_per_configuration=1,
    rounds_per_run=6,
    conversation_mode="hybrid_self_selection",
    description=(
        "One-run-per-cell S02 two-by-two screen of explicit cultural labels and "
        "culturally associated names using the C1 role rotation."
    ),
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
        CALIBRATION_S04_CULTURAL_PRESET,
        CALIBRATION_S02_S06_PRESET,
        CALIBRATION_S02_PRESET,
        CALIBRATION_S02_EXPLICIT_PRESET,
        CALIBRATION_S02_MINIMAL_PRESET,
        CALIBRATION_S02_STAKES_PRESET,
        CALIBRATION_S02_CLEAN_PRESET,
        CALIBRATION_S02_CLEAN_STAKES_PRESET,
        CALIBRATION_S02_PERSONALITY_PRESET,
        CALIBRATION_S02_REASONS_PRESET,
        CALIBRATION_S02_RECURRENCE_PRESET,
        CALIBRATION_S02_RECURRENCE_STAKES_PRESET,
        CALIBRATION_S02_CONVERSATION_PRESET,
        CALIBRATION_S21_PRESET,
        CALIBRATION_S22_PRESET,
        CALIBRATION_S23_PRESET,
        CALIBRATION_S24_PRESET,
        CALIBRATION_S25_PRESET,
        CALIBRATION_S26_PRESET,
        CALIBRATION_S27_PRESET,
        CALIBRATION_S28_PRESET,
        CALIBRATION_S29_PRESET,
        CALIBRATION_S30_PRESET,
        CALIBRATION_S30_PROFILES_PRESET,
        CALIBRATION_S30_PLAIN_PRESET,
        CALIBRATION_S30_MODEL_CHECK_PRESET,
        CALIBRATION_S30_VALUES_PRESET,
        CALIBRATION_S30_NAMED_PRESET,
        CALIBRATION_S31_PORK_PRESET,
        CALIBRATION_S31_PORK_REST_PRESET,
        CALIBRATION_S31_LANGUAGE_PRESET,
        CALIBRATION_S31_EXPLICIT_PRESET,
        CALIBRATION_S31_SAME_CULTURE_PRESET,
        CASE_STUDY_SMELL_PRESET,
        CALIBRATION_S02_CULTURAL_PRESET,
        CALIBRATION_S02_FACTORIAL_PRESET,
        CALIBRATION_S06_PRESET,
        SMOKE_PRESET,
        FOCUSED_PILOT_PRESET,
        FULL_PILOT_PRESET,
        EXPANDED_PRESET,
    )
}


def validate_experiment_preset(preset: ExperimentPreset) -> None:
    """Validate selections and the fixed-horizon post-run evaluation design."""

    unknown_scenarios = set(preset.scenario_ids) - set(RUNNABLE_SCENARIOS)
    if unknown_scenarios:
        raise ValueError(f"Unknown scenarios: {sorted(unknown_scenarios)}")

    unknown_configs = set(preset.configuration_ids) - set(
        MATERIALIZATION_CONFIGURATION_IDS
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
    "CALIBRATION_S04_CULTURAL_PRESET",
    "CALIBRATION_S02_S06_PRESET",
    "CALIBRATION_S02_PRESET",
    "CALIBRATION_S02_EXPLICIT_PRESET",
    "CALIBRATION_S02_MINIMAL_PRESET",
    "CALIBRATION_S02_STAKES_PRESET",
    "CALIBRATION_S02_CLEAN_PRESET",
    "CALIBRATION_S02_CLEAN_STAKES_PRESET",
    "CALIBRATION_S02_PERSONALITY_PRESET",
    "CALIBRATION_S02_REASONS_PRESET",
    "CALIBRATION_S02_RECURRENCE_PRESET",
    "CALIBRATION_S02_RECURRENCE_STAKES_PRESET",
    "CALIBRATION_S21_PRESET",
    "CALIBRATION_S22_PRESET",
    "CALIBRATION_S23_PRESET",
    "CALIBRATION_S24_PRESET",
    "CALIBRATION_S25_PRESET",
    "CALIBRATION_S26_PRESET",
    "CALIBRATION_S27_PRESET",
    "CALIBRATION_S28_PRESET",
    "CALIBRATION_S29_PRESET",
    "CALIBRATION_S30_PRESET",
    "CALIBRATION_S30_PROFILES_PRESET",
    "CALIBRATION_S30_PLAIN_PRESET",
    "CALIBRATION_S30_MODEL_CHECK_PRESET",
    "CALIBRATION_S30_VALUES_PRESET",
    "CALIBRATION_S30_NAMED_PRESET",
    "CALIBRATION_S31_PORK_PRESET",
    "CALIBRATION_S31_PORK_REST_PRESET",
    "CALIBRATION_S31_LANGUAGE_PRESET",
    "CALIBRATION_S31_EXPLICIT_PRESET",
    "CALIBRATION_S31_SAME_CULTURE_PRESET",
    "CALIBRATION_S02_CONVERSATION_PRESET",
    "CALIBRATION_S02_CULTURAL_PRESET",
    "CALIBRATION_S02_FACTORIAL_PRESET",
    "CALIBRATION_S06_PRESET",
    "DEFAULT_ROUNDS_PER_RUN",
    "EXPERIMENT_PRESETS",
    "EXPANDED_PRESET",
    "ExperimentPreset",
    "FACTORIAL_CONFIGURATION_IDS",
    "FOCUSED_PILOT_PRESET",
    "FULL_PILOT_PRESET",
    "RunSpec",
    "SMOKE_PRESET",
    "get_experiment_preset",
    "iter_run_specs",
    "validate_experiment_preset",
]
