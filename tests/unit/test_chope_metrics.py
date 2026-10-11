import pytest
from pydantic import ValidationError

from tinytroupe.examples.chope_metrics import (
    ChopeEvaluation,
    PersonaAdherence,
    boundary_events,
    compute_convergence,
    compute_observable_metrics,
    detect_practical_resolution,
    evaluate_chope_run,
    evaluation_metrics,
    flatten_actions,
    public_transcript_text,
)


def _evaluation(**overrides):
    values = {
        "conflict_emerged": True,
        "resolution_achieved": True,
        "outcome": "compromise",
        "resolution_turn": 8,
        "norm_recognized": True,
        "rachel_acknowledged_norm": True,
        "first_norm_recognizer": "Mr Lim",
        "mediator_emerged": True,
        "mediator_identity": "Nur Aisyah",
        "resolution_initiator": "Nur Aisyah",
        "immediate_capitulation": False,
        "premature_yield": False,
        "perspective_diversity": 3,
        "age_deference": False,
        "persona_adherence": PersonaAdherence(
            mr_lim=8, rachel=7, nur_aisyah=9, arjun=6
        ),
        "boundary_violations": [],
        "evidence": [
            {"category": "resolution", "agent": "Rachel Pereira", "quote": "Okay, we can share.", "turn": 6}
        ],
        "confidence": 0.84,
    }
    values.update(overrides)
    return ChopeEvaluation(**values)


def test_flatten_and_observable_metrics_exclude_private_thoughts():
    actions = [
        {
            "Mr Lim": [
                {"action": {"type": "THINK", "content": "I should confront her."}},
                {"action": {"type": "TALK", "content": "This one is choped lah."}},
            ],
            "Rachel Pereira": [
                {"action": {"type": "TALK", "content": "Sorry, maybe we can share?"}}
            ],
        }
    ]

    events = flatten_actions(actions)
    metrics = compute_observable_metrics(events)
    transcript = public_transcript_text(events)

    assert len(events) == 3
    assert events[0]["turn"] == events[1]["turn"] == 1
    assert events[2]["turn"] == 2
    assert metrics["observable_action_count"] == 2
    assert metrics["talk_action_count"] == 2
    assert metrics["singlish_count"] >= 1
    assert metrics["norm_reference_count"] >= 1
    assert metrics["apology_count"] == 1
    assert metrics["near_repeated_talk_pair_count"] == 0
    assert "confront" not in transcript


def test_evaluation_metrics_preserve_scores_and_censor_unresolved_turn():
    metrics = evaluation_metrics(
        _evaluation(resolution_achieved=False, outcome="unresolved", resolution_turn=None),
        max_turns=12,
    )

    assert metrics["persona_adherence_mean"] == 7.5
    assert metrics["resolution_turn_censored"] == 13


def test_observable_metrics_detect_repeated_same_agent_dialogue():
    events = [
        {"round": 1, "turn": 1, "agent": "Nur Aisyah", "type": "TALK", "content": "Perhaps you can share the table."},
        {"round": 2, "turn": 5, "agent": "Nur Aisyah", "type": "TALK", "content": "Perhaps you can share the table!"},
    ]

    metrics = compute_observable_metrics(events)

    assert metrics["exact_repeated_talk_pair_count"] == 1
    assert metrics["near_repeated_talk_pair_count"] == 1
    assert metrics["max_same_agent_talk_similarity"] == 1.0


def test_resolution_stop_detects_explicit_move_commitment():
    events = [
        {
            "round": 1,
            "turn": 1,
            "agent": "Mr Lim",
            "type": "TALK",
            "content": "That is my chope. Can you please move?",
        },
        {
            "round": 1,
            "turn": 2,
            "agent": "Rachel Pereira",
            "type": "TALK",
            "content": "Sorry, I’ll move aside right away.",
        },
    ]

    signal = detect_practical_resolution(events)

    assert signal["kind"] == "rachel_commits_to_move"
    assert signal["outcome"] == "consensus"
    assert signal["turn"] == 2


def test_resolution_stop_requires_commitment_not_conditional_offer():
    events = [
        {
            "round": 1,
            "turn": 1,
            "agent": "Mr Lim",
            "type": "TALK",
            "content": "If you need a seat, we can share the table.",
        },
        {
            "round": 1,
            "turn": 2,
            "agent": "Rachel Pereira",
            "type": "TALK",
            "content": "I can move aside, or we can share. Which do you prefer?",
        },
    ]

    assert detect_practical_resolution(events) is None


def test_resolution_stop_detects_mutually_committed_sharing():
    events = [
        {
            "round": 2,
            "turn": 5,
            "agent": "Mr Lim",
            "type": "TALK",
            "content": "Okay lah, we share the table so everyone can eat.",
        },
        {
            "round": 2,
            "turn": 6,
            "agent": "Rachel Pereira",
            "type": "TALK",
            "content": "Thanks, sharing the table is fine.",
        },
    ]

    signal = detect_practical_resolution(events)

    assert signal["kind"] == "principals_commit_to_share"
    assert [item["turn"] for item in signal["evidence"]] == [5, 6]


def test_structured_evaluation_rejects_out_of_range_scores():
    with pytest.raises(ValidationError):
        _evaluation(perspective_diversity=5)


def test_evaluator_uses_one_structured_call(monkeypatch):
    expected = _evaluation()

    class FakeClient:
        def __init__(self):
            self.calls = []

        def send_message(self, messages, **kwargs):
            self.calls.append((messages, kwargs))
            return expected

    fake = FakeClient()
    monkeypatch.setattr(
        "tinytroupe.examples.chope_metrics.client", lambda: fake
    )
    result = evaluate_chope_run(
        [{"round": 1, "turn": 1, "agent": "Mr Lim", "type": "TALK", "content": "This seat is reserved."}],
        "judge-model",
    )

    assert result is expected
    assert len(fake.calls) == 1
    assert fake.calls[0][1]["response_format"] is ChopeEvaluation
    assert fake.calls[0][1]["model"] == "judge-model"


def _stable_rows(count):
    return [
        {
            "run_id": f"run-{index:02d}",
            "outcome": "compromise",
            "conflict_emerged": True,
            "resolution_achieved": True,
            "norm_recognized": True,
            "rachel_acknowledged_norm": True,
            "mediator_emerged": True,
            "immediate_capitulation": False,
            "premature_yield": False,
            "age_deference": False,
            "resolution_turn_censored": 8,
            "persona_adherence_mean": 7.5,
            "perspective_diversity": 3,
        }
        for index in range(count)
    ]


def test_convergence_requires_two_consecutive_checkpoint_passes():
    rows = _stable_rows(20)
    embeddings = {row["run_id"]: [1.0, 0.0] for row in rows}

    records = compute_convergence(rows, embeddings)

    assert [record["n"] for record in records] == [10, 15, 20]
    assert records[0]["is_baseline"] is True
    assert records[1]["criteria_passed"] is True
    assert records[1]["converged"] is False
    assert records[2]["converged"] is True


def test_convergence_detects_material_outcome_shift():
    rows = _stable_rows(15)
    for row in rows[10:]:
        row["outcome"] = "escalation"
        row["resolution_achieved"] = False

    records = compute_convergence(rows)

    assert records[-1]["outcome_tvd"] > 0.10
    assert records[-1]["criteria_passed"] is False


def test_boundary_events_keep_failures_cost_gaps_and_evaluator_findings():
    events = boundary_events(
        {
            "run_id": "r-1",
            "model": "model-a",
            "status": "failed",
            "error": "timeout",
            "boundary_violations": ["Agent claimed impossible knowledge."],
            "exact_cost_complete": False,
            "total_resources": {
                "failed_calls": 1,
                "call_error_types": ["LengthFinishReasonError"],
            },
        }
    )

    assert {event["category"] for event in events} == {
        "run_failure",
        "evaluator_boundary_violation",
        "missing_exact_cost",
        "billed_api_retry",
    }


def test_boundary_events_record_resolution_source_disagreement():
    events = boundary_events(
        {
            "run_id": "r-2",
            "model": "model-a",
            "status": "completed",
            "execution_mode": "outcome",
            "deterministic_resolution_signal": {
                "kind": "rachel_commits_to_move",
                "turn": 2,
            },
            "deterministic_resolution_achieved": True,
            "deterministic_outcome": "consensus",
            "resolution_achieved": False,
            "exact_cost_complete": True,
            "total_resources": {"failed_calls": 0},
        }
    )

    assert [event["category"] for event in events] == [
        "resolution_source_disagreement"
    ]

