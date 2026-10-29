from __future__ import annotations

from dataclasses import asdict
from types import SimpleNamespace

import pytest

from research_questions import evaluator, runner
from research_questions.evaluator import public_transcript_text
from research_questions.experiment_presets import RunSpec
from research_questions.models import ConflictEvaluation
from research_questions.scenario_presets import SCENARIOS
from research_questions.simulation import (
    create_scenario_instance,
    flatten_actions,
    inject_round_observation,
    reset_simulation_state,
)
from research_questions.storage import read_json, write_json_once


def valid_evaluation(rounds=2):
    return ConflictEvaluation(
        round_scores=[
            {
                "round": number,
                "peak_conflict_score": 0,
                "remaining_conflict_score": 0,
                "movement": "no_conflict",
                "evidence": "No conflict observed.",
            }
            for number in range(1, rounds + 1)
        ],
        conflict_ever_observed=False,
        conflict_topics=[],
        final_status="no_conflict",
        resolution_round=None,
        resolution_mechanism="none",
        final_reason="No incompatible demands were expressed.",
        dialogue_naturalness_score=4,
        dialogue_repetition_score=1,
        dialogue_groundedness_score=5,
        dialogue_substantiveness_score=3,
        independent_reasoning_score=4,
        premature_consensus_observed=False,
        dialogue_quality_notes=["Speech is concise and grounded."],
        substantive_insights=["The parties distinguish urgency from entitlement."],
        position_change_notes=["No unjustified position change occurred."],
    )


def test_public_transcript_keeps_rounds_and_excludes_private_actions():
    events = [
        {
            "round": 1,
            "turn": 1,
            "agent": "Agent A",
            "type": "THINK",
            "content": "private thought",
        },
        {
            "round": 1,
            "turn": 1,
            "agent": "Agent A",
            "type": "TALK",
            "content": "Hello",
        },
        {
            "round": 2,
            "turn": 0,
            "agent": "Environment",
            "type": "OBSERVE",
            "content": "Two minutes pass and no one moves.",
        },
    ]
    rendered = public_transcript_text(events, completed_rounds=2)
    assert "private thought" not in rendered
    assert "Agent A: Hello" in rendered
    assert "## Round 2" in rendered
    assert "Public environment update" in rendered
    assert "Two minutes pass" in rendered


def test_evaluation_rejects_missing_rounds_and_normalizes_resolution_round():
    with pytest.raises(ValueError, match="Expected round scores"):
        valid_evaluation(rounds=1).validate_round_count(2)

    evaluation = ConflictEvaluation(
        round_scores=[
            {
                "round": 1,
                "peak_conflict_score": 2,
                "remaining_conflict_score": 0,
                "movement": "resolved",
                "evidence": "Settled.",
            },
            {
                "round": 2,
                "peak_conflict_score": 2,
                "remaining_conflict_score": 2,
                "movement": "reopened",
                "evidence": "Reopened.",
            },
            {
                "round": 3,
                "peak_conflict_score": 2,
                "remaining_conflict_score": 0,
                "movement": "resolved",
                "evidence": "Settled again.",
            },
        ],
        conflict_ever_observed=True,
        conflict_topics=["seat"],
        final_status="resolved",
        resolution_round=1,
        resolution_mechanism="compromise",
        final_reason="The later disagreement was settled in the last round.",
        dialogue_naturalness_score=4,
        dialogue_repetition_score=1,
        dialogue_groundedness_score=5,
        dialogue_substantiveness_score=3,
        independent_reasoning_score=4,
        premature_consensus_observed=False,
        dialogue_quality_notes=["Speech is concise and grounded."],
        substantive_insights=["The parties distinguish urgency from entitlement."],
        position_change_notes=["No unjustified position change occurred."],
    ).validate_round_count(3)
    assert evaluation.resolution_round == 3
    assert "Adjusted resolution_round from 1 to 3" in evaluation.normalization_notes[0]


def test_evaluator_makes_one_blinded_structured_call(monkeypatch):
    class FakeClient:
        def __init__(self):
            self.calls = []

        def send_message(self, messages, **kwargs):
            self.calls.append((messages, kwargs))
            return valid_evaluation(rounds=1)

    fake = FakeClient()
    monkeypatch.setattr(evaluator, "client", lambda: fake)
    result = evaluator.evaluate_transcript(
        events=[
            {
                "round": 1,
                "turn": 1,
                "agent": "Agent A",
                "type": "TALK",
                "content": "Could you move this?",
            }
        ],
        shared_setting="A shared corridor.",
        completed_rounds=1,
        evaluator_model="judge-model",
    )
    assert result.final_status == "no_conflict"
    assert len(fake.calls) == 1
    messages, kwargs = fake.calls[0]
    serialized = str(messages)
    assert "Singaporean Chinese" not in serialized
    assert "cultural_background" not in serialized
    assert kwargs["response_format"] is ConflictEvaluation


def test_agent_factory_omits_c0_background_and_uses_custom_prompt():
    reset_simulation_state()
    c0 = create_scenario_instance(SCENARIOS["S04"], "C0")
    assert all("cultural_background" not in person._persona for person in c0.participants.values())
    assert all(
        "There is no required conflict" in person._init_system_message
        for person in c0.participants.values()
    )

    reset_simulation_state()
    c2 = create_scenario_instance(SCENARIOS["S04"], "C2")
    assert c2.participants["A"]._persona["cultural_background"] == "Singaporean Malay"
    assert c2.participants["B"]._persona["cultural_background"] == "Singaporean Indian"
    reset_simulation_state()


def test_s04_seat_actions_change_public_world_state():
    reset_simulation_state()
    instance = create_scenario_instance(SCENARIOS["S04"], "C0")
    inject_round_observation(instance, 4)

    instance.world._handle_seat_action(
        instance.participants["D"],
        {"type": "TAKE_SEAT", "target": "alternative_seat},{"},
    )
    instance.world._handle_seat_action(
        instance.participants["A"],
        {"type": "TAKE_SEAT", "target": "alternative_seat"},
    )
    instance.world._handle_seat_action(
        instance.participants["B"],
        {"type": "LEAVE_SEAT", "target": "disputed_seat"},
    )
    instance.world._handle_seat_action(
        instance.participants["D"],
        {"type": "TAKE_SEAT", "target": "disputed_seat"},
    )

    assert instance.world.seat_occupants["alternative_seat"] == "Agent D"
    assert instance.world.seat_occupants["disputed_seat"] is None
    rendered = " ".join(
        event["content"] for event in instance.world.public_state_events
    )
    assert "Agent D physically takes alternative_seat" in rendered
    assert "occupied by Agent D" in rendered
    assert "Agent B physically leaves disputed_seat" in rendered
    assert "already occupy alternative_seat" in rendered
    reset_simulation_state()


def test_face_to_face_talk_distinguishes_addressee_from_overhearers():
    reset_simulation_state()
    instance = create_scenario_instance(SCENARIOS["S04"], "C0")

    instance.world._handle_talk(
        instance.participants["A"],
        "Could you let me use this seat?",
        target="B",
    )

    b_memory = instance.participants["B"].episodic_memory.retrieve_all()[-1]
    c_memory = instance.participants["C"].episodic_memory.retrieve_all()[-1]
    assert b_memory["content"]["stimuli"][0]["type"] == "CONVERSATION"
    assert c_memory["content"]["stimuli"][0]["type"] == "SOCIAL"
    assert (
        "You overhear Agent A say to Agent B"
        in c_memory["content"]["stimuli"][0]["content"]
    )
    reset_simulation_state()


def test_hybrid_scheduler_prioritizes_direct_reply_then_rotates():
    reset_simulation_state()
    instance = create_scenario_instance(SCENARIOS["S04"], "C0")
    instance.world.scheduler_cursor = 2
    instance.world.pending_reply_agent = "Agent B"

    assert instance.world._scheduler_candidate_names() == [
        "Agent B",
        "Agent C",
        "Agent D",
        "Agent A",
    ]

    instance.world.scheduler_direct_reply_streak = 2
    assert instance.world._scheduler_candidate_names(
        defer_direct_reply=True
    ) == [
        "Agent C",
        "Agent D",
        "Agent A",
        "Agent B",
    ]
    reset_simulation_state()


def test_flatten_actions_preserves_multiple_hybrid_turns_in_one_round():
    events = flatten_actions(
        [
            [
                {
                    "Agent A": [
                        {"action": {"type": "TALK", "content": "B?", "target": "B"}}
                    ]
                },
                {
                    "Agent B": [
                        {"action": {"type": "TALK", "content": "Yes.", "target": "A"}}
                    ]
                },
            ]
        ]
    )

    assert [(event["round"], event["agent"], event["turn"]) for event in events] == [
        (1, "Agent A", 1),
        (1, "Agent B", 2),
    ]


def test_s02_kitchen_actions_keep_issues_and_access_observable():
    reset_simulation_state()
    instance = create_scenario_instance(SCENARIOS["S02"], "C0")
    inject_round_observation(instance, 2)

    instance.world._handle_kitchen_action(
        instance.participants["A"], {"type": "MOVE_LAUNDRY", "target": "drying_rack"}
    )
    instance.world._handle_kitchen_action(
        instance.participants["B"], {"type": "OPEN_WINDOW", "target": "kitchen_window"}
    )
    instance.world._handle_kitchen_action(
        instance.participants["C"],
        {"type": "LABEL_PERSONAL_UTENSILS", "target": "personal_utensils"},
    )
    instance.world._handle_kitchen_action(
        instance.participants["A"], {"type": "RELEASE_STOVE", "target": "stove"}
    )
    instance.world._handle_kitchen_action(
        instance.participants["D"], {"type": "TAKE_STOVE", "target": "stove"}
    )

    assert instance.world.window_open is True
    assert instance.world.laundry_protected is True
    assert instance.world.personal_utensils_labeled is True
    assert instance.world.stove_occupant == "Agent D"
    assert instance.world.shared_utensils_clean is False
    reset_simulation_state()


def test_s06_order_actions_distinguish_recording_preparation_and_service():
    reset_simulation_state()
    instance = create_scenario_instance(SCENARIOS["S06"], "C0")

    instance.world._handle_order_action(
        instance.participants["B"],
        {"type": "RECORD_ORDER", "target": "dry_no_chilli"},
    )
    instance.world._handle_order_action(
        instance.participants["B"],
        {"type": "START_PREPARATION", "target": "dry_no_chilli"},
    )
    instance.world._handle_order_action(
        instance.participants["B"], {"type": "SERVE_ORDER", "target": "order"}
    )

    assert instance.world.recorded_spec == "dry_no_chilli"
    assert instance.world.preparation_spec == "dry_no_chilli"
    assert instance.world.served is True
    rendered = " ".join(event["content"] for event in instance.world.public_state_events)
    assert "records the order specification as dry_no_chilli" in rendered
    assert "physically starts preparing dry_no_chilli" in rendered
    assert "physically serves one dry_no_chilli order" in rendered
    assert "focal customer transaction is complete" in instance.world.prepare_round(
        4, "Twenty more seconds have passed."
    )
    reset_simulation_state()


def test_immutable_json_refuses_overwrite(tmp_path):
    path = tmp_path / "artifact.json"
    write_json_once(path, {"value": 1})
    with pytest.raises(FileExistsError):
        write_json_once(path, {"value": 2})
    assert read_json(path) == {"value": 1}


def test_simulation_stage_saves_complete_immutable_transcript(monkeypatch, tmp_path):
    class FakeWorld:
        def encode_complete_state(self):
            return {"fake": "state"}

        def decode_complete_state(self, state):
            assert state == {"fake": "state"}

    fake_preset = {
        "scenario_id": "S04",
        "configuration_id": "C0",
        "shared_setting": "A hawker centre.",
        "shared_trigger": "Agent A arrives at the table.",
        "agents": {},
    }
    monkeypatch.setattr(runner, "reset_simulation_state", lambda: None)
    monkeypatch.setattr(runner, "_reset_client_usage", lambda: None)
    monkeypatch.setattr(runner.config_manager, "update", lambda *args: None)
    monkeypatch.setattr(runner, "_call_records", lambda: [])
    monkeypatch.setattr(
        runner,
        "create_scenario_instance",
        lambda *args: SimpleNamespace(preset=fake_preset, world=FakeWorld()),
    )
    monkeypatch.setattr(
        runner,
        "run_one_round",
        lambda instance, conversation_mode="fixed_round_robin": [
            {
                "Agent A": [
                    {
                        "action": {
                            "type": "TALK",
                            "content": "Is this seat taken?",
                            "target": "Agent B",
                        }
                    }
                ]
            }
        ],
    )
    spec = RunSpec(
        run_id="S04-C0-R01",
        experiment_name="smoke",
        scenario_id="S04",
        configuration_id="C0",
        repetition=1,
        rounds=1,
        stop_on_resolution=False,
        evaluate_after_run=True,
        randomize_agent_order=False,
        parallelize_agent_actions=False,
    )

    transcript = runner.execute_simulation_run(
        run_spec=spec,
        simulation_model="simulation-model",
        output_dir=tmp_path,
    )

    transcript_path = tmp_path / "transcripts" / "S04-C0-R01.json"
    assert transcript_path.exists()
    assert (tmp_path / "transcripts" / "S04-C0-R01.md").exists()
    assert (tmp_path / "resources" / "S04-C0-R01.json").exists()
    assert not (tmp_path / "checkpoints" / "S04-C0-R01.json").exists()
    assert transcript["run"]["completed_rounds"] == 1
    assert transcript["events"][0]["content"] == "Is this seat taken?"


def test_execute_evaluation_writes_separate_artifact(monkeypatch, tmp_path):
    monkeypatch.setattr(runner, "_call_records", lambda: [])
    monkeypatch.setattr(
        runner,
        "evaluate_transcript",
        lambda **kwargs: valid_evaluation(rounds=kwargs["completed_rounds"]),
    )
    transcript = {
        "run": {
            "run_id": "S04-C0-R01",
            "scenario_id": "S04",
            "configuration_id": "C0",
            "repetition": 1,
            "completed_rounds": 1,
        },
        "scenario": {
            "shared_setting": "A hawker centre.",
            "shared_trigger": "The group must choose one table.",
        },
        "events": [],
    }
    artifact = runner.execute_evaluation(
        transcript=transcript,
        evaluator_model="judge-model",
        output_dir=tmp_path,
        evaluator_max_completion_tokens=1000,
    )
    path = tmp_path / "evaluations" / "S04-C0-R01.json"
    assert path.exists()
    assert artifact["evaluation"]["final_status"] == "no_conflict"
    assert "cultural_background" not in path.read_text(encoding="utf-8")


def test_dry_run_cli_does_not_create_outputs(tmp_path, capsys):
    exit_code = runner.main(
        [
            "--preset",
            "smoke",
            "--dry-run",
            "--output-root",
            str(tmp_path),
            "--simulation-model",
            "simulation-model",
            "--evaluator-model",
            "judge-model",
        ]
    )
    output = capsys.readouterr().out
    assert exit_code == 0
    assert '"run_ids": [' in output
    assert "S04-C0-R01" in output
    assert list(tmp_path.iterdir()) == []


def test_run_spec_roundtrip_shape():
    spec = RunSpec(
        run_id="S04-C0-R01",
        experiment_name="smoke",
        scenario_id="S04",
        configuration_id="C0",
        repetition=1,
        rounds=1,
        stop_on_resolution=False,
        evaluate_after_run=True,
        randomize_agent_order=False,
        parallelize_agent_actions=False,
    )
    assert RunSpec(**asdict(spec)) == spec
