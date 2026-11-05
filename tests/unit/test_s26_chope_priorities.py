"""S26/S27 scenario design and the private debrief."""

import re

import pytest

from research_questions.debrief import build_debrief_messages
from research_questions.evaluator import public_transcript_text
from research_questions.models import AgentDebrief
from research_questions.scenario_presets import RUNNABLE_SCENARIOS, materialize_configuration
from research_questions.scenario_presets.s04_variants import RESOLUTION_EXPECTATION
from research_questions.simulation import (
    _agent_persona,
    create_scenario_instance,
    reset_simulation_state,
)

S25 = RUNNABLE_SCENARIOS["S25"]
S26 = RUNNABLE_SCENARIOS["S26"]
S27 = RUNNABLE_SCENARIOS["S27"]
S28 = RUNNABLE_SCENARIOS["S28"]
S29 = RUNNABLE_SCENARIOS["S29"]


def _persona(scenario):
    preset = materialize_configuration(scenario, "C0")
    return _agent_persona(
        "A",
        preset["agents"]["A"],
        preset["resolution_expectation"],
        preset["timing_free"],
        preset["conversation_only"],
        preset["priced_priority"],
    )


def test_s27_differs_from_s26_only_in_the_notice():
    assert S26.resolution_expectation == RESOLUTION_EXPECTATION
    assert S27.resolution_expectation == ""
    assert S27.agents == S26.agents
    assert S27.shared_setting == S26.shared_setting
    assert S27.shared_trigger == S26.shared_trigger
    assert S27.conversation_only and S27.timing_free


def test_both_variants_get_the_same_priority_rule():
    for scenario in (S26, S27):
        persona = _persona(scenario)
        assert persona["priority_rule_open"] is True
        assert any("not a wall" in fact for fact in persona["other_facts"])


def test_priced_flag_leaves_earlier_scenarios_unchanged():
    assert _persona(S25)["priority_rule_open"] is True
    s24 = _persona(RUNNABLE_SCENARIOS["S24"])
    assert "priority_rule_open" not in s24
    assert not any("not a wall" in fact for fact in s24["other_facts"])


@pytest.mark.parametrize("config", ["C0", "C1"])
def test_role_letters_never_reach_the_agents(config):
    preset = materialize_configuration(S26, config)
    for agent in preset["agents"].values():
        for field in ("private_knowledge", "initial_observation", "immediate_priority"):
            assert not re.search(r"(?<![A-Za-z'])[BCD]\b", agent[field]), agent[field]
            assert "Agent " not in agent[field]


def test_scenario_text_states_no_outcome():
    banned = ("should accept", "should agree", "must agree", "apologis", "apologiz", "compromise")
    text = " ".join(
        [S26.shared_setting, S26.shared_trigger]
        + [a.private_knowledge + a.immediate_priority for a in S26.agents.values()]
    ).lower()
    assert not any(word in text for word in banned)


def test_second_seat_is_known_only_to_c():
    assert "finish before" in S26.agents["C"].private_knowledge
    public = S26.shared_setting + S26.shared_trigger
    assert "finish" not in public
    for agent_id in "ABD":
        assert "finish" not in S26.agents[agent_id].private_knowledge


def _transcript(configuration="C0"):
    preset = materialize_configuration(S26, configuration)
    first = preset["agents"]["A"]["display_name"]
    second = preset["agents"]["B"]["display_name"]
    return {
        "scenario": preset,
        "run": {"completed_rounds": 1},
        "events": [
            {"round": 1, "turn": 1, "agent": first, "type": "THINK", "content": "FIRST SECRET", "action_index": 1},
            {"round": 1, "turn": 1, "agent": first, "type": "TALK", "content": "That's my seat.", "action_index": 2},
            {"round": 1, "turn": 2, "agent": second, "type": "THINK", "content": "SECOND SECRET", "action_index": 1},
        ],
    }


def test_debrief_sees_only_that_agents_private_thoughts():
    transcript = _transcript()
    first = build_debrief_messages(transcript, "A")[1]["content"]
    second = build_debrief_messages(transcript, "B")[1]["content"]
    assert "FIRST SECRET" in first and "SECOND SECRET" not in first
    assert "SECOND SECRET" in second and "FIRST SECRET" not in second
    assert "That's my seat." in first


def test_debrief_carries_background_only_when_present():
    assert "Cultural background" not in build_debrief_messages(_transcript("C0"), "A")[1]["content"]
    labelled = build_debrief_messages(_transcript("C1"), "A")[1]["content"]
    assert "Cultural background: Singaporean Chinese" in labelled


def _section(prompt, start, end):
    return prompt[prompt.find(start) : prompt.find(end)]


def test_cognitive_state_is_rendered_into_the_agent_prompt():
    reset_simulation_state()
    jamie = create_scenario_instance(S26, "C0").participants["B"]
    prompt = jamie.generate_agent_system_prompt()
    section = _section(prompt, "## Current cognitive state", "### Working memory context")
    assert "Your current location is: Hawker centre" in section
    assert "no other free seat anywhere" in section
    assert "stops at the only disputed seat" in section
    assert "Alex:" in section and "Casey:" in section and "Robin:" in section
    assert jamie._mental_state["goals"].split(",")[0] in section


def test_setting_stays_visible_after_the_model_rewrites_context():
    for scenario, expected in ((S28, True), (S26, False)):
        reset_simulation_state()
        person = create_scenario_instance(scenario, "C0").participants["B"]
        person._update_cognitive_state(context=["Alex wants my seat."])
        prompt = person.generate_agent_system_prompt()
        assert ("no other free seat anywhere" in prompt) is expected


def test_opening_event_is_stored_in_memory_only_when_pinned():
    for scenario, expected in ((S28, True), (S26, False)):
        reset_simulation_state()
        person = create_scenario_instance(scenario, "C0").participants["A"]
        memory = str(person.retrieve_recent_memories())
        assert ("What has just happened" in memory) is expected


def test_s28_and_s29_only_add_the_pin():
    assert S28.agents == S26.agents and S29.agents == S27.agents
    assert S28.shared_setting == S26.shared_setting
    assert S28.resolution_expectation == S26.resolution_expectation
    assert S29.resolution_expectation == "" and S29.priced_priority


def test_private_thoughts_never_reach_the_evaluator_text():
    assert "SECRET" not in public_transcript_text(_transcript()["events"], 1)


def test_debrief_schema_rejects_out_of_range_fairness():
    with pytest.raises(ValueError):
        AgentDebrief(
            settled="settled",
            what_was_agreed="x",
            what_i_gave_up="x",
            what_i_got="x",
            why_i_went_along="x",
            what_still_bothers_me="x",
            fairness_to_me=6,
        )
