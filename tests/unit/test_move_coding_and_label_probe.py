"""Move coding, its reliability helpers, and the label probe design."""

import random
import re
from pathlib import Path
from typing import get_args

import pytest

from research_questions import label_probe as probe
from research_questions.coding import (
    CODING_SYSTEM_PROMPT,
    MOVE_DEFINITIONS,
    build_coding_input,
    strip_strategy_label,
)
from research_questions.coding_report import cohen_kappa, concern_presence
from research_questions.models import (
    AgentConcernCode,
    ArrangementCode,
    ConcernNote,
    ConcernTag,
    RunCoding,
    TurnCode,
)
from research_questions.runner import coding_dirname
from research_questions.scenario_presets import RUNNABLE_SCENARIOS, materialize_configuration
from research_questions.simulation import AGENT_PROMPT_PATH, create_scenario_instance, reset_simulation_state


def _turn(line):
    return TurnCode(
        line=line, uses_interest=False, uses_right=False, uses_power=False,
        concedes=False, conditional_ask=False,
    )


def _coding(lines):
    return RunCoding(
        turns=[_turn(line) for line in lines],
        agents=[
            AgentConcernCode(
                agent="Agent A",
                concerns=[
                    ConcernNote(tag="access", detail="stove", in_thoughts=True, in_speech=False),
                    ConcernNote(tag="respect", detail="not asked", in_thoughts=True, in_speech=True),
                ],
            )
        ],
        arrangement=ArrangementCode(
            exists=False, covers=[], unsettled=[], gave_way=[], summary="None."
        ),
    )


def test_coding_prompt_is_universal():
    assert CODING_SYSTEM_PROMPT.startswith(MOVE_DEFINITIONS)
    for tag in get_args(ConcernTag):
        assert f"- {tag}:" in CODING_SYSTEM_PROMPT
    for word in ("tissue", "packet", "stove", "pan", "hawker", "kitchen", "flatmate", "housemate"):
        assert not re.search(rf"\b{word}\b", CODING_SYSTEM_PROMPT, re.I), word


def test_new_coder_version_gets_its_own_folder():
    name = coding_dirname("anthropic/claude-haiku-5.5")
    assert name == "coding-move-coding-v3-anthropic-claude-haiku-5-5"


def test_concern_presence_separates_thought_from_speech():
    run = _coding([1]).model_dump(mode="json")
    assert concern_presence(run, "in_thoughts") == {("Agent A", "access"), ("Agent A", "respect")}
    assert concern_presence(run, "in_speech") == {("Agent A", "respect")}


@pytest.mark.parametrize(
    "text, expected",
    [
        ("STRATEGY: ASSERT. I want the seat.", "I want the seat."),
        ("STRATEGY: COUNTER_PROPOSE — wait a bit", "wait a bit"),
        ("No label here.", "No label here."),
    ],
)
def test_strategy_labels_are_removed(text, expected):
    assert strip_strategy_label(text) == expected


def test_coder_input_numbers_lines_and_hides_labels():
    events = [
        {"type": "THINK", "agent": "Agent A", "round": 1, "content": "STRATEGY: ASSERT. Mine."},
        {"type": "TALK", "agent": "Agent A", "round": 1, "content": "That's my seat."},
        {"type": "TALK", "agent": "Agent B", "round": 1, "content": "   "},
        {"type": "DONE", "agent": "Agent B", "round": 1, "content": "done"},
        {"type": "TALK", "agent": "Agent B", "round": 2, "content": "No."},
    ]
    text, lines = build_coding_input(events, "A table.")
    assert lines == 2
    assert "[1] (round 1) Agent A: That's my seat." in text
    assert "[2] (round 2) Agent B: No." in text
    assert "STRATEGY" not in text and "ASSERT" not in text


def test_run_coding_rejects_skipped_lines():
    assert _coding([1, 2]).validate_lines(2)
    with pytest.raises(ValueError):
        _coding([1, 3]).validate_lines(2)


def test_kappa_known_values():
    assert cohen_kappa([1, 1, 0, 0], [1, 1, 0, 0]) == 1
    assert cohen_kappa([1, 0, 1, 0], [1, 1, 0, 0]) == 0
    assert cohen_kappa([1, 1, 1], [1, 1, 1]) is None
    assert round(cohen_kappa([1, 1, 1, 0, 0, 0], [1, 1, 0, 0, 0, 0]), 3) == 0.667


def test_plan_is_balanced_stable_and_covers_every_cell():
    plan = probe.build_plan(2)
    assert len(plan) == 2 * 2 * 9 * 2
    assert len({item["key"] for item in plan}) == len(plan)
    assert plan == probe.build_plan(2)
    assert [item["key"] for item in plan] != sorted(item["key"] for item in plan)
    shards = [[item for index, item in enumerate(plan) if index % 6 == shard] for shard in range(6)]
    assert sum(len(shard) for shard in shards) == len(plan)


@pytest.mark.parametrize("role, moment", [("B", "B_hears_demand"), ("A", "A_hears_refusal")])
def test_associated_configuration_gives_the_role_that_label(role, moment):
    assert probe.MOMENTS[moment]["role"] == role
    for background in probe.CULTURAL_BACKGROUNDS:
        config = probe.configuration_for(role, background, "associated")
        preset = materialize_configuration(RUNNABLE_SCENARIOS["S28"], config)
        assert preset["agents"][role]["cultural_background"] == background
        assert probe.configuration_for(role, background, "neutral") == "C0"


def test_rule_removal_touches_only_the_rule():
    template = Path(AGENT_PROMPT_PATH).read_text(encoding="utf-8")
    without = probe.template_without_rule(template)
    assert "biographical fact" not in without
    assert "A label alone" not in without
    assert len(template) - len(without) == sum(len(line) for line in probe.RULE_LINES)
    assert "Do not invent friendship" in without


def test_neutral_label_reaches_only_the_probed_agent():
    reset_simulation_state()
    instance = create_scenario_instance(RUNNABLE_SCENARIOS["S28"], "C0")
    person = instance.participants["B"]
    person.include_persona_definitions({"cultural_background": "Singaporean Malay"})
    assert person.name == "Jamie"
    assert '"cultural_background": "Singaporean Malay"' in person.generate_agent_system_prompt()
    assert "cultural_background" not in instance.participants["A"].generate_agent_system_prompt()


def test_replies_are_anonymised_for_the_coder():
    record = {"moment": "B_hears_demand", "agent_name": "Fatimah", "other_name": "John"}
    assert probe.anonymize_reply("John, wait. Fatimah is eating.", record) == (
        "Agent A, wait. Agent B is eating."
    )
    batch = [{**record, "talk": "John, wait."}]
    text = probe._reply_batch_text("B_hears_demand", batch)
    assert "John" not in text and "Fatimah" not in text and "Malay" not in text


def test_permutation_test_separates_signal_from_noise():
    signal = [("s", group, value) for group, value in [("a", 1.0)] * 20 + [("b", 0.0)] * 20]
    assert probe.stratified_permutation_p(signal, permutations=300) < 0.01


def test_permutation_test_is_calibrated_under_no_effect():
    rng = random.Random(7)
    groups = ("a", "b", "c", "d")
    p_values = []
    for trial in range(60):
        rows = [
            (stratum, groups[index % 4], float(rng.random() < 0.4))
            for stratum in range(4)
            for index in range(20)
        ]
        p_values.append(probe.stratified_permutation_p(rows, permutations=200, seed=trial))
    below = sum(value < 0.05 for value in p_values) / len(p_values)
    assert below <= 0.15
    assert 0.3 < sum(p_values) / len(p_values) < 0.7


def test_outcomes_treat_silence_correctly():
    silent = {"key": "k", "talk": "", "think": "Chinese food"}
    assert probe.outcome_value(silent, {}, "spoke") == 0
    assert probe.outcome_value(silent, {}, "words") is None
    assert probe.outcome_value(silent, {}, "concedes") is None
    assert probe.outcome_value(silent, {}, "mentions_identity") == 1


def test_holm_correction():
    result = probe.holm({"a": 0.01, "b": 0.04, "c": 0.03})
    assert result == {"a": 0.03, "c": 0.06, "b": 0.06}
