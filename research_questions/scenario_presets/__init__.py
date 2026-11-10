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
from .s04_variants import (
    CHOPE_CONVERSATION as S25,
    CHOPE_PRIORITIES as S26,
    CHOPE_PRIORITIES_NO_NOTICE as S27,
    CHOPE_PRIORITIES_VISIBLE as S28,
    CHOPE_PRIORITIES_VISIBLE_NO_NOTICE as S29,
    CHOPE_RESOLUTION as S22,
    CHOPE_TALK_ONLY as S21,
    CHOPE_TIMING_FREE as S24,
    CHOPE_UNTIMED as S23,
)
from .s30_flat import (
    BEEF_PAN as S38,
    BEREAVEMENT_BUDDHIST as S57,
    BEREAVEMENT_CONTROL as S58,
    BEREAVEMENT_HINDU as S56,
    BEREAVEMENT_MUSLIM as S55,
    CORNER_BUDDHIST as S61,
    CORNER_CONTROL as S62,
    CORNER_HINDU as S60,
    CORNER_MUSLIM as S59,
    BEEF_SMELL as S33,
    BURNT_RICE_SMELL as S35,
    FAITH_PAN as S36,
    LANGUAGE_CONTROL as S85,
    LANGUAGE_MALAY as S83,
    LANGUAGE_MANDARIN as S82,
    LANGUAGE_TAMIL as S84,
    NOISE_BUDDHIST as S88,
    NOISE_CONTROL as S89,
    NOISE_HINDU as S87,
    NOISE_MUSLIM as S86,
    ROOM_BUDDHIST as S96,
    ROOM_CONTROL as S97,
    ROOM_HINDU as S95,
    ROOM_MUSLIM as S94,
    SMELL_CHINESE as S100,
    SMELL_CONTROL as S101,
    SMELL_INDIAN as S99,
    SMELL_MALAY as S98,
    SLOT_BUDDHIST as S92,
    SLOT_CONTROL as S93,
    SLOT_HINDU as S91,
    SLOT_MUSLIM as S90,
    FAREWELL_BUDDHIST as S73,
    FAREWELL_CONTROL as S74,
    FAREWELL_HINDU as S72,
    FAREWELL_MUSLIM as S71,
    UNIFORM_BUDDHIST as S76,
    UNIFORM_CATHOLIC as S77,
    UNIFORM_CONTROL as S78,
    UNIFORM_HINDU as S75,
    VOID_DECK_BUDDHIST as S79,
    VOID_DECK_CATHOLIC as S80,
    VOID_DECK_CONTROL as S81,
    HOUSEWARMING_BUDDHIST as S43,
    HOUSEWARMING_CONTROL as S45,
    HOUSEWARMING_HINDU as S44,
    HOUSEWARMING_MUSLIM as S42,
    HOUSEWARMING_V2_BUDDHIST as S48,
    HOUSEWARMING_V2_CONTROL as S49,
    HOUSEWARMING_V2_HINDU as S47,
    HOUSEWARMING_V2_HINDU_PERSONAL as S50,
    HOUSEWARMING_V2_MUSLIM as S46,
    INCENSE_PRACTICE as S40,
    INCENSE_SMELL as S34,
    MEDICATED_STEAM as S41,
    PEANUT_PAN as S39,
    PORK_PAN as S31,
    PORK_SMELL as S32,
    ROSTER_CHINESE as S65,
    ROSTER_V2_CHINESE as S69,
    ROSTER_V2_CONTROL as S70,
    ROSTER_V2_HINDU as S68,
    ROSTER_V2_MUSLIM as S67,
    ROSTER_CONTROL as S66,
    ROSTER_HINDU as S64,
    ROSTER_MUSLIM as S63,
    ROTA_BUDDHIST as S53,
    ROTA_CONTROL as S54,
    ROTA_HINDU as S52,
    ROTA_MUSLIM as S51,
    SHELLFISH_PAN as S37,
    SCENARIO as S30,
)
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
EXPERIMENTAL_SCENARIOS = {scenario.scenario_id: scenario for scenario in (S12, S13, S14, S15, S16, S17, S18, S19, S20, S21, S22, S23, S24, S25, S26, S27, S28, S29, S30, S31, S32, S33, S34, S35, S36, S37, S38, S39, S40, S41, S42, S43, S44, S45, S46, S47, S48, S49, S50, S51, S52, S53, S54, S55, S56, S57, S58, S59, S60, S61, S62, S63, S64, S65, S66, S67, S68, S69, S70, S71, S72, S73, S74, S75, S76, S77, S78, S79, S80, S81, S82, S83, S84, S85, S86, S87, S88, S89, S90, S91, S92, S93, S94, S95, S96, S97, S98, S99, S100, S101)}
RUNNABLE_SCENARIOS = {**SCENARIOS, **EXPERIMENTAL_SCENARIOS}


def get_scenario(scenario_id: str):
    """Return one scenario by its S01-S10 (or experimental S12-S101) identifier."""

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
