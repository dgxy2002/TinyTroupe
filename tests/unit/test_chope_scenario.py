import json

import pytest

from tinytroupe.examples.chope import (
    PARTICIPANT_SPECIFICATIONS,
    create_chope_participants,
    create_chope_scenario,
)

from testing_utils import *


EXPECTED_NAMES = {
    "mr_lim": "Mr Lim",
    "rachel": "Rachel Pereira",
    "nur_aisyah": "Nur Aisyah",
    "arjun": "Arjun",
}


def _memory_text(agent):
    return json.dumps(agent.episodic_memory.retrieve_all(), ensure_ascii=False)


@pytest.mark.core
def test_chope_personas_load_with_explicit_independent_traits():
    participants = create_chope_participants()

    assert set(participants) == set(PARTICIPANT_SPECIFICATIONS)
    assert {key: person.name for key, person in participants.items()} == EXPECTED_NAMES
    for key, person in participants.items():
        assert person.get("country_of_residence") == "Singapore"
        assert person.get("experimental_traits")
        assert person.get("conflict_style")
        relationship_names = {
            relationship["name"] for relationship in person.get("relationships")
        }
        assert relationship_names == set(EXPECTED_NAMES.values()) - {EXPECTED_NAMES[key]}
        assert "stereotype" in " ".join(person.get("other_facts")).lower()


@pytest.mark.core
def test_chope_trigger_preserves_asymmetric_knowledge():
    scenario = create_chope_scenario()
    state = scenario.trigger()

    assert scenario.world.broadcast_if_no_target is True

    mr_lim = _memory_text(scenario.participant("mr_lim")).lower()
    rachel = _memory_text(scenario.participant("rachel")).lower()
    nur_aisyah = _memory_text(scenario.participant("nur_aisyah")).lower()
    arjun = _memory_text(scenario.participant("arjun")).lower()

    assert state.key == "tissue_packet_moved"
    assert "intending to reserve" in mr_lim
    assert "otherwise empty table" in rachel
    assert "intending to reserve" not in rachel
    assert "you do not know either person" in nur_aisyah
    assert "you do not know either person" in arjun


@pytest.mark.core
def test_chope_event_can_only_be_triggered_once():
    scenario = create_chope_scenario()
    scenario.trigger()

    with pytest.raises(RuntimeError, match="already been triggered"):
        scenario.trigger()


@pytest.mark.core
def test_table_talk_is_audible_to_all_other_participants():
    scenario = create_chope_scenario()
    mr_lim = scenario.participant("mr_lim")

    scenario.world._handle_talk(
        mr_lim,
        "This public table remark should be audible nearby.",
        target="Rachel Pereira",
    )

    for key in ("rachel", "nur_aisyah", "arjun"):
        assert "public table remark" in _memory_text(scenario.participant(key))
    assert "public table remark" not in _memory_text(mr_lim)


@pytest.mark.core
def test_chope_run_uses_fixed_sequential_defaults(monkeypatch):
    scenario = create_chope_scenario()
    received = {}

    def fake_run(steps, **kwargs):
        received["steps"] = steps
        received.update(kwargs)
        return ["actions"]

    monkeypatch.setattr(scenario.world, "run", fake_run)

    assert scenario.run(rounds=3) == ["actions"]
    assert received == {
        "steps": 3,
        "return_actions": True,
        "parallelize": False,
        "randomize_agents_order": False,
    }


@pytest.mark.core
def test_chope_scenarios_are_fresh_objects():
    first = create_chope_scenario()
    first.trigger()

    # TinyPerson names are globally registered, as expected by TinyTroupe; an
    # independent experimental run resets registries before constructing again.
    TinyPerson.clear_agents()
    TinyWorld.clear_environments()
    second = create_chope_scenario()

    assert first.world is not second.world
    assert first.participant("mr_lim") is not second.participant("mr_lim")
    assert "intending to reserve" not in _memory_text(second.participant("mr_lim")).lower()

