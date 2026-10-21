from __future__ import annotations

import json
from pathlib import Path

import pytest
from pydantic import ValidationError

from research_scenarios.analysis import analyze_run, first_consecutive_candidate
from research_scenarios.hdb_space.evaluation import HDBEvaluation
from research_scenarios.hdb_space.scenario import (
    PERSONA_FILES as HDB_PERSONA_FILES,
    PRINCIPAL_PARTICIPANTS as HDB_PRINCIPALS,
)
from research_scenarios.mrt_loud_audio.evaluation import MRTEvaluation
from research_scenarios.mrt_loud_audio.scenario import (
    PERSONA_FILES as MRT_PERSONA_FILES,
    PRINCIPAL_PARTICIPANTS as MRT_PRINCIPALS,
)
from research_scenarios.runtime import flatten_actions


ROOT = Path(__file__).resolve().parents[1]


def valid_evaluation(model):
    common = {
        "conflict_emerged": True,
        "resolution_achieved": True,
        "outcome": "consensus",
        "resolution_turn": 4,
        "evidence": [{"category": "agreement", "quote": "Agreed", "turn": 4}],
        "confidence": 0.9,
    }
    if model is HDBEvaluation:
        return model(
            **common,
            cook_goal_addressed=True,
            sensitive_housemate_goal_addressed=True,
            ventilation_protocol_agreed=True,
            dedicated_cookware_agreed=True,
            off_peak_cooking_agreed=False,
            immediate_cleanup_agreed=True,
            landlord_intervention_requested=False,
        )
    return model(
        **common,
        listener_goal_addressed=True,
        commuter_goal_addressed=True,
        audio_muted=False,
        headphones_used=True,
        volume_lowered=False,
        commuter_moved=False,
        staff_alerted=False,
        shouting_or_insults=False,
    )


@pytest.mark.parametrize("model", [HDBEvaluation, MRTEvaluation])
def test_resolution_schema_accepts_consistent_consensus(model):
    assert valid_evaluation(model).resolution_achieved is True


@pytest.mark.parametrize("model", [HDBEvaluation, MRTEvaluation])
def test_resolution_schema_rejects_unresolved_marked_resolved(model):
    data = valid_evaluation(model).model_dump()
    data.update(outcome="unresolved", resolution_achieved=True)
    with pytest.raises(ValidationError):
        model.model_validate(data)


def test_personas_are_local_and_include_scenario_goals():
    expected = {
        "hdb_space/personas/alex_tan.agent.json": "preferred dishes and ingredients",
        "hdb_space/personas/nadia_rahman.agent.json": "cross-contact",
        "mrt_loud_audio/personas/ethan_goh.agent.json": "entertainment or news",
        "mrt_loud_audio/personas/meera_iyer.agent.json": "quiet enough",
    }
    for relative_path, phrase in expected.items():
        data = json.loads((ROOT / relative_path).read_text(encoding="utf-8"))
        assert phrase.lower() in json.dumps(data).lower()


@pytest.mark.parametrize(
    ("persona_files", "principals"),
    [
        (HDB_PERSONA_FILES, HDB_PRINCIPALS),
        (MRT_PERSONA_FILES, MRT_PRINCIPALS),
    ],
)
def test_each_scenario_has_four_agents_and_two_principal_parties(
    persona_files, principals
):
    assert len(persona_files) == 4
    assert len(principals) == 2
    assert set(principals) < set(persona_files)
    assert all(
        any(path.name == filename for path in ROOT.rglob("*.agent.json"))
        for filename in persona_files.values()
    )


def test_flatten_actions_preserves_round_and_turn():
    events = flatten_actions(
        [
            {
                "Alex Tan": [{"action": {"type": "TALK", "content": "Hello"}}],
                "Nadia Rahman": [{"action": {"type": "THINK", "content": "Hmm"}}],
            }
        ]
    )
    assert events == [
        {
            "round": 1,
            "turn": 1,
            "agent": "Alex Tan",
            "action_index": 1,
            "type": "TALK",
            "content": "Hello",
            "target": None,
        },
        {
            "round": 1,
            "turn": 2,
            "agent": "Nadia Rahman",
            "action_index": 1,
            "type": "THINK",
            "content": "Hmm",
            "target": None,
        },
    ]


def test_repetition_requires_two_consecutive_candidate_rounds():
    rows = [
        {"round": 1, "repeated_round_candidate": False},
        {"round": 2, "repeated_round_candidate": True},
        {"round": 3, "repeated_round_candidate": True},
    ]
    assert first_consecutive_candidate(rows) == 2


def test_analyze_run_keeps_resolution_and_repetition_separate():
    run = {
        "run_id": "run-001",
        "scenario": "mrt-audio",
        "model": "openai/gpt-4o-mini",
        "completed_rounds": 3,
        "resolution_achieved": True,
        "resolution_round": 2,
        "outcome": "consensus",
        "total_resources": {"total_tokens": 100, "cost_usd": 0.01},
        "exact_cost_complete": True,
    }
    events = [
        {"round": 1, "turn": 1, "agent": "A", "type": "TALK", "content": "Please mute it"},
        {"round": 2, "turn": 2, "agent": "A", "type": "TALK", "content": "Thank you for muting it"},
        {"round": 3, "turn": 3, "agent": "A", "type": "TALK", "content": "Have a good trip"},
    ]
    result, _ = analyze_run(run, events)
    assert result["resolved"] is True
    assert result["resolution_round"] == 2
    assert result["repetitive"] is False
    assert result["category"] == "Resolved + not repetitive"

