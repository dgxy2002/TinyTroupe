from unittest.mock import Mock, patch

from examples.chope_boundary_analysis import analyze_run, create_manual_review


def _talk(round_number, turn, agent, content):
    return {
        "round": round_number,
        "turn": turn,
        "agent": agent,
        "type": "TALK",
        "content": content,
    }


def test_boundary_analysis_separates_resolution_and_later_saturation():
    events = [
        _talk(1, 1, "Mr Lim", "This is my chope. Can you move so I can sit?"),
        _talk(1, 2, "Rachel Pereira", "Sorry, I'll move now so you can sit."),
        _talk(2, 5, "Mr Lim", "Thank you. The issue is settled and we can eat."),
        _talk(2, 6, "Rachel Pereira", "Thank you. The issue is settled and we can eat."),
        _talk(3, 9, "Mr Lim", "Thank you. The issue is settled and we can eat."),
        _talk(3, 10, "Rachel Pereira", "Thank you. The issue is settled and we can eat."),
        _talk(4, 13, "Mr Lim", "Thank you. The issue is settled and we can eat."),
        _talk(4, 14, "Rachel Pereira", "Thank you. The issue is settled and we can eat."),
    ]
    run = {
        "run_id": "test-001",
        "model": "openai/gpt-4o-mini",
        "completed_rounds": 4,
    }

    result, rounds = analyze_run(run, events)

    assert result["resolution_round"] == 1
    assert result["repetition_onset_round"] == 3
    assert result["saturation_round"] == 3
    assert result["post_saturation_rounds"] == 1
    assert rounds[2]["repeated_round_candidate"] is True
    assert rounds[3]["repeated_round_candidate"] is True


def test_repetition_without_resolution_is_not_saturation():
    events = []
    for round_number in range(1, 5):
        events.extend(
            [
                _talk(round_number, round_number * 4 - 3, "Mr Lim", "I still disagree."),
                _talk(
                    round_number,
                    round_number * 4 - 2,
                    "Rachel Pereira",
                    "I still disagree.",
                ),
            ]
        )
    run = {
        "run_id": "test-002",
        "model": "openai/gpt-4o-mini",
        "completed_rounds": 4,
    }

    result, _ = analyze_run(run, events)

    assert result["resolution_round"] is None
    assert result["repetition_onset_round"] == 2
    assert result["saturation_round"] is None


def test_structured_evaluator_is_primary_resolution_source():
    events = [
        _talk(1, 1, "Mr Lim", "This seat was reserved with my tissue packet."),
        _talk(2, 6, "Rachel Pereira", "Fine, we have worked something out."),
    ]
    run = {
        "run_id": "test-003",
        "model": "openai/gpt-4o-mini",
        "completed_rounds": 4,
        "planned_agent_turns": 16,
        "resolution_achieved": True,
        "resolution_turn": 6,
    }

    result, rounds = analyze_run(run, events)

    assert result["resolution_source"] == "structured_evaluator"
    assert result["resolution_round"] == 2
    assert rounds[0]["resolution_detected_by_round"] is False
    assert rounds[1]["resolution_detected_by_round"] is True


def test_manual_review_is_not_overwritten():
    output = Mock()
    output.exists.return_value = True

    with patch("examples.chope_boundary_analysis.write_csv") as write_csv:
        create_manual_review(output, [{"run_id": "test-001"}])

    write_csv.assert_not_called()
