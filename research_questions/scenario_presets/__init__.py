"""Registry of the ten editable conflict-scenario presets."""

from .common import (
    BACKGROUND_CONFIGURATIONS,
    FACTORIAL_CONFIGURATIONS,
    MATERIALIZATION_CONFIGURATION_IDS,
    materialize_configuration,
)
from .s01_presets import SCENARIO as S01
from .s02_presets import SCENARIO as S02
from .s03_presets import SCENARIO as S03
from .s04_presets import SCENARIO as S04
from .s05_presets import SCENARIO as S05
from .s06_presets import SCENARIO as S06
from .s07_presets import SCENARIO as S07
from .s08_presets import SCENARIO as S08
from .s09_presets import SCENARIO as S09
from .s10_presets import SCENARIO as S10
from .s02_variants import (
    CLEAN as S14,
    CLEAN_STAKES as S15,
    CONVERSATION_ONLY as S19,
    MINIMAL as S12,
    PERSONALITY as S16,
    REASONS as S17,
    RECURRENCE as S18,
    RECURRENCE_STAKES as S20,
    STAKES as S13,
)


SCENARIOS = {
    scenario.scenario_id: scenario
    for scenario in (S01, S02, S03, S04, S05, S06, S07, S08, S09, S10)
}

# Calibration-only ablations. They are runnable by id but deliberately excluded
# from SCENARIOS so full-pilot and expanded presets keep their S01-S10 scope.
EXPERIMENTAL_SCENARIOS = {scenario.scenario_id: scenario for scenario in (S12, S13, S14, S15, S16, S17, S18, S19, S20)}
RUNNABLE_SCENARIOS = {**SCENARIOS, **EXPERIMENTAL_SCENARIOS}


def get_scenario(scenario_id: str):
    """Return one scenario by its S01-S10 (or experimental S12-S20) identifier."""

    try:
        return RUNNABLE_SCENARIOS[scenario_id.upper()]
    except KeyError as exc:
        expected = ", ".join(RUNNABLE_SCENARIOS)
        raise KeyError(f"Unknown scenario {scenario_id!r}; expected {expected}.") from exc


__all__ = [
    "BACKGROUND_CONFIGURATIONS",
    "EXPERIMENTAL_SCENARIOS",
    "FACTORIAL_CONFIGURATIONS",
    "MATERIALIZATION_CONFIGURATION_IDS",
    "RUNNABLE_SCENARIOS",
    "SCENARIOS",
    "get_scenario",
    "materialize_configuration",
]
