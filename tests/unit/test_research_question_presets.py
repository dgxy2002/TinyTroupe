from dataclasses import asdict

from research_questions.experiment_presets import (
    CALIBRATION_S04_HYBRID_PRESET,
    CALIBRATION_S04_PRESET,
    EXPANDED_PRESET,
    FOCUSED_PILOT_PRESET,
    FULL_PILOT_PRESET,
    SMOKE_PRESET,
    iter_run_specs,
)
from research_questions.scenario_presets import (
    BACKGROUND_CONFIGURATIONS,
    SCENARIOS,
    materialize_configuration,
)
from research_questions.scenario_presets.common import (
    AGENT_IDS,
    CULTURAL_BACKGROUNDS,
)


def test_scenario_registry_contains_ten_complete_scenarios():
    assert tuple(SCENARIOS) == tuple(f"S{number:02d}" for number in range(1, 11))
    assert all(set(scenario.agents) == set(AGENT_IDS) for scenario in SCENARIOS.values())


def test_background_rotation_is_balanced_for_every_agent_slot():
    for config_id in ("C1", "C2", "C3", "C4"):
        assert set(BACKGROUND_CONFIGURATIONS[config_id].values()) == set(
            CULTURAL_BACKGROUNDS
        )

    for agent_id in AGENT_IDS:
        assigned = {
            BACKGROUND_CONFIGURATIONS[config_id][agent_id]
            for config_id in ("C1", "C2", "C3", "C4")
        }
        assert assigned == set(CULTURAL_BACKGROUNDS)


def test_c0_omits_background_field_instead_of_assigning_a_baseline_identity():
    preset = materialize_configuration(SCENARIOS["S01"], "C0")
    assert all("cultural_background" not in agent for agent in preset["agents"].values())


def test_only_materialized_configurations_contain_background_labels():
    raw = asdict(SCENARIOS["S01"])
    configured = materialize_configuration(SCENARIOS["S01"], "C2")

    assert all("cultural_background" not in agent for agent in raw["agents"].values())
    assert {
        agent_id: agent["cultural_background"]
        for agent_id, agent in configured["agents"].items()
    } == BACKGROUND_CONFIGURATIONS["C2"]


def test_all_fifty_scenario_configurations_materialize():
    materialized = []
    for scenario in SCENARIOS.values():
        for config_id in BACKGROUND_CONFIGURATIONS:
            preset = materialize_configuration(scenario, config_id)
            materialized.append((preset["scenario_id"], preset["configuration_id"]))
            for agent_id, agent in preset["agents"].items():
                if config_id == "C0":
                    assert "cultural_background" not in agent
                else:
                    assert agent["cultural_background"] == BACKGROUND_CONFIGURATIONS[
                        config_id
                    ][agent_id]

    assert len(materialized) == 50
    assert len(set(materialized)) == 50


def test_revised_information_boundaries_and_timing_are_explicit():
    s04 = SCENARIOS["S04"]
    assert "Every table currently visible" in s04.shared_setting
    assert "uncovered a bowl" in s04.shared_trigger
    assert "does not accept" in s04.agents["B"].private_knowledge
    assert "Saw A place" in s04.agents["D"].private_knowledge

    s06 = SCENARIOS["S06"]
    assert "Chicken noodles, dry, no chilli" in s06.agents["A"].private_knowledge
    assert "default is soup with chilli" in s06.agents["B"].private_knowledge

    s10 = SCENARIOS["S10"]
    assert "doors are still closed" in s10.shared_setting
    assert "few minutes" in s10.shared_setting


def test_experiment_presets_define_expected_run_and_round_counts():
    assert (
        CALIBRATION_S04_PRESET.total_runs,
        CALIBRATION_S04_PRESET.total_simulation_rounds,
    ) == (1, 6)
    assert CALIBRATION_S04_HYBRID_PRESET.conversation_mode == "hybrid_self_selection"
    assert (SMOKE_PRESET.total_runs, SMOKE_PRESET.total_simulation_rounds) == (1, 1)
    assert (
        FOCUSED_PILOT_PRESET.total_runs,
        FOCUSED_PILOT_PRESET.total_simulation_rounds,
    ) == (45, 450)
    assert (FULL_PILOT_PRESET.total_runs, FULL_PILOT_PRESET.total_simulation_rounds) == (
        150,
        1500,
    )
    assert (EXPANDED_PRESET.total_runs, EXPANDED_PRESET.total_simulation_rounds) == (
        250,
        2500,
    )


def test_full_pilot_generates_stable_unique_run_ids_without_resolution_stopping():
    runs = list(iter_run_specs(FULL_PILOT_PRESET))
    assert runs[0].run_id == "S01-C0-R01"
    assert runs[-1].run_id == "S10-C4-R03"
    assert len({run.run_id for run in runs}) == 150
    assert all(run.rounds == 10 for run in runs)
    assert all(run.stop_on_resolution is False for run in runs)
    assert all(run.evaluate_after_run is True for run in runs)
    assert all(run.randomize_agent_order is False for run in runs)
    assert all(run.parallelize_agent_actions is False for run in runs)
