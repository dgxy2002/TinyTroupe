"""Registry of the ten editable conflict-scenario presets."""

from .common import BACKGROUND_CONFIGURATIONS, materialize_configuration
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


SCENARIOS = {
    scenario.scenario_id: scenario
    for scenario in (S01, S02, S03, S04, S05, S06, S07, S08, S09, S10)
}


def get_scenario(scenario_id: str):
    """Return one scenario by its S01-S10 identifier."""

    try:
        return SCENARIOS[scenario_id.upper()]
    except KeyError as exc:
        expected = ", ".join(SCENARIOS)
        raise KeyError(f"Unknown scenario {scenario_id!r}; expected {expected}.") from exc


__all__ = [
    "BACKGROUND_CONFIGURATIONS",
    "SCENARIOS",
    "get_scenario",
    "materialize_configuration",
]
