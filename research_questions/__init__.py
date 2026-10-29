"""Research definitions for the Singapore conflict pilot."""

from .experiment_presets import EXPERIMENT_PRESETS, get_experiment_preset
from .scenario_presets import SCENARIOS, get_scenario

__all__ = [
    "EXPERIMENT_PRESETS",
    "SCENARIOS",
    "get_experiment_preset",
    "get_scenario",
]
