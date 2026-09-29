import json

import pytest

from tinytroupe.examples.shared_housing import (
    EPISODES,
    RESIDENT_SPECIFICATIONS,
    create_shared_housing_residents,
    create_shared_housing_scenario,
)

from testing_utils import *


EXPECTED_NAMES = {
    "wei_ling": "Wei Ling Chen",
    "ravi": "Ravi Krishnamurthy",
    "maria": "Maria Santos",
    "zhang_wei": "Zhang Wei",
}


def _messages_as_text(agent):
    return json.dumps(agent.episodic_memory.retrieve_all(), ensure_ascii=False)


@pytest.mark.core
def test_shared_housing_personas_load_with_languages_and_relationships():
    residents = create_shared_housing_residents()

    assert set(residents) == set(RESIDENT_SPECIFICATIONS)
    assert {key: agent.name for key, agent in residents.items()} == EXPECTED_NAMES

    for key, resident in residents.items():
        assert resident.get("country_of_residence") == "Singapore"
        assert resident.get("languages")
        assert resident.get("conflict_style")
        assert resident.get("household_role")
        relationship_names = {
            relationship["name"] for relationship in resident.get("relationships")
        }
        assert relationship_names == set(EXPECTED_NAMES.values()) - {EXPECTED_NAMES[key]}


@pytest.mark.core
def test_shared_housing_scenario_initializes_world_and_whatsapp_access():
    scenario = create_shared_housing_scenario()

    assert len(scenario.world.agents) == 4
    assert len(scenario.available_episodes) == 11
    assert set(EPISODES) == {episode.key for episode in scenario.available_episodes}

    for resident in scenario.residents.values():
        assert len(resident.accessible_agents) == 3
        assert resident._mental_state["location"] == "their bedroom"
        assert "WhatsApp" in json.dumps(resident._mental_state["accessible_agents"])


@pytest.mark.core
def test_bathroom_rush_limits_in_person_access_to_affected_residents():
    scenario = create_shared_housing_scenario()
    state = scenario.trigger("bathroom_rush")

    ravi = scenario.resident("ravi")
    maria = scenario.resident("maria")
    wei_ling = scenario.resident("wei_ling")

    assert state.definition.category == "everyday"
    assert maria in ravi.accessible_agents
    assert ravi in maria.accessible_agents
    assert wei_ling not in ravi.accessible_agents
    assert "early hospital shift" in _messages_as_text(maria)
    assert "early hospital shift" in _messages_as_text(ravi)


@pytest.mark.core
def test_late_kitchen_incident_posts_unnamed_group_reminder():
    scenario = create_shared_housing_scenario()
    state = scenario.trigger_late_kitchen_incident()

    assert state.definition.key == "late_kitchen_incident"
    assert scenario.current_episode == state

    for key in ("ravi", "maria", "zhang_wei"):
        messages = _messages_as_text(scenario.resident(key))
        assert "[Household WhatsApp group]" in messages
        assert "Please clean the stove after cooking, thanks." in messages

    wei_ling_messages = _messages_as_text(scenario.resident("wei_ling"))
    assert "oil residue" in wei_ling_messages
    assert "You have just posted" in wei_ling_messages


@pytest.mark.core
def test_maria_night_shift_episode_starts_as_private_conversation():
    scenario = create_shared_housing_scenario()
    scenario.trigger("maria_night_shift_return")

    maria = scenario.resident("maria")
    wei_ling = scenario.resident("wei_ling")
    ravi = scenario.resident("ravi")

    assert wei_ling in maria.accessible_agents
    assert maria in wei_ling.accessible_agents
    assert ravi not in maria.accessible_agents
    assert "Private in-person conversation" in _messages_as_text(wei_ling)
    assert "takeaway containers" not in _messages_as_text(ravi)


@pytest.mark.core
def test_unknown_episode_and_zero_step_run_are_rejected():
    scenario = create_shared_housing_scenario()

    with pytest.raises(KeyError, match="Unknown episode"):
        scenario.trigger("not_an_episode")

    with pytest.raises(ValueError, match="at least 1"):
        scenario.run_episode("kitchen_scheduling", steps=0)


@pytest.mark.core
def test_every_declared_episode_can_be_triggered_without_an_llm_call():
    scenario = create_shared_housing_scenario()

    for episode_key, definition in EPISODES.items():
        state = scenario.trigger(episode_key)
        assert state.definition == definition
        assert scenario.current_episode == state
        assert scenario.world.current_datetime == state.started_at


@pytest.mark.core
def test_run_episode_uses_reproducible_defaults(monkeypatch):
    scenario = create_shared_housing_scenario()
    received = {}

    def fake_run(steps, **kwargs):
        received["steps"] = steps
        received.update(kwargs)
        return ["actions"]

    monkeypatch.setattr(scenario.world, "run", fake_run)

    result = scenario.run_episode("maintenance_request", steps=2)

    assert result == ["actions"]
    assert received == {
        "steps": 2,
        "return_actions": True,
        "parallelize": False,
        "randomize_agents_order": False,
    }

